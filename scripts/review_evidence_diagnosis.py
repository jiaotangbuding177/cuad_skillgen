#!/usr/bin/env python3
"""LLM review and mapper sensitivity analysis for an evidence diagnosis sample."""

import argparse
import json
import os
import sys
from collections import Counter
from itertools import product

sys.path.insert(0, os.path.dirname(__file__))

from common.loader import CUADSkillGenLoader
from common.llm_client import LLMClient
from runtime.package_evaluator import (
    GoldEvidenceMapper,
    compute_evidence_f1,
    load_latest_results,
)


REVIEW_LABELS = {
    "valid_alternative",
    "partial_support",
    "wrong_evidence",
    "ambiguous",
}

JUDGE_SYSTEM = """You are a blinded evidence relevance evaluator for contract review.

Decide whether the candidate evidence from the target contract supports the
substantive reference finding. Do not require the candidate to copy the gold
annotation span. Distinguish a legally/relevantly valid alternative passage
from partial support and genuinely wrong evidence. Return JSON only."""


def load_jsonl_latest(path: str, key: str) -> dict:
    latest = {}
    if not os.path.exists(path):
        return latest
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                item = json.loads(line)
                if item.get(key):
                    latest[item[key]] = item
    return latest


def build_review_prompt(task: dict, result: dict, gold_units: list) -> str:
    payload = {
        "task": {
            "category": task.get("category"),
            "question": task.get("question"),
        },
        "reference_answer": task.get("reference_answer", ""),
        "gold_annotated_evidence": [
            unit.get("source_span", "") for unit in gold_units
        ],
        "candidate_answer": result.get("answer", ""),
        "candidate_verified_target_contract_evidence": [
            item.get("text", "") for item in result.get("evidence", [])
        ],
        "rubric": {
            "valid_alternative": (
                "The candidate passage independently supports the same material "
                "finding, even though it differs from the annotated span."
            ),
            "partial_support": (
                "The passage supports only part of the finding or omits a material "
                "condition, exception, party, date, or limitation."
            ),
            "wrong_evidence": (
                "The passage does not support the requested/reference finding or "
                "supports a materially different conclusion."
            ),
            "ambiguous": (
                "The available text is insufficient to distinguish the above."
            ),
        },
        "output_schema": {
            "label": "valid_alternative | partial_support | wrong_evidence | ambiguous",
            "relevance_score": 0.0,
            "supports_reference": False,
            "rationale": "brief evidence-specific reason",
        },
    }
    return json.dumps(payload, ensure_ascii=False, indent=2)


def task_and_evidence_indexes(loader: CUADSkillGenLoader):
    tasks, units = {}, {}
    for case_id in loader.get_all_case_ids():
        for task in loader.load_tasks(case_id):
            tasks[task["task_id"]] = task
        for unit in loader.load_evidence_units(case_id):
            units[unit["evidence_unit_id"]] = unit
    return tasks, units


def result_for_record(record: dict, diagnosis_config: dict, results_root: str) -> dict:
    path = os.path.join(
        results_root,
        record["method"],
        "package_runtime_results",
        diagnosis_config["split"],
        diagnosis_config["run_id"],
        f"{record['case_id']}_results.jsonl",
    )
    return load_latest_results(path).get(record["task_id"], {})


