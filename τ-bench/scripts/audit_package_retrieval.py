from __future__ import annotations

import argparse
import json
from pathlib import Path

from common import ROOT, read_json, write_json
from runtime.package_runtime import RetrievalConfig, SkillPackage


DEFAULT_QUERIES = {
    "retail": "customer wants to cancel a pending order and asks about payment refund",
    "airline": "customer wants to change a flight reservation and baggage",
    "telecom": "customer abroad has slow mobile data with roaming and data saver",
    "banking_knowledge": "customer asks for a credit card with high cash back and no annual fee",
}


def main() -> None:
    parser = argparse.ArgumentParser(description="Offline audit of all Package-aware v1 profiles")
    parser.add_argument("--domain", choices=list(DEFAULT_QUERIES), default="telecom")
    parser.add_argument("--query")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    experiment = read_json(ROOT / "config" / "experiment.json")
    runtime = experiment["runtime"]
    config = RetrievalConfig(
        skill_top_k=runtime["skill_top_k"], atom_top_k=runtime["atom_top_k"],
        rule_top_k=runtime["rule_top_k"], workflow_top_k=runtime["workflow_top_k"],
        pattern_top_k=runtime["pattern_top_k"], max_context_chars=runtime["max_context_chars"],
        max_item_chars=runtime["max_item_chars"], history_messages=runtime["history_messages"],
    )
    query = args.query or DEFAULT_QUERIES[args.domain]
    rows = []
    for method in experiment["methods"]:
        package = SkillPackage(ROOT / "skills" / method / args.domain, args.domain, config)
        retrieval = package.retrieve(query)
        lane_hits: dict[str, int] = {}
        for item in retrieval["items"]:
            lane_hits[item["lane"]] = lane_hits.get(item["lane"], 0) + 1
        rows.append({
            "method": method, "profile": package.describe()["capability_profile"],
            "lane_counts": package.describe()["lane_counts"], "lane_hits": lane_hits,
            "context_chars": retrieval["context_chars"], "items": retrieval["items"],
            "graph_traversal_enabled": False,
        })
    output = {
        "runtime": "package_v1", "domain": args.domain, "query": query,
        "config": runtime, "methods": rows,
        "note": "Offline deterministic retrieval audit; not an Agent benchmark result.",
    }
    destination = args.output or ROOT / "results" / "evaluation" / f"package_v1_{args.domain}_retrieval_audit.json"
    write_json(destination, output)
    print(json.dumps({"output": str(destination), "methods": len(rows), "context_chars": {row["method"]: row["context_chars"] for row in rows}}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
