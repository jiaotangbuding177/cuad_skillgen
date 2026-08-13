from __future__ import annotations

import argparse
from collections import Counter
from pathlib import Path
from typing import Any

from common import ROOT, read_json, write_json


def canonical(value: Any) -> Any:
    if isinstance(value, dict):
        return {key: canonical(value[key]) for key in sorted(value)}
    if isinstance(value, list):
        return [canonical(item) for item in value]
    return value


def macro_f1(pairs: list[tuple[str, str]]) -> float:
    labels = sorted({label for pair in pairs for label in pair})
    scores = []
    for label in labels:
        tp = sum(gold == label and pred == label for gold, pred in pairs)
        fp = sum(gold != label and pred == label for gold, pred in pairs)
        fn = sum(gold == label and pred != label for gold, pred in pairs)
        precision = tp / (tp + fp) if tp + fp else 0.0
        recall = tp / (tp + fn) if tp + fn else 0.0
        scores.append(2 * precision * recall / (precision + recall) if precision + recall else 0.0)
    return sum(scores) / len(scores) if scores else 0.0


def evaluate_record(record: dict[str, Any]) -> dict[str, Any]:
    gold_actions = record["gold"]["consequential_actions"]
    pred_actions = record["prediction"]["consequential_actions"]
    tool_names_gold = [item["name"] for item in gold_actions]
    tool_names_pred = [item["name"] for item in pred_actions]
    aligned = min(len(gold_actions), len(pred_actions))
    argument_hits = sum(
        canonical(gold_actions[i].get("arguments", {})) == canonical(pred_actions[i].get("arguments", {}))
        for i in range(aligned)
    )
    policy_values = list(record.get("policy_checks", {}).values())
    state_exact = canonical(record["gold"]["expected_final_state"]) == canonical(record["prediction"]["final_state"])
    action_exact = canonical(gold_actions) == canonical(pred_actions)
    policy_compliant = bool(policy_values) and all(policy_values)
    provenance_covered = bool(record["prediction"].get("policy_evidence_ids"))
    return {
        "task_id": record["task_id"],
        "environment_task_success": float(state_exact),
        "consequential_action_exact_match": float(action_exact),
        "tool_sequence_exact_match": float(tool_names_gold == tool_names_pred),
        "argument_exact_accuracy": argument_hits / len(gold_actions) if gold_actions else float(not pred_actions),
        "decision_status_correct": float(record["gold"]["decision_status"] == record["prediction"]["decision_status"]),
        "policy_compliance": sum(bool(value) for value in policy_values) / len(policy_values) if policy_values else 0.0,
        "governed_task_success": float(state_exact and action_exact and policy_compliant),
        "policy_provenance_coverage": float(provenance_covered),
        "excess_consequential_actions": max(0, len(pred_actions) - len(gold_actions)),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Evaluate normalized tau SkillBench run records")
    parser.add_argument("--input", default=str(ROOT / "results" / "mock"))
    parser.add_argument("--output", default=str(ROOT / "results" / "evaluation" / "mock_summary.json"))
    args = parser.parse_args()
    input_path = Path(args.input)
    files = [input_path] if input_path.is_file() else sorted(input_path.rglob("*.json"))
    records = [read_json(path) for path in files]
    records = [record for record in records if record.get("record_type") == "tau_skillbench_run"]
    if not records:
        raise SystemExit(f"No run records under {input_path}")
    per_task = [evaluate_record(record) for record in records]
    numeric_keys = [key for key in per_task[0] if key != "task_id"]
    aggregate = {
        key: sum(float(row[key]) for row in per_task) / len(per_task)
        for key in numeric_keys
    }
    aggregate["decision_status_macro_f1"] = macro_f1(
        [(record["gold"]["decision_status"], record["prediction"]["decision_status"]) for record in records]
    )
    summary = {
        "records": len(records),
        "warning": "Mock/smoke-test metrics are not paper results.",
        "aggregate": aggregate,
        "per_task": per_task,
        "task_distribution": dict(Counter(record["domain"] for record in records)),
    }
    write_json(Path(args.output), summary)
    print(f"Evaluated {len(records)} records -> {args.output}")


if __name__ == "__main__":
    main()