def run_llm_review(args, diagnosis: dict, loader, tasks, units) -> dict:
    cache_path = args.review_cache or os.path.join(
        args.results_root,
        "evidence_llm_review_evoskill_test_final-k10-k6.jsonl",
    )
    existing = load_jsonl_latest(cache_path, "review_key")
    candidates = [
        record for record in diagnosis["records"]
        if record["failure_bucket"] == "alternative_or_wrong_evidence"
    ]
    pending = [
        record for record in candidates
        if record["task_id"] not in existing
    ]
    if args.max_reviews is not None:
        pending = pending[:args.max_reviews]
    print(
        f"LLM evidence review candidates={len(candidates)} "
        f"cached={len(existing)} pending={len(pending)}"
    )

    if pending and not args.evaluate_only:
        os.makedirs(os.path.dirname(cache_path), exist_ok=True)
        llm = LLMClient(
            model=args.model,
            temperature=0.0,
            max_tokens=1200,
        )
        with open(cache_path, "a", encoding="utf-8", buffering=1) as f:
            for index, record in enumerate(pending, 1):
                task = tasks[record["task_id"]]
                result = result_for_record(
                    record, diagnosis["config"], args.results_root
                )
                gold_units = [
                    units[unit_id]
                    for unit_id in task.get("gold_evidence_unit_ids", [])
                    if unit_id in units
                ]
                judgment, usage = llm.call_json(
                    JUDGE_SYSTEM,
                    build_review_prompt(task, result, gold_units),
                    max_tokens=1200,
                )
                label = str(judgment.get("label", "ambiguous")).strip().lower()
                if label not in REVIEW_LABELS:
                    label = "ambiguous"
                item = {
                    "review_key": record["task_id"],
                    "method": record["method"],
                    "case_id": record["case_id"],
                    "task_id": record["task_id"],
                    "label": label,
                    "relevance_score": judgment.get("relevance_score", 0.0),
                    "supports_reference": bool(
                        judgment.get("supports_reference", False)
                    ),
                    "rationale": judgment.get("rationale", ""),
                    "usage": usage,
                }
                f.write(json.dumps(item, ensure_ascii=False) + "\n")
                existing[item["review_key"]] = item
                if index % 10 == 0:
                    print(f"review checkpoint: {index}/{len(pending)}")

    reviewed = [
        existing[record["task_id"]]
        for record in candidates
        if record["task_id"] in existing
    ]
    counts = Counter(item["label"] for item in reviewed)
    supports = sum(bool(item.get("supports_reference")) for item in reviewed)
    return {
        "cache_path": cache_path,
        "candidate_tasks": len(candidates),
        "reviewed_tasks": len(reviewed),
        "label_counts": dict(sorted(counts.items())),
        "supports_reference_count": supports,
        "supports_reference_rate": round(supports / len(reviewed), 4)
        if reviewed else 0.0,
    }


def mapper_sensitivity(diagnosis: dict, loader, tasks, units, results_root: str):
    mapper = GoldEvidenceMapper(loader)
    prepared = []
    for record in diagnosis["records"]:
        task = tasks[record["task_id"]]
        prepared.append((
            record,
            task,
            result_for_record(record, diagnosis["config"], results_root),
        ))
    thresholds = list(product(
        (0.3, 0.4, 0.5, 0.6, 0.7),
        (0.5, 0.6, 0.7, 0.8, 0.9),
    ))
    rows = []
    for iou_threshold, text_threshold in thresholds:
        metrics = []
        matched_tasks = 0
        for record, task, result in prepared:
            mapped, details = mapper.map_evidence(
                record["case_id"],
                task["contract_id"],
                task["category"],
                result.get("evidence", []),
                iou_threshold=iou_threshold,
                text_threshold=text_threshold,
            )
            if mapped:
                matched_tasks += 1
            metrics.append(compute_evidence_f1(
                predicted_count=len(result.get("evidence", [])),
                matched_gold=mapped,
                gold=set(task.get("gold_evidence_unit_ids", [])),
                matched_count=len(details),
            ))
        denominator = len(metrics)
        rows.append({
            "iou_threshold": iou_threshold,
            "text_threshold": text_threshold,
            "tasks": denominator,
            "matched_tasks": matched_tasks,
            "matched_task_rate": round(matched_tasks / denominator, 4)
            if denominator else 0.0,
            "evidence_precision": round(
                sum(item["precision"] for item in metrics) / denominator, 4
            ) if denominator else 0.0,
            "evidence_recall": round(
                sum(item["recall"] for item in metrics) / denominator, 4
            ) if denominator else 0.0,
            "evidence_f1": round(
                sum(item["f1"] for item in metrics) / denominator, 4
            ) if denominator else 0.0,
        })
    return rows


