#!/usr/bin/env python3
"""Run the package-aware, checkpointed CUAD-SkillGen experiment track."""

import argparse
import json
import os
import sys
import time

sys.path.insert(0, os.path.dirname(__file__))

from common.loader import CUADSkillGenLoader
from common.llm_client import LLMClient
from runtime.package_agent import IncrementalPackageRunner, PackageAwareAgent
from runtime.package_evaluator import evaluate_methods


METHODS = [
    "native_prompt_skill",
    "schema_prompt_skill",
    "summary2skill",
    "document_tool_maker",
    "evoskill_compiler",
]


def ensure_run_config(output_dir: str, config: dict) -> None:
    """Prevent incremental runs from mixing incompatible experiment settings."""
    os.makedirs(output_dir, exist_ok=True)
    path = os.path.join(output_dir, "run_config.json")
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            existing = json.load(f)
        if existing != config:
            raise RuntimeError(
                f"Run configuration differs from {path}. Use a new --run-id."
            )
        return
    with open(path, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=2, ensure_ascii=False)


def main():
    parser = argparse.ArgumentParser(description="Package-aware CUAD-SkillGen runtime")
    parser.add_argument("--data-root", default="data/cuad_skillgen")
    parser.add_argument("--results-root", default="results/skillgen/generated")
    parser.add_argument("--model", default="ecnu-plus")
    parser.add_argument("--method", choices=METHODS)
    parser.add_argument("--case-id")
    parser.add_argument("--split", choices=("dev", "test", "all"), default="test")
    parser.add_argument("--no-governance", action="store_true")
    parser.add_argument("--no-retry-errors", action="store_true")
    parser.add_argument("--top-k-chunks", type=int, default=10)
    parser.add_argument("--top-k-knowledge", type=int, default=6)
    parser.add_argument("--max-tasks", type=int)
    parser.add_argument("--run-id", default="package-v1")
    parser.add_argument("--evaluate-only", action="store_true")
    args = parser.parse_args()

    loader = CUADSkillGenLoader(args.data_root)
    methods = [args.method] if args.method else METHODS
    case_ids = [args.case_id] if args.case_id else loader.get_all_case_ids()

    if not args.evaluate_only:
        llm = LLMClient(model=args.model)
        start = time.time()
        for method in methods:
            print(f"\n=== {method} ===")
            agent = PackageAwareAgent(
                loader,
                llm,
                args.results_root,
                method,
                top_k_chunks=args.top_k_chunks,
                top_k_knowledge=args.top_k_knowledge,
            )
            runner = IncrementalPackageRunner(agent, loader)
            output_dir = os.path.join(
                args.results_root,
                method,
                "package_runtime_results",
                args.split,
                args.run_id,
            )
            ensure_run_config(output_dir, {
                "protocol_version": "package-aware-v1",
                "method": method,
                "model": args.model,
                "split": args.split,
                "include_governance": not args.no_governance,
                "top_k_chunks": args.top_k_chunks,
                "top_k_knowledge": args.top_k_knowledge,
            })
            for case_id in case_ids:
                skill_path = os.path.join(args.results_root, method, case_id, "SKILL.md")
                if not os.path.exists(skill_path):
                    print(f"  [{case_id}] missing SKILL.md; skipped")
                    continue
                summary = runner.run_case(
                    case_id,
                    output_dir,
                    split=args.split,
                    include_governance=not args.no_governance,
                    retry_errors=not args.no_retry_errors,
                    max_tasks=args.max_tasks,
                )
                print(
                    f"  [{case_id}] processed={summary['processed_tasks']} "
                    f"tokens={summary['usage']['total_tokens']} "
                    f"seconds={summary['duration']:.1f}"
                )
        print(f"\nRuntime completed in {time.time() - start:.1f}s")

    evaluations = evaluate_methods(
        loader,
        args.results_root,
        methods,
        case_ids,
        split=args.split,
        run_id=args.run_id,
    )
    output_path = os.path.join(
        args.results_root,
        f"package_runtime_evaluation_{args.split}_{args.run_id}.json",
    )
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(evaluations, f, indent=2, ensure_ascii=False)
    print(f"Evaluation saved to {output_path}")
    for item in evaluations:
        print(
            f"{item['method']:<28} tasks={item['total_tasks']:>6} "
            f"coverage={item['result_coverage']:.4f} "
            f"success={item['task_success_rate']:.4f} "
            f"status_macro_f1={item['status_macro_f1']:.4f} "
            f"balanced_acc={item['status_balanced_accuracy']:.4f} "
            f"evidence_f1={item['evidence_f1']:.4f} "
            f"containment_f1={item['containment_evidence_f1']:.4f} "
            f"no_answer={item.get('no_answer_correct', 0.0):.4f} "
            f"governance_boundary={item.get('governance_boundary_correct', item['boundary_correct']):.4f} "
            f"boundary={item['boundary_correct']:.4f} "
            f"isolation={item['contract_isolation']:.4f} "
            f"errors={item['error_rate']:.4f}"
        )


if __name__ == "__main__":
    main()
