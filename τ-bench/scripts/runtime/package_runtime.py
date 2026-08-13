from __future__ import annotations

import hashlib
import json
import math
import re
from html import escape
from collections import Counter
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Iterable


TOKEN_RE = re.compile(r"[a-zA-Z0-9_]+")


def tokens(text: str) -> list[str]:
    return [token.lower() for token in TOKEN_RE.findall(text) if len(token) > 1]


def stable_hash(paths: Iterable[Path]) -> str:
    digest = hashlib.sha256()
    for path in sorted(paths, key=lambda value: value.name):
        digest.update(path.name.encode("utf-8"))
        digest.update(path.read_bytes())
    return digest.hexdigest()


@dataclass(frozen=True)
class RetrievalConfig:
    skill_top_k: int = 4
    atom_top_k: int = 6
    rule_top_k: int = 3
    workflow_top_k: int = 3
    pattern_top_k: int = 3
    max_context_chars: int = 12000
    max_item_chars: int = 1800
    history_messages: int = 6


@dataclass(frozen=True)
class PackageItem:
    item_id: str
    lane: str
    title: str
    text: str
    source: str | None
    metadata: dict[str, Any]

    @property
    def searchable_text(self) -> str:
        return f"{self.title} {self.title} {self.text}"


class BM25Index:
    def __init__(self, items: list[PackageItem], k1: float = 1.5, b: float = 0.75):
        self.items = items
        self.k1 = k1
        self.b = b
        self.documents = [tokens(item.searchable_text) for item in items]
        self.term_frequencies = [Counter(document) for document in self.documents]
        self.lengths = [len(document) for document in self.documents]
        self.average_length = sum(self.lengths) / len(self.lengths) if self.lengths else 0.0
        document_frequency: Counter[str] = Counter()
        for document in self.documents:
            document_frequency.update(set(document))
        count = len(items)
        self.idf = {
            term: math.log(1.0 + (count - frequency + 0.5) / (frequency + 0.5))
            for term, frequency in document_frequency.items()
        }

    def search(self, query: str, top_k: int) -> list[tuple[PackageItem, float]]:
        query_terms = tokens(query)
        if not query_terms or not self.items or top_k <= 0:
            return []
        scored = []
        for item, frequencies, length in zip(self.items, self.term_frequencies, self.lengths):
            score = 0.0
            for term in query_terms:
                frequency = frequencies.get(term, 0)
                if frequency == 0:
                    continue
                denominator = frequency + self.k1 * (
                    1.0 - self.b + self.b * length / max(self.average_length, 1.0)
                )
                score += self.idf.get(term, 0.0) * frequency * (self.k1 + 1.0) / denominator
            if score > 0:
                scored.append((item, score))
        scored.sort(key=lambda pair: (-pair[1], pair[0].item_id))
        return scored[:top_k]


def _read(path: Path, default: Any) -> Any:
    if not path.exists():
        return default
    return json.loads(path.read_text(encoding="utf-8"))


