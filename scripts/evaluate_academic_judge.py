#!/usr/bin/env python3
"""Incremental academic judge for package-aware runtime answers.

This evaluator scores answer semantics only. It is intentionally separate from
the deterministic package runtime evaluator because it calls an LLM and can be
expensive on the full test track.
"""

import argparse
import json
import os
import sys
from typing import Dict, Iterable, List

sys.path.insert(0, os.path.dirname(__file__))

from common.loader import CUADSkillGenLoader
from common.llm_client import LLMClient
from runtime.package_evaluator import load_latest_results


METHODS = [
    "native_prompt_skill",
    "schema_prompt_skill",
    "summary2skill",
    "document_tool_maker",
    "evoskill_compiler",
    "graph_evoskill_compiler",
]

JUDGE_SYSTEM = """You are an academic evaluator for contract review answers.

Score only the candidate answer quality for the given task. Do not infer the
method name. Use the reference answer and verified target-contract evidence as
evaluation context. Return JSON only with numeric scores from 0.0 to 1.0."""


def load_jsonl_latest(path: str, key: str) -> Dict[str, dict]:
    latest = {}
    if not os.path.exists(path):
        return latest
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                record = json.loads(line)
                if record.get(key):
                    latest[record[key]] = record
    return latest


def task_index(loader: CUADSkillGenLoader, case_ids: Iterable[str]) -> Dict[str, dict]:
    tasks = {}
    for case_id in case_ids:
        for task in loader.load_tasks(case_id):
            tasks[task["task_id"]] = task
    return tasks


def build_prompt(task: dict, result: dict) -> str:
    evidence = [
        {
            "text": item.get("text", ""),
            "span_start": item.get("span_start"),
            "span_end": item.get("span_end"),
        }
        for item in result.get("evidence", [])[:5]
    ]
    payload = {
        "task": {
            "case_id": task.get("case_id"),
            "category": task.get("category"),
            "question": task.get("question"),
        },
        "reference_answer": task.get("reference_answer", ""),
        "candidate": {
            "status": result.get("status"),
            "answer": result.get("answer", ""),
            "verified_evidence": evidence,
        },
        "rubric": {
            "semantic_correctness": "Does the candidate answer make the same substantive finding as the reference?",
            "completeness": "Does it include the important conditions, exceptions, parties, dates, or limitations?",
            "faithfulness": "Is the answer supported by the verified target-contract evidence and not by unsupported claims?",
            "clarity": "Is the answer concise, usable, and understandable for contract review?",
        },
        "output_schema": {
            "semantic_correctness": 0.0,
            "completeness": 0.0,
            "faithfulness": 0.0,
            "clarity": 0.0,
            "rationale": "brief reason, no method name",
        },
    }
    return json.dumps(payload, ensure_ascii=False, indent=2)


def weighted_score(judgment: dict) -> float:
    weights = {
        "semantic_correctness": 0.40,
        "completeness": 0.25,
        "faithfulness": 0.20,
        "clarity": 0.15,
    }
    total = 0.0
    for key, weight in weights.items():
        value = judgment.get(key, 0.0)
        try:
            value = float(value)
        except (TypeError, ValueError):
            value = 0.0
        total += max(0.0, min(1.0, value)) * weight
    return round(total, 4)


def iter_answered_results(results_root: str, methods: List[str], case_ids: List[str], split: str, run_id: str):
    for method in methods:
        run_dir = os.path.join(results_root, method, "package_runtime_results", split, run_id)
        for case_id in case_ids:
            path = os.path.join(run_dir, f"{case_id}_results.jsonl")
            for task_id, result in load_latest_results(path).items():
                if result.get("_gold_status") == "answered" and result.get("status") == "answered":
                    yield method, case_id, task_id, result


