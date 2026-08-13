from __future__ import annotations

import argparse
import json
from pathlib import Path
from statistics import mean

from common import PROCESSED_ROOT, read_json, read_jsonl, write_json
from evaluate_results import summarize
from extract_audit_trace import extract
from evaluate_action_metrics import evaluate as evaluate_action_metrics


def check_rate(checks: list[dict] | None, field: str) -> float | None:
    values = [bool(item.get(field)) for item in (checks or [])]
    return mean(values) if values else None


def main() -> None:
    parser = argparse.ArgumentParser(description="Compute native, audit, and Banking retrieval metrics")
    parser.add_argument("results", type=Path)
    parser.add_argument("--domain", required=True)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    payload = read_json(args.results)
    native = summarize(payload)
    _, audit = extract(payload)
    action = evaluate_action_metrics(payload)
    tasks = {row["source_task_id"]: row for row in read_jsonl(PROCESSED_ROOT / args.domain / "tasks" / ("base.jsonl" if args.domain == "banking_knowledge" else "test.jsonl"))}
    rows = []
    for sim, trace in zip(payload.get("simulations", []), audit["per_simulation"]):
        reward = sim.get("reward_info") or {}
        source_id = sim.get("task_id")
        task = tasks.get(source_id) or tasks.get(str(source_id).removeprefix(f"{args.domain}-"))
        required = set((task or {}).get("gold", {}).get("required_documents") or [])
        retrieved = trace["retrieved_document_ids"]
        hits = [doc for doc in retrieved if doc in required]
        first_rank = next((i for i, doc in enumerate(retrieved, 1) if doc in required), None)
        rows.append({
            "task_id": source_id,
            "trial": sim.get("trial"),
            "reward": reward.get("reward"),
            "db": (reward.get("db_check") or {}).get("db_reward"),
            "env_assertion_rate": check_rate(reward.get("env_assertions"), "met"),
            "communication_rate": check_rate(reward.get("communicate_checks"), "met"),
            "nl_assertion_rate": check_rate(reward.get("nl_assertions"), "met"),
            "action_match_rate": check_rate(reward.get("action_checks"), "action_match"),
            "actor_ownership_accuracy": trace["actor_ownership_accuracy"],
            "illegal_cross_actor_tool_calls": trace["illegal_cross_actor_tool_calls"],
            "package_retrievals": trace["package_retrievals"],
            "package_context_chars": trace["package_context_chars"],
            "package_unique_items": len(trace["package_item_ids"]),
            "skill_activations": trace.get("skill_activations", 0),
            "activation_context_chars": trace.get("activation_context_chars", 0),
            "activated_source_atom_count": len(trace.get("activated_source_atom_ids") or []),
            "required_document_recall": len(set(hits)) / len(required) if required else None,
            "required_document_mrr": 1 / first_rank if first_rank else (0.0 if required else None),
        })
    def avg(key: str):
        values = [r[key] for r in rows if isinstance(r[key], (int, float))]
        return mean(values) if values else None
    output = {
        "native": {k: v for k, v in native.items() if k != "rows"},
        "process": {
            key: avg(key) for key in ["db", "env_assertion_rate", "communication_rate", "nl_assertion_rate", "action_match_rate", "actor_ownership_accuracy", "illegal_cross_actor_tool_calls", "package_retrievals", "package_context_chars", "package_unique_items", "skill_activations", "activation_context_chars", "activated_source_atom_count", "required_document_recall", "required_document_mrr"]
        },
        "action": action["summary"],
        "rows": rows,
        "limitations": [
            "Policy compliance, decision-status Macro-F1, exception recall and provenance validity require an annotated trace set; they are not inferred automatically.",
            "Required-document labels are read only after simulation for offline evaluation.",
        ],
    }
    write_json(args.output or args.results.with_name("extended_metrics.json"), output)
    print(json.dumps({
        "native": output["native"], "process": output["process"], "action": output["action"]
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
