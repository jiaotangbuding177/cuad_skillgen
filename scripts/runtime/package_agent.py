"""Package-aware runtime agent for CUAD-SkillGen.

This runtime treats a generated skill as a package rather than placing only
SKILL.md in one large prompt. Training evidence is used as retrieval guidance;
only verified spans from the target contract may be returned as evidence.
"""

import json
import math
import os
import re
import time
from collections import Counter
from dataclasses import dataclass
from typing import Dict, Iterable, List, Optional, Sequence, Tuple

from common.loader import CUADSkillGenLoader
from common.llm_client import LLMClient


ALLOWED_STATUS = {
    "answered",
    "evidence_missing",
    "missing_input",
    "unsupported_scope",
    "needs_human_review",
}

TOKEN_RE = re.compile(r"[A-Za-z0-9][A-Za-z0-9_/-]*")
LEGAL_ADVICE_RE = re.compile(
    r"\b(advise|advice|should we sue|legal strategy|litigation|prevail|"
    r"recover in court|legally enforceable|negotiation strategy|legal risks?)\b",
    re.IGNORECASE,
)
EXTERNAL_OUTPUT_RE = re.compile(
    r"\b(draft|write|produce|generate)\b.{0,80}\b(letter|memorandum|memo|"
    r"notice|certificate|official documentation|legal opinion)\b",
    re.IGNORECASE | re.DOTALL,
)


def _read_json(path: str, default):
    if not os.path.exists(path):
        return default
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def _tokens(text: str) -> List[str]:
    return [token.lower() for token in TOKEN_RE.findall(text or "")]


def _compact_text(text: str, limit: int = 900) -> str:
    text = re.sub(r"\s+", " ", text or "").strip()
    return text if len(text) <= limit else text[:limit] + "..."


@dataclass
class ContractChunk:
    chunk_id: str
    text: str
    span_start: int
    span_end: int

    def to_dict(self) -> dict:
        return {
            "chunk_id": self.chunk_id,
            "text": self.text,
            "span_start": self.span_start,
            "span_end": self.span_end,
        }


