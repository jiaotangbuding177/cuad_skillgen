from __future__ import annotations

import argparse
import json
import math
import random
from pathlib import Path
from statistics import mean

from common import read_json, write_json


def paired_rows(left: dict, right: dict, metric: str = "reward"):
    def index(payload):
        return {(str(r["task_id"]), r.get("trial")): float(r[metric]) for r in payload["rows"] if isinstance(r.get(metric), (int, float))}
    a, b = index(left), index(right)
    keys = sorted(a.keys() & b.keys())
    return [(a[k], b[k]) for k in keys]


def bootstrap(pairs, seed=42, n=10000):
    rng = random.Random(seed)
    diffs = []
    for _ in range(n):
        sample = [pairs[rng.randrange(len(pairs))] for _ in pairs]
        diffs.append(mean(b - a for a, b in sample))
    diffs.sort()
    return {"mean_difference": mean(b - a for a, b in pairs), "ci95": [diffs[int(.025*n)], diffs[min(n-1, int(.975*n))]]}


def mcnemar(pairs):
    b = sum(a >= 1 and c < 1 for a, c in pairs)
    c = sum(a < 1 and c >= 1 for a, c in pairs)
    n = b + c
    if n == 0:
        return {"discordant_left_only": b, "discordant_right_only": c, "exact_p": 1.0}
    tail = sum(math.comb(n, k) for k in range(0, min(b, c) + 1)) / (2 ** n)
    return {"discordant_left_only": b, "discordant_right_only": c, "exact_p": min(1.0, 2 * tail)}


def main():
    parser = argparse.ArgumentParser(description="Paired comparison of two method metrics files")
    parser.add_argument("left", type=Path)
    parser.add_argument("right", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--bootstrap", type=int, default=10000)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--metric", default="reward")
    args = parser.parse_args()
    pairs = paired_rows(read_json(args.left), read_json(args.right), args.metric)
    if not pairs:
        raise SystemExit("No paired task-trial rows")
    result = {"metric": args.metric, "n_pairs": len(pairs), "paired_bootstrap": bootstrap(pairs, args.seed, args.bootstrap)}
    if args.metric == "reward":
        result["mcnemar"] = mcnemar(pairs)
    write_json(args.output, result)
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
