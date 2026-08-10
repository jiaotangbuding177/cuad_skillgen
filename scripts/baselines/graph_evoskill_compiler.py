#!/usr/bin/env python3
"""Graph-enhanced compilation baseline built on existing EvoSkill packages.

This baseline deliberately reuses EvoSkill knowledge atoms and its security
policy.  It changes only the compilation stage: atoms are linked, clustered
into clause-pattern cards, and selected with graph-aware diversity before one
LLM call renders the final SKILL.md.
"""

import argparse
import json
import math
import os
import re
import sys
import time
from collections import Counter, defaultdict

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from common.llm_client import LLMClient
from common.loader import CUADSkillGenLoader
from common.writer import SkillOutputWriter


METHOD_NAME = "graph_evoskill_compiler"
SOURCE_METHOD = "evoskill_compiler"
TOKEN_RE = re.compile(r"[a-z][a-z0-9_-]{2,}")
STOPWORDS = {
    "the", "and", "for", "that", "this", "with", "from", "shall", "may",
    "any", "such", "under", "upon", "agreement", "party", "parties", "its",
    "their", "have", "has", "not", "are", "will", "into", "other", "each",
}
CONDITION_CUES = (" if ", " when ", " upon ", "subject to", "provided that", "in the event")
EXCEPTION_CUES = (" except ", " unless ", "notwithstanding", "other than", "excluding", "provided, however")

GENERATE_SYSTEM = """You compile a contract-review Skill from graph-derived clause-pattern cards.
Return only the complete Markdown for SKILL.md. Preserve the supplied category boundaries,
conditions, exceptions, and governance rules. Do not invent legal rules or citations.
Teach the runtime agent how to recognize semantic variants, answer conservatively, quote
verbatim evidence, and abstain when the target contract does not support a finding.

Required sections:
1. Purpose and Scope
2. Review Workflow
3. Common Clause Patterns (one subsection per category)
4. Evidence and Citation Protocol
5. Boundary and Abstention Rules

For every pattern, explain its invariant meaning, variation cues, conditions/exceptions,
and include the supplied representative phrasings. Treat examples as recognition aids,
never as evidence for a target contract."""


def _tokens(text):
    return {t for t in TOKEN_RE.findall((text or "").lower()) if t not in STOPWORDS}


def _jaccard(left, right):
    union = left | right
    return len(left & right) / len(union) if union else 0.0


def _has_cue(text, cues):
    padded = " " + (text or "").lower() + " "
    return any(cue in padded for cue in cues)


def _slug(text):
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")[:32] or "category"


def _prepare_atoms(evidence_index, graph_ka_limit):
    prepared = {}
    for category, raw_items in evidence_index.items():
        if not isinstance(raw_items, list):
            continue
        valid = [item for item in raw_items if item.get("text") and item.get("ka_id")]
        valid.sort(key=lambda item: (-float(item.get("confidence", 0.0)), item["ka_id"]))
        prepared[category] = valid[:graph_ka_limit]
    return prepared


def _similarity_edges(items, threshold, max_neighbors):
    """Create sparse within-category VARIANT_OF edges using an inverted index."""
    token_sets = [_tokens(item.get("text", "") + " " + item.get("interpretation", "")) for item in items]
    postings = defaultdict(list)
    for index, tokens in enumerate(token_sets):
        for token in tokens:
            postings[token].append(index)

    edges = []
    for left, tokens in enumerate(token_sets):
        candidates = Counter()
        for token in tokens:
            if len(postings[token]) <= 80:
                for right in postings[token]:
                    if right > left:
                        candidates[right] += 1
        scored = []
        for right, overlap in candidates.items():
            if overlap < 2:
                continue
            score = _jaccard(tokens, token_sets[right])
            if score >= threshold:
                scored.append((score, right))
        for score, right in sorted(scored, reverse=True)[:max_neighbors]:
            edges.append({
                "source": items[left]["ka_id"], "target": items[right]["ka_id"],
                "type": "VARIANT_OF", "weight": round(score, 4),
            })
    return edges


def _representatives(members, degrees, count=3):
    """Centrality/confidence ranking followed by source-diverse MMR selection."""
    chosen, used_sources = [], set()
    token_sets = {item["ka_id"]: _tokens(item.get("text", "")) for item in members}
    while members and len(chosen) < count:
        best = None
        best_score = -1e9
        for item in members:
            base = 0.55 * float(item.get("confidence", 0.0)) + 0.25 * math.log1p(degrees[item["ka_id"]])
            diversity = 0.15 if item.get("source_contract_id") not in used_sources else 0.0
            redundancy = max((_jaccard(token_sets[item["ka_id"]], token_sets[x["ka_id"]]) for x in chosen), default=0.0)
            score = base + diversity - 0.20 * redundancy
            if score > best_score:
                best, best_score = item, score
        chosen.append(best)
        used_sources.add(best.get("source_contract_id"))
        members = [item for item in members if item["ka_id"] != best["ka_id"]]
    return chosen


