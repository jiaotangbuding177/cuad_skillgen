from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "vendor" / "tau3-bench" / "src"))

from evaluate_results import summarize  # noqa: E402
from extract_audit_trace import extract  # noqa: E402
from compare_methods import paired_rows, bootstrap, mcnemar  # noqa: E402
from evaluate_action_metrics import evaluate as evaluate_action_metrics  # noqa: E402
from evaluate_annotations import routing as evaluate_routing  # noqa: E402
from evaluate_agreement import evaluate as evaluate_agreement  # noqa: E402
from runtime.package_runtime import (  # noqa: E402
    ProgressiveConfig, ProgressiveSkillPackage, RetrievalConfig, SkillPackage, build_query,
)
from runtime.package_agent import ProgressiveSkillAgent, ProgressiveSkillAgentState  # noqa: E402
from tau2.data_model.message import AssistantMessage, ToolCall, UserMessage  # noqa: E402


class PipelineTests(unittest.TestCase):
    def test_domain_counts_and_tool_catalogs(self):
        expected = {
            "retail": (114, 16),
            "airline": (50, 14),
            "telecom": (2285, 43),
            "banking_knowledge": (97, 21),
        }
        for domain, (tasks, tools) in expected.items():
            manifest = json.loads((ROOT / "data" / "processed" / domain / "manifest.json").read_text(encoding="utf-8"))
            all_rows = (ROOT / "data" / "processed" / domain / "tasks" / "all.jsonl").read_text(encoding="utf-8").splitlines()
            self.assertEqual(tasks, len(all_rows))
            self.assertEqual(tools, manifest["tools"])

    def test_heldout_tasks_not_compilation_sources(self):
        for domain in ("retail", "airline", "telecom", "banking_knowledge"):
            manifest = json.loads((ROOT / "data" / "processed" / domain / "manifest.json").read_text(encoding="utf-8"))
            self.assertNotIn("tasks/test.jsonl", manifest["compilation_sources"])
            self.assertNotIn("tasks/base.jsonl", manifest["compilation_sources"])

    def test_all_skill_packages_exist_and_are_leakage_marked(self):
        config = json.loads((ROOT / "config" / "experiment.json").read_text(encoding="utf-8"))
        methods = config["methods"] + config.get("ablation_methods", [])
        for method in methods:
            for domain in ("retail", "airline", "telecom", "banking_knowledge"):
                package = ROOT / "skills" / method / domain
                self.assertTrue((package / "SKILL.md").exists())
                self.assertTrue((package / "action_modules.json").exists())
                self.assertTrue((package / "typed_atoms.json").exists())
                manifest = json.loads((package / "manifest.json").read_text(encoding="utf-8"))
                self.assertFalse(manifest["uses_held_out_tasks"])
                self.assertTrue(manifest.get("compiler_code_hash"))

    def test_metric_summary(self):
        summary = summarize({"simulations": [
            {"task_id": "a", "trial": 0, "reward_info": {"reward": 1.0, "reward_breakdown": {"DB": 1.0}}, "duration": 2.0},
            {"task_id": "a", "trial": 1, "reward_info": {"reward": 0.0, "reward_breakdown": {"DB": 0.0}}, "duration": 4.0},
        ]})
        self.assertEqual(summary["mean_reward"], 0.5)
        self.assertEqual(summary["pass_at_k"], 1.0)
        self.assertEqual(summary["pass_power_k"], 0.0)

    def test_audit_trace_actor_ownership_and_retrieval(self):
        payload = {"simulations": [{
            "id": "sim-1", "task_id": "task_001", "messages": [
                {"role": "assistant", "tool_calls": [{"name": "KB_search", "arguments": {"query": "card"}, "requestor": "assistant"}]},
                {"role": "tool", "requestor": "assistant", "error": False, "content": "ID: doc_credit_cards_gold_rewards_card_001"},
                {"role": "assistant", "tool_calls": [{"name": "toggle_roaming", "arguments": {}, "requestor": "user"}]},
            ]
        }]}
        _, summary = extract(payload)
        self.assertEqual(summary["tool_calls"], 2)
        self.assertEqual(summary["actor_ownership_accuracy"], 0.5)
        self.assertEqual(summary["illegal_cross_actor_tool_calls"], 1)
        self.assertEqual(summary["per_simulation"][0]["retrieved_document_ids"], ["doc_credit_cards_gold_rewards_card_001"])

    def test_paired_statistics(self):
        left = {"rows": [{"task_id": "a", "trial": 0, "reward": 0}, {"task_id": "b", "trial": 0, "reward": 1}]}
        right = {"rows": [{"task_id": "a", "trial": 0, "reward": 1}, {"task_id": "b", "trial": 0, "reward": 1}]}
        pairs = paired_rows(left, right)
        self.assertEqual(len(pairs), 2)
        self.assertEqual(bootstrap(pairs, seed=1, n=100)["mean_difference"], 0.5)
        self.assertEqual(mcnemar(pairs)["discordant_right_only"], 1)

    def test_package_runtime_supports_every_baseline(self):
        config_json = json.loads((ROOT / "config" / "experiment.json").read_text(encoding="utf-8"))
        methods = config_json["methods"] + config_json.get("ablation_methods", [])
        config = RetrievalConfig(max_context_chars=2500, max_item_chars=600)
        for method in methods:
            for domain in ("retail", "airline", "telecom", "banking_knowledge"):
                package = SkillPackage(ROOT / "skills" / method / domain, domain, config)
                result = package.retrieve("customer policy tools workflow payment data reservation order")
                self.assertLessEqual(result["context_chars"], 2500)
                if method == "no_skill":
                    self.assertFalse(result["items"])
                else:
                    self.assertTrue(result["items"], f"{method}/{domain}")
                self.assertFalse(package.describe()["graph_traversal_enabled"])

    def test_banking_package_excludes_target_knowledge_documents(self):
        package = SkillPackage(ROOT / "skills" / "evoskill_compiler" / "banking_knowledge", "banking_knowledge", RetrievalConfig())
        self.assertTrue(package.describe()["banking_knowledge_documents_excluded"])
        self.assertFalse(any(item.metadata.get("kind") == "knowledge_document" for item in package.items))
        self.assertEqual(package.describe()["lane_counts"]["atom"], 23)

    def test_gesc_graph_file_is_not_an_active_v1_runtime_input(self):
        package = SkillPackage(ROOT / "skills" / "graph_evoskill_compiler" / "telecom", "telecom", RetrievalConfig())
        self.assertIn("pattern_cards.json", package.describe()["active_files"])
        self.assertIn("knowledge_graph.json", package.describe()["ignored_files"])

    def test_package_retrieval_is_deterministic(self):
        package = SkillPackage(ROOT / "skills" / "evoskill_compiler" / "telecom", "telecom", RetrievalConfig())
        first = package.retrieve("roaming mobile data")
        second = package.retrieve("roaming mobile data")
        self.assertEqual(first, second)
        query = build_query({"role": "user", "content": "mobile data fails"}, [{"role": "assistant", "content": "Are you abroad?"}], 6)
        self.assertIn("mobile data fails", query)

    def test_synthetic_result_contains_package_retrieval_trace(self):
        payload = json.loads((ROOT / "tests" / "fixtures" / "synthetic_results.json").read_text(encoding="utf-8"))
        events, summary = extract(payload)
        self.assertEqual(summary["package_retrievals"], 1)
        self.assertEqual(summary["package_context_chars"], 300)
        self.assertTrue(any(event["event"] == "package_retrieval" for event in events))

    def test_a2sc_mock_is_derived_from_current_package(self):
        mock = json.loads((ROOT / "results" / "mock" / "telecom_dual_control_case.json").read_text(encoding="utf-8"))
        manifest = json.loads((ROOT / "skills" / "a2sc" / "telecom" / "manifest.json").read_text(encoding="utf-8"))
        modules = {
            module["module_id"]: module for module in json.loads((
                ROOT / "skills" / "a2sc" / "telecom" / "action_modules.json"
            ).read_text(encoding="utf-8"))["modules"]
        }
        self.assertEqual(mock["compiler_input"]["compiler_code_hash"], manifest["compiler_code_hash"])
        for snapshot in mock["compiler_output"]["activated_modules"]:
            self.assertEqual(snapshot["source_atom_ids"], modules[snapshot["module_id"]]["source_atom_ids"])
        self.assertFalse(mock["compiler_input"]["uses_held_out_tasks"])

    def test_progressive_runtime_supports_every_method(self):
        config_json = json.loads((ROOT / "config" / "experiment.json").read_text(encoding="utf-8"))
        methods = config_json["methods"] + config_json.get("ablation_methods", [])
        config = ProgressiveConfig(max_catalog_chars=12000, max_module_chars=9000, max_active_modules=2)
        for method in methods:
            for domain in ("retail", "airline", "telecom", "banking_knowledge"):
                package = ProgressiveSkillPackage(ROOT / "skills" / method / domain, domain, config)
                self.assertLessEqual(len(package.catalog()), 12000)
                self.assertFalse(package.describe()["graph_traversal_enabled"])
                if method == "no_skill":
                    self.assertEqual(package.describe()["module_count"], 0)
                else:
                    self.assertGreater(package.describe()["module_count"], 0)

    def test_a2sc_uses_typed_atoms_and_valid_tools(self):
        allowed_types = {
            "fact", "precondition", "required_input", "permission", "prohibition",
            "confirmation", "actor_constraint", "postcondition", "exception", "escalation",
            "communication_requirement",
        }
        for domain in ("retail", "airline", "telecom", "banking_knowledge"):
            root = ROOT / "skills" / "a2sc" / domain
            atoms = json.loads((root / "typed_atoms.json").read_text(encoding="utf-8"))["atoms"]
            modules = json.loads((root / "action_modules.json").read_text(encoding="utf-8"))["modules"]
            tools = json.loads((ROOT / "data" / "processed" / domain / "documents" / "tool_catalog.json").read_text(encoding="utf-8"))["tools"]
            valid_tools = {tool["name"] for tool in tools}
            self.assertTrue(atoms)
            self.assertTrue(set(atom["type"] for atom in atoms) <= allowed_types)
            self.assertTrue(any(atom["type"] == "actor_constraint" for atom in atoms))
            self.assertTrue(modules)
            for module in modules:
                self.assertTrue(set(module["required_tools"]) <= valid_tools)

    def test_g_a2sc_is_aligned_and_graph_is_compile_time_only(self):
        for domain in ("retail", "airline", "telecom", "banking_knowledge"):
            flat_root = ROOT / "skills" / "a2sc" / domain
            graph_root = ROOT / "skills" / "g_a2sc" / domain
            flat = {m["module_id"]: m for m in json.loads((flat_root / "action_modules.json").read_text(encoding="utf-8"))["modules"]}
            graph = {m["module_id"]: m for m in json.loads((graph_root / "action_modules.json").read_text(encoding="utf-8"))["modules"]}
            self.assertEqual(set(flat), set(graph))
            self.assertTrue((graph_root / "knowledge_graph.json").exists())
            for module_id in flat:
                self.assertEqual(flat[module_id].get("primary_tool"), graph[module_id].get("primary_tool"))
                self.assertEqual(flat[module_id].get("required_tools"), graph[module_id].get("required_tools"))
            package = ProgressiveSkillPackage(graph_root, domain)
            self.assertIn("knowledge_graph.json", package.describe()["ignored_compile_time_files"])
            flat_atom_ids = {
                atom["atom_id"] for atom in json.loads(
                    (flat_root / "typed_atoms.json").read_text(encoding="utf-8")
                )["atoms"]
            }
            graph_atoms = {
                atom["atom_id"]: atom for atom in json.loads(
                    (graph_root / "typed_atoms.json").read_text(encoding="utf-8")
                )["atoms"]
            }
            expanded = {
                atom_id for module_id in flat
                for atom_id in set(graph[module_id].get("source_atom_ids") or [])
                - set(flat[module_id].get("source_atom_ids") or [])
            }
            self.assertTrue(expanded <= flat_atom_ids)
            self.assertTrue(all(graph_atoms[atom_id]["origin"] == "policy" for atom_id in expanded))

    def test_a2sc_ablations_remove_only_declared_mechanism(self):
        for domain in ("retail", "airline", "telecom", "banking_knowledge"):
            no_typed = json.loads((
                ROOT / "skills" / "a2sc_no_typed_atoms" / domain / "action_modules.json"
            ).read_text(encoding="utf-8"))["modules"]
            self.assertTrue(all(not module.get("source_atom_ids") for module in no_typed))
            no_binding = json.loads((
                ROOT / "skills" / "a2sc_no_tool_binding" / domain / "action_modules.json"
            ).read_text(encoding="utf-8"))["modules"]
            self.assertTrue(all(not module.get("required_tools") and not module.get("primary_tool") for module in no_binding))
            no_motifs = json.loads((
                ROOT / "skills" / "a2sc_no_local_motifs" / domain / "action_modules.json"
            ).read_text(encoding="utf-8"))["modules"]
            self.assertTrue(all(
                requirement.get("kind") not in {"ordering", "precondition", "verification"}
                for module in no_motifs for requirement in module.get("trace_requirements") or []
            ))

    def test_activation_trace_and_observable_action_metrics(self):
        payload = {"simulations": [{
            "id": "sim-a2sc", "task_id": "task-a2sc", "trial": 0,
            "messages": [
                {"role": "assistant", "tool_calls": [{"name": "check_status", "arguments": {}, "requestor": "assistant"}]},
                {"role": "tool", "requestor": "assistant", "error": False, "content": "ok"},
                {"role": "assistant", "tool_calls": [{"name": "modify_state", "arguments": {}, "requestor": "assistant"}], "raw_data": {
                    "skillgen_activation": {"events": [{
                        "module_id": "x.modify", "status": "activated", "context_chars": 100,
                        "source_atom_ids": ["A1", "A2"], "trace_requirements": [
                            {"requirement_id": "R1", "kind": "precondition", "evidence_tool": "check_status", "action_tool": "modify_state"},
                            {"requirement_id": "R2", "kind": "actor", "tool": "modify_state", "actor": "assistant"},
                        ],
                    }]}
                }},
            ],
        }]}
        events, summary = extract(payload)
        self.assertEqual(summary["skill_activations"], 1)
        self.assertTrue(any(event["event"] == "skill_activation" for event in events))
        action = evaluate_action_metrics(payload)
        self.assertEqual(action["summary"]["precondition_proxy"], 1.0)
        self.assertEqual(action["summary"]["actor_constraint_satisfaction"], 1.0)

    def test_progressive_agent_hard_loads_module_and_keeps_state_local(self):
        package = ProgressiveSkillPackage(ROOT / "skills" / "a2sc" / "retail", "retail")
        agent = ProgressiveSkillAgent(
            tools=[], fixed_adapter="fixed", retrieval_adapter="", package=package,
            llm="mock-model", llm_args={"temperature": 0.0},
        )
        state = agent.get_init_state()
        self.assertIsInstance(state, ProgressiveSkillAgentState)
        activation = AssistantMessage.text(
            "", tool_calls=[ToolCall(
                id="activate-1", name="activate_skill",
                arguments={"module_id": "retail.cancel_pending_order"},
            )], cost=0.1, usage={"prompt_tokens": 10},
        )
        final = AssistantMessage.text(
            "I can help with that cancellation.", cost=0.2,
            usage={"prompt_tokens": 20, "completion_tokens": 5},
        )
        with patch("runtime.package_agent.generate", side_effect=[activation, final]):
            response, new_state = agent.generate_next_message(UserMessage.text("Cancel my order"), state)
        self.assertEqual(response.content, "I can help with that cancellation.")
        self.assertAlmostEqual(response.cost, 0.3)
        self.assertEqual(response.usage["prompt_tokens"], 30)
        self.assertIn("retail.cancel_pending_order", new_state.active_modules)
        event = response.raw_data["skillgen_activation"]["events"][0]
        self.assertEqual(event["status"], "activated")
        self.assertIn("cancel_pending_order", event["required_tools"])
        self.assertIn("# Cancel Pending Order", new_state.system_messages[0].content)
        fresh_state = agent.get_init_state()
        self.assertFalse(fresh_state.active_modules)

    def test_annotated_routing_and_agreement_metrics(self):
        rows = [{
            "simulation_id": "s1", "task_id": "t1", "trial": 0,
            "annotator_id": "a", "gold_requires_skill": True,
            "gold_applicable_module_ids": ["retail.cancel_pending_order"],
            "pred_activated_module_ids": ["retail.cancel_pending_order"],
            "tool_binding_correct": True, "policy_compliant": True,
        }, {
            "simulation_id": "s1", "task_id": "t1", "trial": 0,
            "annotator_id": "b", "gold_requires_skill": True,
            "gold_applicable_module_ids": ["retail.cancel_pending_order"],
            "pred_activated_module_ids": ["retail.cancel_pending_order"],
            "tool_binding_correct": True, "policy_compliant": True,
        }]
        route = evaluate_routing(rows[:1])
        self.assertEqual(route["trigger_recall"], 1.0)
        self.assertEqual(route["route_at_1"], 1.0)
        agreement = evaluate_agreement(rows)
        self.assertEqual(agreement["annotation_pairs"], 1)
        self.assertEqual(agreement["categorical"]["policy_compliant"]["cohen_kappa"], 1.0)


if __name__ == "__main__":
    unittest.main()
