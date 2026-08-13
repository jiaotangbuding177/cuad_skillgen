from __future__ import annotations

import hashlib
import json
import re
from collections import Counter, defaultdict
from typing import Any, Iterable


WORD_RE = re.compile(r"[a-zA-Z0-9_]+")
SENTENCE_RE = re.compile(r"(?<=[.!?])\s+")
CONSEQUENTIAL = re.compile(
    r"cancel|modify|change|update|delete|return|exchange|book|reserve|pay|send|toggle|set|reset|reboot|grant|connect|disconnect|transfer",
    re.I,
)
OBSERVATION = re.compile(r"get|find|check|list|search|calculate|status|details|can_", re.I)
ROUTING_STOPWORDS = {
    "get", "set", "toggle", "enable", "disable", "check", "find", "list",
    "search", "update", "modify", "change", "run", "tool", "mode", "status",
    "details", "user", "customer", "data", "information",
}


def words(text: str) -> set[str]:
    return {token.lower() for token in WORD_RE.findall(text or "") if len(token) > 2}


def stable_id(prefix: str, *parts: str) -> str:
    digest = hashlib.sha256("\x1f".join(parts).encode("utf-8")).hexdigest()[:10]
    return f"{prefix}-{digest}"


def split_sentences(text: str) -> list[str]:
    # Tool docstrings and policy Markdown contain hard-wrapped prose.  Treating
    # every newline as a sentence boundary produced fragments such as
    # "If the order is delivered," and "it cannot be cancelled." as unrelated
    # atoms. Preserve list boundaries, then collapse prose wrapping.
    normalized = (text or "").replace("\r\n", "\n").replace("\r", "\n")
    normalized = re.sub(r"\n\s*(?:[-*]|\d+[.)])\s+", ". ", normalized)
    normalized = re.sub(r"\s+", " ", normalized).strip()
    return [sentence.strip(" -\t") for sentence in SENTENCE_RE.split(normalized) if len(sentence.strip()) >= 18]


def classify_atom(sentence: str) -> str:
    lower = sentence.lower()
    if re.search(r"transfer|human agent|escalat", lower):
        return "escalation"
    if re.search(r"confirm|confirmation|yes/no|consent", lower):
        return "confirmation"
    if re.search(r"must not|cannot|can not|never|prohibited|forbidden|only if|at most", lower):
        return "prohibition"
    if re.search(r"requestor|belongs to the user|user tool|assistant tool|user must", lower):
        return "actor_constraint"
    if re.search(r"after|then verify|verify|ensure.*(?:updated|changed|completed)|check.*after", lower):
        return "postcondition"
    if re.search(r"if .*fail|otherwise|exception|unless|in case", lower):
        return "exception"
    if re.search(r"before|require|required|must|only when|only after|if ", lower):
        return "precondition"
    if re.search(r"parameter|argument|provide|collect|need .*information", lower):
        return "required_input"
    if re.search(r"tell|inform|explain|communicat|say to the user", lower):
        return "communication_requirement"
    if re.search(r"allow|may |can ", lower):
        return "permission"
    return "fact"


def build_typed_atoms(data: dict[str, Any]) -> list[dict[str, Any]]:
    atoms: list[dict[str, Any]] = []
    for section in data["sections"]:
        sentences = split_sentences(section.get("text", "")) or [section.get("text", "").strip()]
        for sentence in sentences:
            if not sentence:
                continue
            atom_id = stable_id("ATOM", section.get("source", ""), section.get("title", ""), sentence)
            atoms.append({
                "atom_id": atom_id,
                "type": classify_atom(sentence),
                "subject": section.get("title", "policy"),
                "text": sentence,
                "source": {
                    "file": section.get("source"),
                    "title": section.get("title"),
                    "line_start": section.get("line_start"),
                    "line_end": section.get("line_end"),
                },
                "origin": "policy",
            })
    for tool in data["tools"]:
        tool_name = tool["name"]
        actor_id = stable_id("ATOM", tool.get("source", ""), tool_name, "actor")
        atoms.append({
            "atom_id": actor_id, "type": "actor_constraint", "subject": tool_name,
            "text": f"The {tool_name} tool is owned by the {tool.get('requestor', 'assistant')} actor.",
            "object": tool.get("requestor", "assistant"),
            "source": {"file": tool.get("source"), "title": tool_name}, "origin": "tool_schema",
        })
        for parameter in tool.get("parameters") or []:
            atoms.append({
                "atom_id": stable_id("ATOM", tool_name, "parameter", str(parameter)),
                "type": "required_input", "subject": tool_name,
                "text": f"The {tool_name} tool requires the {parameter} argument.",
                "object": parameter, "source": {"file": tool.get("source"), "title": tool_name},
                "origin": "tool_schema",
            })
        for sentence in split_sentences(tool.get("description", "")):
            atoms.append({
                "atom_id": stable_id("ATOM", tool_name, sentence),
                "type": classify_atom(sentence), "subject": tool_name, "text": sentence,
                "source": {"file": tool.get("source"), "title": tool_name}, "origin": "tool_description",
            })
    unique = {atom["atom_id"]: atom for atom in atoms}
    return sorted(unique.values(), key=lambda item: item["atom_id"])


