from __future__ import annotations

import argparse
import json
from pathlib import Path
from statistics import mean

from common import read_jsonl, write_json


STATUSES = ["observe", "clarify", "execute", "instruct_user", "deny", "escalate", "complete", "failed"]


def safe_div(a: float, b: float) -> float:
    return a / b if b else 0.0


def classification(rows: list[dict]) -> dict:
    if not rows:
        return {"accuracy": None, "macro_f1": None, "balanced_accuracy": None, "per_class": {}}
    labels = sorted(set(STATUSES) | {r["gold_status"] for r in rows} | {r["pred_status"] for r in rows})
    per_class = {}
    for label in labels:
        tp = sum(r["gold_status"] == label and r["pred_status"] == label for r in rows)
        fp = sum(r["gold_status"] != label and r["pred_status"] == label for r in rows)
        fn = sum(r["gold_status"] == label and r["pred_status"] != label for r in rows)
        tn = len(rows) - tp - fp - fn
        precision, recall = safe_div(tp, tp + fp), safe_div(tp, tp + fn)
        per_class[label] = {
            "support": tp + fn,
            "precision": precision,
            "recall": recall,
            "f1": safe_div(2 * precision * recall, precision + recall),
            "specificity": safe_div(tn, tn + fp),
        }
    supported = [v for v in per_class.values() if v["support"] > 0]
    return {
        "accuracy": mean([r["gold_status"] == r["pred_status"] for r in rows]) if rows else None,
        "macro_f1": mean(v["f1"] for v in supported) if supported else None,
        "balanced_accuracy": mean(v["recall"] for v in supported) if supported else None,
        "per_class": per_class,
    }


def avg(rows, field):
    values = [float(r[field]) for r in rows if r.get(field) is not None]
    return mean(values) if values else None


def routing(rows: list[dict]) -> dict:
    required = [row for row in rows if row.get("gold_requires_skill") is True]
    not_required = [row for row in rows if row.get("gold_requires_skill") is False]
    route_rows = [row for row in required if row.get("gold_applicable_module_ids")]
    triggered_required = [bool(row.get("pred_activated_module_ids")) for row in required]
    route_at_1 = [
        row["pred_activated_module_ids"][0] in set(row["gold_applicable_module_ids"])
        if row.get("pred_activated_module_ids") else False
        for row in route_rows
    ]
    unnecessary = [bool(row.get("pred_activated_module_ids")) for row in not_required]
    precision_rows = []
    for row in route_rows:
        predicted = row.get("pred_activated_module_ids") or []
        if predicted:
            applicable = set(row["gold_applicable_module_ids"])
            precision_rows.append(sum(module in applicable for module in predicted) / len(predicted))
    return {
        "annotated_required_tasks": len(required),
        "trigger_recall": mean(triggered_required) if triggered_required else None,
        "route_at_1": mean(route_at_1) if route_at_1 else None,
        "activated_module_precision": mean(precision_rows) if precision_rows else None,
        "unnecessary_activation_rate": mean(unnecessary) if unnecessary else None,
        "activated_module_utility": avg(rows, "activated_module_utility"),
        "tool_binding_accuracy": avg(rows, "tool_binding_correct"),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Evaluate blinded human trace annotations")
    parser.add_argument("annotations", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    rows = read_jsonl(args.annotations)
    required = {"task_id", "trial", "gold_status", "pred_status"}
    for i, row in enumerate(rows, 1):
        missing = required - row.keys()
        if missing:
            raise SystemExit(f"Line {i} missing {sorted(missing)}")
    completed_status_rows = [
        row for row in rows
        if row.get("gold_status") is not None and row.get("pred_status") is not None
    ]
    output = {
        "num_annotations": len(rows),
        "num_completed_status_annotations": len(completed_status_rows),
        "status": classification(completed_status_rows),
        "skill_routing": routing(rows),
        "governance": {
            "policy_compliance_rate": avg(rows, "policy_compliant"),
            "precondition_recall": avg(rows, "precondition_recall"),
            "exception_branch_recall": avg(rows, "exception_branch_recall"),
            "verification_recall": avg(rows, "verification_recall"),
        },
        "provenance": {
            "coverage": avg(rows, "provenance_present"),
            "validity_precision": avg(rows, "provenance_valid"),
        },
        "note": "Inter-annotator agreement must be computed on the unreconciled double-coded file before adjudication.",
    }
    write_json(args.output or args.annotations.with_name("annotation_metrics.json"), output)
    print(json.dumps(output, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