def _center_constrained_clusters(items, threshold):
    """Greedy star clustering; every member must match its center directly.

    Connected components over similarity edges suffer from chaining on legal
    boilerplate.  The center constraint keeps patterns locally coherent while
    remaining deterministic and auditable.
    """
    clusters = []
    centers = []
    center_tokens = []
    for item in items:  # already confidence-sorted by _prepare_atoms
        tokens = _tokens(item.get("text", "") + " " + item.get("interpretation", ""))
        scored = [(_jaccard(tokens, known), index) for index, known in enumerate(center_tokens)]
        score, target = max(scored, default=(0.0, -1))
        if score >= threshold:
            clusters[target].append(item)
        else:
            centers.append(item)
            center_tokens.append(tokens)
            clusters.append([item])
    return clusters


def build_graph_and_patterns(evidence_index, graph_ka_limit=200, similarity_threshold=0.24,
                             max_neighbors=6, patterns_per_category=6,
                             examples_per_pattern=3):
    atoms_by_category = _prepare_atoms(evidence_index, graph_ka_limit)
    nodes, edges, pattern_cards = [], [], {}
    all_contracts = set()

    for category, items in atoms_by_category.items():
        category_id = "CAT-" + _slug(category)
        nodes.append({"id": category_id, "type": "Category", "label": category})
        for item in items:
            contract_id = item.get("source_contract_id", "unknown")
            all_contracts.add(contract_id)
            nodes.append({
                "id": item["ka_id"], "type": "KnowledgeAtom", "category": category,
                "confidence": float(item.get("confidence", 0.0)),
                "has_condition": _has_cue(item.get("text"), CONDITION_CUES),
                "has_exception": _has_cue(item.get("text"), EXCEPTION_CUES),
            })
            edges.extend([
                {"source": item["ka_id"], "target": category_id, "type": "BELONGS_TO", "weight": 1.0},
                {"source": item["ka_id"], "target": "DOC-" + _slug(contract_id), "type": "DERIVED_FROM", "weight": 1.0},
            ])

        similarity_edges = _similarity_edges(items, similarity_threshold, max_neighbors)
        edges.extend(similarity_edges)
        degrees = Counter()
        for edge in similarity_edges:
            degrees[edge["source"]] += 1
            degrees[edge["target"]] += 1

        ranked = []
        for members in _center_constrained_clusters(items, similarity_threshold):
            sources = {item.get("source_contract_id") for item in members}
            avg_conf = sum(float(item.get("confidence", 0.0)) for item in members) / len(members)
            centrality = sum(degrees[item["ka_id"]] for item in members) / len(members)
            coverage = math.log1p(len(sources))
            cue_bonus = 0.15 * any(_has_cue(item.get("text"), CONDITION_CUES + EXCEPTION_CUES) for item in members)
            ranked.append((0.45 * avg_conf + 0.30 * coverage + 0.20 * math.log1p(centrality) + cue_bonus, members))
        ranked.sort(key=lambda pair: (-pair[0], -len(pair[1]), pair[1][0]["ka_id"]))

        cards = []
        for ordinal, (score, members) in enumerate(ranked[:patterns_per_category], 1):
            pattern_id = f"PAT-{_slug(category)}-{ordinal:02d}"
            reps = _representatives(list(members), degrees, examples_per_pattern)
            keywords = Counter(token for item in members for token in _tokens(item.get("text", "")))
            card = {
                "pattern_id": pattern_id,
                "category": category,
                "member_count": len(members),
                "source_contract_count": len({item.get("source_contract_id") for item in members}),
                "selection_score": round(score, 4),
                "variation_cues": [token for token, _ in keywords.most_common(10)],
                "has_condition": any(_has_cue(item.get("text"), CONDITION_CUES) for item in members),
                "has_exception": any(_has_cue(item.get("text"), EXCEPTION_CUES) for item in members),
                "representative_examples": [{
                    "ka_id": item["ka_id"], "text": item["text"],
                    "interpretation": item.get("interpretation", ""),
                    "source_contract_id": item.get("source_contract_id"),
                } for item in reps],
            }
            cards.append(card)
            nodes.append({"id": pattern_id, "type": "ClausePattern", "category": category,
                          "member_count": len(members), "selection_score": round(score, 4)})
            for item in members:
                edges.append({"source": item["ka_id"], "target": pattern_id,
                              "type": "INSTANCE_OF", "weight": 1.0})
        pattern_cards[category] = cards

    for contract_id in sorted(all_contracts):
        nodes.append({"id": "DOC-" + _slug(contract_id), "type": "Contract", "label": contract_id})
    type_counts = Counter(node["type"] for node in nodes)
    edge_counts = Counter(edge["type"] for edge in edges)
    graph = {
        "schema_version": "gesc-1.0", "source_method": SOURCE_METHOD,
        "nodes": nodes, "edges": edges,
        "statistics": {"node_types": dict(type_counts), "edge_types": dict(edge_counts)},
    }
    return graph, pattern_cards