def atom_tool_score(atom: dict[str, Any], tool: dict[str, Any]) -> float:
    name = tool["name"].lower()
    text = f"{atom.get('subject', '')} {atom.get('text', '')}".lower()
    if atom.get("subject", "").lower() == name or name in text:
        return 1.0
    name_terms = words(name.replace("_", " ")) - ROUTING_STOPWORDS
    if not name_terms:
        name_terms = words(name.replace("_", " "))
    atom_terms = words(text)
    overlap = name_terms & atom_terms
    if not name_terms or not overlap:
        return 0.0
    name_coverage = len(overlap) / len(name_terms)
    description_terms = words(tool.get("description", "")) - ROUTING_STOPWORDS
    union = description_terms | atom_terms
    description_score = len(description_terms & atom_terms) / len(union) if union else 0.0
    return 0.85 * name_coverage + 0.15 * description_score


def build_tool_cards(data: dict[str, Any], atoms: list[dict[str, Any]]) -> list[dict[str, Any]]:
    cards = []
    for tool in data["tools"]:
        # Schema and docstring atoms are authoritative only for their declared
        # tool. Lexical cross-binding between similarly named tools (for
        # example several address modifiers) injects contradictory parameters
        # and actor ownership. Only policy atoms may be linked lexically.
        candidates = [
            atom for atom in atoms
            if atom.get("origin") == "policy" or atom.get("subject", "").lower() == tool["name"].lower()
        ]
        scored = [(atom_tool_score(atom, tool), atom) for atom in candidates]
        bound = [atom for score, atom in sorted(scored, key=lambda pair: (-pair[0], pair[1]["atom_id"])) if score >= 0.45]
        direct = [atom for atom in atoms if atom.get("subject", "").lower() == tool["name"].lower()]
        selected_atoms = list({atom["atom_id"]: atom for atom in [*direct, *bound[:12]]}.values())
        by_type: dict[str, list[str]] = defaultdict(list)
        for atom in selected_atoms:
            by_type[atom["type"]].append(atom["atom_id"])
        cards.append({
            "tool": tool["name"], "actor": tool.get("requestor", "assistant"),
            "description": tool.get("description", ""), "parameters": tool.get("parameters") or [],
            "consequential": bool(CONSEQUENTIAL.search(tool["name"])),
            "observation": bool(OBSERVATION.search(tool["name"])),
            # Preserve direct atoms first so the downstream module budget does
            # not discard the primary tool's own schema in favor of lexical
            # policy matches.
            "bound_atom_ids": [atom["atom_id"] for atom in selected_atoms],
            "precondition_atom_ids": sorted(by_type["precondition"] + by_type["required_input"] + by_type["confirmation"]),
            "prohibition_atom_ids": sorted(by_type["prohibition"]),
            "verification_atom_ids": sorted(by_type["postcondition"]),
            "exception_atom_ids": sorted(by_type["exception"] + by_type["escalation"]),
            "source": tool.get("source"),
        })
    return cards


def build_local_motifs(tasks: list[dict[str, Any]]) -> list[dict[str, Any]]:
    edge_counts: Counter[tuple[str, str]] = Counter()
    outgoing: Counter[str] = Counter()
    for task in tasks:
        sequence = [f"{action.get('requestor', 'assistant')}:{action.get('name')}" for action in task.get("gold", {}).get("reference_actions", [])]
        for left, right in zip(sequence, sequence[1:]):
            edge_counts[(left, right)] += 1
            outgoing[left] += 1
    motifs = []
    for (left, right), support in edge_counts.items():
        confidence = support / outgoing[left] if outgoing[left] else 0.0
        # Single observations are demonstrations, not reusable motifs. Self
        # loops are usually retries or repeated confirmations and must not be
        # compiled as recommended SOP structure.
        if left == right or support < 2:
            continue
        motifs.append({
            "motif_id": stable_id("MOTIF", left, right), "type": "PRECEDES",
            "before_actor": left.split(":", 1)[0], "before_tool": left.split(":", 1)[1],
            "after_actor": right.split(":", 1)[0], "after_tool": right.split(":", 1)[1],
            "support": support, "confidence": round(confidence, 4),
            "source": "tasks/train.jsonl",
            "warning": "A local training motif is a soft ordering hint and never overrides policy.",
        })
    return sorted(motifs, key=lambda item: (-item["support"], -item["confidence"], item["motif_id"]))


