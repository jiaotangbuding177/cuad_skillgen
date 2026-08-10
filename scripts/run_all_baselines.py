#!/usr/bin/env python3
"""
Master script to run all CUAD-SkillGen baselines.

Usage:
  # Dry run (check all pipelines without calling LLM)
  python scripts/run_all_baselines.py --dry-run

  # Generate skills for all baselines, all cases
  python scripts/run_all_baselines.py --model claude-sonnet-4-20250514

  # Generate for a single baseline and case
  python scripts/run_all_baselines.py --method native_prompt_skill --case-id ip_and_license

  # Run runtime evaluation after skill generation
  python scripts/run_all_baselines.py --evaluate
"""

import argparse
import os
import subprocess
import sys
import time

BASELINES = [
    "native_prompt",
    "schema_prompt",
    "summary2skill",
    "document_tool_maker",
    "evoskill_compiler",
    "graph_evoskill_compiler",
]

METHOD_NAMES = {
    "native_prompt": "native_prompt_skill",
    "schema_prompt": "schema_prompt_skill",
    "summary2skill": "summary2skill",
    "document_tool_maker": "document_tool_maker",
    "evoskill_compiler": "evoskill_compiler",
    "graph_evoskill_compiler": "graph_evoskill_compiler",
}


def run_baseline(baseline: str, args):
    """Run a single baseline."""
    script = f"scripts/baselines/{baseline}.py"
    cmd = [sys.executable, script]
    cmd.extend(["--data-root", args.data_root])
    cmd.extend(["--results-root", args.results_root])
    cmd.extend(["--model", args.model])

    if args.case_id:
        cmd.extend(["--case-id", args.case_id])
    if args.overwrite:
        cmd.append("--overwrite")
    if args.dry_run:
        cmd.append("--dry-run")
    if baseline == "evoskill_compiler" and args.skip_compile:
        cmd.append("--skip-compile")

    print(f"\n{'='*60}")
    print(f"Running: {baseline}")
    print(f"Command: {' '.join(cmd)}")
    print(f"{'='*60}\n")

    result = subprocess.run(cmd, cwd=args.project_root)
    return result.returncode


def run_evaluation(args):
    """Run runtime evaluation for all methods."""
    script = "scripts/runtime/evaluator.py"
    cmd = [sys.executable, script]
    cmd.extend(["--results-root", args.results_root])
    for method in METHOD_NAMES.values():
        cmd.extend(["--methods", method])

    print(f"\n{'='*60}")
    print(f"Running evaluation")
    print(f"{'='*60}\n")

    result = subprocess.run(cmd, cwd=args.project_root)
    return result.returncode


def main():
    parser = argparse.ArgumentParser(description="Run all CUAD-SkillGen baselines")
    parser.add_argument("--project-root", default=".",
                        help="Project root directory")
    parser.add_argument("--data-root", default="data/cuad_skillgen")
    parser.add_argument("--results-root", default="results/skillgen/generated")
    parser.add_argument("--model", default="claude-sonnet-4-20250514")
    parser.add_argument("--method", default=None,
                        help="Run only this baseline (default: all)")
    parser.add_argument("--case-id", default=None,
                        help="Run only this case (default: all 9)")
    parser.add_argument("--overwrite", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--skip-compile", action="store_true",
                        help="Skip compile step for evoskill_compiler")
    parser.add_argument("--evaluate", action="store_true",
                        help="Run evaluation after generation")
    parser.add_argument("--evaluate-only", action="store_true",
                        help="Only run evaluation, skip generation")
    args = parser.parse_args()

    baselines_to_run = [args.method] if args.method else BASELINES

    if not args.evaluate_only:
        print(f"=== CUAD-SkillGen Baseline Pipeline ===")
        print(f"Baselines: {baselines_to_run}")
        print(f"Model: {args.model}")
        print(f"Case: {args.case_id or 'all 9 cases'}")
        print(f"Mode: {'dry-run' if args.dry_run else 'live'}")
        print()

        start_time = time.time()
        for baseline in baselines_to_run:
            if baseline not in BASELINES:
                print(f"Unknown baseline: {baseline}")
                print(f"Available: {BASELINES}")
                sys.exit(1)
            rc = run_baseline(baseline, args)
            if rc != 0:
                print(f"WARNING: {baseline} exited with code {rc}")

        total_duration = time.time() - start_time
        print(f"\n=== Generation complete in {total_duration:.1f}s ===")

    if args.evaluate or args.evaluate_only:
        run_evaluation(args)


if __name__ == "__main__":
    main()
