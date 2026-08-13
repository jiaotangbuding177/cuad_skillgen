from __future__ import annotations

import argparse
import json
from collections import defaultdict
from pathlib import Path
from statistics import mean

from common import ROOT, read_json, write_json


def main():
    parser = argparse.ArgumentParser(description="Aggregate completed run metrics into method/domain tables")
    parser.add_argument("--run-prefix", default="main")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    grouped = defaultdict(list)
    missing = []
    for manifest_path in (ROOT / "results" / "runs").glob(f"{args.run_prefix}-*/run_manifest.json"):
        manifest = read_json(manifest_path)
        metrics_path = manifest_path.with_name("extended_metrics.json")
        if manifest.get("status") != "complete" or not metrics_path.exists():
            missing.append({"run_id": manifest.get("run_id"), "status": manifest.get("status"), "metrics_exists": metrics_path.exists()})
            continue
        grouped[(manifest["method"], manifest["domain"])].append(read_json(metrics_path))
    table = []
    for (method, domain), runs in sorted(grouped.items()):
        def values(section, key):
            return [r[section][key] for r in runs if isinstance(r[section].get(key), (int, float))]
        row = {"method": method, "domain": domain, "num_runs": len(runs)}
        for key in ["mean_reward", "strict_success_rate", "mean_agent_cost", "mean_duration_seconds"]:
            v = values("native", key)
            row[key] = mean(v) if v else None
        for key in ["actor_ownership_accuracy", "skill_activations", "activation_context_chars", "activated_source_atom_count", "required_document_recall", "required_document_mrr"]:
            v = values("process", key)
            row[key] = mean(v) if v else None
        for key in [
            "observable_atom_execution_coverage", "actor_constraint_satisfaction",
            "ordering_compliance", "precondition_proxy", "verification_proxy",
            "activated_required_tool_recall_proxy", "business_tool_grounding_precision_proxy",
        ]:
            v = values("action", key)
            row[key] = mean(v) if v else None
        table.append(row)
    domain_macro = []
    for method in sorted({r["method"] for r in table}):
        rows = [r for r in table if r["method"] == method]
        rewards = [r["mean_reward"] for r in rows if r["mean_reward"] is not None]
        successes = [r["strict_success_rate"] for r in rows if r["strict_success_rate"] is not None]
        domain_macro.append({"method": method, "domains": len(rows), "domain_macro_reward": mean(rewards) if rewards else None, "domain_macro_strict_success": mean(successes) if successes else None})
    output = {"run_prefix": args.run_prefix, "method_domain": table, "domain_macro": domain_macro, "incomplete_units": missing}
    write_json(args.output or ROOT / "results" / "evaluation" / f"{args.run_prefix}_aggregate.json", output)
    print(json.dumps({"groups": len(table), "methods": len(domain_macro), "incomplete": len(missing)}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