class SkillPackage:
    """Uniformly loads every baseline package into the same retrieval lanes."""

    def __init__(self, root: Path, domain: str, config: RetrievalConfig):
        self.root = root
        self.domain = domain
        self.config = config
        self.skill = (root / "SKILL.md").read_text(encoding="utf-8")
        self.manifest = _read(root / "manifest.json", {})
        self.method = self.manifest.get("method", root.parent.name)
        self.items = self._load_items()
        self.by_lane: dict[str, list[PackageItem]] = {
            lane: [item for item in self.items if item.lane == lane]
            for lane in ("skill", "atom", "rule", "workflow", "pattern")
        }
        self.indexes = {lane: BM25Index(items) for lane, items in self.by_lane.items()}
        active_names = {"SKILL.md", "manifest.json"}
        if self.method in {"raw_policy_rag", "document_tool_maker", "evoskill_compiler", "graph_evoskill_compiler"}:
            active_names.add("evidence_index.json")
        if self.method in {"evoskill_compiler", "graph_evoskill_compiler"}:
            active_names.update({"security_policy.json", "workflow_patterns.json"})
        if self.method == "graph_evoskill_compiler":
            active_names.add("pattern_cards.json")
        self.active_files = sorted(name for name in active_names if (root / name).exists())
        self.ignored_files = sorted(path.name for path in root.iterdir() if path.is_file() and path.name not in active_names)
        self.package_hash = stable_hash(root / name for name in self.active_files)

    def _load_items(self) -> list[PackageItem]:
        items: list[PackageItem] = []
        profiles = {
            "raw_policy_rag": {"skill", "atom"},
            "native_prompt_skill": {"skill"},
            "schema_prompt_skill": {"skill"},
            "summary2skill": {"skill"},
            "document_tool_maker": {"skill", "tool_atom"},
            "evoskill_compiler": {"skill", "atom", "rule", "workflow"},
            "graph_evoskill_compiler": {"skill", "atom", "rule", "workflow", "pattern"},
        }
        capabilities = profiles.get(self.method, {"skill"})
        heading = "Overview"
        section_lines: list[str] = []
        section_index = 0
        for line in self.skill.splitlines() + ["# __END__"]:
            if line.startswith("#"):
                body = "\n".join(section_lines).strip()
                if body:
                    section_index += 1
                    items.append(PackageItem(
                        item_id=f"SK-{section_index:04d}", lane="skill", title=heading,
                        text=body, source="SKILL.md", metadata={"method": self.method},
                    ))
                heading = line.lstrip("#").strip()
                section_lines = []
            else:
                section_lines.append(line)
        evidence = _read(self.root / "evidence_index.json", {}).get("knowledge_atoms", [])
        for atom in evidence:
            # Banking product knowledge remains behind the official KB_search tool.
            # Package retrieval only supplies task-independent process/policy context.
            if self.domain == "banking_knowledge" and atom.get("kind") == "knowledge_document":
                continue
            if "atom" not in capabilities and not (
                "tool_atom" in capabilities and atom.get("kind") == "tool_contract"
            ):
                continue
            items.append(PackageItem(
                item_id=atom.get("ka_id", f"atom-{len(items)}"), lane="atom",
                title=atom.get("title", "Untitled atom"), text=atom.get("text", ""),
                source=atom.get("source"),
                metadata={key: value for key, value in atom.items() if key not in {"text", "title", "source"}},
            ))
        policy = _read(self.root / "security_policy.json", {})
        for rule in policy.get("rules", []) if "rule" in capabilities else []:
            items.append(PackageItem(
                item_id=rule.get("rule_id", f"rule-{len(items)}"), lane="rule",
                title=rule.get("title", "Untitled rule"), text=rule.get("text", ""),
                source=",".join(rule.get("source_ka_ids", [])) or None,
                metadata={key: value for key, value in rule.items() if key not in {"text", "title"}},
            ))
        workflows = _read(self.root / "workflow_patterns.json", {}).get("patterns", []) if "workflow" in capabilities else []
        for workflow in workflows:
            steps = workflow.get("steps", [])
            items.append(PackageItem(
                item_id=workflow.get("workflow_id", f"workflow-{len(items)}"), lane="workflow",
                title=f"Workflow {workflow.get('workflow_id', '')}",
                text=" -> ".join(steps), source=workflow.get("source"), metadata=workflow,
            ))
        # Pattern Cards are a compile-time GESC artifact. V1 indexes their text/IDs
        # like ordinary candidates and deliberately does not traverse knowledge_graph.json.
        patterns = _read(self.root / "pattern_cards.json", {}).get("patterns", []) if "pattern" in capabilities else []
        for pattern in patterns:
            text = (
                f"central={pattern.get('central_ka_id', '')}; "
                f"members={', '.join(pattern.get('member_ka_ids', []))}"
            )
            items.append(PackageItem(
                item_id=pattern.get("pattern_id", f"pattern-{len(items)}"), lane="pattern",
                title=pattern.get("name", "Untitled pattern"), text=text,
                source=pattern.get("central_ka_id"), metadata=pattern,
            ))
        return items

    def retrieve(self, query: str) -> dict[str, Any]:
        limits = {
            "skill": self.config.skill_top_k,
            "atom": self.config.atom_top_k,
            "rule": self.config.rule_top_k,
            "workflow": self.config.workflow_top_k,
            "pattern": self.config.pattern_top_k,
        }
        selected: list[dict[str, Any]] = []
        remaining = self.config.max_context_chars
        lane_order = ("skill", "rule", "atom", "workflow", "pattern")
        candidates = {
            lane: self.indexes[lane].search(query, limits[lane]) for lane in lane_order
        }
        max_rounds = max((len(values) for values in candidates.values()), default=0)
        for rank in range(max_rounds):
            for lane in lane_order:
                if rank >= len(candidates[lane]):
                    continue
                item, score = candidates[lane][rank]
                body = item.text[: self.config.max_item_chars]
                rendered = (
                    f"### [{lane}] {item.item_id}: {item.title}\n"
                    f"Source: {item.source or 'package'}\n{body}\n"
                )
                if len(rendered) > remaining:
                    continue
                remaining -= len(rendered)
                selected.append({
                    "item_id": item.item_id, "lane": lane, "title": item.title,
                    "source": item.source, "score": round(score, 6),
                    "chars": len(rendered), "rendered": rendered,
                })
        context = "".join(item["rendered"] for item in selected)
        return {
            "query": query,
            "items": [{key: value for key, value in item.items() if key != "rendered"} for item in selected],
            "context": context,
            "context_chars": len(context),
            "budget_chars": self.config.max_context_chars,
        }

    def describe(self) -> dict[str, Any]:
        return {
            "package_root": str(self.root), "package_hash": self.package_hash,
            "method": self.manifest.get("method"), "domain": self.domain,
            "lane_counts": {lane: len(items) for lane, items in self.by_lane.items()},
            "retrieval_config": asdict(self.config),
            "banking_knowledge_documents_excluded": self.domain == "banking_knowledge",
            "graph_traversal_enabled": False,
            "active_files": self.active_files,
            "ignored_files": self.ignored_files,
            "capability_profile": sorted({
                "raw_policy_rag": {"skill", "atom"},
                "native_prompt_skill": {"skill"},
                "schema_prompt_skill": {"skill"},
                "summary2skill": {"skill"},
                "document_tool_maker": {"skill", "tool_atom"},
                "evoskill_compiler": {"skill", "atom", "rule", "workflow"},
                "graph_evoskill_compiler": {"skill", "atom", "rule", "workflow", "pattern"},
            }.get(self.method, {"skill"})),
        }


