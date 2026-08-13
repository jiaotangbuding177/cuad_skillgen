from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import time
import urllib.request
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

from common import PROCESSED_ROOT, ROOT, read_json, read_jsonl, sha256_file, write_json


METHODS = [
    "raw_policy_rag",
    "native_prompt_skill",
    "schema_prompt_skill",
    "summary2skill",
    "document_tool_maker",
    "evoskill_compiler",
    "graph_evoskill_compiler",
]

STOPWORDS = {
    "the", "a", "an", "to", "of", "and", "or", "for", "is", "are", "be",
    "with", "in", "on", "by", "from", "that", "this", "user", "agent",
}


def tokens(text: str) -> set[str]:
    return {
        token for token in re.findall(r"[a-z0-9_]+", text.lower())
        if len(token) > 2 and token not in STOPWORDS
    }


def source_hash(domain_root: Path) -> str:
    manifest = read_json(domain_root / "manifest.json")
    paths = [domain_root / item for item in manifest["compilation_sources"]]
    digest = hashlib.sha256()
    for path in paths:
        digest.update(str(path.relative_to(domain_root)).encode())
        digest.update(sha256_file(path).encode())
    return digest.hexdigest()


def load_sources(domain: str) -> dict[str, Any]:
    root = PROCESSED_ROOT / domain
    manifest = read_json(root / "manifest.json")
    return {
        "root": root,
        "manifest": manifest,
        "policy": (root / "documents" / "policy.md").read_text(encoding="utf-8"),
        "sections": read_jsonl(root / "documents" / "policy_sections.jsonl"),
        "rules": read_json(root / "documents" / "runtime_rules.json")["rules"],
        "tools": read_json(root / "documents" / "tool_catalog.json")["tools"],
        "train_tasks": read_jsonl(root / "tasks" / "train.jsonl") if (root / "tasks" / "train.jsonl").exists() else [],
    }


def build_workflows(train_tasks: list[dict[str, Any]]) -> list[dict[str, Any]]:
    counts: Counter[tuple[str, ...]] = Counter()
    for task in train_tasks:
        signature = tuple(action["name"] for action in task["gold"]["actions"])
        if signature:
            counts[signature] += 1
    return [
        {
            "workflow_id": f"WF-{index:03d}",
            "actions": list(signature),
            "training_frequency": count,
            "provenance": "tasks/train.jsonl",
        }
        for index, (signature, count) in enumerate(counts.most_common(), 1)
    ]


def build_atoms(sources: dict[str, Any]) -> list[dict[str, Any]]:
    atoms: list[dict[str, Any]] = []
    for section in sources["sections"]:
        atoms.append(
            {
                "ka_id": f"KA-{len(atoms) + 1:04d}",
                "kind": "policy_section",
                "title": section["title"],
                "text": section["text"],
                "source": section["source"],
                "line_start": section["line_start"],
                "line_end": section["line_end"],
            }
        )
    for index, rule in enumerate(sources["rules"], 1):
        atoms.append(
            {
                "ka_id": f"KA-{len(atoms) + 1:04d}",
                "kind": "runtime_rule",
                "title": f"Runtime rule {index}",
                "text": rule,
                "source": f"tau_bench/envs/{sources['manifest']['domain']}/rules.py",
            }
        )
    for schema in sources["tools"]:
        function = schema["function"]
        atoms.append(
            {
                "ka_id": f"KA-{len(atoms) + 1:04d}",
                "kind": "tool_contract",
                "title": function["name"],
                "text": function.get("description", ""),
                "parameters": function.get("parameters", {}),
                "source": schema["source"],
            }
        )
    return atoms


def build_security_policy(sources: dict[str, Any], atoms: list[dict[str, Any]]) -> dict[str, Any]:
    rules = []
    for index, rule in enumerate(sources["rules"], 1):
        lowered = rule.lower()
        enforcement = "hard" if any(term in lowered for term in ["must", "should not", "always", "at most"]) else "soft"
        rules.append(
            {
                "rule_id": f"POL-{index:03d}",
                "text": rule,
                "enforcement": enforcement,
                "source_ka_ids": [atom["ka_id"] for atom in atoms if atom["kind"] == "runtime_rule" and atom["text"] == rule],
            }
        )
    return {
        "decision_statuses": ["execute", "clarify", "deny", "escalate", "no_action", "execution_failed"],
        "rules": rules,
        "invariants": [
            "Never mutate backend state before all policy preconditions are satisfied.",
            "Use only information returned by the user or tools.",
            "Record the policy atom and tool observation supporting each consequential action.",
        ],
    }


