#!/usr/bin/env python3
"""Offline small-sample diagnosis for CUAD-SkillGen evidence failures."""

import argparse
import json
import os
import random
import sys
from collections import Counter
from typing import Dict, Iterable, List, Sequence

sys.path.insert(0, os.path.dirname(__file__))

from common.loader import CUADSkillGenLoader
from runtime.package_agent import (
    SkillPackage,
    build_contract_query,
    chunk_contract,
    score_texts,
)
from runtime.package_evaluator import (
    GoldEvidenceMapper,
    load_latest_results,
    span_iou,
    text_f1,
)


QUERY_VARIANTS = ("task_only", "package_without_knowledge", "full")


def rank_chunks(chunks, query: str) -> list:
    scores = score_texts(query, [chunk.text for chunk in chunks])
    return [
        chunk for chunk, _ in sorted(
            zip(chunks, scores), key=lambda pair: pair[1], reverse=True
        )
    ]


def gold_units_for_task(loader: CUADSkillGenLoader, task: dict) -> List[dict]:
    wanted = set(task.get("gold_evidence_unit_ids", []))
    return [
        unit for unit in loader.load_evidence_units(task["case_id"])
        if unit["evidence_unit_id"] in wanted
    ]


def retrieval_metrics(ranked_chunks: Sequence, gold_units: Sequence[dict], k: int) -> dict:
    ranks = []
    for unit in gold_units:
        rank = next(
            (
                index
                for index, chunk in enumerate(ranked_chunks, 1)
                if chunk.span_start <= unit["answer_start"]
                and chunk.span_end >= unit["answer_end"]
            ),
            None,
        )
        ranks.append(rank)
    found = [rank for rank in ranks if rank is not None and rank <= k]
    return {
        "any_gold_recall": bool(found),
        "all_gold_recall": bool(ranks) and len(found) == len(ranks),
        "reciprocal_rank": 1.0 / min(found) if found else 0.0,
        "gold_ranks": ranks,
    }


def best_relaxed_match(predicted: Sequence[dict], gold_units: Sequence[dict]) -> dict:
    best = {"score": 0.0, "span_iou": 0.0, "text_f1": 0.0}
    for evidence in predicted:
        for gold in gold_units:
            iou = span_iou(
                int(evidence.get("span_start", -1)),
                int(evidence.get("span_end", -1)),
                int(gold.get("answer_start", -2)),
                int(gold.get("answer_end", -2)),
            )
            similarity = text_f1(
                evidence.get("text", ""), gold.get("source_span", "")
            )
            if max(iou, similarity) > best["score"]:
                best = {
                    "score": round(max(iou, similarity), 4),
                    "span_iou": round(iou, 4),
                    "text_f1": round(similarity, 4),
                    "gold_evidence_unit_id": gold["evidence_unit_id"],
                }
    return best


def classify_failure(
    result: dict,
    retrieval: Dict[str, dict],
    mapped_gold: set,
    relaxed: dict,
) -> str:
    if mapped_gold:
        return "matched"
    if not retrieval["full"]["any_gold_recall"]:
        if retrieval["package_without_knowledge"]["any_gold_recall"]:
            return "knowledge_query_drift"
        if retrieval["task_only"]["any_gold_recall"]:
            return "package_query_drift"
        return "contract_retrieval_failure"
    if result.get("status") != "answered" or not result.get("evidence"):
        return "citation_extraction_failure"
    if relaxed.get("span_iou", 0.0) >= 0.3 or relaxed.get("text_f1", 0.0) >= 0.5:
        return "gold_mapping_threshold_or_boundary"
    return "alternative_or_wrong_evidence"


def iter_tasks(
    loader: CUADSkillGenLoader,
    case_ids: Iterable[str],
    split: str,
) -> Iterable[dict]:
    contract_ids = set(loader.get_split_contract_ids(split))
    for case_id in case_ids:
        for task in loader.load_tasks(case_id):
            if (
                task.get("gold_status") == "answered"
                and task.get("contract_id") in contract_ids
            ):
                yield task