class SkillPackage:
    """Read-only, lossless access to a generated skill package."""

    def __init__(self, root: str, method: str, case_id: str, case_json: dict):
        self.method = method
        self.case_id = case_id
        self.case_json = case_json
        self.path = os.path.join(root, method, case_id)
        skill_path = os.path.join(self.path, "SKILL.md")
        if not os.path.exists(skill_path):
            raise FileNotFoundError(skill_path)
        with open(skill_path, "r", encoding="utf-8") as f:
            self.skill_md = f.read()
        self.evidence_index = _read_json(
            os.path.join(self.path, "evidence_index.json"), {}
        )
        self.security_policy = _read_json(
            os.path.join(self.path, "security_policy.json"), {}
        )
        self.tool_manifest = _read_json(
            os.path.join(self.path, "tool_manifest.json"), {}
        )
        self.manifest = _read_json(
            os.path.join(self.path, "skill_manifest.json"), {}
        )

    @property
    def covered_categories(self) -> List[str]:
        policy_rules = self.security_policy.get("boundary_rules", [])
        for rule in policy_rules:
            if isinstance(rule, dict) and rule.get("covered_categories"):
                return list(rule["covered_categories"])
        return list(self.case_json.get("covered_categories", []))

    @property
    def allowed_status(self) -> List[str]:
        values = self.security_policy.get("allowed_status", [])
        return list(values) if values else sorted(ALLOWED_STATUS)

    def policy_text(self) -> str:
        parts = []
        for key in ("required_behaviors", "safety_requirements"):
            for item in self.security_policy.get(key, []):
                if isinstance(item, dict):
                    parts.append(f"[{item.get('rule_id', '')}] {item.get('text', '')}")
                else:
                    parts.append(str(item))
        return "\n".join(parts)

    def policy_supports(self, concept: str) -> bool:
        haystack = (self.policy_text() + "\n" + self.skill_md).lower()
        if concept == "legal_advice":
            return "legal advice" in haystack or "human review" in haystack
        if concept == "external_output":
            markers = ("externally sendable", "external output", "legal opinion")
            return any(marker in haystack for marker in markers)
        return False

    def skill_guidance(self, category: str, question: str, top_k: int = 4) -> List[str]:
        sections = re.split(r"(?=^#{1,4}\s)", self.skill_md, flags=re.MULTILINE)
        query = f"{category} {question}"
        ranked = rank_texts(query, sections)
        return [_compact_text(text, 1800) for text, _ in ranked[:top_k] if text.strip()]

    def knowledge_items(self, category: str) -> List[dict]:
        """Normalize package-specific evidence without changing source files."""
        result = []
        index = self.evidence_index
        value = index.get(category) if isinstance(index, dict) else None

        # EvoSkill: category -> list[KA]
        if isinstance(value, list):
            for item in value:
                if isinstance(item, dict):
                    result.append({
                        "id": item.get("ka_id", ""),
                        "text": item.get("text", ""),
                        "interpretation": item.get("interpretation", ""),
                        "source_contract_id": item.get("source_contract_id", ""),
                    })

        # Summary2Skill: category -> {source_paragraphs: [...]}
        elif isinstance(value, dict):
            for i, item in enumerate(value.get("source_paragraphs", [])):
                result.append({
                    "id": f"summary-{i + 1}",
                    "text": item.get("paragraph_snippet", ""),
                    "interpretation": "",
                    "source_contract_id": item.get("contract_id", ""),
                })

        # DocumentToolMaker evidence index: tool_id -> tool metadata.
        if not result and isinstance(index, dict):
            for tool_id, item in index.items():
                if not isinstance(item, dict) or item.get("category") != category:
                    continue
                example = item.get("example", {})
                result.append({
                    "id": tool_id,
                    "text": json.dumps(example, ensure_ascii=False),
                    "interpretation": item.get("name", ""),
                    "source_contract_id": "",
                })
        return result

    def tool_specs(self, category: str) -> List[dict]:
        tools = self.tool_manifest.get("tools", [])
        return [tool for tool in tools if tool.get("category") == category]

    def retrieve_knowledge(self, category: str, question: str, top_k: int) -> List[dict]:
        items = self.knowledge_items(category)
        texts = [f"{item['text']} {item['interpretation']}" for item in items]
        scores = score_texts(f"{category} {question}", texts)
        ranked = sorted(zip(items, scores), key=lambda pair: pair[1], reverse=True)
        return [item for item, score in ranked[:top_k] if score > 0]

def expand_chunk_context(
    chunks: Sequence[ContractChunk],
    full_text: str,
    window_chars: int = 1200,
) -> List[ContractChunk]:
    """Expand each chunk by a context window on both sides from the full contract text.

    This gives the LLM more clause-level context around each matched chunk,
    reducing fragmented quotes from short retrieval windows.
    """
    if not chunks:
        return []
    max_len = len(full_text)
    expanded = []
    for chunk in chunks:
        new_start = max(0, chunk.span_start - window_chars)
        new_end = min(max_len, chunk.span_end + window_chars)
        expanded.append(ContractChunk(
            chunk.chunk_id,
            full_text[new_start:new_end],
            new_start,
            new_end,
        ))
    return expanded


def score_texts(query: str, texts: Sequence[str]) -> List[float]:
    """Small dependency-free BM25 implementation."""
    if not texts:
        return []
    query_terms = list(dict.fromkeys(_tokens(query)))
    documents = [_tokens(text) for text in texts]
    avg_len = sum(len(doc) for doc in documents) / max(len(documents), 1)
    doc_freq = Counter()
    for doc in documents:
        doc_freq.update(set(doc))
    scores = []
    for doc in documents:
        tf = Counter(doc)
        score = 0.0
        for term in query_terms:
            if not tf[term]:
                continue
            idf = math.log(1 + (len(documents) - doc_freq[term] + 0.5) / (doc_freq[term] + 0.5))
            denom = tf[term] + 1.5 * (1 - 0.75 + 0.75 * len(doc) / max(avg_len, 1))
            score += idf * tf[term] * 2.5 / denom
        scores.append(score)
    return scores


