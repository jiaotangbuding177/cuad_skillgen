from __future__ import annotations

import argparse
import json
from pathlib import Path

from common import read_json, write_jsonl
from extract_audit_trace import extract


def main():
    parser = argparse.ArgumentParser(description="Create a blinded trace annotation template")
    parser.add_argument("results", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    payload = read_json(args.results)
    _, audit = extract(payload)
    rows = []
    for sim, trace in zip(payload.get("simulations", []), audit["per_simulation"]):
        rows.append({
            "task_id": sim.get("task_id"), "trial": sim.get("trial"),
            "simulation_id": sim.get("id"),
            "transcript": [{"role": m.get("role"), "content": m.get("content"), "tool_calls": m.get("tool_calls")} for m in sim.get("messages") or []],
            "gold_status": None, "pred_status": None,
            "policy_compliant": None, "precondition_recall": None,
            "exception_branch_recall": None, "verification_recall": None,
            "provenance_present": None, "provenance_valid": None,
            "pred_activated_module_ids": trace.get("activated_module_ids") or [],
            "pred_activated_required_tools": trace.get("activated_required_tools") or [],
            "gold_requires_skill": None,
            "gold_applicable_module_ids": [],
            "activated_module_utility": None,
            "tool_binding_correct": None,
            "annotator_id": None, "notes": None,
        })
    write_jsonl(args.output, rows)
    print(json.dumps({"rows": len(rows), "output": str(args.output)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
