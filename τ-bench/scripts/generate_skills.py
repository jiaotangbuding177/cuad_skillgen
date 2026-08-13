from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import time
import urllib.request
from collections import Counter
from pathlib import Path
from typing import Any

from common import DOMAINS, PROCESSED_ROOT, ROOT, read_json, read_jsonl, sha256_file, write_json
from action_compiler import (
    build_action_modules,
    build_local_motifs,
    build_semantic_graph,
    build_tool_cards,
    build_typed_atoms,
    package_contract_hash,
    render_catalog_skill,
)


METHODS = [
    "no_skill",
    "raw_policy_rag",
    "native_prompt_skill",
    "schema_prompt_skill",
    "summary2skill",
    "document_tool_maker",
    "evoskill_compiler",
    "graph_evoskill_compiler",
    "tool_schema_compiler",
    "a2sc",
    "g_a2sc",
    "a2sc_no_typed_atoms",
    "a2sc_no_tool_binding",
    "a2sc_no_local_motifs",
]

DETERMINISTIC_CONTRACT_METHODS = {
    "no_skill", "raw_policy_rag", "document_tool_maker", "tool_schema_compiler",
    "a2sc", "g_a2sc",
    "a2sc_no_typed_atoms", "a2sc_no_tool_binding", "a2sc_no_local_motifs",
}


def word_tokens(text: str) -> set[str]:
    return {token for token in re.findall(r"[a-z0-9_]+", text.lower()) if len(token) > 2}


def source_hash(root: Path, sources: list[str]) -> str:
    digest = hashlib.sha256()
    for relative in sources:
        path = root / relative
        digest.update(relative.encode())
        digest.update(sha256_file(path).encode())
    return digest.hexdigest()


def compiler_code_hash() -> str:
    digest = hashlib.sha256()
    for path in (Path(__file__), ROOT / "scripts" / "action_compiler.py"):
        digest.update(path.name.encode())
        digest.update(sha256_file(path).encode())
    return digest.hexdigest()


def load_domain(domain: str) -> dict[str, Any]:
    root = PROCESSED_ROOT / domain
    manifest = read_json(root / "manifest.json")
    train = root / "tasks" / "train.jsonl"
    return {
        "root": root,
        "manifest": manifest,
        "sections": read_jsonl(root / "documents" / "policy_sections.jsonl"),
        "tools": read_json(root / "documents" / "tool_catalog.json")["tools"],
        "knowledge": read_jsonl(root / "documents" / "knowledge_documents.jsonl") if (root / "documents" / "knowledge_documents.jsonl").exists() else [],
        "train_tasks": read_jsonl(train) if train.exists() else [],
    }


def build_atoms(data: dict[str, Any]) -> list[dict[str, Any]]:
    atoms = []
    for section in data["sections"]:
        atoms.append(
            {
                "ka_id": f"KA-{len(atoms) + 1:05d}",
                "kind": "policy_section",
                "title": section["title"],
                "text": section["text"],
                "source": section["source"],
                "line_start": section["line_start"],
                "line_end": section["line_end"],
            }
        )
    for tool in data["tools"]:
        atoms.append(
            {
                "ka_id": f"KA-{len(atoms) + 1:05d}",
                "kind": "tool_contract",
                "title": tool["name"],
                "text": tool["description"],
                "requestor": tool["requestor"],
                "parameters": tool["parameters"],
                "source": tool["source"],
            }
        )
    for document in data["knowledge"]:
        atoms.append(
            {
                "ka_id": f"KA-{len(atoms) + 1:05d}",
                "kind": "knowledge_document",
                "title": document["title"],
                "text": document["content"],
                "document_id": document["document_id"],
                "source": document["source"],
            }
        )
    return atoms


def build_workflows(tasks: list[dict[str, Any]]) -> list[dict[str, Any]]:
    counter: Counter[tuple[str, ...]] = Counter()
    for task in tasks:
        signature = tuple(
            f"{action['requestor']}:{action['name']}"
            for action in task["gold"]["reference_actions"]
        )
        if signature:
            counter[signature] += 1
    return [
        {
            "workflow_id": f"WF-{index:04d}",
            "steps": list(signature),
            "training_frequency": count,
            "source": "tasks/train.jsonl",
            "warning": "Reference trajectory is not necessarily the unique correct path.",
        }
        for index, (signature, count) in enumerate(counter.most_common(), 1)
    ]


