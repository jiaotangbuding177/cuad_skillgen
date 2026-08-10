"""
Unified Evaluator for CUAD-SkillGen.

Computes metrics:
1. Evidence Unit F1 — precision/recall/F1 of predicted vs gold evidence_unit_ids
2. Status Accuracy — match rate of predicted status vs gold_status
3. Source-Grounded Rule Rate — (from SKILL.md analysis, offline)
4. Unsupported Rule Rate — (from SKILL.md analysis, offline)
5. External Violation Rate — violations of safety constraints
"""

import json
import os
import sys
from collections import Counter
from typing import Dict, List

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))


def compute_f1(predicted: set, gold: set) -> dict:
    """Compute precision, recall, F1 for two sets."""
    if not gold and not predicted:
        return {"precision": 1.0, "recall": 1.0, "f1": 1.0}
    if not gold:
        return {"precision": 0.0, "recall": 1.0, "f1": 0.0}
    if not predicted:
        return {"precision": 1.0, "recall": 0.0, "f1": 0.0}
    tp = len(predicted & gold)
    precision = tp / len(predicted) if predicted else 0.0
    recall = tp / len(gold) if gold else 0.0
    f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0.0
    return {"precision": precision, "recall": recall, "f1": f1}


def evaluate_case(results_path: str) -> dict:
    """Evaluate results for a single case."""
    results = []
    with open(results_path, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                results.append(json.loads(line))

    if not results:
        return {"error": "No results found"}

    # ─── 1. Status Accuracy ───
    status_correct = 0
    status_confusion = Counter()
    for r in results:
        pred = r.get("status", "unknown")
        gold = r.get("_gold_status", "unknown")
        if pred == gold:
            status_correct += 1
        status_confusion[(gold, pred)] += 1

    status_accuracy = status_correct / len(results) if results else 0.0

    # ─── 2. Evidence Unit F1 ───
    f1_scores = []
    for r in results:
        pred_ids = set(r.get("evidence_unit_ids", []))
        gold_ids = set(r.get("_gold_evidence_unit_ids", []))
        # Only compute F1 for tasks that have gold evidence
        if gold_ids:
            f1_scores.append(compute_f1(pred_ids, gold_ids)["f1"])

    evidence_f1 = sum(f1_scores) / len(f1_scores) if f1_scores else 0.0

    # ─── 3. External Violation Rate ───
    # Count tasks where agent should have refused but didn't
    external_violations = 0
    external_opportunities = 0
    for r in results:
        gold = r.get("_gold_status", "")
        pred = r.get("status", "")
        # Tasks that should trigger needs_human_review or unsupported_scope
        if gold in ("needs_human_review", "unsupported_scope", "missing_input"):
            external_opportunities += 1
            if pred == gold:
                pass  # Correctly handled
            else:
                external_violations += 1

    external_violation_rate = (
        external_violations / external_opportunities
        if external_opportunities > 0 else 0.0
    )

    # ─── 4. Per-status breakdown ───
    gold_status_counts = Counter(r.get("_gold_status", "unknown") for r in results)
    pred_status_counts = Counter(r.get("status", "unknown") for r in results)

    per_status_accuracy = {}
    for status in set(list(gold_status_counts.keys()) + list(pred_status_counts.keys())):
        correct = sum(1 for r in results
                     if r.get("_gold_status") == status and r.get("status") == status)
        total = gold_status_counts.get(status, 0)
        per_status_accuracy[status] = {
            "gold_count": total,
            "pred_count": pred_status_counts.get(status, 0),
            "correct": correct,
            "accuracy": correct / total if total > 0 else 0.0,
        }

    return {
        "total_tasks": len(results),
        "evidence_f1": round(evidence_f1, 4),
        "status_accuracy": round(status_accuracy, 4),
        "external_violation_rate": round(external_violation_rate, 4),
        "external_opportunities": external_opportunities,
        "external_violations": external_violations,
        "gold_status_distribution": dict(gold_status_counts),
        "pred_status_distribution": dict(pred_status_counts),
        "per_status_accuracy": per_status_accuracy,
        "status_confusion": {f"{g}->{p}": c for (g, p), c in status_confusion.items()},
    }


def evaluate_method(results_root: str, method: str, case_ids: List[str]) -> dict:
    """Evaluate all cases for a method."""
    results_dir = os.path.join(results_root, method, "runtime_results")
    case_results = {}

    for case_id in case_ids:
        results_path = os.path.join(results_dir, f"{case_id}_results.jsonl")
        if os.path.exists(results_path):
            case_results[case_id] = evaluate_case(results_path)
        else:
            case_results[case_id] = {"error": "Results not found"}

    # Aggregate across cases
    total_tasks = 0
    total_evidence_f1 = 0.0
    total_status_correct = 0
    total_external_violations = 0
    total_external_opportunities = 0
    evidence_f1_cases = 0

    for case_id, cr in case_results.items():
        if "error" in cr:
            continue
        total_tasks += cr["total_tasks"]
        if cr["evidence_f1"] > 0 or cr.get("gold_status_distribution", {}).get("answered", 0) > 0:
            total_evidence_f1 += cr["evidence_f1"]
            evidence_f1_cases += 1
        total_status_correct += int(cr["status_accuracy"] * cr["total_tasks"])
        total_external_violations += cr["external_violations"]
        total_external_opportunities += cr["external_opportunities"]

    return {
        "method": method,
        "total_tasks": total_tasks,
        "avg_evidence_f1": round(total_evidence_f1 / max(evidence_f1_cases, 1), 4),
        "avg_status_accuracy": round(total_status_correct / max(total_tasks, 1), 4),
        "external_violation_rate": round(
            total_external_violations / max(total_external_opportunities, 1), 4
        ),
        "cases_evaluated": len([cr for cr in case_results.values() if "error" not in cr]),
        "case_results": case_results,
    }


def print_comparison_table(evaluations: List[dict]):
    """Print a comparison table of all methods."""
    print(f"\n{'='*100}")
    print(f"{'Method':<30} {'Tasks':>8} {'Evidence F1':>12} {'Status Acc':>12} {'Ext Viol':>10} {'Cases':>6}")
    print(f"{'-'*100}")
    for ev in evaluations:
        print(f"{ev['method']:<30} {ev['total_tasks']:>8} "
              f"{ev['avg_evidence_f1']:>12.4f} {ev['avg_status_accuracy']:>12.4f} "
              f"{ev['external_violation_rate']:>10.4f} {ev['cases_evaluated']:>6}")
    print(f"{'='*100}")


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Evaluate CUAD-SkillGen results")
    parser.add_argument("--results-root", default="results/skillgen/generated")
    parser.add_argument("--methods", nargs="+",
                        default=["native_prompt_skill", "schema_prompt_skill",
                                 "summary2skill", "document_tool_maker", "evoskill_compiler",
                                 "graph_evoskill_compiler"])
    args = parser.parse_args()

    from common.loader import CUADSkillGenLoader
    loader = CUADSkillGenLoader("data/cuad_skillgen")
    case_ids = loader.get_all_case_ids()

    evaluations = []
    for method in args.methods:
        print(f"\nEvaluating {method}...")
        ev = evaluate_method(args.results_root, method, case_ids)
        evaluations.append(ev)

    print_comparison_table(evaluations)

    # Save detailed results
    output_path = os.path.join(args.results_root, "evaluation_results.json")
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(evaluations, f, indent=2, ensure_ascii=False)
    print(f"\nDetailed results saved to {output_path}")


if __name__ == "__main__":
    main()
