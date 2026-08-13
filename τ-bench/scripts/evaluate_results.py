from __future__ import annotations

import argparse
import json
from collections import defaultdict
from pathlib import Path
from statistics import mean

from common import write_json


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def summarize(payload: dict) -> dict:
    simulations = payload.get("simulations", [])
    rows = []
    for sim in simulations:
        reward = sim.get("reward_info") or {}
        rows.append({
            "task_id": sim.get("task_id"),
            "trial": sim.get("trial"),
            "reward": reward.get("reward"),
            "breakdown": reward.get("reward_breakdown") or {},
            "agent_cost": sim.get("agent_cost"),
            "duration": sim.get("duration"),
            "termination_reason": sim.get("termination_reason"),
        })
    valid_rewards = [r["reward"] for r in rows if isinstance(r["reward"], (int, float))]
    by_component: dict[str, list[float]] = defaultdict(list)
    for row in rows:
        for key, value in row["breakdown"].items():
            if isinstance(value, (int, float)):
                by_component[str(key)].append(float(value))
    by_task: dict[str, list[float]] = defaultdict(list)
    for row in rows:
        if isinstance(row["reward"], (int, float)):
            by_task[str(row["task_id"])].append(float(row["reward"]))
    pass_at_k = mean([float(any(v >= 1.0 for v in values)) for values in by_task.values()]) if by_task else None
    pass_power_k = mean([float(all(v >= 1.0 for v in values)) for values in by_task.values()]) if by_task else None
    return {
        "num_simulations": len(rows),
        "num_tasks": len(by_task),
        "mean_reward": mean(valid_rewards) if valid_rewards else None,
        "strict_success_rate": mean([float(v >= 1.0) for v in valid_rewards]) if valid_rewards else None,
        "pass_at_k": pass_at_k,
        "pass_power_k": pass_power_k,
        "reward_components": {k: mean(v) for k, v in sorted(by_component.items())},
        "mean_agent_cost": mean([r["agent_cost"] for r in rows if isinstance(r["agent_cost"], (int, float))]) if any(isinstance(r["agent_cost"], (int, float)) for r in rows) else None,
        "mean_duration_seconds": mean([r["duration"] for r in rows if isinstance(r["duration"], (int, float))]) if any(isinstance(r["duration"], (int, float)) for r in rows) else None,
        "rows": rows,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("results", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    summary = summarize(load(args.results))
    output = args.output or args.results.with_name("metrics.json")
    write_json(output, summary)
    print(json.dumps({k: v for k, v in summary.items() if k != "rows"}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