def build_policy(data: dict[str, Any], atoms: list[dict[str, Any]]) -> dict[str, Any]:
    rules = []
    for atom in atoms:
        if atom["kind"] != "policy_section":
            continue
        rules.append(
            {
                "rule_id": f"POL-{len(rules) + 1:04d}",
                "title": atom["title"],
                "text": atom["text"],
                "source_ka_ids": [atom["ka_id"]],
                "enforcement": "source_grounded",
            }
        )
    return {
        "decision_statuses": [
            "observe", "clarify", "execute", "instruct_user", "deny", "escalate", "complete", "failed"
        ],
        "rules": rules,
        "runtime_invariants": [
            "Do not treat a reference action trajectory as the only valid path unless ACTION is in reward_basis.",
            "Separate assistant tools from user tools in the dual-control environment.",
            "Never use held-out task text or required_documents annotations as compilation knowledge.",
            "Every consequential decision should retain policy or knowledge provenance.",
        ],
    }


def build_graph(atoms: list[dict[str, Any]]) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    nodes = [{"id": atom["ka_id"], "type": atom["kind"], "label": atom["title"]} for atom in atoms]
    edges = []
    token_sets = {
        atom["ka_id"]: word_tokens(atom["title"] + " " + atom["text"])
        for atom in atoms
    }
    for index, left in enumerate(atoms):
        lt = token_sets[left["ka_id"]]
        for right in atoms[index + 1 :]:
            rt = token_sets[right["ka_id"]]
            union = lt | rt
            score = len(lt & rt) / len(union) if union else 0
            if score >= 0.09:
                edges.append({"source": left["ka_id"], "target": right["ka_id"], "type": "SEMANTIC_VARIANT_OR_DEPENDENCY", "score": round(score, 4)})
    patterns = []
    centers = [atom for atom in atoms if atom["kind"] == "policy_section"]
    for index, center in enumerate(centers, 1):
        connected = []
        for edge in edges:
            if edge["source"] == center["ka_id"]:
                connected.append(edge["target"])
            elif edge["target"] == center["ka_id"]:
                connected.append(edge["source"])
        patterns.append(
            {
                "pattern_id": f"PAT-{index:04d}",
                "name": center["title"],
                "central_ka_id": center["ka_id"],
                "member_ka_ids": connected[:20],
            }
        )
    return {"nodes": nodes, "edges": edges}, patterns


def render(method: str, domain: str, data: dict[str, Any], atoms: list[dict[str, Any]], workflows: list[dict[str, Any]], policy: dict[str, Any], patterns: list[dict[str, Any]]) -> str:
    header = (
        f"# {domain.replace('_', ' ').title()} τ³ SOP Skill\n\n"
        f"> Method: `{method}`. Compile-time sources are frozen τ³-bench policy, tool contracts, "
        "knowledge documents where applicable, and training tasks only where an official train split exists.\n\n"
    )
    policy_text = "\n\n".join(f"## {s['title']}\n\n{s['text']}" for s in data["sections"])
    tool_text = "\n".join(
        f"- `{tool['requestor']}:{tool['name']}`({', '.join(tool['parameters'])}): {tool['description'][:300]}"
        for tool in data["tools"]
    )
    if method == "no_skill":
        return header + "No domain Skill is supplied in this control condition.\n"
    if method == "raw_policy_rag":
        return header + "## Source retrieval protocol\n\nRetrieve relevant original policy or knowledge before decisions.\n\n" + policy_text
    if method == "native_prompt_skill":
        return header + policy_text + "\n\n## Tools\n\n" + tool_text
    if method == "schema_prompt_skill":
        return header + """## Runtime states

Use `observe`, `clarify`, `execute`, `instruct_user`, `deny`, `escalate`, `complete`, or `failed`.

## Procedure

1. Determine current state using observations and tools.
2. Retrieve applicable policy or knowledge.
3. Identify missing information, preconditions, exceptions, and actor ownership.
4. Ask the user to act when the required tool belongs to the user.
5. Execute assistant tools only when permitted.
6. Verify DB state, environment assertions, communicated facts, and provenance.

## Policy

""" + policy_text + "\n\n## Tools\n\n" + tool_text
    if method == "summary2skill":
        summary = "\n".join(f"- **{s['title']}**: {s['text'][:420]}" for s in data["sections"])
        wf = "\n".join(f"- `{w['workflow_id']}` ({w['training_frequency']}): {' → '.join(w['steps'])}" for w in workflows[:30]) or "- No official training trajectories are used."
        return header + "## Policy summary\n\n" + summary + "\n\n## Training workflow summaries\n\n" + wf + "\n\nWorkflow frequency is not policy and does not define a unique correct trajectory.\n"
    if method == "document_tool_maker":
        return header + "## Actor-aware tools\n\n" + tool_text + "\n\n## Tool execution contract\n\nSelect the correct actor, validate arguments and policy gates, execute one consequential step at a time, then verify state and required communication.\n\n" + policy_text
    if method == "tool_schema_compiler":
        return header + "## Deterministic Tool Cards\n\n" + tool_text + "\n\nThis baseline contains only official tool schema information and no train-derived workflow or policy-to-tool binding.\n"
    if method in {"evoskill_compiler", "a2sc"}:
        atom_text = "\n".join(
            f"- `{a['ka_id']}` [{a['kind']}] **{a['title']}**: {a['text'][:500]}"
            for a in atoms if a["kind"] != "knowledge_document"
        )
        knowledge_count = sum(a["kind"] == "knowledge_document" for a in atoms)
        if knowledge_count:
            atom_text += (
                f"\n- `{knowledge_count}` knowledge documents are runtime-retrievable from "
                "`evidence_index.json`; their task-independent catalog and content are not inlined here."
            )
        rule_text = "\n".join(f"- `{r['rule_id']}` {r['title']} — sources {', '.join(r['source_ka_ids'])}" for r in policy["rules"])
        return header + "## Knowledge atoms\n\n" + atom_text + "\n\n## Governance rules\n\n" + rule_text + "\n\n## Runtime strategy\n\nRetrieve knowledge and policy separately, identify the acting party, check state and exceptions, execute or instruct, verify all reward dimensions, and retain provenance.\n"
    cards = "\n".join(
        f"### {p['pattern_id']}: {p['name']}\n\nCentral atom `{p['central_ka_id']}`; related atoms: {', '.join(p['member_ka_ids']) or 'none'}.\n"
        for p in patterns
    )
    return header + "## Graph-selected Pattern Cards\n\n" + cards + "\n## Runtime boundary\n\nThe graph changes compile-time organization only. Runtime tools, environment, task evaluator and retrieval budget remain fixed.\n\n## Governance\n\n" + "\n".join(f"- `{r['rule_id']}` {r['title']}" for r in policy["rules"])


