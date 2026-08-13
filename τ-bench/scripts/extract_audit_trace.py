from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

from common import read_json, write_json, write_jsonl


DOC_ID = re.compile(r"\b(?:ID:\s*)?(doc_[a-zA-Z0-9_\-]+)\b")


def iter_tool_calls(message: dict):
    for call in message.get("tool_calls") or []:
        yield call


def extract(results: dict) -> tuple[list[dict], dict]:
    events: list[dict] = []
    per_sim = []
    for sim in results.get("simulations", []):
        calls = 0
        ownership_correct = 0
        errors = 0
        retrieved_docs: list[str] = []
        package_retrievals = 0
        package_context_chars = 0
        package_item_ids: list[str] = []
        skill_activations = 0
        activated_module_ids: list[str] = []
        activation_context_chars = 0
        activated_source_atom_ids: list[str] = []
        activated_required_tools: list[str] = []
        activated_trace_requirements: list[dict] = []
        for message_index, message in enumerate(sim.get("messages") or []):
            role = message.get("role")
            package_data = (message.get("raw_data") or {}).get("skillgen_package_retrieval")
            if package_data:
                package_retrievals += 1
                package_context_chars += int(package_data.get("context_chars") or 0)
                item_ids = [item.get("item_id") for item in package_data.get("items") or [] if item.get("item_id")]
                package_item_ids.extend(item_ids)
                events.append({
                    "simulation_id": sim.get("id"), "task_id": sim.get("task_id"),
                    "event": "package_retrieval", "message_index": message_index,
                    "query": package_data.get("query"), "items": package_data.get("items") or [],
                    "context_chars": package_data.get("context_chars"),
                    "budget_chars": package_data.get("budget_chars"),
                    "package_hash": package_data.get("package_hash"),
                })
            activation_data = (message.get("raw_data") or {}).get("skillgen_activation")
            if activation_data:
                for activation in activation_data.get("events") or []:
                    if activation.get("status") == "activated":
                        skill_activations += 1
                        activated_module_ids.append(activation.get("module_id"))
                        activation_context_chars += int(activation.get("context_chars") or 0)
                        activated_source_atom_ids.extend(activation.get("source_atom_ids") or [])
                        activated_required_tools.extend(activation.get("required_tools") or [])
                        activated_trace_requirements.extend(activation.get("trace_requirements") or [])
                    events.append({
                        "simulation_id": sim.get("id"), "task_id": sim.get("task_id"),
                        "event": "skill_activation", "message_index": message_index,
                        **activation,
                    })
            for call in iter_tool_calls(message):
                calls += 1
                requestor = call.get("requestor", role)
                correct = requestor == role
                ownership_correct += int(correct)
                events.append({
                    "simulation_id": sim.get("id"), "task_id": sim.get("task_id"),
                    "event": "tool_call", "message_index": message_index,
                    "actor": role, "declared_requestor": requestor,
                    "tool": call.get("name"), "arguments": call.get("arguments") or {},
                    "actor_ownership_correct": correct,
                })
            if role == "tool":
                errors += int(bool(message.get("error")))
                docs = DOC_ID.findall(message.get("content") or "")
                retrieved_docs.extend(docs)
                events.append({
                    "simulation_id": sim.get("id"), "task_id": sim.get("task_id"),
                    "event": "tool_result", "message_index": message_index,
                    "actor": message.get("requestor"), "error": bool(message.get("error")),
                    "retrieved_document_ids": docs,
                })
        per_sim.append({
            "simulation_id": sim.get("id"), "task_id": sim.get("task_id"),
            "tool_calls": calls, "tool_errors": errors,
            "actor_ownership_accuracy": ownership_correct / calls if calls else None,
            "illegal_cross_actor_tool_calls": calls - ownership_correct,
            "retrieved_document_ids": list(dict.fromkeys(retrieved_docs)),
            "package_retrievals": package_retrievals,
            "package_context_chars": package_context_chars,
            "package_item_ids": list(dict.fromkeys(package_item_ids)),
            "skill_activations": skill_activations,
            "activated_module_ids": list(dict.fromkeys(module for module in activated_module_ids if module)),
            "activation_context_chars": activation_context_chars,
            "activated_source_atom_ids": list(dict.fromkeys(activated_source_atom_ids)),
            "activated_required_tools": list(dict.fromkeys(activated_required_tools)),
            "activated_trace_requirements": activated_trace_requirements,
        })
    valid_ownership = [x["actor_ownership_accuracy"] for x in per_sim if x["actor_ownership_accuracy"] is not None]
    summary = {
        "num_simulations": len(per_sim),
        "tool_calls": sum(x["tool_calls"] for x in per_sim),
        "tool_errors": sum(x["tool_errors"] for x in per_sim),
        "illegal_cross_actor_tool_calls": sum(x["illegal_cross_actor_tool_calls"] for x in per_sim),
        "actor_ownership_accuracy": sum(valid_ownership) / len(valid_ownership) if valid_ownership else None,
        "package_retrievals": sum(x["package_retrievals"] for x in per_sim),
        "package_context_chars": sum(x["package_context_chars"] for x in per_sim),
        "skill_activations": sum(x["skill_activations"] for x in per_sim),
        "activation_context_chars": sum(x["activation_context_chars"] for x in per_sim),
        "per_simulation": per_sim,
    }
    return events, summary


def main() -> None:
    parser = argparse.ArgumentParser(description="Extract auditable tool and retrieval events")
    parser.add_argument("results", type=Path)
    parser.add_argument("--events", type=Path)
    parser.add_argument("--summary", type=Path)
    args = parser.parse_args()
    events, summary = extract(read_json(args.results))
    write_jsonl(args.events or args.results.with_name("audit_trace.jsonl"), events)
    write_json(args.summary or args.results.with_name("audit_metrics.json"), summary)
    print(json.dumps({k: v for k, v in summary.items() if k != "per_simulation"}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
