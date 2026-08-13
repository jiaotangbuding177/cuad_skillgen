from __future__ import annotations

from common import PROCESSED_ROOT, ROOT, read_json, read_jsonl, write_json


def main() -> None:
    task = read_jsonl(PROCESSED_ROOT / "telecom" / "tasks" / "test.jsonl")[0]
    package_root = ROOT / "skills" / "a2sc" / "telecom"
    package_manifest = read_json(package_root / "manifest.json")
    modules = {
        module["module_id"]: module
        for module in read_json(package_root / "action_modules.json")["modules"]
    }
    selected_ids = ["telecom.toggle_data_saver_mode", "telecom.toggle_roaming"]
    selected = [modules[module_id] for module_id in selected_ids]
    source_atom_ids = list(dict.fromkeys(
        atom_id for module in selected for atom_id in module["source_atom_ids"]
    ))
    mock = {
        "case_type": "illustrative_mock_not_a_benchmark_result",
        "method": "a2sc",
        "runtime_mode": "hard_progressive_advisory",
        "compiler_input": {
            "domain_manifest": "data/processed/telecom/manifest.json",
            "compilation_sources": read_json(PROCESSED_ROOT / "telecom" / "manifest.json")["compilation_sources"],
            "uses_held_out_tasks": False,
            "compiler_code_hash": package_manifest["compiler_code_hash"],
        },
        "compiler_output": {
            "package_contract": package_manifest["package_contract"],
            "activated_modules": [{
                "module_id": module["module_id"],
                "actor": module["actor"],
                "required_tools": module["required_tools"],
                "source_atom_ids": module["source_atom_ids"],
                "trace_requirements": module["trace_requirements"],
                "instructions_chars": len(module["instructions"]),
            } for module in selected],
        },
        "task_input": {
            "task_id": task["task_id"],
            "user_instruction": task["user_instruction"],
            "initial_state": task["initial_state"],
            "available_actor_tools": {
                "assistant": ["get_customer_by_phone", "get_data_usage", "enable_roaming"],
                "user": ["check_data_restriction_status", "toggle_data_saver_mode", "toggle_roaming", "run_speed_test"],
            },
        },
        "runtime_operations": [
            {"status": "activate", "actor": "assistant", "tool": "activate_skill", "module_id": selected_ids[0]},
            {"status": "observe", "actor": "assistant", "tool": "get_customer_by_phone", "arguments": {"phone_number": "555-123-2002"}, "provenance": ["policy", "tool_contract"]},
            {"status": "observe", "actor": "user", "tool": "check_data_restriction_status", "arguments": {}},
            {"status": "instruct_user", "actor": "assistant", "operation": "ask user to disable data saver", "next_tool_owner": "user"},
            {"status": "execute", "actor": "user", "tool": "toggle_data_saver_mode", "arguments": {}},
            {"status": "activate", "actor": "assistant", "tool": "activate_skill", "module_id": selected_ids[1]},
            {"status": "instruct_user", "actor": "assistant", "operation": "ask user to enable device roaming", "next_tool_owner": "user"},
            {"status": "execute", "actor": "user", "tool": "toggle_roaming", "arguments": {}},
            {"status": "verify", "actor": "user", "tool": "run_speed_test", "expected": "excellent"},
            {"status": "complete", "actor": "assistant", "operation": "report verified resolution"},
        ],
        "expected_output": {
            "environment_assertions": {"mobile_data_status": True, "internet_speed": "excellent"},
            "actor_ownership_accuracy": 1.0,
            "illegal_cross_actor_tool_calls": 0,
            "native_reward_target": 1.0,
            "skill_activations": 2,
            "activated_module_ids": selected_ids,
            "activation_context_chars": sum(len(module["instructions"]) for module in selected),
            "activated_source_atom_count": len(source_atom_ids),
            "activated_required_tool_recall_proxy": 1.0,
            "business_tool_grounding_precision_proxy": 0.4,
            "annotated_route_at_1": 1.0,
        },
        "metric_note": "The two proxy metrics are descriptive only. Formal Route@1 and Tool Binding Accuracy require the preregistered task-module annotation set.",
        "gold_usage_boundary": "Gold actions/assertions are included only here as an offline expected-output oracle; they are never supplied to the runtime agent or Skill compiler.",
    }
    write_json(ROOT / "results" / "mock" / "telecom_dual_control_case.json", mock)


if __name__ == "__main__":
    main()
