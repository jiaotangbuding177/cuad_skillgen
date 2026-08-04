"""
Runtime Agent Container for CUAD-SkillGen evaluation.

Loads a generated SKILL.md and processes tasks from tasks.jsonl.
For each task, the agent:
1. Reads the SKILL.md for guidance
2. Reads the target contract
3. Answers the question following the skill's instructions
4. Outputs a standardized JSON response
"""

import json
import os
import sys
import time
from typing import Optional

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from common.loader import CUADSkillGenLoader
from common.llm_client import LLMClient, estimate_tokens, truncate_to_tokens


AGENT_SYSTEM_PROMPT = """You are a contract review agent. You have been given a SKILL.md that describes how to review contracts.

Your task:
1. Read the SKILL.md carefully and follow its instructions.
2. Read the target contract.
3. Answer the review question following the skill's rules.
4. Output a JSON response in the exact format specified by the skill.

IMPORTANT:
- Only use information from the target contract.
- Do not cite other contracts.
- If the answer is not found, return status "evidence_missing".
- If required inputs are missing, return status "missing_input".
- If the question is outside the skill's scope, return status "unsupported_scope".
- If the question requires legal advice, return status "needs_human_review".

Return your response as valid JSON only."""


def build_agent_user_prompt(skill_md: str, task: dict, contract_text: str) -> str:
    """Build the prompt for a single task."""
    parts = []

    parts.append("=== YOUR SKILL ===")
    parts.append(skill_md)
    parts.append("")

    parts.append("=== TASK ===")
    parts.append(f"Task ID: {task['task_id']}")
    parts.append(f"Case ID: {task['case_id']}")
    parts.append(f"Contract ID: {task.get('contract_id', '(not provided)')}")
    parts.append(f"Category: {task.get('category', '(not provided)')}")
    parts.append(f"Question: {task['question']}")
    parts.append(f"Query Type: {task.get('query_type', 'unknown')}")
    parts.append("")

    parts.append("=== TARGET CONTRACT ===")
    if task.get("contract_id") and contract_text:
        parts.append(f"Contract ID: {task['contract_id']}")
        parts.append(truncate_to_tokens(contract_text, 50000))  # ~50K tokens for the contract
    else:
        parts.append("(No contract provided)")
    parts.append("")

    parts.append("=== INSTRUCTION ===")
    parts.append("Answer the question following your SKILL.md instructions.")
    parts.append("Return ONLY a JSON object with these fields:")
    parts.append('  {"status": "...", "answer": "...", "evidence_unit_ids": [...], '
                 '"source_contract_ids": [...], "missing_inputs": [...], '
                 '"human_review_required": false, "selected_skill": "..."}')

    return "\n".join(parts)