def summarize(records: List[dict]) -> List[dict]:
    groups: Dict[str, List[dict]] = {}
    for record in records:
        groups.setdefault(record["method"], []).append(record)
    summary = []
    for method, items in sorted(groups.items()):
        row = {"method": method, "judged_tasks": len(items)}
        for key in ["academic_judge_score", "semantic_correctness", "completeness", "faithfulness", "clarity"]:
            row[key] = round(sum(float(item.get(key, 0.0)) for item in items) / len(items), 4) if items else 0.0
        summary.append(row)
    return summary


def main():
    parser = argparse.ArgumentParser(description="Incrementally judge runtime answer semantic quality")
    parser.add_argument("--data-root", default="data/cuad_skillgen")
    parser.add_argument("--results-root", default="results/skillgen/generated")
    parser.add_argument("--model", default="ecnu-plus")
    parser.add_argument("--method", choices=METHODS)
    parser.add_argument("--case-id")
    parser.add_argument("--split", choices=("dev", "test", "all"), default="test")
    parser.add_argument("--run-id", default="final-k10-k6")
    parser.add_argument("--max-items", type=int, help="Limit new judge calls for smoke/incremental runs")
    parser.add_argument("--evaluate-only", action="store_true", help="Only summarize existing judge cache")
    parser.add_argument("--output")
    args = parser.parse_args()

    loader = CUADSkillGenLoader(args.data_root)
    methods = [args.method] if args.method else METHODS
    case_ids = [args.case_id] if args.case_id else loader.get_all_case_ids()
    tasks = task_index(loader, case_ids)

    output_path = args.output or os.path.join(
        args.results_root,
        f"academic_judge_evaluation_{args.split}_{args.run_id}.jsonl",
    )
    summary_path = output_path[:-6] + "_summary.json" if output_path.endswith(".jsonl") else output_path + ".summary.json"
    existing = load_jsonl_latest(output_path, "judge_key")

    total_candidates = 0
    pending = []
    for method, case_id, task_id, result in iter_answered_results(args.results_root, methods, case_ids, args.split, args.run_id):
        total_candidates += 1
        judge_key = f"{method}:{case_id}:{task_id}"
        if judge_key not in existing:
            pending.append((judge_key, method, case_id, task_id, result))
    if args.max_items is not None:
        pending = pending[:args.max_items]

    print(
        f"Judge candidates={total_candidates} cached={len(existing)} "
        f"pending={len(pending)}"
    )

    if not args.evaluate_only and pending:
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        llm = LLMClient(model=args.model, temperature=0.0, max_tokens=4096)
        with open(output_path, "a", encoding="utf-8", buffering=1) as f:
            for index, (judge_key, method, case_id, task_id, result) in enumerate(pending, 1):
                judgment, usage = llm.call_json(JUDGE_SYSTEM, build_prompt(tasks[task_id], result), max_tokens=4096)
                record = {
                    "judge_key": judge_key,
                    "method": method,
                    "case_id": case_id,
                    "task_id": task_id,
                    "semantic_correctness": judgment.get("semantic_correctness", 0.0),
                    "completeness": judgment.get("completeness", 0.0),
                    "faithfulness": judgment.get("faithfulness", 0.0),
                    "clarity": judgment.get("clarity", 0.0),
                    "academic_judge_score": weighted_score(judgment),
                    "rationale": judgment.get("rationale", ""),
                    "usage": usage,
                }
                f.write(json.dumps(record, ensure_ascii=False) + "\n")
                existing[judge_key] = record
                if index % 25 == 0:
                    print(f"checkpoint: {index}/{len(pending)}")

    records = list(load_jsonl_latest(output_path, "judge_key").values())
    summary = summarize(records)
    with open(summary_path, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)
    print(f"Judge cache: {output_path}")
    print(f"Summary saved to {summary_path}")
    for row in summary:
        print(f"{row['method']:<28} judged={row['judged_tasks']:>5} academic={row['academic_judge_score']:.4f}")


if __name__ == "__main__":
    main()