def message_text(message: Any) -> str:
    if hasattr(message, "model_dump"):
        value = message.model_dump(mode="json")
    elif isinstance(message, dict):
        value = message
    else:
        return str(message)
    parts = [str(value.get("content") or "")]
    for call in value.get("tool_calls") or []:
        parts.append(str(call.get("name") or ""))
        parts.append(json.dumps(call.get("arguments") or {}, ensure_ascii=False))
    if value.get("role") == "tool":
        parts.append(str(value.get("requestor") or ""))
    return " ".join(parts)


def build_query(incoming: Any, history: list[Any], history_messages: int) -> str:
    messages = list(history[-history_messages:]) + [incoming]
    parts = [message_text(message) for message in messages]
    return "\n".join(part for part in parts if part.strip())


@dataclass(frozen=True)
class ProgressiveConfig:
    max_catalog_chars: int = 12000
    max_module_chars: int = 9000
    max_active_modules: int = 2


class ProgressiveSkillPackage:
    """Loads the v2 module contract without reading compile-time graphs at runtime."""

    def __init__(self, root: Path, domain: str, config: ProgressiveConfig | None = None):
        self.root = root
        self.domain = domain
        self.config = config or ProgressiveConfig()
        self.manifest = _read(root / "manifest.json", {})
        self.method = self.manifest.get("method", root.parent.name)
        self.skill = (root / "SKILL.md").read_text(encoding="utf-8")
        payload = _read(root / "action_modules.json", {})
        modules = payload.get("modules", [])
        if not modules and self.method != "no_skill":
            modules = [{
                "module_id": f"{domain}.{self.method}",
                "name": self.method.replace("_", " ").title(),
                "description": f"General {domain.replace('_', ' ')} SOP guidance.",
                "required_tools": [], "instructions": self.skill,
                "source_atom_ids": [], "trace_requirements": [], "method": self.method,
            }]
        self.modules = {module["module_id"]: module for module in modules}
        active = [root / name for name in ("SKILL.md", "manifest.json", "action_modules.json", "typed_atoms.json", "tool_cards.json", "local_motifs.json") if (root / name).exists()]
        self.package_hash = stable_hash(active)

    def catalog(self) -> str:
        def render(description_chars: int, tool_limit: int, include_description: bool = True) -> str:
            lines = [
                "<available_skill_modules>",
                "Use activate_skill when a module matches the current task. Load at most two modules. Do not guess a module id.",
            ]
            for module in self.modules.values():
                tools = ", ".join((module.get("required_tools") or [])[:tool_limit])
                lines.extend([
                    "  <module>", f"    <id>{escape(module['module_id'])}</id>",
                    f"    <name>{escape(module.get('name', module['module_id']))}</name>",
                ])
                if include_description:
                    description = module.get("description", "")[:description_chars]
                    lines.append(f"    <description>{escape(description)}</description>")
                if tools:
                    lines.append(f"    <required_tools>{escape(tools)}</required_tools>")
                lines.append("  </module>")
            lines.append("</available_skill_modules>")
            return "\n".join(lines)

        for mode in ((320, 8, True), (160, 4, True), (80, 1, True), (0, 0, False)):
            rendered = render(*mode)
            if len(rendered) <= self.config.max_catalog_chars:
                return rendered
        raise ValueError(
            f"Even the identity-only module catalog exceeds the frozen {self.config.max_catalog_chars}-char budget"
        )

    def activate(self, module_id: str) -> dict[str, Any]:
        module = self.modules.get(module_id)
        if module is None:
            return {"ok": False, "module_id": module_id, "error": "unknown_module"}
        instructions = module.get("instructions", "")
        truncated = len(instructions) > self.config.max_module_chars
        rendered = instructions[: self.config.max_module_chars]
        return {
            "ok": True, "module_id": module_id, "name": module.get("name"),
            "instructions": rendered, "truncated": truncated,
            "required_tools": module.get("required_tools") or [],
            "source_atom_ids": module.get("source_atom_ids") or [],
            "trace_requirements": module.get("trace_requirements") or [],
            "package_hash": self.package_hash,
        }

    def describe(self) -> dict[str, Any]:
        return {
            "package_root": str(self.root), "package_hash": self.package_hash,
            "method": self.method, "domain": self.domain, "module_count": len(self.modules),
            "catalog_chars": len(self.catalog()), "config": asdict(self.config),
            "graph_traversal_enabled": False,
            "ignored_compile_time_files": [name for name in ("knowledge_graph.json", "pattern_cards.json") if (self.root / name).exists()],
            "contract": self.manifest.get("package_contract", "action_modules.v2-fallback"),
        }