def tool_table(tools: list[dict[str, Any]]) -> str:
    rows = ["| Tool | Required arguments | Purpose |", "|---|---|---|"]
    for item in tools:
        fn = item["function"]
        required = ", ".join(fn.get("parameters", {}).get("required", [])) or "none"
        description = fn.get("description", "").replace("\n", " ")[:220]
        rows.append(f"| `{fn['name']}` | {required} | {description} |")
    return "\n".join(rows)


def common_header(method: str, domain: str) -> str:
    return (
        f"# {domain.title()} SOP Skill\n\n"
        f"> Method: `{method}`. Source: frozen original tau-bench policy and tool contracts.\n\n"
        "This package supports policy-grounded customer-service decisions and tool execution. "
        "It must not use held-out task instructions as compilation knowledge.\n"
    )


def render_skill(method: str, domain: str, sources: dict[str, Any], atoms: list[dict[str, Any]], workflows: list[dict[str, Any]], policy: dict[str, Any], patterns: list[dict[str, Any]]) -> str:
    header = common_header(method, domain)
    if method == "raw_policy_rag":
        return header + "\n## Runtime protocol\n\nRetrieve the most relevant original policy section before every consequential decision. Do not infer policy from training trajectories.\n\n## Original policy\n\n" + sources["policy"]
    if method == "native_prompt_skill":
        return header + "\n## Instructions\n\nFollow the supplied policy, inspect the current backend state with read-only tools, ask for missing information, and call mutation tools only when permitted.\n\n" + sources["policy"] + "\n\n## Available tools\n\n" + tool_table(sources["tools"])
    if method == "schema_prompt_skill":
        return header + """

## Scope

Handle only requests supported by the domain policy and available tools.

## Decision procedure

1. Identify the user and requested outcome.
2. Retrieve current state with read-only tools.
3. Check eligibility, required inputs, prohibitions, and confirmation requirements.
4. Choose `execute`, `clarify`, `deny`, `escalate`, `no_action`, or `execution_failed`.
5. Before a mutation, state the exact transaction and obtain any required authorization.
6. Execute one tool at a time and verify the resulting state.

## Policy sections

""" + "\n".join(f"- **{s['title']}**: {s['text'][:300]}" for s in sources["sections"]) + "\n\n## Tool schema\n\n" + tool_table(sources["tools"]) + "\n\n## Output\n\nReturn status, answer, tool actions, policy evidence IDs, missing inputs, and final-state verification.\n"
    if method == "summary2skill":
        workflow_text = "\n".join(
            f"- `{item['workflow_id']}` ({item['training_frequency']} train examples): " + " → ".join(item["actions"])
            for item in workflows[:20]
        ) or "- No training trajectories are available; rely only on policy and tool contracts."
        return header + "\n## Policy summary\n\n" + "\n".join(f"- **{s['title']}**: {re.split(r'(?<=[.!?])\\s+', s['text'])[0][:360]}" for s in sources["sections"]) + "\n\n## Frequent training workflows\n\n" + workflow_text + "\n\n## Guardrail\n\nTraining workflow frequency is not policy. The current policy and backend state always take precedence.\n"
    if method == "document_tool_maker":
        return header + "\n## Tool-oriented procedure\n\nFor every request, bind the request to a permitted tool, validate its required arguments from observations, apply policy gates, request confirmation where required, execute, and verify.\n\n" + tool_table(sources["tools"]) + "\n\n## Policy gates\n\n" + "\n".join(f"- `{r['rule_id']}` {r['text']}" for r in policy["rules"]) + "\n"
    if method == "evoskill_compiler":
        return header + "\n## Knowledge atoms\n\n" + "\n".join(f"- `{a['ka_id']}` **{a['title']}** ({a['kind']}): {a['text'][:420]}" for a in atoms) + "\n\n## Governance policy\n\n" + "\n".join(f"- `{r['rule_id']}` [{r['enforcement']}] {r['text']} Sources: {', '.join(r['source_ka_ids'])}" for r in policy["rules"]) + "\n\n## Execution strategy\n\nRetrieve policy atoms and tool contracts separately. Check identity, current state, eligibility, required arguments, authorization, mutation result, and provenance in that order. A frequent workflow never overrides a policy atom.\n"
    pattern_text = []
    for pattern in patterns:
        pattern_text.append(
            f"### {pattern['pattern_id']}: {pattern['name']}\n\n"
            f"- Central atom: `{pattern['central_ka_id']}`\n"
            f"- Related atoms: {', '.join(f'`{x}`' for x in pattern['member_ka_ids'])}\n"
            f"- Related tools: {', '.join(f'`{x}`' for x in pattern['tools']) or 'none'}\n"
            f"- Required reasoning: retrieve state → check conditions/exceptions → choose status → obtain authorization if required → execute → verify.\n"
        )
    return header + "\n## Graph-selected SOP Pattern Cards\n\n" + "\n".join(pattern_text) + "\n## Governance policy\n\n" + "\n".join(f"- `{r['rule_id']}` {r['text']}" for r in policy["rules"]) + "\n\n## Runtime boundary\n\nThe graph is compile-time organization only. Runtime still uses the same tools and environment as every baseline.\n"