def rank_texts(query: str, texts: Sequence[str]) -> List[Tuple[str, float]]:
    scores = score_texts(query, texts)
    return sorted(zip(texts, scores), key=lambda pair: pair[1], reverse=True)


def chunk_contract(text: str, target_chars: int = 4800, overlap_chars: int = 600) -> List[ContractChunk]:
    """Create stable target-contract chunks while preserving character offsets."""
    if not text:
        return []
    chunks = []
    start = 0
    index = 1
    while start < len(text):
        hard_end = min(start + target_chars, len(text))
        end = hard_end
        if hard_end < len(text):
            candidates = [
                text.rfind("\n\n", start + target_chars // 2, hard_end),
                text.rfind("\n", start + target_chars // 2, hard_end),
                text.rfind(". ", start + target_chars // 2, hard_end),
            ]
            boundary = max(candidates)
            if boundary > start:
                end = boundary + (2 if text[boundary:boundary + 2] in ("\n\n", ". ") else 1)
        chunk_text = text[start:end]
        chunks.append(ContractChunk(f"chunk-{index:04d}", chunk_text, start, end))
        if end >= len(text):
            break
        start = max(end - overlap_chars, start + 1)
        index += 1
    return chunks


def retrieve_contract_chunks(
    chunks: Sequence[ContractChunk], query: str, top_k: int
) -> List[ContractChunk]:
    ranked = rank_texts(query, [chunk.text for chunk in chunks])
    text_to_chunks: Dict[str, List[ContractChunk]] = {}
    for chunk in chunks:
        text_to_chunks.setdefault(chunk.text, []).append(chunk)
    selected = []
    for text, _ in ranked[:top_k]:
        selected.append(text_to_chunks[text].pop(0))
    return sorted(selected, key=lambda chunk: chunk.span_start)


def build_contract_query(
    category: str,
    question: str,
    guidance: Sequence[str],
    knowledge: Sequence[dict],
    tools: Sequence[dict],
    variant: str = "full",
) -> str:
    """Build reproducible query variants for runtime and retrieval diagnostics."""
    parts = [category, question]
    if variant in {"package_without_knowledge", "full"}:
        parts.extend(guidance)
        parts.extend(
            f"{tool.get('name', '')} {tool.get('description', '')}"
            for tool in tools
        )
    if variant == "full":
        parts.extend(
            f"{item.get('text', '')} {item.get('interpretation', '')}"
            for item in knowledge
        )
    if variant not in {"task_only", "package_without_knowledge", "full"}:
        raise ValueError(f"Unknown query variant: {variant}")
    return " ".join(parts)


def _find_quote(text: str, quote: str, ranges: Sequence[Tuple[int, int]]) -> Optional[Tuple[int, int]]:
    quote = (quote or "").strip()
    if not quote:
        return None
    for start, end in ranges:
        pos = text.find(quote, start, end)
        if pos >= 0:
            return pos, pos + len(quote)
    # Models often normalize contract whitespace. Match flexibly but only inside retrieved ranges.
    pieces = [re.escape(piece) for piece in re.split(r"\s+", quote) if piece]
    if not pieces:
        return None
    pattern = re.compile(r"\s+".join(pieces), re.DOTALL)
    for start, end in ranges:
        match = pattern.search(text, start, end)
        if match:
            return match.start(), match.end()
    return None


class PackageAwareAgent:
    SYSTEM_PROMPT = """You are a contract evidence extraction agent.

You receive review guidance, training-derived search patterns, and excerpts from ONE target contract.
Training knowledge describes what to look for. Never quote it or cite its source contracts as target evidence.
Only evidence copied from TARGET CONTRACT EXCERPTS may support an answer.
Return valid JSON only. Use exactly one status: answered, evidence_missing, missing_input,
unsupported_scope, or needs_human_review."""

    def __init__(
        self,
        loader: CUADSkillGenLoader,
        llm: LLMClient,
        results_root: str,
        method: str,
        top_k_chunks: int = 10,
        top_k_knowledge: int = 6,
    ):
        self.loader = loader
        self.llm = llm
        self.results_root = results_root
        self.method = method
        self.top_k_chunks = top_k_chunks
        self.top_k_knowledge = top_k_knowledge
        self._packages: Dict[str, SkillPackage] = {}

    def package(self, case_id: str) -> SkillPackage:
        if case_id not in self._packages:
            self._packages[case_id] = SkillPackage(
                self.results_root,
                self.method,
                case_id,
                self.loader.load_case_json(case_id),
            )
        return self._packages[case_id]

    def boundary_decision(self, task: dict, package: SkillPackage) -> Optional[dict]:
        missing = []
        if not task.get("contract_id"):
            missing.append("contract_id")
        if not task.get("category"):
            missing.append("category")
        question = (task.get("question") or "").strip()
        if not question or question.lower() in {"review this contract.", "review this contract"}:
            missing.append("question")
        if missing:
            return self._boundary_result("missing_input", package, missing)
        if task["category"] not in package.covered_categories:
            return self._boundary_result("unsupported_scope", package)
        if LEGAL_ADVICE_RE.search(question) and package.policy_supports("legal_advice"):
            return self._boundary_result("needs_human_review", package, human_review=True)
        if EXTERNAL_OUTPUT_RE.search(question) and package.policy_supports("external_output"):
            return self._boundary_result("needs_human_review", package, human_review=True)
        return None

    @staticmethod
    def _boundary_result(
        status: str,
        package: SkillPackage,
        missing: Optional[List[str]] = None,
        human_review: bool = False,
    ) -> dict:
        return {
            "status": status,
            "answer": "",
            "evidence": [],
            "source_contract_ids": [],
            "missing_inputs": missing or [],
            "human_review_required": human_review,
            "selected_skill": package.case_id,
            "retrieved_knowledge_ids": [],
            "selected_tool_ids": [],
            "validation_errors": [],
            "boundary_routed": True,
        }

    def process_task(self, task: dict) -> dict:
        package = self.package(task["case_id"])
        boundary = self.boundary_decision(task, package)
        if boundary:
            return boundary

        contract_id = task["contract_id"]
        try:
            contract_text = self.loader.load_contract_text(contract_id)
        except FileNotFoundError:
            return self._boundary_result("missing_input", package, ["contract_text"])

        category = task["category"]
        question = task["question"]
        guidance = package.skill_guidance(category, question)
        knowledge = package.retrieve_knowledge(category, question, self.top_k_knowledge)
        tools = package.tool_specs(category)[:3]

        knowledge_query = build_contract_query(
            category,
            question,
            guidance,
            knowledge,
            tools,
            variant="full",
        )
        all_chunks = chunk_contract(contract_text)
        selected_chunks = retrieve_contract_chunks(all_chunks, knowledge_query, self.top_k_chunks)
        selected_chunks = expand_chunk_context(selected_chunks, contract_text, window_chars=1200)
        prompt = self._build_prompt(task, package, guidance, knowledge, tools, selected_chunks)

        try:
            raw, usage = self.llm.call_json(self.SYSTEM_PROMPT, prompt, max_tokens=4096)
            result = self._validate_response(raw, task, package, contract_text, selected_chunks)
            result["retrieved_knowledge_ids"] = [item["id"] for item in knowledge]
            result["selected_tool_ids"] = [
                tool.get("tool_id", tool.get("name", "")) for tool in tools
            ]
            result["_usage"] = usage
            return result
        except Exception as exc:
            return {
                "status": "error",
                "answer": "",
                "evidence": [],
                "source_contract_ids": [],
                "missing_inputs": [],
                "human_review_required": False,
                "selected_skill": package.case_id,
                "retrieved_knowledge_ids": [item["id"] for item in knowledge],
                "selected_tool_ids": [tool.get("tool_id", tool.get("name", "")) for tool in tools],
                "validation_errors": [],
                "boundary_routed": False,
                "_error": str(exc),
            }

    def _build_prompt(
        self,
        task: dict,
        package: SkillPackage,
        guidance: Sequence[str],
        knowledge: Sequence[dict],
        tools: Sequence[dict],
        chunks: Sequence[ContractChunk],
    ) -> str:
        safe_knowledge = [
            {
                "knowledge_id": item["id"],
                "pattern": _compact_text(item["text"]),
                "interpretation": _compact_text(item["interpretation"], 400),
            }
            for item in knowledge
        ]
        safe_tools = [
            {
                "tool_id": tool.get("tool_id", tool.get("name", "")),
                "name": tool.get("name", ""),
                "description": tool.get("description", ""),
            }
            for tool in tools
        ]
        chunk_payload = [chunk.to_dict() for chunk in chunks]
        schema = {
            "status": "answered or evidence_missing",
            "answer": "concise answer based only on verified target evidence",
            "evidence": [
                {
                    "chunk_id": "chunk-0001",
                    "text": "exact quote copied from a target excerpt",
                }
            ],
            "source_contract_ids": [task["contract_id"]],
            "missing_inputs": [],
            "human_review_required": False,
            "selected_skill": package.case_id,
        }
        return "\n\n".join([
            "=== TASK ===\n" + json.dumps({
                "task_id": task["task_id"],
                "case_id": task["case_id"],
                "contract_id": task["contract_id"],
                "category": task["category"],
                "question": task["question"],
            }, ensure_ascii=False, indent=2),
            "=== RELEVANT SKILL GUIDANCE ===\n" + "\n\n".join(guidance),
            "=== ENFORCED PACKAGE POLICY ===\n" + package.policy_text(),
            "=== TRAINING KNOWLEDGE (SEARCH GUIDANCE ONLY; NEVER CITE) ===\n"
            + json.dumps(safe_knowledge, ensure_ascii=False, indent=2),
            "=== DECLARATIVE TOOL SPECS ===\n"
            + json.dumps(safe_tools, ensure_ascii=False, indent=2),
            "=== TARGET CONTRACT EXCERPTS ===\n"
            + json.dumps(chunk_payload, ensure_ascii=False, indent=2),
            "=== OUTPUT ===\nReturn only this JSON shape:\n"
            + json.dumps(schema, ensure_ascii=False, indent=2),
        ])

    def _validate_response(
        self,
        raw: dict,
        task: dict,
        package: SkillPackage,
        contract_text: str,
        chunks: Sequence[ContractChunk],
    ) -> dict:
        if not isinstance(raw, dict):
            raise ValueError("Agent response must be a JSON object")
        status_map = {"success": "answered", "ok": "answered"}
        status = status_map.get(str(raw.get("status", "")).lower(), str(raw.get("status", "")).lower())
        errors = []
        if status not in set(package.allowed_status):
            errors.append(f"invalid_status:{status}")
            status = "evidence_missing"

        ranges = [(chunk.span_start, chunk.span_end) for chunk in chunks]
        valid_evidence = []
        for item in raw.get("evidence", []):
            if not isinstance(item, dict):
                continue
            located = _find_quote(contract_text, str(item.get("text", "")), ranges)
            if not located:
                errors.append("unverified_evidence_quote")
                continue
            start, end = located
            valid_evidence.append({
                "contract_id": task["contract_id"],
                "text": contract_text[start:end],
                "span_start": start,
                "span_end": end,
                "chunk_id": item.get("chunk_id", ""),
            })

        if status == "answered" and not valid_evidence:
            errors.append("answered_without_verified_evidence")
            status = "evidence_missing"
        source_ids = [task["contract_id"]] if valid_evidence else []
        return {
            "status": status,
            "answer": str(raw.get("answer", "")),
            "evidence": valid_evidence,
            "source_contract_ids": source_ids,
            "missing_inputs": list(raw.get("missing_inputs", [])),
            "human_review_required": bool(raw.get("human_review_required", False)),
            "selected_skill": package.case_id,
            "retrieved_knowledge_ids": [],  # populated from the prompt trace below
            "selected_tool_ids": [],
            "validation_errors": errors,
            "boundary_routed": False,
        }


class IncrementalPackageRunner:
    """Append-only runner. The latest record for each task is authoritative."""

    def __init__(self, agent: PackageAwareAgent, loader: CUADSkillGenLoader):
        self.agent = agent
        self.loader = loader

    @staticmethod
    def load_latest(path: str) -> Dict[str, dict]:
        latest = {}
        if not os.path.exists(path):
            return latest
        with open(path, "r", encoding="utf-8") as f:
            for line in f:
                if not line.strip():
                    continue
                record = json.loads(line)
                if record.get("_task_id"):
                    latest[record["_task_id"]] = record
        return latest

    def select_tasks(self, case_id: str, split: str, include_governance: bool) -> List[dict]:
        tasks = self.loader.load_tasks(case_id)
        if split == "all":
            return tasks
        contract_ids = set(self.loader.get_split_contract_ids(split))
        selected = []
        for task in tasks:
            is_governance = task.get("construction_source") == "newly_added_governance_task"
            if task.get("contract_id") in contract_ids or (include_governance and is_governance):
                selected.append(task)
        return selected

    def run_case(
        self,
        case_id: str,
        output_dir: str,
        split: str = "test",
        include_governance: bool = True,
        retry_errors: bool = True,
        max_tasks: Optional[int] = None,
        stop_on_quota_error: bool = True,
    ) -> dict:
        os.makedirs(output_dir, exist_ok=True)
        output_path = os.path.join(output_dir, f"{case_id}_results.jsonl")
        existing = self.load_latest(output_path)
        tasks = self.select_tasks(case_id, split, include_governance)
        pending = []
        for task in tasks:
            prior = existing.get(task["task_id"])
            if prior is None or (retry_errors and prior.get("status") == "error"):
                pending.append(task)
        if max_tasks is not None:
            pending = pending[:max_tasks]

        print(
            f"  [{case_id}] selected={len(tasks)}, existing={len(existing)}, "
            f"pending={len(pending)}"
        )
        usage_total = {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0}
        start_time = time.time()
        halted_reason = None
        with open(output_path, "a", encoding="utf-8", buffering=1) as f:
            for index, task in enumerate(pending, 1):
                result = self.agent.process_task(task)
                usage = result.pop("_usage", {})
                for key in usage_total:
                    usage_total[key] += usage.get(key, 0)
                result["_task_id"] = task["task_id"]
                result["_case_id"] = case_id
                result["_target_contract_id"] = task.get("contract_id", "")
                result["_category"] = task.get("category", "")
                result["_gold_status"] = task["gold_status"]
                result["_gold_evidence_unit_ids"] = task.get("gold_evidence_unit_ids", [])
                result["_split"] = split
                f.write(json.dumps(result, ensure_ascii=False) + "\n")
                f.flush()
                error_text = str(result.get("_error", "")).lower()
                quota_markers = (
                    "每天 credits 限制",
                    "daily credits",
                    "daily credit",
                    "quota exceeded",
                    "insufficient_quota",
                )
                if (
                    stop_on_quota_error
                    and result.get("status") == "error"
                    and any(marker in error_text for marker in quota_markers)
                ):
                    halted_reason = result.get("_error") or "daily quota exhausted"
                    print(
                        f"    quota exhausted at {index}/{len(pending)}; "
                        "checkpoint saved, stopping this run"
                    )
                    break
                if index % 25 == 0:
                    print(f"    checkpoint: {index}/{len(pending)}")
        return {
            "selected_tasks": len(tasks),
            "processed_tasks": index if pending else 0,
            "remaining_tasks": max(0, len(pending) - (index if pending else 0)),
            "halted_reason": halted_reason,
            "usage": usage_total,
            "duration": time.time() - start_time,
            "output_path": output_path,
        }
