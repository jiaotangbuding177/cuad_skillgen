"""
Runtime Evaluation Script for CUAD-SkillGen.

Runs the runtime agent on all generated skills and computes evaluation metrics.

Usage:
  # Run all methods and cases
  python scripts/run_runtime_evaluation.py --model ecnu-plus

  # Run specific method only
  python scripts/run_runtime_evaluation.py --model ecnu-plus --method evoskill_compiler

  # Run specific case only
  python scripts/run_runtime_evaluation.py --model ecnu-plus --case-id ip_and_license

  # Overwrite existing results
  python scripts/run_runtime_evaluation.py --model ecnu-plus --overwrite
"""

import argparse
import os
import subprocess
import sys
import time

sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

from common.loader import CUADSkillGenLoader
from common.llm_client import LLMClient
from runtime.agent import RuntimeAgent


METHODS = [
    "native_prompt_skill",
    "schema_prompt_skill",
    "summary2skill",
    "document_tool_maker",
    "evoskill_compiler",
    "graph_evoskill_compiler",
]


def run_method(method: str, case_ids: list, loader: CUADSkillGenLoader, 
               llm: LLMClient, results_root: str, overwrite: bool = False, incremental: bool = False):
    """Run runtime evaluation for a single method."""
    print(f"\n{'='*60}")
    print(f"Method: {method}")
    print(f"{'='*60}")
    
    agent = RuntimeAgent(loader, llm, results_root, method)
    
    for case_id in case_ids:
        print(f"\n--- Case: {case_id} ---")
        
        # Check if SKILL.md exists
        skill_path = os.path.join(results_root, method, case_id, "SKILL.md")
        if not os.path.exists(skill_path):
            print(f"  WARNING: SKILL.md not found at {skill_path}, skipping")
            continue
        
        # Create runtime_results directory
        runtime_dir = os.path.join(results_root, method, "runtime_results")
        os.makedirs(runtime_dir, exist_ok=True)
        
        # Run all tasks for this case
        result = agent.run_all_tasks(case_id, runtime_dir, overwrite, incremental)
        
        if result.get("skipped"):
            print(f"  Skipped (results already exist)")
        else:
            print(f"  Completed: {result.get('task_count', 0)} tasks, "
                  f"{result.get('usage', {}).get('total_tokens', 0)} tokens, "
                  f"{result.get('duration', 0):.1f}s")


def run_evaluator(results_root: str, methods: list):
    """Run the evaluator to compute metrics."""
    print(f"\n{'='*60}")
    print(f"Running Evaluator")
    print(f"{'='*60}")
    
    evaluator_script = os.path.join(os.path.dirname(__file__), "runtime", "evaluator.py")
    cmd = [sys.executable, evaluator_script, "--results-root", results_root]
    
    for method in methods:
        cmd.extend(["--methods", method])
    
    result = subprocess.run(cmd, cwd=os.path.dirname(os.path.dirname(__file__)))
    return result.returncode


def main():
    parser = argparse.ArgumentParser(description="Run runtime evaluation for CUAD-SkillGen")
    parser.add_argument("--data-root", default="data/cuad_skillgen",
                        help="Path to CUAD-SkillGen data root")
    parser.add_argument("--results-root", default="results/skillgen/generated",
                        help="Path to results output root")
    parser.add_argument("--model", default="ecnu-plus",
                        help="LLM model name for runtime agent")
    parser.add_argument("--method", default=None,
                        help="Run only this method (default: all 5 methods)")
    parser.add_argument("--case-id", default=None,
                        help="Run only this case (default: all 9 cases)")
    parser.add_argument("--overwrite", action="store_true",
                        help="Overwrite existing runtime results")
    parser.add_argument("--incremental", action="store_true",
                        help="Only re-run tasks with status='error'")
    parser.add_argument("--skip-eval", action="store_true",
                        help="Skip running evaluator after runtime evaluation")
    args = parser.parse_args()
    
    # Initialize loader and LLM client
    loader = CUADSkillGenLoader(args.data_root)
    llm = LLMClient(model=args.model)
    
    # Determine which methods and cases to run
    methods_to_run = [args.method] if args.method else METHODS
    case_ids = [args.case_id] if args.case_id else loader.get_all_case_ids()
    
    print(f"=== CUAD-SkillGen Runtime Evaluation ===")
    print(f"Model: {args.model}")
    print(f"Methods: {len(methods_to_run)}")
    print(f"Cases: {len(case_ids)}")
    print()
    
    start_time = time.time()
    
    # Run runtime evaluation for each method
    for method in methods_to_run:
        if method not in METHODS:
            print(f"Unknown method: {method}")
            print(f"Available: {METHODS}")
            sys.exit(1)
        
        run_method(method, case_ids, loader, llm, args.results_root, args.overwrite, args.incremental)
    
    total_duration = time.time() - start_time
    print(f"\n=== Runtime evaluation complete in {total_duration:.1f}s ===")
    
    # Run evaluator
    if not args.skip_eval:
        rc = run_evaluator(args.results_root, methods_to_run)
        if rc != 0:
            print(f"WARNING: Evaluator exited with code {rc}")
    
    # Print total usage
    total_usage = llm.get_total_usage()
    print(f"\n=== Total LLM Usage ===")
    print(f"Calls: {total_usage['calls']}")
    print(f"Tokens: {total_usage['total_tokens']}")
    print(f"Errors: {total_usage['errors']}")


if __name__ == "__main__":
    main()
