from __future__ import annotations

import argparse
import itertools
import json
from collections import Counter, defaultdict
from pathlib import Path
from statistics import mean

from common import read_jsonl, write_json


CATEGORICAL_FIELDS = [
    "gold_status", "pred_status", "policy_compliant", "provenance_present",
    "provenance_valid", "gold_requires_skill", "tool_binding_correct",
]
NUMERIC_FIELDS = [
    "precondition_recall", "exception_branch_recall", "verification_recall",
    "activated_module_utility",
]


def cohen_kappa(pairs: list[tuple[object, object]]) -> float | None:
    if not pairs:
        return None
    observed = mean(left == right for left, right in pairs)
    left_counts = Counter(left for left, _ in pairs)
    right_counts = Counter(right for _, right in pairs)
    labels = set(left_counts) | set(right_counts)
    expected = sum(left_counts[label] * right_counts[label] for label in labels) / (len(pairs) ** 2)
    if expected == 1.0:
        return 1.0 if observed == 1.0 else None
    return (observed - expected) / (1.0 - expected)


def paired_annotations(rows: list[dict]) -> list[tuple[dict, dict]]:
    grouped: dict[tuple, list[dict]] = defaultdict(list)
    for row in rows:
        key = (row.get("simulation_id"), row.get("task_id"), row.get("trial"))
        grouped[key].append(row)
    pairs = []
    for group in grouped.values():
        distinct = [row for row in group if row.get("annotator_id") is not None]
        for left, right in itertools.combinations(distinct, 2):
            if left.get("annotator_id") != right.get("annotator_id"):
                pairs.append((left, right))
    return pairs


def evaluate(rows: list[dict]) -> dict:
    annotation_pairs = paired_annotations(rows)
    categorical = {}
    for field in CATEGORICAL_FIELDS:
        values = [
            (left[field], right[field]) for left, right in annotation_pairs
            if left.get(field) is not None and right.get(field) is not None
        ]
        categorical[field] = {
            "pairs": len(values),
            "percent_agreement": mean(a == b for a, b in values) if values else None,
            "cohen_kappa": cohen_kappa(values),
        }
    numeric = {}
    for field in NUMERIC_FIELDS:
        values = [
            (float(left[field]), float(right[field])) for left, right in annotation_pairs
            if left.get(field) is not None and right.get(field) is not None
        ]
        numeric[field] = {
            "pairs": len(values),
            "mean_absolute_difference": mean(abs(a - b) for a, b in values) if values else None,
            "exact_agreement": mean(a == b for a, b in values) if values else None,
        }
    return {
        "annotation_pairs": len(annotation_pairs),
        "categorical": categorical,
        "numeric": numeric,
        "note": "Compute this report on unreconciled double-coded annotations; adjudicated labels are evaluated separately.",
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Compute inter-annotator agreement for SkillGen trace labels")
    parser.add_argument("annotations", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    report = evaluate(read_jsonl(args.annotations))
    write_json(args.output or args.annotations.with_name("annotation_agreement.json"), report)
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
