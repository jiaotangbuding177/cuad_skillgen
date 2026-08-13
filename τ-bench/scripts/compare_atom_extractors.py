"""Minimal, held-out-safe rule-vs-LLM Knowledge Atom extraction comparison.

The script deliberately compares extraction only. It does not compile a Skill,
read test tasks, or let the LLM see gold trajectories. The output is suitable
for deciding whether an LLM extractor is worth introducing as a second-stage
component; it is not a benchmark result.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import urllib.request
from collections import Counter
from pathlib import Path
from typing import Any

from action_compiler import build_typed_atoms
from common import PROCESSED_ROOT, ROOT, read_jsonl, write_json


TOKEN_RE = re.compile(r"[a-z0-9_]+")
ALLOWED_TYPES = {
    "fact", "precondition", "required_input", "permission", "prohibition",
    "confirmation", "actor_constraint", "postcondition", "exception",
    "escalation", "communication_requirement",
}


def tokens(text: str) -> set[str]:
    return set(TOKEN_RE.findall((text or "").lower()))


def similarity(left: str, right: str) -> float:
    a, b = tokens(left), tokens(right)
    return len(a & b) / len(a | b) if a and b else 0.0


def load_config(model_override: str | None, base_override: str | None) -> tuple[str, str, str]:
    # common.py loads τ-bench/.env without printing values.
    model = (model_override or os.environ.get("TAU3_MODEL_NAME") or "").strip()
    base_url = (base_override or os.environ.get("TAU3_LLM_BASE_URL") or os.environ.get("OPENAI_BASE_URL") or "").strip()
    api_key = (os.environ.get("TAU3_LLM_API_KEY") or os.environ.get("OPENAI_API_KEY") or "").strip()
    if not model or not base_url or not api_key:
        raise SystemExit("Missing TAU3_MODEL_NAME, OPENAI_BASE_URL/TAU3_LLM_BASE_URL, or API key in .env")
    return model, base_url.rstrip("/"), api_key


def select_input(domain: str, max_sections: int) -> dict[str, Any]:
    root = PROCESSED_ROOT / domain
    sections = [section for section in read_jsonl(root / "documents" / "policy_sections.jsonl") if section.get("text", "").strip()]
    # Keep the case small but structurally mixed: policy rules plus tool
    # contracts. No train/test task is passed to the LLM.
    selected_sections = sections[:max_sections]
    tools = json.loads((root / "documents" / "tool_catalog.json").read_text(encoding="utf-8"))["tools"]
    selected_tools = tools[: min(8, len(tools))]
    return {"sections": selected_sections, "tools": selected_tools}


def llm_extract(data: dict[str, Any], model: str, base_url: str, api_key: str) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    source = {
        "policy_sections": [
            {"title": section["title"], "text": section["text"], "source": section["source"]}
            for section in data["sections"]
        ],
        "tool_contracts": [
            {"name": tool["name"], "requestor": tool["requestor"], "parameters": tool["parameters"], "description": tool["description"]}
            for tool in data["tools"]
        ],
    }
    system = (
        "You extract executable Knowledge Atoms from enterprise SOP text. "
        "Return JSON only with key atoms. Each atom must contain type, subject, text, "
        "object (string or null), and source_title. Do not invent facts. Split compound "
        "rules when possible. Allowed types: " + ", ".join(sorted(ALLOWED_TYPES))
    )
    user = json.dumps(source, ensure_ascii=False)
    payload = {
        "model": model,
        "temperature": 0,
        "messages": [{"role": "system", "content": system}, {"role": "user", "content": user}],
        "response_format": {"type": "json_object"},
    }
    request = urllib.request.Request(
        base_url + "/chat/completions",
        data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
        headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(request, timeout=180) as response:
        raw = json.loads(response.read().decode("utf-8"))
    content = raw["choices"][0]["message"]["content"]
    content = content.strip()
    if content.startswith("```"):
        content = re.sub(r"^```(?:json)?\s*|\s*```$", "", content, flags=re.I | re.S).strip()
    parsed = json.loads(content)
    response_shape = "object"
    if isinstance(parsed, list):
        response_shape = "array"
        atoms = parsed
    elif isinstance(parsed, dict):
        atoms = parsed.get("atoms", [])
    else:
        raise ValueError("LLM response must be a JSON object or array")
    if not isinstance(atoms, list):
        raise ValueError("LLM response key 'atoms' is not a list")
    valid = []
    invalid = []
    for index, atom in enumerate(atoms, 1):
        if not isinstance(atom, dict) or atom.get("type") not in ALLOWED_TYPES or not str(atom.get("text", "")).strip():
            invalid.append({"index": index, "atom": atom})
            continue
        valid.append({
            "atom_id": f"LLM-{index:04d}", "type": atom["type"], "subject": atom.get("subject", "policy"),
            "text": str(atom["text"]).strip(), "object": atom.get("object"),
            "source": {"title": atom.get("source_title")}, "origin": "llm_extractor",
        })
    usage = raw.get("usage") or {}
    return valid, {
        "invalid_atoms": invalid, "usage": usage, "request_id": raw.get("id"),
        "response_shape": response_shape,
    }


def compare(rule_atoms: list[dict[str, Any]], llm_atoms: list[dict[str, Any]], threshold: float) -> dict[str, Any]:
    matches = []
    used: set[int] = set()
    for rule in rule_atoms:
        candidates = sorted(
            ((similarity(rule["text"], llm["text"]), index, llm) for index, llm in enumerate(llm_atoms) if index not in used),
            reverse=True,
        )
        if candidates and candidates[0][0] >= threshold:
            score, index, llm = candidates[0]
            used.add(index)
            matches.append({
                "rule_atom_id": rule["atom_id"], "llm_atom_id": llm["atom_id"],
                "similarity": round(score, 4), "rule_type": rule["type"], "llm_type": llm["type"],
                "type_match": rule["type"] == llm["type"], "rule_text": rule["text"], "llm_text": llm["text"],
            })
    type_confusions = Counter(
        f"{row['rule_type']}->{row['llm_type']}" for row in matches if not row["type_match"]
    )
    matched_rule = len(matches)
    return {
        "rule_atom_count": len(rule_atoms), "llm_atom_count": len(llm_atoms),
        "text_match_count": matched_rule,
        "text_recall": matched_rule / len(rule_atoms) if rule_atoms else None,
        "llm_precision": matched_rule / len(llm_atoms) if llm_atoms else None,
        "type_accuracy_on_matches": sum(row["type_match"] for row in matches) / matched_rule if matched_rule else None,
        "type_confusions": dict(type_confusions), "matches": matches,
        "llm_unmatched_atoms": [atom for index, atom in enumerate(llm_atoms) if index not in used],
        "rule_unmatched_atoms": [atom for atom in rule_atoms if atom["atom_id"] not in {row["rule_atom_id"] for row in matches}],
        "rule_type_distribution": dict(Counter(atom["type"] for atom in rule_atoms)),
        "llm_type_distribution": dict(Counter(atom["type"] for atom in llm_atoms)),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Compare deterministic and LLM Knowledge Atom extraction")
    parser.add_argument("--domain", choices=["retail", "airline", "telecom", "banking_knowledge"], default="telecom")
    parser.add_argument("--max-sections", type=int, default=3)
    parser.add_argument("--model")
    parser.add_argument("--base-url")
    parser.add_argument("--threshold", type=float, default=0.55)
    parser.add_argument("--output", type=Path, default=ROOT / "results" / "evaluation" / "atom_extraction_llm_comparison.json")
    args = parser.parse_args()
    model, base_url, api_key = load_config(args.model, args.base_url)
    data = select_input(args.domain, args.max_sections)
    rule_atoms = build_typed_atoms(data)
    llm_atoms, llm_meta = llm_extract(data, model, base_url, api_key)
    result = {
        "case_type": "minimal_extractor_comparison_not_a_benchmark_result",
        "domain": args.domain, "max_sections": args.max_sections, "similarity_threshold": args.threshold,
        "model": model, "base_url_host": re.sub(r"^https?://", "", base_url).split("/", 1)[0],
        "input_sha256": hashlib.sha256(json.dumps(data, sort_keys=True, ensure_ascii=False).encode()).hexdigest(),
        "held_out_boundary": {"uses_test_tasks": False, "uses_train_tasks": False, "uses_reward_labels": False},
        "comparison": compare(rule_atoms, llm_atoms, args.threshold),
        "llm_meta": llm_meta,
        "rule_atoms": rule_atoms,
        "llm_atoms": llm_atoms,
        "interpretation": [
            "Text matching is a lexical diagnostic, not semantic ground truth.",
            "Type accuracy is computed only on text-matched pairs.",
            "A small case cannot establish that LLM extraction improves downstream τ³ performance.",
        ],
    }
    write_json(args.output, result)
    summary = {key: result["comparison"][key] for key in ("rule_atom_count", "llm_atom_count", "text_recall", "llm_precision", "type_accuracy_on_matches")}
    print(json.dumps({"model": model, "input_sha256": result["input_sha256"], **summary}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
