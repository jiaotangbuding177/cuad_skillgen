from __future__ import annotations

import argparse
import copy
import hashlib
import json
from pathlib import Path
from typing import Any

from common import PROCESSED_ROOT, ROOT, read_json, read_jsonl, write_json


MOCK_TASK_ID = "retail-dev-0000"


def canonical(value: Any) -> Any:
    if isinstance(value, dict):
        return {key: canonical(value[key]) for key in sorted(value)}
    if isinstance(value, list):
        return [canonical(item) for item in value]
    return value


def cancel_order(data: dict[str, Any], order_id: str, reason: str) -> dict[str, Any]:
    order = data["orders"][order_id]
    if order["status"] != "pending":
        raise ValueError("non-pending order cannot be cancelled")
    if reason not in {"no longer needed", "ordered by mistake"}:
        raise ValueError("invalid cancellation reason")
    refunds = []
    for payment in order["payment_history"]:
        payment_id = payment["payment_method_id"]
        refunds.append(
            {
                "transaction_type": "refund",
                "amount": payment["amount"],
                "payment_method_id": payment_id,
            }
        )
        if "gift_card" in payment_id:
            method = data["users"][order["user_id"]]["payment_methods"][payment_id]
            method["balance"] = round(method["balance"] + payment["amount"], 2)
    order["status"] = "cancelled"
    order["cancel_reason"] = reason
    order["payment_history"].extend(refunds)
    return copy.deepcopy(order)


def main() -> None:
    parser = argparse.ArgumentParser(description="Run a deterministic full-chain tau-bench mock")
    parser.add_argument("--method", default="graph_evoskill_compiler")
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()

    task = next(
        row for row in read_jsonl(PROCESSED_ROOT / "retail" / "tasks" / "dev.jsonl")
        if row["task_id"] == MOCK_TASK_ID
    )
    skill_root = ROOT / "skills" / args.method / "retail"
    if not (skill_root / "manifest.json").exists():
        raise SystemExit(f"Generate {args.method}/retail first")
    skill_manifest = read_json(skill_root / "manifest.json")

    upstream_data = ROOT / "vendor" / "tau-bench" / "tau_bench" / "envs" / "retail" / "data"
    users = read_json(upstream_data / "users.json")
    orders = read_json(upstream_data / "orders.json")
    data = {"users": copy.deepcopy(users), "orders": copy.deepcopy(orders)}
    gold_action = task["gold"]["actions"][0]
    order_id = gold_action["arguments"]["order_id"]
    user_id = task["user_id"]
    initial_order = copy.deepcopy(data["orders"][order_id])
    input_hash = hashlib.sha256(
        json.dumps(
            {"task": task, "initial_order": initial_order, "skill_input_hash": skill_manifest["input_hash"]},
            sort_keys=True,
        ).encode()
    ).hexdigest()
    result_path = ROOT / "results" / "mock" / args.method / "retail-dev-0000.json"
    if result_path.exists() and not args.force:
        existing = read_json(result_path)
        if existing.get("input_hash") == input_hash:
            print(f"Mock result unchanged: {result_path}")
            return

    trace = [
        {
            "turn": 1,
            "actor": "user",
            "content": task["user_instruction"],
        },
        {
            "turn": 2,
            "actor": "agent",
            "decision_status": "clarify",
            "operation": "identity_check",
            "tool_call": {
                "name": "find_user_id_by_name_zip",
                "arguments": {"first_name": "Olivia", "last_name": "Ito", "zip": "80218"},
            },
            "observation": {"user_id": user_id},
            "policy_evidence_ids": ["POL-002", "POL-003"],
        },
        {
            "turn": 3,
            "actor": "agent",
            "decision_status": "clarify",
            "operation": "state_retrieval",
            "tool_call": {"name": "get_order_details", "arguments": {"order_id": order_id}},
            "observation": {"order_id": order_id, "status": initial_order["status"]},
        },
        {
            "turn": 4,
            "actor": "agent",
            "decision_status": "clarify",
            "operation": "authorization_gate",
            "content": f"Please confirm cancellation of {order_id} for 'no longer needed' and its refund.",
            "policy_evidence_ids": ["POL-004"],
        },
        {"turn": 5, "actor": "user", "content": "Yes, cancel it."},
    ]
    final_order = cancel_order(data, order_id, gold_action["arguments"]["reason"])
    trace.append(
        {
            "turn": 6,
            "actor": "agent",
            "decision_status": "execute",
            "operation": "consequential_tool_execution",
            "tool_call": gold_action,
            "observation": {
                "order_id": order_id,
                "status": final_order["status"],
                "cancel_reason": final_order["cancel_reason"],
            },
            "policy_evidence_ids": ["POL-004"],
        }
    )
    trace.append(
        {
            "turn": 7,
            "actor": "agent",
            "decision_status": "completed",
            "operation": "final_state_verification",
            "content": f"Order {order_id} is cancelled; non-gift-card refund timing follows policy.",
        }
    )

    expected_data = {"users": copy.deepcopy(users), "orders": copy.deepcopy(orders)}
    expected_order = cancel_order(expected_data, order_id, gold_action["arguments"]["reason"])
    result = {
        "record_type": "tau_skillbench_run",
        "input_hash": input_hash,
        "method": args.method,
        "compiler_backend": skill_manifest["compiler_backend"],
        "domain": "retail",
        "split": "dev",
        "task_id": task["task_id"],
        "input": {
            "sop_document": "data/processed/retail/documents/policy.md",
            "skill_package": f"skills/{args.method}/retail",
            "user_instruction": task["user_instruction"],
            "initial_state": {
                "user_id": user_id,
                "order": initial_order,
            },
            "available_tools": [
                "find_user_id_by_name_zip", "get_order_details", "cancel_pending_order"
            ],
        },
        "gold": {
            "decision_status": "execute",
            "consequential_actions": task["gold"]["actions"],
            "outputs": task["gold"]["outputs"],
            "expected_final_state": {"order": expected_order},
        },
        "prediction": {
            "decision_status": "execute",
            "consequential_actions": [gold_action],
            "final_state": {"order": final_order},
            "policy_evidence_ids": ["POL-002", "POL-003", "POL-004"],
        },
        "policy_checks": {
            "identity_verified_before_task": True,
            "no_task_when_identity_missing": True,
            "explicit_authorization_before_mutation": True,
            "one_tool_call_per_turn": True,
            "no_fabricated_external_information": True,
            "no_unnecessary_human_transfer": True,
        },
        "trace": trace,
        "mock_only_not_paper_result": True,
    }
    write_json(result_path, result)
    print(f"Wrote mock run: {result_path}")


if __name__ == "__main__":
    main()

