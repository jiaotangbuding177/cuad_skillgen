"""
Common output writer for CUAD-SkillGen baselines.

Writes standardized output to:
  results/skillgen/generated/{method}/{case_id}/
    ├── SKILL.md
    ├── skill_manifest.json
    ├── evidence_index.json
    ├── security_policy.json
    └── generation_log.json
"""

import json
import os
from datetime import datetime, timezone
from typing import Any, Dict, Optional


class SkillOutputWriter:
    """Standardized output writer for Skill generation baselines."""

    def __init__(self, results_root: str, method: str, case_id: str):
        """
        Args:
            results_root: Path to results/skillgen/generated/
            method: Method name (e.g., 'native_prompt_skill')
            case_id: Case ID (e.g., 'ip_and_license')
        """
        self.output_dir = os.path.join(results_root, method, case_id)
        self.method = method
        self.case_id = case_id
        os.makedirs(self.output_dir, exist_ok=True)

    def write_skill_md(self, content: str):
        """Write SKILL.md file."""
        path = os.path.join(self.output_dir, "SKILL.md")
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)

    def write_skill_manifest(self, manifest: dict):
        """Write skill_manifest.json file.

        Expected fields:
        - method: str
        - case_id: str
        - model: str
        - input_summary: dict
        - usage: dict (prompt_tokens, completion_tokens, total_tokens)
        - duration_seconds: float
        Additional fields are method-specific.
        """
        # Ensure required fields
        manifest.setdefault("method", self.method)
        manifest.setdefault("case_id", self.case_id)
        manifest.setdefault("created_at", datetime.now(timezone.utc).isoformat())
        path = os.path.join(self.output_dir, "skill_manifest.json")
        with open(path, "w", encoding="utf-8") as f:
            json.dump(manifest, f, indent=2, ensure_ascii=False)

    def write_evidence_index(self, index: dict):
        """Write evidence_index.json file.

        Structure varies by method:
        - native/schema: {} (empty)
        - summary2skill: {category: {found_in_contracts, source_paragraphs}}
        - document_tool_maker: {tool_id: {example_sources}}
        - evoskill: {category: [{ka_id, text, source_contract_id, span_start, span_end, ...}]}
        """
        path = os.path.join(self.output_dir, "evidence_index.json")
        with open(path, "w", encoding="utf-8") as f:
            json.dump(index, f, indent=2, ensure_ascii=False)

    def write_security_policy(self, policy: dict):
        """Write security_policy.json file.

        Structure varies by method:
        - native/schema/summary/tool_maker: {} (empty)
        - evoskill: {allowed_status, required_behaviors, safety_requirements}
        """
        path = os.path.join(self.output_dir, "security_policy.json")
        with open(path, "w", encoding="utf-8") as f:
            json.dump(policy, f, indent=2, ensure_ascii=False)

    def write_generation_log(self, log: dict):
        """Write generation_log.json file.

        Contains:
        - prompts and responses (full text)
        - per-step LLM usage
        - intermediate artifacts
        """
        path = os.path.join(self.output_dir, "generation_log.json")
        with open(path, "w", encoding="utf-8") as f:
            json.dump(log, f, indent=2, ensure_ascii=False)

    def write_all(
        self,
        skill_md: str,
        manifest: dict,
        evidence_index: Optional[dict] = None,
        security_policy: Optional[dict] = None,
        generation_log: Optional[dict] = None,
    ):
        """Write all output files at once."""
        self.write_skill_md(skill_md)
        self.write_skill_manifest(manifest)
        self.write_evidence_index(evidence_index if evidence_index is not None else {})
        self.write_security_policy(security_policy if security_policy is not None else {})
        if generation_log is not None:
            self.write_generation_log(generation_log)

    def output_exists(self) -> bool:
        """Check if output already exists (for --overwrite flag)."""
        return os.path.isfile(os.path.join(self.output_dir, "SKILL.md"))


def create_empty_evidence_index() -> dict:
    """Create an empty evidence index (for methods that don't produce one)."""
    return {}


def create_empty_security_policy() -> dict:
    """Create an empty security policy (for methods that don't produce one)."""
    return {}


def create_text_only_security_policy(case_json: dict) -> dict:
    """Create a text-only security policy from case.json constraints.

    Used by schema_prompt to embed constraints in SKILL.md rather than
    a separate structured file.
    """
    reqs = case_json.get("capability_requirements", {})
    return {
        "_note": "Security constraints are embedded in SKILL.md Boundary Rules section",
        "required_behaviors": reqs.get("required_behaviors", []),
        "safety_requirements": reqs.get("safety_requirements", []),
    }
