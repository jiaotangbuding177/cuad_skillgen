from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from common import PROCESSED_ROOT, read_json, read_jsonl  # noqa: E402
from generate_skills import METHODS  # noqa: E402


class PipelineArtifactsTest(unittest.TestCase):
    def test_frozen_source_manifest(self):
        manifest = read_json(ROOT / "data" / "raw" / "source_manifest.json")
        self.assertEqual(manifest["checked_out_commit"], "59a200c6d575d595120f1cb70fea53cef0632f6b")
        self.assertEqual(manifest["license"], "MIT")

    def test_normalized_split_counts(self):
        retail = read_json(PROCESSED_ROOT / "retail" / "manifest.json")
        airline = read_json(PROCESSED_ROOT / "airline" / "manifest.json")
        self.assertEqual(retail["splits"], {"train": 500, "dev": 20, "test": 115})
        self.assertEqual(airline["splits"], {"test": 50})

    def test_compilation_leakage_boundary(self):
        for domain in ["retail", "airline"]:
            domain_manifest = read_json(PROCESSED_ROOT / domain / "manifest.json")
            self.assertNotIn("tasks/dev.jsonl", domain_manifest["compilation_sources"])
            self.assertNotIn("tasks/test.jsonl", domain_manifest["compilation_sources"])
            for method in METHODS:
                manifest = read_json(ROOT / "skills" / method / domain / "manifest.json")
                self.assertFalse(manifest["uses_dev_or_test_tasks"])
        self.assertTrue(read_json(PROCESSED_ROOT / "retail" / "manifest.json")["training_task_use_allowed"])
        self.assertFalse(read_json(PROCESSED_ROOT / "airline" / "manifest.json")["training_task_use_allowed"])

    def test_all_skill_packages_exist(self):
        for method in METHODS:
            for domain in ["retail", "airline"]:
                root = ROOT / "skills" / method / domain
                self.assertTrue((root / "SKILL.md").stat().st_size > 100)
                self.assertTrue((root / "evidence_index.json").exists())
                self.assertTrue((root / "security_policy.json").exists())
        graph_root = ROOT / "skills" / "graph_evoskill_compiler" / "retail"
        self.assertTrue((graph_root / "knowledge_graph.json").exists())
        self.assertTrue((graph_root / "pattern_cards.json").exists())

    def test_mock_has_real_task_and_governance_gates(self):
        mock = read_json(ROOT / "results" / "mock" / "graph_evoskill_compiler" / "retail-dev-0000.json")
        self.assertEqual(mock["task_id"], "retail-dev-0000")
        self.assertTrue(all(mock["policy_checks"].values()))
        self.assertEqual(mock["prediction"]["final_state"]["order"]["status"], "cancelled")
        self.assertEqual(mock["prediction"]["consequential_actions"], mock["gold"]["consequential_actions"])

    def test_mock_evaluation_is_marked_non_paper(self):
        summary = read_json(ROOT / "results" / "evaluation" / "mock_summary.json")
        self.assertIn("not paper results", summary["warning"])
        self.assertEqual(summary["records"], 1)
        self.assertEqual(summary["aggregate"]["governed_task_success"], 1.0)


if __name__ == "__main__":
    unittest.main()