def module_description(card: dict[str, Any]) -> str:
    readable = card["tool"].replace("_", " ")
    actor = card["actor"]
    return f"Use for tasks involving {readable}; the declared tool actor is {actor}."


def split_markdown_modules(method: str, domain: str, skill_text: str) -> list[dict[str, Any]]:
    def chunks(text: str, limit: int = 8000) -> list[str]:
        paragraphs = [part.strip() for part in re.split(r"\n\s*\n", text) if part.strip()]
        output: list[str] = []
        current = ""
        for paragraph in paragraphs:
            pieces = [paragraph[i:i + limit] for i in range(0, len(paragraph), limit)]
            for piece in pieces:
                candidate = f"{current}\n\n{piece}".strip()
                if current and len(candidate) > limit:
                    output.append(current)
                    current = piece
                else:
                    current = candidate
        if current:
            output.append(current)
        return output or [text[:limit]]

    modules = []
    heading = "Overview"
    body: list[str] = []
    section_index = 0
    for line in skill_text.splitlines() + ["# __END__"]:
        if line.startswith("#"):
            text = "\n".join(body).strip()
            if text:
                section_chunks = chunks(text)
                for chunk_index, chunk in enumerate(section_chunks, 1):
                    section_index += 1
                    module_id = f"{domain}.{method}.section_{section_index:03d}"
                    suffix = f" (part {chunk_index})" if len(section_chunks) > 1 else ""
                    modules.append({
                        "module_id": module_id, "name": heading + suffix,
                        "description": f"{method.replace('_', ' ')} guidance section about {heading}{suffix}.",
                        "required_tools": [], "instructions": f"# {heading}{suffix}\n\n{chunk}",
                        "source_atom_ids": [], "trace_requirements": [], "method": method,
                    })
            heading = line.lstrip("#").strip()
            body = []
        else:
            body.append(line)
    return modules