class RuntimeAgent:
    """Agent container that processes tasks using a generated skill."""

    def __init__(
        self,
        loader: CUADSkillGenLoader,
        llm: LLMClient,
        results_root: str,
        method: str,
    ):
        self.loader = loader
        self.llm = llm
        self.results_root = results_root
        self.method = method
        self._skill_cache = {}

    def load_skill(self, case_id: str) -> str:
        """Load SKILL.md for a case (with caching)."""
        if case_id not in self._skill_cache:
            skill_path = os.path.join(self.results_root, self.method, case_id, "SKILL.md")
            with open(skill_path, "r", encoding="utf-8") as f:
                self._skill_cache[case_id] = f.read()
        return self._skill_cache[case_id]

    def process_task(self, task: dict) -> dict:
        """Process a single task and return the agent's response."""
        case_id = task["case_id"]
        skill_md = self.load_skill(case_id)

        # Load target contract
        contract_id = task.get("contract_id", "")
        contract_text = ""
        if contract_id:
            try:
                contract_text = self.loader.load_contract_text(contract_id)
            except FileNotFoundError:
                contract_text = ""

        # Build prompt and call LLM
        user_prompt = build_agent_user_prompt(skill_md, task, contract_text)
        try:
            response_text, usage = self.llm.call_json(AGENT_SYSTEM_PROMPT, user_prompt)
            # Ensure required fields
            response_text.setdefault("status", "unknown")
            response_text.setdefault("answer", "")
            response_text.setdefault("evidence_unit_ids", [])
            response_text.setdefault("source_contract_ids", [])
            response_text.setdefault("missing_inputs", [])
            response_text.setdefault("human_review_required", False)
            response_text.setdefault("selected_skill", case_id)
            response_text["_usage"] = usage
            return response_text
        except Exception as e:
            return {
                "status": "error",
                "answer": f"Agent error: {str(e)}",
                "evidence_unit_ids": [],
                "source_contract_ids": [],
                "missing_inputs": [],
                "human_review_required": False,
                "selected_skill": case_id,
                "_error": str(e),
            }

    def run_all_tasks(self, case_id: str, output_dir: str, overwrite: bool = False, incremental: bool = False) -> dict:
        """Run all tasks for a case and save results.
        
        Args:
            case_id: Case identifier
            output_dir: Output directory path
            overwrite: If True, overwrite existing results
            incremental: If True, only re-run tasks with status="error"
        """
        tasks = self.loader.load_tasks(case_id)
        os.makedirs(output_dir, exist_ok=True)
        output_path = os.path.join(output_dir, f"{case_id}_results.jsonl")

        # Load existing results if incremental mode
        existing_results = {}
        if incremental and os.path.exists(output_path):
            print(f"  [{case_id}] Loading existing results for incremental run...")
            with open(output_path, "r", encoding="utf-8") as f:
                for line in f:
                    if line.strip():
                        r = json.loads(line)
                        task_id = r.get("_task_id")
                        if task_id:
                            existing_results[task_id] = r
            
            # Count how many are errors
            error_count = sum(1 for r in existing_results.values() if r.get("status") == "error")
            print(f"  [{case_id}] Found {len(existing_results)} existing results, {error_count} errors to retry")

        if os.path.exists(output_path) and not overwrite and not incremental:
            print(f"  [{case_id}] Results already exist, skipping")
            return {"skipped": True}

        # Determine which tasks to process
        if incremental and existing_results:
            tasks_to_process = [t for t in tasks if t["task_id"] not in existing_results or 
                               existing_results[t["task_id"]].get("status") == "error"]
            print(f"  [{case_id}] Processing {len(tasks_to_process)} tasks (incremental)...")
        else:
            tasks_to_process = tasks
            print(f"  [{case_id}] Processing {len(tasks_to_process)} tasks...")

        results = []
        total_usage = {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0}
        start_time = time.time()

        for i, task in enumerate(tasks_to_process):
            result = self.process_task(task)
            result["_task_id"] = task["task_id"]
            result["_gold_status"] = task["gold_status"]
            result["_gold_evidence_unit_ids"] = task.get("gold_evidence_unit_ids", [])

            # Track usage
            usage = result.pop("_usage", {})
            for k in total_usage:
                total_usage[k] += usage.get(k, 0)

            # Update existing results or add new
            existing_results[task["task_id"]] = result

            if (i + 1) % 100 == 0:
                print(f"    Progress: {i+1}/{len(tasks_to_process)}")

        # Write all results (including existing ones)
        all_results = list(existing_results.values())
        with open(output_path, "w", encoding="utf-8") as f:
            for r in all_results:
                f.write(json.dumps(r, ensure_ascii=False) + "\n")

        duration = time.time() - start_time
        print(f"  [{case_id}] Done: {len(tasks_to_process)} tasks in {duration:.1f}s, {total_usage['total_tokens']} tokens")
        print(f"  [{case_id}] Total results: {len(all_results)}")

        return {
            "skipped": False,
            "task_count": len(tasks_to_process),
            "total_results": len(all_results),
            "usage": total_usage,
            "duration": duration,
        }
