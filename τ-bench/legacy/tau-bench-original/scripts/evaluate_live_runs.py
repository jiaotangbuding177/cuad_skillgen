from __future__ import annotations

import argparse
import math
from collections import defaultdict
from pathlib import Path

from common import ROOT, read_json, write_json


def main() -> None:
    parser = argparse.ArgumentParser(description="Aggregate incremental live tau-bench outputs")
    parser.add_argument("--run-root", required=True)
    parser.add_argument("--output")
    args = parser.parse_args()
    root = Path(args.run_root)
    records = []
    for path in sorted(root.rglob("task-*-trial-*.json")):
        record = read_json(path)
        if record.get("record_type") == "tau_live_run":
            records.append(record)
    if not records:
        raise SystemExit(f"No live records under {root}")
    by_task = defaultdict(list)
    for record in records:
        by_task[record["task_id"]].append(float(record["reward"] >= 1.0 - 1e-6))
    trials = min(len(values) for values in by_task.values())
    pass_k = {}
    for k in range(1, trials + 1):
        estimates = []
        for values in by_task.values():
            n = len(values)
            c = int(sum(values))
            estimates.append(math.comb(c, k) / math.comb(n, k) if c >= k else 0.0)
        pass_k[str(k)] = sum(estimates) / len(estimates)
    output = Path(args.output) if args.output else root / "evaluation_summary.json"
    write_json(
        output,
        {
            "records": len(records),
            "tasks": len(by_task),
            "average_reward": sum(record["reward"] for record in records) / len(records),
            "pass_hat_k": pass_k,
            "runtime_error_rate": sum(bool(record.get("error")) for record in records) / len(records),
            "average_cost": sum(record.get("total_cost") or 0.0 for record in records) / len(records),
            "note": "Policy, decision-status, provenance, and paired significance metrics require normalized trace analysis described in docs/METRICS.md.",
        },
    )
    print(f"Aggregated {len(records)} records -> {output}")


if __name__ == "__main__":
    main()