def formal_compile(method: str, domain: str, draft: str, model: str, base_url: str, api_key: str) -> tuple[str, dict[str, Any]]:
    system = "You compile enterprise SOP sources into executable, source-grounded Agent Skills. Return only Markdown. Do not invent tools, policies, sources, exceptions, or task facts. Preserve dual-control actor ownership and provenance IDs."
    user = f"Method: {method}\nDomain: {domain}\nImprove this deterministic method-specific draft without changing its causal boundary. Held-out test tasks and required-document labels are forbidden.\n\n{draft}"
    request = urllib.request.Request(
        base_url.rstrip("/") + "/chat/completions",
        data=json.dumps({"model": model, "temperature": 0, "messages": [{"role": "system", "content": system}, {"role": "user", "content": user}]}).encode(),
        headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(request, timeout=300) as response:
        payload = json.loads(response.read().decode())
    skill = payload["choices"][0]["message"]["content"].strip()
    if len(skill) < 100:
        raise ValueError("Implausibly short formal Skill")
    return skill, {"model": model, "usage": payload.get("usage", {}), "request_id": payload.get("id")}


def generate(method: str, domain: str, args: argparse.Namespace) -> dict[str, Any]:
    data = load_domain(domain)
    input_hash = source_hash(data["root"], data["manifest"]["compilation_sources"])
    code_hash = compiler_code_hash()
    output_root = Path(args.output_root) if args.output_root else ROOT / ("skills_formal" if args.backend == "openai_compatible" else "skills")
    output = output_root / method / domain
    manifest_path = output / "manifest.json"
    if manifest_path.exists() and not args.force:
        existing = read_json(manifest_path)
        if (
            existing.get("input_hash") == input_hash
            and existing.get("compiler_code_hash") == code_hash
            and existing.get("compiler_backend") == args.backend
            and existing.get("model") == args.model
        ):
            print(f"[{method}/{domain}] unchanged; skipping")
            return existing
    started = time.time()
    atoms = build_atoms(data)
    workflows = build_workflows(data["train_tasks"])
    security = build_policy(data, atoms)
    graph, patterns = build_graph(atoms)
    draft = render(method, domain, data, atoms, workflows, security, patterns)
    llm = {}
    if args.backend == "openai_compatible" and method not in DETERMINISTIC_CONTRACT_METHODS:
        key = os.environ.get(args.api_key_env)
        base = args.base_url or os.environ.get("TAU3_LLM_BASE_URL")
        if not args.model or not key or not base:
            raise SystemExit("Formal generation requires --model, TAU3_LLM_BASE_URL/--base-url, and the configured API key environment variable.")
        skill, llm = formal_compile(method, domain, draft, args.model, base, key)
    else:
        skill = draft
        if args.backend == "openai_compatible":
            llm = {
                "skipped": True,
                "reason": "This method's frozen structured compiler does not use an LLM rewrite.",
            }
    typed_atoms = build_typed_atoms(data)
    tool_cards = build_tool_cards(data, typed_atoms)
    local_motifs = build_local_motifs(data["train_tasks"])
    semantic_graph = None
    graph_expansion = None
    if method == "g_a2sc":
        semantic_graph, graph_expansion = build_semantic_graph(typed_atoms, tool_cards)
    effective_motifs = [] if method in {
        "a2sc_no_typed_atoms", "a2sc_no_tool_binding", "a2sc_no_local_motifs"
    } else local_motifs
    module_method = "a2sc" if method == "a2sc_no_local_motifs" else method
    modules = build_action_modules(
        module_method, domain, skill, data, typed_atoms, tool_cards, effective_motifs,
        graph_expansion=graph_expansion,
    )
    if method == "a2sc_no_local_motifs":
        for module in modules:
            module["method"] = method
    if method in {
        "a2sc", "g_a2sc", "tool_schema_compiler", "no_skill",
        "a2sc_no_typed_atoms", "a2sc_no_tool_binding", "a2sc_no_local_motifs",
    }:
        skill = render_catalog_skill(method, domain, modules)
    output.mkdir(parents=True, exist_ok=True)
    (output / "SKILL.md").write_text(skill, encoding="utf-8", newline="\n")
    write_json(output / "evidence_index.json", {"knowledge_atoms": atoms})
    write_json(output / "security_policy.json", security)
    write_json(output / "workflow_patterns.json", {"patterns": workflows})
    write_json(output / "typed_atoms.json", {"atoms": typed_atoms})
    write_json(output / "tool_cards.json", {"tools": tool_cards})
    write_json(output / "local_motifs.json", {"motifs": effective_motifs})
    write_json(output / "action_modules.json", {"modules": modules})
    if method == "graph_evoskill_compiler":
        write_json(output / "knowledge_graph.json", graph)
        write_json(output / "pattern_cards.json", {"patterns": patterns})
    if method == "g_a2sc":
        write_json(output / "knowledge_graph.json", semantic_graph)
    manifest = {
        "benchmark": "tau3-bench",
        "method": method,
        "domain": domain,
        "compiler_backend": args.backend,
        "effective_compiler_backend": (
            "deterministic_structured" if method in DETERMINISTIC_CONTRACT_METHODS
            else args.backend
        ),
        "model": args.model,
        "input_hash": input_hash,
        "compiler_code_hash": code_hash,
        "uses_train_tasks": bool(data["train_tasks"]),
        "uses_held_out_tasks": False,
        "counts": {
            "policy_sections": len(data["sections"]), "tools": len(data["tools"]),
            "knowledge_documents": len(data["knowledge"]), "knowledge_atoms": len(atoms),
            "typed_atoms": len(typed_atoms), "tool_cards": len(tool_cards),
            "local_motifs": len(effective_motifs), "action_modules": len(modules),
            "workflow_patterns": len(workflows),
            "graph_patterns": len(patterns) if method == "graph_evoskill_compiler" else 0,
            "semantic_graph_edges": len((semantic_graph or {}).get("edges", [])),
        },
        "package_contract": "action_modules.v2",
        "package_contract_hash": package_contract_hash(modules),
        "runtime_graph_traversal": False,
        "llm": llm,
        "duration_seconds": round(time.time() - started, 4),
    }
    write_json(manifest_path, manifest)
    print(f"[{method}/{domain}] skill={len(skill)} chars, typed_atoms={len(typed_atoms)}, modules={len(modules)}")
    return manifest


def main() -> None:
    parser = argparse.ArgumentParser(description="Incremental tau3 Document-to-Skill compiler")
    parser.add_argument("--method", choices=[*METHODS, "all"], default="all")
    parser.add_argument("--domain", choices=[*DOMAINS, "all"], default="all")
    parser.add_argument("--backend", choices=["deterministic_bootstrap", "openai_compatible"], default="deterministic_bootstrap")
    parser.add_argument("--model")
    parser.add_argument("--base-url")
    parser.add_argument("--api-key-env", default="TAU3_LLM_API_KEY")
    parser.add_argument("--output-root")
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()
    methods = METHODS if args.method == "all" else [args.method]
    domains = DOMAINS if args.domain == "all" else [args.domain]
    for method in methods:
        for domain in domains:
            generate(method, domain, args)


if __name__ == "__main__":
    main()