def compile_with_openai_compatible(
    method: str,
    domain: str,
    draft: str,
    model: str,
    base_url: str,
    api_key: str,
) -> tuple[str, dict[str, Any]]:
    method_requirements = {
        "raw_policy_rag": "Preserve the original policy verbatim and add only a minimal retrieval protocol.",
        "native_prompt_skill": "Produce a useful free-form Skill without imposing a fixed schema.",
        "schema_prompt_skill": "Preserve the fixed scope, decision procedure, policy, tools, output, and boundary sections.",
        "summary2skill": "Compile concise policy and workflow summaries; explicitly state that workflow frequency is not policy.",
        "document_tool_maker": "Organize the Skill around tool selection, arguments, preconditions, authorization, and state verification.",
        "evoskill_compiler": "Preserve KA IDs, source provenance, explicit policy rules, decision statuses, and governance gates.",
        "graph_evoskill_compiler": "Preserve graph-selected Pattern Cards, related KA IDs and tools; do not introduce runtime Graph-RAG.",
    }
    system = (
        "You compile enterprise SOP documents into executable Agent Skills. Return only SKILL.md markdown. "
        "Never invent policy, tools, preconditions, exceptions, identifiers, or sources. Preserve explicit governance gates. "
        "Held-out dev/test tasks are unavailable and must not be inferred."
    )
    user = (
        f"Method: {method}\nDomain: {domain}\n"
        f"Method-specific requirement: {method_requirements[method]}\n\n"
        "The following deterministic draft contains the complete frozen source material and method-specific intermediate representation. "
        "Improve clarity and operational usefulness without changing facts, provenance IDs, or causal boundaries.\n\n"
        f"=== DRAFT ===\n{draft}"
    )
    endpoint = base_url.rstrip("/") + "/chat/completions"
    body = json.dumps(
        {
            "model": model,
            "temperature": 0,
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
        }
    ).encode("utf-8")
    request = urllib.request.Request(
        endpoint,
        data=body,
        headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(request, timeout=300) as response:
        payload = json.loads(response.read().decode("utf-8"))
    content = payload["choices"][0]["message"]["content"].strip()
    if len(content) < 100:
        raise ValueError("LLM returned an implausibly short SKILL.md")
    return content, {
        "model": model,
        "usage": payload.get("usage", {}),
        "request_id": payload.get("id"),
        "prompt_sha256": hashlib.sha256((system + "\n" + user).encode()).hexdigest(),
    }


def build_graph(atoms: list[dict[str, Any]], tools: list[dict[str, Any]]) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    nodes = [{"id": atom["ka_id"], "type": atom["kind"], "label": atom["title"]} for atom in atoms]
    edges = []
    for left_index, left in enumerate(atoms):
        left_tokens = tokens(left["title"] + " " + left["text"])
        for right in atoms[left_index + 1 :]:
            right_tokens = tokens(right["title"] + " " + right["text"])
            union = left_tokens | right_tokens
            score = len(left_tokens & right_tokens) / len(union) if union else 0.0
            if score >= 0.08:
                edges.append({"source": left["ka_id"], "target": right["ka_id"], "type": "RELATED_POLICY_OR_TOOL", "score": round(score, 4)})

    tool_names = [item["function"]["name"] for item in tools]
    patterns = []
    policy_atoms = [atom for atom in atoms if atom["kind"] == "policy_section"]
    for index, atom in enumerate(policy_atoms, 1):
        atom_tokens = tokens(atom["title"] + " " + atom["text"])
        related_atoms = []
        for other in atoms:
            if other["ka_id"] == atom["ka_id"]:
                continue
            if atom_tokens & tokens(other["title"] + " " + other["text"]):
                related_atoms.append(other["ka_id"])
        related_tools = [name for name in tool_names if tokens(name.replace("_", " ")) & atom_tokens]
        patterns.append(
            {
                "pattern_id": f"PAT-{index:03d}",
                "name": atom["title"],
                "central_ka_id": atom["ka_id"],
                "member_ka_ids": related_atoms[:12],
                "tools": related_tools,
            }
        )
    return {"nodes": nodes, "edges": edges}, patterns


def generate(
    method: str,
    domain: str,
    force: bool,
    backend: str,
    model: str | None,
    base_url: str | None,
    api_key: str | None,
    output_root: Path,
) -> dict[str, Any]:
    sources = load_sources(domain)
    input_hash = source_hash(sources["root"])
    output = output_root / method / domain
    manifest_path = output / "manifest.json"
    if manifest_path.exists() and not force:
        existing = read_json(manifest_path)
        if (
            existing.get("input_hash") == input_hash
            and existing.get("compiler_backend") == backend
            and existing.get("model") == model
        ):
            print(f"[{method}/{domain}] unchanged; skipping")
            return existing

    started = time.time()
    workflows = build_workflows(sources["train_tasks"])
    atoms = build_atoms(sources)
    security_policy = build_security_policy(sources, atoms)
    graph, patterns = build_graph(atoms, sources["tools"])
    draft = render_skill(method, domain, sources, atoms, workflows, security_policy, patterns)
    llm_metadata: dict[str, Any] = {}
    if backend == "openai_compatible":
        if not model or not base_url or not api_key:
            raise ValueError("openai_compatible backend requires model, base URL, and API key")
        skill, llm_metadata = compile_with_openai_compatible(
            method, domain, draft, model, base_url, api_key
        )
    else:
        skill = draft

    output.mkdir(parents=True, exist_ok=True)
    (output / "SKILL.md").write_text(skill, encoding="utf-8", newline="\n")
    write_json(output / "evidence_index.json", {"knowledge_atoms": atoms})
    write_json(output / "security_policy.json", security_policy)
    write_json(output / "workflow_patterns.json", {"patterns": workflows})
    if method == "graph_evoskill_compiler":
        write_json(output / "knowledge_graph.json", graph)
        write_json(output / "pattern_cards.json", {"patterns": patterns})
    manifest = {
        "method": method,
        "domain": domain,
        "compiler_backend": backend,
        "model": model,
        "formal_llm_generation_required_for_paper_result": backend != "openai_compatible",
        "input_hash": input_hash,
        "uses_training_tasks": bool(sources["train_tasks"]),
        "uses_dev_or_test_tasks": False,
        "counts": {
            "policy_sections": len(sources["sections"]),
            "tools": len(sources["tools"]),
            "knowledge_atoms": len(atoms),
            "training_workflow_patterns": len(workflows),
            "graph_patterns": len(patterns) if method == "graph_evoskill_compiler" else 0,
        },
        "duration_seconds": round(time.time() - started, 4),
        "llm": llm_metadata,
        "artifacts": [
            "SKILL.md", "evidence_index.json", "security_policy.json", "workflow_patterns.json"
        ] + (["knowledge_graph.json", "pattern_cards.json"] if method == "graph_evoskill_compiler" else []),
    }
    write_json(manifest_path, manifest)
    print(f"[{method}/{domain}] generated {len(skill)} chars, {len(atoms)} KAs")
    return manifest


def main() -> None:
    parser = argparse.ArgumentParser(description="Incremental tau-bench baseline Skill compiler")
    parser.add_argument("--method", choices=METHODS + ["all"], default="all")
    parser.add_argument("--domain", choices=["retail", "airline", "all"], default="all")
    parser.add_argument("--force", action="store_true")
    parser.add_argument("--backend", choices=["deterministic_bootstrap", "openai_compatible"], default="deterministic_bootstrap")
    parser.add_argument("--model", help="One frozen generation model for every method when using openai_compatible")
    parser.add_argument("--base-url", help="OpenAI-compatible API base ending in /v1; alternatively TAU_LLM_BASE_URL")
    parser.add_argument("--api-key-env", default="TAU_LLM_API_KEY")
    parser.add_argument("--output-root", help="Defaults to skills for bootstrap and skills_formal for LLM generation")
    args = parser.parse_args()
    methods = METHODS if args.method == "all" else [args.method]
    domains = ["retail", "airline"] if args.domain == "all" else [args.domain]
    base_url = args.base_url or os.environ.get("TAU_LLM_BASE_URL")
    api_key = os.environ.get(args.api_key_env)
    output_root = Path(args.output_root) if args.output_root else ROOT / ("skills_formal" if args.backend == "openai_compatible" else "skills")
    if args.backend == "openai_compatible" and (not args.model or not base_url or not api_key):
        raise SystemExit(
            "Formal generation requires --model, TAU_LLM_BASE_URL (or --base-url), "
            f"and the API key environment variable {args.api_key_env}."
        )
    for method in methods:
        for domain in domains:
            generate(method, domain, args.force, args.backend, args.model, base_url, api_key, output_root)


if __name__ == "__main__":
    main()