def _read_json(path):
    with open(path, "r", encoding="utf-8") as handle:
        return json.load(handle)


def _write_json(path, value):
    with open(path, "w", encoding="utf-8") as handle:
        json.dump(value, handle, indent=2, ensure_ascii=False)


def compile_case(loader, case_id, llm, args):
    writer = SkillOutputWriter(args.results_root, METHOD_NAME, case_id)
    if writer.output_exists() and not args.overwrite:
        print(f"  [{case_id}] exists; skipped")
        return {"skipped": True}
    source_dir = os.path.join(args.results_root, args.source_method, case_id)
    evidence_path = os.path.join(source_dir, "evidence_index.json")
    policy_path = os.path.join(source_dir, "security_policy.json")
    if not os.path.exists(evidence_path):
        raise FileNotFoundError(f"Missing source EvoSkill evidence index: {evidence_path}")
    evidence_index = _read_json(evidence_path)
    policy = _read_json(policy_path) if os.path.exists(policy_path) else {}
    graph, cards = build_graph_and_patterns(
        evidence_index, args.graph_ka_limit, args.similarity_threshold,
        args.max_neighbors, args.patterns_per_category, args.examples_per_pattern,
    )
    if args.dry_run:
        print(f"  [{case_id}] nodes={len(graph['nodes'])} edges={len(graph['edges'])} "
              f"patterns={sum(map(len, cards.values()))}")
        return {"dry_run": True}

    case_json = loader.load_case_json(case_id)
    prompt_payload = {
        "case_id": case_id,
        "domain": case_json.get("domain"),
        "task_description": case_json.get("task_description"),
        "graph_pattern_cards": cards,
        "security_policy": policy,
    }
    start = time.time()
    skill_md, call_usage = llm.call(GENERATE_SYSTEM, json.dumps(prompt_payload, ensure_ascii=False),
                                    temperature=0.2, max_tokens=7000)
    duration = time.time() - start
    manifest = {
        "method": METHOD_NAME, "case_id": case_id, "model": llm.model,
        "source_method": args.source_method, "compilation_protocol": "gesc-1.0",
        "graph_config": {
            "graph_ka_limit": args.graph_ka_limit,
            "similarity_threshold": args.similarity_threshold,
            "max_neighbors": args.max_neighbors,
            "patterns_per_category": args.patterns_per_category,
            "examples_per_pattern": args.examples_per_pattern,
        },
        "graph_statistics": graph["statistics"], "usage": call_usage,
        "duration_seconds": round(duration, 3),
    }
    writer.write_all(skill_md, manifest, evidence_index, policy, {
        "system_prompt": GENERATE_SYSTEM, "pattern_cards": cards,
        "response": skill_md, "usage": call_usage,
    })
    _write_json(os.path.join(writer.output_dir, "knowledge_graph.json"), graph)
    _write_json(os.path.join(writer.output_dir, "pattern_cards.json"), cards)
    print(f"  [{case_id}] compiled patterns={sum(map(len, cards.values()))} tokens={call_usage.get('total_tokens', 0)}")
    return {"skipped": False, "patterns": sum(map(len, cards.values()))}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data-root", default="data/cuad_skillgen")
    parser.add_argument("--results-root", default="results/skillgen/generated")
    parser.add_argument("--source-method", default=SOURCE_METHOD)
    parser.add_argument("--model", default="ecnu-plus")
    parser.add_argument("--case-id")
    parser.add_argument("--graph-ka-limit", type=int, default=200)
    parser.add_argument("--similarity-threshold", type=float, default=0.24)
    parser.add_argument("--max-neighbors", type=int, default=6)
    parser.add_argument("--patterns-per-category", type=int, default=6)
    parser.add_argument("--examples-per-pattern", type=int, default=3)
    parser.add_argument("--overwrite", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    loader = CUADSkillGenLoader(args.data_root)
    llm = LLMClient(model=args.model)
    case_ids = [args.case_id] if args.case_id else loader.get_all_case_ids()
    print(f"=== {METHOD_NAME} (source={args.source_method}) ===")
    for case_id in case_ids:
        compile_case(loader, case_id, llm, args)


if __name__ == "__main__":
    main()
