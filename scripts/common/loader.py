"""
Common data loader for CUAD-SkillGen baselines.

Provides unified access to:
- case.json (capability case definitions)
- category_descriptions.jsonl (41 CUAD categories)
- contract_metadata.jsonl (510 contracts)
- splits.json (train/dev/test contract splits)
- Contract full text (.txt files)
- evidence_units.jsonl (per-case expert evidence spans)
- tasks.jsonl (per-case runtime tasks)
"""

import json
import os
from typing import Dict, List, Optional, Set


class CUADSkillGenLoader:
    """Unified data loader for CUAD-SkillGen dataset."""

    def __init__(self, data_root: str):
        """
        Args:
            data_root: Path to data/cuad_skillgen/
        """
        self.data_root = data_root
        self.corpus_dir = os.path.join(data_root, "corpus")
        self.cases_dir = os.path.join(data_root, "cases")
        self.splits_dir = os.path.join(data_root, "splits")
        self.contracts_dir = os.path.join(self.corpus_dir, "contracts")

        # Cached data
        self._category_descriptions: Optional[List[dict]] = None
        self._contract_metadata: Optional[Dict[str, dict]] = None
        self._splits: Optional[dict] = None
        self._case_mapping: Optional[dict] = None
        self._contract_texts: Dict[str, str] = {}

    # ─── Category Descriptions ───

    def load_category_descriptions(self) -> List[dict]:
        """Load all 41 category descriptions."""
        if self._category_descriptions is None:
            path = os.path.join(self.corpus_dir, "category_descriptions.jsonl")
            self._category_descriptions = []
            with open(path, "r", encoding="utf-8") as f:
                for line in f:
                    if line.strip():
                        self._category_descriptions.append(json.loads(line))
        return self._category_descriptions

    def get_category_descriptions_for_case(self, case_id: str) -> List[dict]:
        """Get category descriptions for a specific case's covered categories."""
        all_cats = self.load_category_descriptions()
        mapping = self.load_category_to_case_mapping()
        covered = set(mapping[case_id])
        return [c for c in all_cats if c["category"] in covered]

    # ─── Contract Metadata ───

    def load_contract_metadata(self) -> Dict[str, dict]:
        """Load all 510 contract metadata entries, keyed by contract_id."""
        if self._contract_metadata is None:
            path = os.path.join(self.corpus_dir, "contract_metadata.jsonl")
            self._contract_metadata = {}
            with open(path, "r", encoding="utf-8") as f:
                for line in f:
                    if line.strip():
                        entry = json.loads(line)
                        self._contract_metadata[entry["contract_id"]] = entry
        return self._contract_metadata

    # ─── Splits ───

    def load_splits(self) -> dict:
        """Load train/dev/test contract splits."""
        if self._splits is None:
            path = os.path.join(self.splits_dir, "splits.json")
            with open(path, "r", encoding="utf-8") as f:
                self._splits = json.load(f)
        return self._splits

    def get_split_contract_ids(self, split: str) -> List[str]:
        """Get contract IDs for a specific split ('train', 'dev', or 'test')."""
        splits = self.load_splits()
        return splits[split]["contract_ids"]

    def get_train_contract_ids(self) -> List[str]:
        return self.get_split_contract_ids("train")

    def get_dev_contract_ids(self) -> List[str]:
        return self.get_split_contract_ids("dev")

    def get_test_contract_ids(self) -> List[str]:
        return self.get_split_contract_ids("test")

    # ─── Category-to-Case Mapping ───

    def load_category_to_case_mapping(self) -> dict:
        """Load category → case_id mapping."""
        if self._case_mapping is None:
            path = os.path.join(self.corpus_dir, "category_to_case_mapping.json")
            with open(path, "r", encoding="utf-8") as f:
                self._case_mapping = json.load(f)
        return self._case_mapping

    def get_all_case_ids(self) -> List[str]:
        """Get all 9 case IDs."""
        return list(self.load_category_to_case_mapping().keys())

    # ─── Case Definition ───

    def load_case_json(self, case_id: str) -> dict:
        """Load case.json for a specific case."""
        path = os.path.join(self.cases_dir, case_id, "case.json")
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)

    # ─── Contract Text ───

    def load_contract_text(self, contract_id: str) -> str:
        """Load full text of a specific contract."""
        if contract_id not in self._contract_texts:
            path = os.path.join(self.contracts_dir, f"{contract_id}.txt")
            with open(path, "r", encoding="utf-8") as f:
                self._contract_texts[contract_id] = f.read()
        return self._contract_texts[contract_id]

    def load_contract_texts(self, contract_ids: List[str]) -> Dict[str, str]:
        """Load full text for multiple contracts."""
        result = {}
        for cid in contract_ids:
            result[cid] = self.load_contract_text(cid)
        return result

    # ─── Evidence Units ───

    def load_evidence_units(self, case_id: str) -> List[dict]:
        """Load evidence units for a specific case."""
        path = os.path.join(self.cases_dir, case_id, "evidence_units.jsonl")
        units = []
        with open(path, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    units.append(json.loads(line))
        return units

    def get_train_evidence_units(self, case_id: str) -> List[dict]:
        """Get evidence units from train split contracts only."""
        train_cids = set(self.get_train_contract_ids())
        all_units = self.load_evidence_units(case_id)
        return [u for u in all_units if u["contract_id"] in train_cids]

    def get_contracts_with_evidence(self, case_id: str, split: str = "train") -> Set[str]:
        """Get contract IDs that have at least one evidence unit in the given split."""
        split_cids = set(self.get_split_contract_ids(split))
        all_units = self.load_evidence_units(case_id)
        return set(u["contract_id"] for u in all_units if u["contract_id"] in split_cids)

    # ─── Tasks ───

    def load_tasks(self, case_id: str) -> List[dict]:
        """Load all tasks for a specific case."""
        path = os.path.join(self.cases_dir, case_id, "tasks.jsonl")
        tasks = []
        with open(path, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    tasks.append(json.loads(line))
        return tasks

    def get_tasks_by_status(self, case_id: str, gold_status: str) -> List[dict]:
        """Get tasks filtered by gold_status."""
        return [t for t in self.load_tasks(case_id) if t["gold_status"] == gold_status]

    # ─── Utility ───

    def get_stats(self) -> dict:
        """Get dataset statistics."""
        meta = self.load_contract_metadata()
        splits = self.load_splits()
        mapping = self.load_category_to_case_mapping()
        cats = self.load_category_descriptions()

        stats = {
            "total_contracts": len(meta),
            "total_categories": len(cats),
            "total_cases": len(mapping),
            "splits": {
                split: {
                    "contract_count": info["contract_count"],
                    "ratio": info["ratio"],
                }
                for split, info in splits.items()
                if split in ("train", "dev", "test")
            },
            "cases": {
                case_id: {
                    "covered_categories_count": len(cats_list),
                    "covered_categories": cats_list,
                }
                for case_id, cats_list in mapping.items()
            },
        }
        return stats