def summarize_existing_academic_review(diagnosis: dict, path: str) -> dict:
    """Reuse the already completed blinded LLM judge as a secondary review.

    The mapping is declared explicitly and is not presented as an independent
    second model call.
    """
    candidate_ids = {
        record["task_id"] for record in diagnosis["records"]
        if record["failure_bucket"] == "alternative_or_wrong_evidence"
    }
    latest = {}
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            for line in f:
                if not line.strip():
                    continue
                item = json.loads(line)
                if (
                    item.get("method") == "evoskill_compiler"
                    and item.get("task_id") in candidate_ids
                ):
                    latest[item["task_id"]] = item
    labels = Counter()
    for item in latest.values():
        faithfulness = float(item.get("faithfulness", 0.0))
        semantic = float(item.get("semantic_correctness", 0.0))
        if faithfulness >= 0.9 and semantic >= 0.8:
            label = "valid_alternative"
        elif faithfulness < 0.5 or semantic < 0.3:
            label = "wrong_evidence"
        elif faithfulness >= 0.8 and semantic >= 0.3:
            label = "partial_support"
        else:
            label = "ambiguous"
        labels[label] += 1
    denominator = len(latest)
    return {
        "source": path,
        "review_type": "reused_blinded_academic_llm_judgments",
        "candidate_tasks": len(candidate_ids),
        "reviewed_tasks": denominator,
        "label_rule": {
            "valid_alternative": "faithfulness>=0.9 and semantic_correctness>=0.8",
            "wrong_evidence": "faithfulness<0.5 or semantic_correctness<0.3",
            "partial_support": "faithfulness>=0.8 and semantic_correctness>=0.3 otherwise",
            "ambiguous": "remaining cases",
        },
        "label_counts": dict(sorted(labels.items())),
        "valid_or_partial_rate": round(
            (labels["valid_alternative"] + labels["partial_support"])
            / denominator, 4
        ) if denominator else 0.0,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data-root", default="data/cuad_skillgen")
    parser.add_argument("--results-root", default="results/skillgen/generated")
    parser.add_argument(
        "--diagnosis",
        default=(
            "results/skillgen/generated/"
            "evidence_diagnosis_evoskill_compiler_test_final-k10-k6.json"
        ),
    )
    parser.add_argument("--model", default="ecnu-plus")
    parser.add_argument("--review-cache")
    parser.add_argument(
        "--academic-cache",
        default=(
            "results/skillgen/generated/"
            "academic_judge_evaluation_test_final-k10-k6.jsonl"
        ),
    )
    parser.add_argument("--max-reviews", type=int)
    parser.add_argument("--evaluate-only", action="store_true")
    parser.add_argument("--output")
    args = parser.parse_args()

    with open(args.diagnosis, "r", encoding="utf-8") as f:
        diagnosis = json.load(f)
    loader = CUADSkillGenLoader(args.data_root)
    tasks, units = task_and_evidence_indexes(loader)

    review = run_llm_review(args, diagnosis, loader, tasks, units)
    prior_academic_review = summarize_existing_academic_review(
        diagnosis, args.academic_cache
    )
    sensitivity = mapper_sensitivity(
        diagnosis, loader, tasks, units, args.results_root
    )
    baseline = next(
        row for row in sensitivity
        if row["iou_threshold"] == 0.5 and row["text_threshold"] == 0.8
    )
    report = {
        "diagnosis": args.diagnosis,
        "llm_review": review,
        "prior_academic_llm_review": prior_academic_review,
        "mapper_baseline": baseline,
        "mapper_sensitivity": sensitivity,
    }
    output = args.output or os.path.join(
        args.results_root,
        "evidence_review_and_mapper_sensitivity_evoskill_test_final-k10-k6.json",
    )
    with open(output, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    print(f"Review and sensitivity report saved to {output}")
    print(json.dumps({
        "llm_review": review,
        "prior_academic_llm_review": prior_academic_review,
        "mapper_baseline": baseline,
        "best_evidence_f1": max(
            sensitivity, key=lambda row: row["evidence_f1"]
        ),
    }, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