def build_unbound_atom_modules(method: str, domain: str, atoms: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Expose typed atoms by type while deliberately removing tool binding."""

    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for atom in atoms:
        grouped[atom["type"]].append(atom)
    modules: list[dict[str, Any]] = []
    for atom_type in sorted(grouped):
        chunks: list[list[dict[str, Any]]] = []
        current: list[dict[str, Any]] = []
        current_chars = 0
        for atom in grouped[atom_type]:
            line_chars = len(atom["text"]) + len(atom["atom_id"]) + 16
            if current and current_chars + line_chars > 7000:
                chunks.append(current)
                current, current_chars = [], 0
            current.append(atom)
            current_chars += line_chars
        if current:
            chunks.append(current)
        for index, chunk in enumerate(chunks, 1):
            module_id = f"{domain}.{method}.{atom_type}.{index:02d}"
            lines = [f"# {atom_type.replace('_', ' ').title()} atoms", ""]
            lines.extend(f"- {atom['text']} [{atom['atom_id']}]" for atom in chunk)
            lines.extend(["", "These atoms are intentionally not bound to a tool in this ablation."])
            modules.append({
                "module_id": module_id,
                "name": f"{atom_type.replace('_', ' ').title()} Atoms {index}",
                "description": f"Typed {atom_type.replace('_', ' ')} knowledge without direct tool binding.",
                "required_tools": [],
                "instructions": "\n".join(lines),
                "source_atom_ids": [atom["atom_id"] for atom in chunk],
                "trace_requirements": [],
                "method": method,
            })
    return modules


def _neighbor_tools(tool: str, motifs: list[dict[str, Any]]) -> tuple[list[str], list[str], list[dict[str, Any]]]:
    before, after, edges = [], [], []
    for motif in motifs:
        if motif["after_tool"] == tool and (
            OBSERVATION.search(motif["before_tool"]) or motif["confidence"] >= 0.4
        ):
            before.append(motif["before_tool"])
            edges.append(motif)
        if motif["before_tool"] == tool and (
            OBSERVATION.search(motif["after_tool"]) or motif["confidence"] >= 0.4
        ):
            after.append(motif["after_tool"])
            edges.append(motif)
    return list(dict.fromkeys(before))[:3], list(dict.fromkeys(after))[:3], list({edge["motif_id"]: edge for edge in edges}.values())[:6]


def build_action_modules(
    method: str,
    domain: str,
    skill_text: str,
    data: dict[str, Any],
    atoms: list[dict[str, Any]],
    cards: list[dict[str, Any]],
    motifs: list[dict[str, Any]],
    graph_expansion: dict[str, list[str]] | None = None,
) -> list[dict[str, Any]]:
    if method == "no_skill":
        return []
    if method == "a2sc_no_tool_binding":
        return build_unbound_atom_modules(method, domain, atoms)
    # Prompt/document baselines are adapted to the progressive runtime by
    # exposing chunks of *their own* generated SKILL.md.  In particular, the
    # two v1 EvoSkill methods must not inherit A2SC's typed atom-to-tool
    # compiler, otherwise the comparison would silently give the baselines the
    # treatment's main mechanism.
    if method in {
        "native_prompt_skill", "schema_prompt_skill", "summary2skill",
        "evoskill_compiler", "graph_evoskill_compiler",
    }:
        return split_markdown_modules(method, domain, skill_text)
    atom_map = {atom["atom_id"]: atom for atom in atoms}
    modules = []
    selected_cards = cards
    if method in {"raw_policy_rag", "a2sc_no_typed_atoms"}:
        selected_cards = []
        for index, section in enumerate(data["sections"], 1):
            related = [] if method == "a2sc_no_typed_atoms" else [
                atom["atom_id"] for atom in atoms
                if atom.get("source", {}).get("title") == section.get("title")
            ]
            modules.append({
                "module_id": f"{domain}.policy_{index:03d}", "name": section["title"],
                "description": f"Original policy section about {section['title']}.",
                "required_tools": [], "instructions": section["text"],
                "source_atom_ids": related, "trace_requirements": [], "method": method,
            })
    for card in selected_cards:
        before, after, edges = _neighbor_tools(card["tool"], motifs)
        source_ids = list(card["bound_atom_ids"])
        if graph_expansion:
            for atom_id in list(source_ids):
                source_ids.extend(graph_expansion.get(atom_id, []))
        source_ids = list(dict.fromkeys(source_ids))[:24]
        relevant_atoms = [atom_map[atom_id] for atom_id in source_ids if atom_id in atom_map]
        if method == "tool_schema_compiler":
            relevant_atoms = [atom for atom in relevant_atoms if atom.get("origin") == "tool_schema"]
            source_ids = [atom["atom_id"] for atom in relevant_atoms]
            before, after, edges = [], [], []
        elif method == "document_tool_maker":
            relevant_atoms = [atom for atom in relevant_atoms if atom.get("origin") in {"tool_schema", "tool_description"}]
            source_ids = [atom["atom_id"] for atom in relevant_atoms]
            before, after, edges = [], [], []
        elif method not in {"a2sc", "g_a2sc"}:
            before, after, edges = [], [], []
        trace_requirements = [{
            "requirement_id": atom["atom_id"], "kind": "actor", "tool": card["tool"], "actor": card["actor"]
        } for atom in relevant_atoms if (
            atom["type"] == "actor_constraint"
            and atom.get("origin") == "tool_schema"
            and atom.get("subject", "").lower() == card["tool"].lower()
        )]
        trace_requirements.extend({
            "requirement_id": edge["motif_id"], "kind": "ordering",
            "before_tool": edge["before_tool"], "after_tool": edge["after_tool"],
            "soft": True,
        } for edge in edges)
        evidence_before = [tool for tool in before if OBSERVATION.search(tool)]
        verification_after = [tool for tool in after if OBSERVATION.search(tool)]
        if card["consequential"]:
            trace_requirements.extend({
                "requirement_id": stable_id("REQ", "precondition", tool, card["tool"]),
                "kind": "precondition", "evidence_tool": tool, "action_tool": card["tool"],
                "soft": True,
            } for tool in evidence_before)
            trace_requirements.extend({
                "requirement_id": stable_id("REQ", "verification", card["tool"], tool),
                "kind": "verification", "action_tool": card["tool"], "verification_tool": tool,
                "soft": True,
            } for tool in verification_after)
        instructions = render_module_instructions(card, relevant_atoms, evidence_before, after)
        modules.append({
            "module_id": f"{domain}.{card['tool']}", "name": card["tool"].replace("_", " ").title(),
            "description": module_description(card),
            # This field is a routing/audit declaration, not a hard tool
            # allowlist. Keep the primary action plus evidence/verification
            # reads; unrelated neighboring writes remain only soft hints.
            "required_tools": list(dict.fromkeys([*evidence_before, card["tool"], *verification_after])),
            "primary_tool": card["tool"], "actor": card["actor"], "instructions": instructions,
            "source_atom_ids": source_ids, "precondition_atom_ids": card["precondition_atom_ids"],
            "prohibition_atom_ids": card["prohibition_atom_ids"], "verification_atom_ids": card["verification_atom_ids"],
            "exception_atom_ids": card["exception_atom_ids"], "trace_requirements": trace_requirements,
            "method": method,
        })
    return sorted(modules, key=lambda item: item["module_id"])


def render_module_instructions(card: dict[str, Any], atoms: list[dict[str, Any]], before: list[str], after: list[str]) -> str:
    groups: dict[str, list[str]] = defaultdict(list)
    for atom in atoms:
        groups[atom["type"]].append(f"{atom['text']} [{atom['atom_id']}]")
    lines = [
        f"# {card['tool'].replace('_', ' ').title()}",
        f"Actor: `{card['actor']}`", f"Parameters: {', '.join(card['parameters']) or 'none'}",
        f"Purpose: {card['description']}",
    ]
    if before:
        lines.append("Observe/check before: " + ", ".join(before))
    for title, keys in [
        ("Preconditions", ["precondition", "required_input", "confirmation"]),
        ("Prohibitions", ["prohibition"]), ("Actor constraints", ["actor_constraint"]),
        ("Exceptions", ["exception", "escalation"]),
        ("Communication", ["communication_requirement"]), ("Verification", ["postcondition"]),
    ]:
        values = [value for key in keys for value in groups[key]]
        if values:
            lines.append(f"## {title}\n" + "\n".join(f"- {value}" for value in values[:8]))
    if after:
        lines.append("## Soft local continuations\n" + "\n".join(f"- Consider `{tool}` after this action when relevant." for tool in after))
    lines.append("Policy atoms override training-derived ordering hints. Use only tools exposed by the environment.")
    return "\n\n".join(lines)


def build_semantic_graph(atoms: list[dict[str, Any]], cards: list[dict[str, Any]]) -> tuple[dict[str, Any], dict[str, list[str]]]:
    nodes = [{"id": atom["atom_id"], "type": atom["type"], "label": atom["text"][:160]} for atom in atoms]
    nodes.extend({"id": f"TOOL:{card['tool']}", "type": "tool", "label": card["tool"]} for card in cards)
    edges: list[dict[str, Any]] = []
    expansion: dict[str, list[str]] = defaultdict(list)
    for card in cards:
        for atom_id in card["bound_atom_ids"]:
            edges.append({"source": atom_id, "target": f"TOOL:{card['tool']}", "type": "GROUNDS_TOOL"})
    for index, left in enumerate(atoms):
        if left.get("origin") != "policy" or left["type"] not in {
            "precondition", "prohibition", "exception", "postcondition",
            "confirmation", "escalation", "communication_requirement", "permission",
        }:
            continue
        left_terms = words(left["text"])
        for right in atoms[index + 1:]:
            if right.get("origin") != "policy":
                continue
            if left["type"] != right["type"]:
                continue
            right_terms = words(right["text"])
            union = left_terms | right_terms
            score = len(left_terms & right_terms) / len(union) if union else 0.0
            if score < 0.28:
                continue
            edge_type = "EXCEPTION_TO" if left["type"] in {"exception", "prohibition"} else "SAME_INTENT_VARIANT"
            edges.append({"source": left["atom_id"], "target": right["atom_id"], "type": edge_type, "score": round(score, 4)})
            expansion[left["atom_id"]].append(right["atom_id"])
            expansion[right["atom_id"]].append(left["atom_id"])
    return {"nodes": nodes, "edges": edges}, {key: value[:4] for key, value in expansion.items()}


def render_catalog_skill(method: str, domain: str, modules: list[dict[str, Any]]) -> str:
    lines = [
        f"# {domain.replace('_', ' ').title()} Skill Catalog",
        f"> Method: `{method}`. Full module instructions are loaded on demand by the runtime.",
        "## Modules",
    ]
    if not modules:
        lines.append("- No domain skill modules. This is the no-Skill control.")
    for module in modules:
        tools = ", ".join(module.get("required_tools") or []) or "none"
        lines.append(f"- `{module['module_id']}`: {module['description']} Tools: {tools}.")
    return "\n\n".join(lines) + "\n"


def package_contract_hash(modules: Iterable[dict[str, Any]]) -> str:
    payload = json.dumps(list(modules), sort_keys=True, ensure_ascii=False, separators=(",", ":"))
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()