def diagnose(args) -> dict:
    loader = CUADSkillGenLoader(args.data_root)
    mapper = GoldEvidenceMapper(loader)
    case_ids = [args.case_id] if args.case_id else loader.get_all_case_ids()
    tasks = list(iter_tasks(loader, case_ids, args.split))
    random.Random(args.seed).shuffle(tasks)
    if args.max_tasks:
        tasks = tasks[:args.max_tasks]

    packages = {}
    result_cache = {}
    evidence_cache = {}
    records = []
    for task in tasks:
        case_id = task["case_id"]
        if case_id not in packages:
            packages[case_id] = SkillPackage(
                args.results_root,
                args.method,
                case_id,
                loader.load_case_json(case_id),
            )
            path = os.path.join(
                args.results_root,
                args.method,
                "package_runtime_results",
                args.split,
                args.run_id,
                f"{case_id}_results.jsonl",
            )
            result_cache[case_id] = load_latest_results(path)
            evidence_cache[case_id] = {
                unit["evidence_unit_id"]: unit
                for unit in loader.load_evidence_units(case_id)
            }
        package = packages[case_id]
        result = result_cache[case_id].get(task["task_id"])
        if not result:
            continue

        category, question = task["category"], task["question"]
        guidance = package.skill_guidance(category, question)
        knowledge = package.retrieve_knowledge(
            category, question, args.top_k_knowledge
        )
        tools = package.tool_specs(category)[:3]
        chunks = chunk_contract(loader.load_contract_text(task["contract_id"]))
        gold_units = [
            evidence_cache[case_id][unit_id]
            for unit_id in task.get("gold_evidence_unit_ids", [])
            if unit_id in evidence_cache[case_id]
        ]
        retrieval = {}
        for variant in QUERY_VARIANTS:
            query = build_contract_query(
                category, question, guidance, knowledge, tools, variant
            )
            retrieval[variant] = retrieval_metrics(
                rank_chunks(chunks, query), gold_units, args.top_k_chunks
            )

        mapped, matches = mapper.map_evidence(
            case_id,
            task["contract_id"],
            category,
            result.get("evidence", []),
        )
        relaxed = best_relaxed_match(result.get("evidence", []), gold_units)
        records.append({
            "method": args.method,
            "case_id": case_id,
            "task_id": task["task_id"],
            "status": result.get("status"),
            "gold_evidence_count": len(gold_units),
            "predicted_evidence_count": len(result.get("evidence", [])),
            "retrieved_knowledge_ids": result.get("retrieved_knowledge_ids", []),
            "retrieval": retrieval,
            "mapped_gold_evidence_ids": sorted(mapped),
            "mapping_matches": matches,
            "best_relaxed_match": relaxed,
            "failure_bucket": classify_failure(result, retrieval, mapped, relaxed),
        })

    buckets = Counter(record["failure_bucket"] for record in records)
    retrieval_summary = {}
    for variant in QUERY_VARIANTS:
        denominator = len(records)
        retrieval_summary[variant] = {
            "tasks": denominator,
            f"gold_chunk_recall@{args.top_k_chunks}": round(
                sum(record["retrieval"][variant]["any_gold_recall"] for record in records)
                / denominator, 4
            ) if denominator else 0.0,
            f"all_gold_chunk_recall@{args.top_k_chunks}": round(
                sum(record["retrieval"][variant]["all_gold_recall"] for record in records)
                / denominator, 4
            ) if denominator else 0.0,
            "gold_chunk_mrr": round(
                sum(record["retrieval"][variant]["reciprocal_rank"] for record in records)
                / denominator, 4
            ) if denominator else 0.0,
        }
    return {
        "config": vars(args),
        "analyzed_tasks": len(records),
        "retrieval_summary": retrieval_summary,
        "failure_buckets": dict(sorted(buckets.items())),
        "records": records,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data-root", default="data/cuad_skillgen")
    parser.add_argument("--results-root", default="results/skillgen/generated")
    parser.add_argument("--method", default="evoskill_compiler")
    parser.add_argument("--case-id")
    parser.add_argument("--split", choices=("dev", "test"), default="test")
    parser.add_argument("--run-id", default="final-k10-k6")
    parser.add_argument("--top-k-chunks", type=int, default=10)
    parser.add_argument("--top-k-knowledge", type=int, default=6)
    parser.add_argument("--max-tasks", type=int, default=200)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--output")
    args = parser.parse_args()

    report = diagnose(args)
    output = args.output or os.path.join(
        args.results_root,
        f"evidence_diagnosis_{args.method}_{args.split}_{args.run_id}.json",
    )
    with open(output, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    print(f"Evidence diagnosis saved to {output}")
    print(json.dumps({
        "analyzed_tasks": report["analyzed_tasks"],
        "retrieval_summary": report["retrieval_summary"],
        "failure_buckets": report["failure_buckets"],
    }, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
