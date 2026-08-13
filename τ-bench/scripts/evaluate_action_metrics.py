from __future__ import annotations

import argparse
import json
from pathlib import Path
from statistics import mean

from common import read_json, write_json
from extract_audit_trace import extract


def ordered_calls(simulation: dict) -> list[dict]:
    calls = []
    for message_index, message in enumerate(simulation.get("messages") or []):
        role = message.get("role")
        for call in message.get("tool_calls") or []:
            if call.get("name") == "activate_skill":
                continue
            calls.append({"index": message_index, "tool": call.get("name"), "actor": role})
    return calls


def positions(calls: list[dict], tool: str) -> list[int]:
    return [index for index, call in enumerate(calls) if call["tool"] == tool]


def score_requirement(requirement: dict, calls: list[dict]) -> bool | None:
    kind = requirement.get("kind")
    if kind == "actor":
        relevant = [call for call in calls if call["tool"] == requirement.get("tool")]
        return all(call["actor"] == requirement.get("actor") for call in relevant) if relevant else None
    if kind in {"ordering", "precondition"}:
        before = requirement.get("before_tool") or requirement.get("evidence_tool")
        after = requirement.get("after_tool") or requirement.get("action_tool")
        after_positions = positions(calls, after)
        if not after_positions:
            return None
        before_positions = positions(calls, before)
        return bool(before_positions) and min(before_positions) < min(after_positions)
    if kind == "verification":
        action_positions = positions(calls, requirement.get("action_tool"))
        if not action_positions:
            return None
        verification_positions = positions(calls, requirement.get("verification_tool"))
        return bool(verification_positions) and max(verification_positions) > min(action_positions)
    return None


def evaluate(payload: dict) -> dict:
    _, audit = extract(payload)
    rows = []
    for simulation, trace in zip(payload.get("simulations", []), audit["per_simulation"]):
        calls = ordered_calls(simulation)
        by_kind: dict[str, list[bool]] = {}
        requirement_rows = []
        seen = set()
        for requirement in trace.get("activated_trace_requirements") or []:
            requirement_id = requirement.get("requirement_id") or json.dumps(requirement, sort_keys=True)
            if requirement_id in seen:
                continue
            seen.add(requirement_id)
            score = score_requirement(requirement, calls)
            requirement_rows.append({**requirement, "satisfied": score})
            if score is not None:
                by_kind.setdefault(requirement.get("kind", "unknown"), []).append(score)
        observable = [item["satisfied"] for item in requirement_rows if item["satisfied"] is not None]
        called_tools = [call["tool"] for call in calls if call.get("tool")]
        declared_tools = set(trace.get("activated_required_tools") or [])
        used_declared_tools = declared_tools & set(called_tools)
        rows.append({
            "task_id": simulation.get("task_id"), "trial": simulation.get("trial"),
            "skill_activations": trace.get("skill_activations", 0),
            "activated_module_ids": trace.get("activated_module_ids") or [],
            "activation_context_chars": trace.get("activation_context_chars", 0),
            "activated_source_atom_count": len(trace.get("activated_source_atom_ids") or []),
            "activated_required_tool_recall_proxy": (
                len(used_declared_tools) / len(declared_tools) if declared_tools else None
            ),
            "business_tool_grounding_precision_proxy": (
                sum(tool in declared_tools for tool in called_tools) / len(called_tools)
                if declared_tools and called_tools else None
            ),
            "observable_atom_execution_coverage": mean(observable) if observable else None,
            "actor_constraint_satisfaction": mean(by_kind.get("actor", [])) if by_kind.get("actor") else None,
            "ordering_compliance": mean(by_kind.get("ordering", [])) if by_kind.get("ordering") else None,
            "precondition_proxy": mean(by_kind.get("precondition", [])) if by_kind.get("precondition") else None,
            "verification_proxy": mean(by_kind.get("verification", [])) if by_kind.get("verification") else None,
            "requirements": requirement_rows,
        })

    def average(key: str):
        values = [row[key] for row in rows if isinstance(row.get(key), (int, float))]
        return mean(values) if values else None

    return {
        "summary": {
            "num_simulations": len(rows),
            "mean_skill_activations": average("skill_activations"),
            "mean_activation_context_chars": average("activation_context_chars"),
            "mean_activated_source_atom_count": average("activated_source_atom_count"),
            "activated_required_tool_recall_proxy": average("activated_required_tool_recall_proxy"),
            "business_tool_grounding_precision_proxy": average("business_tool_grounding_precision_proxy"),
            "observable_atom_execution_coverage": average("observable_atom_execution_coverage"),
            "actor_constraint_satisfaction": average("actor_constraint_satisfaction"),
            "ordering_compliance": average("ordering_compliance"),
            "precondition_proxy": average("precondition_proxy"),
            "verification_proxy": average("verification_proxy"),
        },
        "rows": rows,
        "limitations": [
            "Automatic scores cover only requirements observable as tool presence, order, and actor ownership.",
            "Semantic preconditions, correct module routing, policy validity, and provenance precision require a preregistered annotated task-module set.",
            "Required-tool recall and business-tool grounding are descriptive proxies, not Tool Binding Accuracy; valid support tools may lie outside the activated module.",
            "Soft train-derived motifs are reported separately and do not override official tau3 reward or policy.",
        ],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Evaluate observable Atom-to-Action execution metrics")
    parser.add_argument("results", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    output = evaluate(read_json(args.results))
    write_json(args.output or args.results.with_name("action_metrics.json"), output)
    print(json.dumps(output["summary"], ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
