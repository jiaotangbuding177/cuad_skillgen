import json
import os
import sys
import tempfile
import unittest
from collections import Counter


ROOT = os.path.dirname(os.path.dirname(__file__))
sys.path.insert(0, os.path.join(ROOT, "scripts"))

from common.loader import CUADSkillGenLoader
from runtime.package_agent import (
    IncrementalPackageRunner,
    PackageAwareAgent,
    SkillPackage,
    build_contract_query,
    chunk_contract,
)
from runtime.package_evaluator import (
    GoldEvidenceMapper,
    compute_evidence_f1,
    compute_status_metrics,
    evaluate_case,
    evaluate_methods,
    load_latest_results,
)
from run_package_runtime import ensure_run_config
from evaluate_semantic_evidence import evidence_label
from baselines.document_tool_maker import (
    _append_checkpoint,
    _initialize_step1_checkpoint,
    _load_step1_checkpoint,
)


class FailingLLM:
    def call_json(self, *args, **kwargs):
        raise AssertionError("Boundary smoke tests must not call the LLM")


class QuoteLLM:
    def __init__(self, quote):
        self.quote = quote

    def call_json(self, *args, **kwargs):
        return ({
            "status": "answered",
            "answer": self.quote,
            "evidence": [{"chunk_id": "chunk-0001", "text": self.quote}],
            "source_contract_ids": [],
            "missing_inputs": [],
            "human_review_required": False,
        }, {"prompt_tokens": 1, "completion_tokens": 1, "total_tokens": 2})


class PackageRuntimeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data_root = os.path.join(ROOT, "data", "cuad_skillgen")
        cls.results_root = os.path.join(ROOT, "results", "skillgen", "generated")
        cls.loader = CUADSkillGenLoader(cls.data_root)

    def test_chunk_offsets_reconstruct_source(self):
        text = "alpha\n\n" + ("assignment clause. " * 800) + "omega"
        chunks = chunk_contract(text, target_chars=900, overlap_chars=100)
        self.assertGreater(len(chunks), 2)
        for chunk in chunks:
            self.assertEqual(text[chunk.span_start:chunk.span_end], chunk.text)

    def test_contract_query_variants_isolate_knowledge(self):
        task_only = build_contract_query(
            "Assignment", "Is assignment allowed?", ["GUIDANCE"],
            [{"text": "ATOM", "interpretation": "RULE"}],
            [{"name": "TOOL", "description": "SPEC"}],
            "task_only",
        )
        package_only = build_contract_query(
            "Assignment", "Is assignment allowed?", ["GUIDANCE"],
            [{"text": "ATOM", "interpretation": "RULE"}],
            [{"name": "TOOL", "description": "SPEC"}],
            "package_without_knowledge",
        )
        full = build_contract_query(
            "Assignment", "Is assignment allowed?", ["GUIDANCE"],
            [{"text": "ATOM", "interpretation": "RULE"}],
            [{"name": "TOOL", "description": "SPEC"}],
            "full",
        )
        self.assertNotIn("GUIDANCE", task_only)
        self.assertIn("GUIDANCE", package_only)
        self.assertNotIn("ATOM", package_only)
        self.assertIn("ATOM", full)

    def test_evoskill_package_reads_atoms_and_policy(self):
        case_id = "assignment_and_control"
        package = SkillPackage(
            self.results_root,
            "evoskill_compiler",
            case_id,
            self.loader.load_case_json(case_id),
        )
        items = package.knowledge_items("Change of Control")
        self.assertTrue(items)
        self.assertTrue(items[0]["id"].startswith("KA-"))
        self.assertTrue(package.policy_supports("legal_advice"))

    def test_boundary_router_uses_package_without_llm(self):
        case_id = "assignment_and_control"
        agent = PackageAwareAgent(
            self.loader,
            FailingLLM(),
            self.results_root,
            "evoskill_compiler",
        )
        task = next(
            task for task in self.loader.load_tasks(case_id)
            if task["gold_status"] == "missing_input" and not task.get("contract_id")
        )
        result = agent.process_task(task)
        self.assertEqual(result["status"], "missing_input")
        self.assertIn("contract_id", result["missing_inputs"])

    def test_gold_mapping_uses_contract_category_and_span(self):
        mapper = GoldEvidenceMapper(self.loader)
        unit = self.loader.load_evidence_units("assignment_and_control")[0]
        evidence = [{
            "span_start": unit["answer_start"],
            "span_end": unit["answer_end"],
            "text": unit["source_span"],
        }]
        matched, _ = mapper.map_evidence(
            unit["case_id"], unit["contract_id"], unit["category"], evidence
        )
        self.assertEqual(matched, {unit["evidence_unit_id"]})
        wrong_category, _ = mapper.map_evidence(
            unit["case_id"], unit["contract_id"], "Change of Control", evidence
        )
        self.assertNotIn(unit["evidence_unit_id"], wrong_category)

    def test_evidence_precision_penalizes_unmatched_predictions(self):
        metrics = compute_evidence_f1(
            predicted_count=2,
            matched_gold={"gold-1"},
            gold={"gold-1", "gold-2"},
            matched_count=1,
        )
        self.assertEqual(metrics["precision"], 0.5)
        self.assertEqual(metrics["recall"], 0.5)
        self.assertEqual(metrics["f1"], 0.5)

    def test_status_metrics_correct_class_imbalance(self):
        confusion = {
            "answered": {"answered": 1, "evidence_missing": 1},
            "evidence_missing": {"evidence_missing": 8},
            "missing_input": {"missing_input": 1},
            "unsupported_scope": {"answered": 1},
            "needs_human_review": {"needs_human_review": 1},
        }
        metrics = compute_status_metrics({
            gold: Counter(predictions)
            for gold, predictions in confusion.items()
        })
        self.assertEqual(metrics["status_balanced_accuracy"], 0.7)
        self.assertAlmostEqual(metrics["status_macro_f1"], 0.6882, places=4)
        self.assertEqual(metrics["status_per_class"]["answered"]["recall"], 0.5)

    def test_semantic_evidence_label_is_conservative(self):
        self.assertEqual(evidence_label({
            "faithfulness": 1.0, "semantic_correctness": 0.9
        }), "valid")
        self.assertEqual(evidence_label({
            "faithfulness": 0.9, "semantic_correctness": 0.5
        }), "partial")
        self.assertEqual(evidence_label({
            "faithfulness": 0.0, "semantic_correctness": 1.0
        }), "invalid")

    def test_gold_mapping_is_one_to_one(self):
        mapper = GoldEvidenceMapper(self.loader)
        unit = self.loader.load_evidence_units("assignment_and_control")[0]
        evidence = [{
            "span_start": unit["answer_start"],
            "span_end": unit["answer_end"],
            "text": unit["source_span"],
        }] * 2
        matched, details = mapper.map_evidence(
            unit["case_id"], unit["contract_id"], unit["category"], evidence
        )
        self.assertEqual(matched, {unit["evidence_unit_id"]})
        self.assertEqual(len(details), 1)

    def test_containment_mapping_accepts_prediction_covering_gold(self):
        mapper = GoldEvidenceMapper(self.loader)
        unit = self.loader.load_evidence_units("assignment_and_control")[0]
        evidence = [{
            "span_start": max(0, unit["answer_start"] - 1000),
            "span_end": unit["answer_end"] + 1000,
            "text": "unrelated wrapper text",
        }]
        strict, _ = mapper.map_evidence(
            unit["case_id"], unit["contract_id"], unit["category"], evidence
        )
        contained, details = mapper.map_evidence(
            unit["case_id"], unit["contract_id"], unit["category"], evidence,
            containment_aware=True,
        )
        self.assertEqual(strict, set())
        self.assertEqual(contained, {unit["evidence_unit_id"]})
        self.assertTrue(details[0]["gold_fully_contained"])

    def test_latest_append_record_wins(self):
        with tempfile.TemporaryDirectory() as directory:
            path = os.path.join(directory, "results.jsonl")
            records = [
                {"_task_id": "t1", "status": "error"},
                {"_task_id": "t1", "status": "answered"},
            ]
            with open(path, "w", encoding="utf-8") as f:
                for record in records:
                    f.write(json.dumps(record) + "\n")
            latest = load_latest_results(path)
            self.assertEqual(latest["t1"]["status"], "answered")

    def test_test_split_excludes_train_qa_but_keeps_governance(self):
        agent = PackageAwareAgent(
            self.loader,
            FailingLLM(),
            self.results_root,
            "evoskill_compiler",
        )
        runner = IncrementalPackageRunner(agent, self.loader)
        selected = runner.select_tasks(
            "assignment_and_control", "test", include_governance=True
        )
        test_ids = set(self.loader.get_test_contract_ids())
        train_ids = set(self.loader.get_train_contract_ids())
        qa_tasks = [
            task for task in selected
            if task.get("construction_source") != "newly_added_governance_task"
        ]
        self.assertTrue(qa_tasks)
        self.assertTrue(all(task["contract_id"] in test_ids for task in qa_tasks))
        self.assertFalse(any(task["contract_id"] in train_ids for task in qa_tasks))
        self.assertTrue(any(
            task.get("construction_source") == "newly_added_governance_task"
            for task in selected
        ))

    def test_evaluator_handles_missing_results(self):
        with tempfile.TemporaryDirectory() as directory:
            evaluations = evaluate_methods(
                self.loader,
                directory,
                ["evoskill_compiler"],
                ["assignment_and_control"],
                split="test",
            )
            self.assertEqual(evaluations[0]["total_tasks"], 0)
            self.assertEqual(evaluations[0]["result_coverage"], 0.0)
            self.assertFalse(evaluations[0]["complete"])
            self.assertEqual(evaluations[0]["evidence_f1"], 0.0)

    def test_boundary_metrics_split_no_answer_and_governance(self):
        with tempfile.TemporaryDirectory() as directory:
            path = os.path.join(directory, "results.jsonl")
            records = [
                {"_task_id": "t1", "_gold_status": "evidence_missing", "status": "evidence_missing"},
                {"_task_id": "t2", "_gold_status": "evidence_missing", "status": "answered"},
                {"_task_id": "t3", "_gold_status": "missing_input", "status": "missing_input"},
                {"_task_id": "t4", "_gold_status": "needs_human_review", "status": "answered"},
            ]
            with open(path, "w", encoding="utf-8") as f:
                for record in records:
                    f.write(json.dumps(record) + "\n")

            metrics = evaluate_case(path, GoldEvidenceMapper(self.loader), expected_tasks=4)

            self.assertEqual(metrics["no_answer_tasks"], 2)
            self.assertEqual(metrics["governance_boundary_tasks"], 2)
            self.assertEqual(metrics["boundary_tasks"], 4)
            self.assertEqual(metrics["no_answer_correct"], 0.5)
            self.assertEqual(metrics["governance_boundary_correct"], 0.5)
            self.assertEqual(metrics["boundary_correct"], 0.5)
            self.assertEqual(metrics["legacy_boundary_correct"], 0.5)
            self.assertIn("status_macro_f1", metrics)
            self.assertIn("status_balanced_accuracy", metrics)
            self.assertEqual(
                metrics["status_per_class"]["evidence_missing"]["support"], 2
            )

    def test_run_config_prevents_mixed_incremental_results(self):
        with tempfile.TemporaryDirectory() as directory:
            ensure_run_config(directory, {"model": "a", "top_k": 10})
            ensure_run_config(directory, {"model": "a", "top_k": 10})
            with self.assertRaises(RuntimeError):
                ensure_run_config(directory, {"model": "b", "top_k": 10})

    def test_document_tool_checkpoint_latest_record_wins(self):
        with tempfile.TemporaryDirectory() as directory:
            path = os.path.join(directory, "step1_checkpoint.jsonl")
            _initialize_step1_checkpoint(path, "case-a", "model-a")
            _append_checkpoint(path, {
                "contract_id": "contract-1",
                "status": "error",
                "tools": [],
            })
            _append_checkpoint(path, {
                "contract_id": "contract-1",
                "status": "ok",
                "tools": [{"name": "check_assignment"}],
            })
            latest = _load_step1_checkpoint(path, "case-a", "model-a")
            self.assertEqual(latest["contract-1"]["status"], "ok")
            self.assertEqual(len(latest["contract-1"]["tools"]), 1)

    def test_document_tool_checkpoint_rejects_model_mixing(self):
        with tempfile.TemporaryDirectory() as directory:
            path = os.path.join(directory, "step1_checkpoint.jsonl")
            _initialize_step1_checkpoint(path, "case-a", "model-a")
            with self.assertRaises(RuntimeError):
                _load_step1_checkpoint(path, "case-a", "model-b")

    def test_agent_verifies_target_quote_end_to_end(self):
        unit = next(
            unit for unit in self.loader.load_evidence_units("assignment_and_control")
            if unit["contract_id"] in set(self.loader.get_train_contract_ids())
        )
        task = next(
            task for task in self.loader.load_tasks("assignment_and_control")
            if unit["evidence_unit_id"] in task.get("gold_evidence_unit_ids", [])
        )
        agent = PackageAwareAgent(
            self.loader,
            QuoteLLM(unit["source_span"]),
            self.results_root,
            "evoskill_compiler",
            top_k_chunks=100,
        )
        result = agent.process_task(task)
        self.assertEqual(result["status"], "answered")
        self.assertEqual(result["source_contract_ids"], [task["contract_id"]])
        self.assertEqual(result["evidence"][0]["span_start"], unit["answer_start"])


if __name__ == "__main__":
    unittest.main()
