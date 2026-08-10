#!/usr/bin/env python3
"""Evaluate LLM-proxy semantic evidence validity from blinded judge records."""

import argparse
import json
import os
import sys
from collections import Counter

sys.path.insert(0, os.path.dirname(__file__))

from common.loader import CUADSkillGenLoader
from runtime.package_evaluator import load_latest_results


METHODS = [
    "native_prompt_skill",
    "schema_prompt_skill",
    "summary2skill",
    "document_tool_maker",
    "evoskill_compiler",
    "graph_evoskill_compiler",
]


def load_judgments(path: str) -> dict:
    latest = {}
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                item = json.loads(line)
                if item.get("judge_key"):
                    latest[item["judge_key"]] = item
    return latest


def evidence_label(judgment: dict) -> str:
    """Conservative proxy using the existing blinded answer/evidence judge."""
    faithfulness = float(judgment.get("faithfulness", 0.0))
    semantic = float(judgment.get("semantic_correctness", 0.0))
    if faithfulness >= 0.9 and semantic >= 0.8:
        return "valid"
    if faithfulness < 0.5 or semantic < 0.3:
        return "invalid"
    if faithfulness >= 0.8 and semantic >= 0.3:
        return "partial"
    return "ambiguous"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data-root", default="data/cuad_skillgen")
    parser.add_argument("--results-root", default="results/skillgen/generated")
    parser.add_argument("--split", default="test")
    parser.add_argument("--run-id", default="final-k10-k6")
    parser.add_argument(
        "--judge-cache",
        default=(
            "results/skillgen/generated/"
            "academic_judge_evaluation_test_final-k10-k6.jsonl"
        ),
    )
    parser.add_argument("--method", choices=METHODS)
    parser.add_argument("--output")
    args = parser.parse_args()

    loader = CUADSkillGenLoader(args.data_root)
    methods = [args.method] if args.method else METHODS
    judgments = load_judgments(args.judge_cache)
    case_ids = loader.get_all_case_ids()
    rows = []
    for method in methods:
        gold_answered = 0
        candidate_answered = 0
        judged = 0
        labels = Counter()
        for case_id in case_ids:
            path = os.path.join(
                args.results_root,
                method,
                "package_runtime_results",
                args.split,
                args.run_id,
                f"{case_id}_results.jsonl",
            )
            for task_id, result in load_latest_results(path).items():
                if result.get("_gold_status") != "answered":
                    continue
                gold_answered += 1
                if result.get("status") != "answered" or not result.get("evidence"):
                    continue
                candidate_answered += 1
                key = f"{method}:{case_id}:{task_id}"
                judgment = judgments.get(key)
                if not judgment:
                    continue
                judged += 1
                labels[evidence_label(judgment)] += 1

        valid = labels["valid"]
        partial = labels["partial"]
        weighted = valid + 0.5 * partial
        rows.append({
            "method": method,
            "gold_answered_tasks": gold_answered,
            "candidate_answered_with_verified_evidence": candidate_answered,
            "judged_tasks": judged,
            "judge_coverage": round(judged / candidate_answered, 4)
            if candidate_answered else 0.0,
            "label_counts": dict(sorted(labels.items())),
            "semantic_evidence_validity_conditional": round(valid / judged, 4)
            if judged else 0.0,
            "semantic_evidence_validity_end_to_end": round(
                valid / gold_answered, 4
            ) if gold_answered else 0.0,
            "semantic_evidence_validity_weighted_conditional": round(
                weighted / judged, 4
            ) if judged else 0.0,
            "semantic_evidence_validity_weighted_end_to_end": round(
                weighted / gold_answered, 4
            ) if gold_answered else 0.0,
        })

    output = args.output or os.path.join(
        args.results_root,
        f"semantic_evidence_validity_{args.split}_{args.run_id}.json",
    )
    with open(output, "w", encoding="utf-8") as f:
        json.dump(rows, f, indent=2, ensure_ascii=False)
    print(f"Semantic evidence validity saved to {output}")
    for row in rows:
        print(
            f"{row['method']:<28} judged={row['judged_tasks']:>4} "
            f"conditional={row['semantic_evidence_validity_conditional']:.4f} "
            f"end_to_end={row['semantic_evidence_validity_end_to_end']:.4f} "
            f"weighted_e2e={row['semantic_evidence_validity_weighted_end_to_end']:.4f}"
        )


if __name__ == "__main__":
    main()
