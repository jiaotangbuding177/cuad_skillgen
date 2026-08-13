from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

from common import ROOT, VENDOR_ROOT, atomic_write_text, read_json, write_json


def dump_model(value):
    if hasattr(value, "model_dump"):
        return value.model_dump()
    if hasattr(value, "dict"):
        return value.dict()
    return value


def main() -> None:
    parser = argparse.ArgumentParser(description="Incremental live tau-bench runner with generated Skills")
    parser.add_argument("--method", required=True)
    parser.add_argument("--skills-root", default=str(ROOT / "skills"))
    parser.add_argument("--domain", choices=["retail", "airline"], required=True)
    parser.add_argument("--split", choices=["train", "dev", "test"], default="test")
    parser.add_argument("--model", required=True)
    parser.add_argument("--model-provider", required=True)
    parser.add_argument("--user-model", required=True)
    parser.add_argument("--user-model-provider", required=True)
    parser.add_argument("--user-strategy", default="llm")
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--task-ids", type=int, nargs="*")
    parser.add_argument("--start-index", type=int, default=0)
    parser.add_argument("--end-index", type=int, default=-1)
    parser.add_argument("--num-trials", type=int, default=1)
    parser.add_argument("--max-steps", type=int, default=30)
    parser.add_argument("--temperature", type=float, default=0.0)
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()

    skill_root = Path(args.skills_root) / args.method / args.domain
    skill_path = skill_root / "SKILL.md"
    if not skill_path.exists():
        raise SystemExit(f"Missing Skill package: {skill_root}")
    if args.domain == "airline" and args.split != "test":
        raise SystemExit("The frozen original airline environment exposes only the test split")

    sys.path.insert(0, str(VENDOR_ROOT))
    try:
        from tau_bench.agents.tool_calling_agent import ToolCallingAgent
        from tau_bench.envs import get_env
    except ModuleNotFoundError as exc:
        raise SystemExit(
            "Live dependencies are missing. Install the frozen upstream package with "
            "`python -m pip install -e vendor/tau-bench` in a dedicated environment. "
            f"Original error: {exc}"
        ) from exc

    probe = get_env(
        args.domain,
        user_strategy=args.user_strategy,
        user_model=args.user_model,
        user_provider=args.user_model_provider,
        task_split=args.split,
        task_index=0,
    )
    task_ids = args.task_ids or list(
        range(args.start_index, len(probe.tasks) if args.end_index == -1 else min(args.end_index, len(probe.tasks)))
    )
    agent = ToolCallingAgent(
        tools_info=probe.tools_info,
        wiki=skill_path.read_text(encoding="utf-8"),
        model=args.model,
        provider=args.model_provider,
        temperature=args.temperature,
    )
    run_root = ROOT / "results" / "runs" / args.run_id / args.method / args.domain / args.split
    run_root.mkdir(parents=True, exist_ok=True)
    manifest = {
        "run_id": args.run_id,
        "method": args.method,
        "domain": args.domain,
        "split": args.split,
        "model": args.model,
        "model_provider": args.model_provider,
        "user_model": args.user_model,
        "user_model_provider": args.user_model_provider,
        "user_strategy": args.user_strategy,
        "temperature": args.temperature,
        "max_steps": args.max_steps,
        "num_trials": args.num_trials,
        "task_ids": task_ids,
        "skill_manifest": read_json(skill_root / "manifest.json"),
        "incremental_unit": "task_id_x_trial",
    }
    write_json(run_root / "run_manifest.json", manifest)

    completed = 0
    for trial in range(args.num_trials):
        for task_id in task_ids:
            target = run_root / f"task-{task_id:04d}-trial-{trial:02d}.json"
            if target.exists() and not args.force:
                completed += 1
                continue
            env = get_env(
                args.domain,
                user_strategy=args.user_strategy,
                user_model=args.user_model,
                user_provider=args.user_model_provider,
                task_split=args.split,
                task_index=task_id,
            )
            started = time.time()
            try:
                solved = agent.solve(env=env, task_index=task_id, max_num_steps=args.max_steps)
                record = {
                    "record_type": "tau_live_run",
                    "task_id": task_id,
                    "trial": trial,
                    "reward": solved.reward,
                    "messages": solved.messages,
                    "info": dump_model(solved.info),
                    "total_cost": solved.total_cost,
                    "duration_seconds": round(time.time() - started, 3),
                    "error": None,
                }
            except Exception as exc:
                record = {
                    "record_type": "tau_live_run",
                    "task_id": task_id,
                    "trial": trial,
                    "reward": 0.0,
                    "messages": [],
                    "info": {},
                    "total_cost": None,
                    "duration_seconds": round(time.time() - started, 3),
                    "error": f"{type(exc).__name__}: {exc}",
                }
            atomic_write_text(target, json.dumps(record, ensure_ascii=False, indent=2) + "\n")
            completed += 1
            print(f"[{completed}/{len(task_ids) * args.num_trials}] task={task_id} trial={trial} reward={record['reward']}")


if __name__ == "__main__":
    main()
