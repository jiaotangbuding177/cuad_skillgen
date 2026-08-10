import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))

from baselines.graph_evoskill_compiler import build_graph_and_patterns
from run_package_runtime import select_case_range


def _atom(ka_id, text, source, confidence=0.9):
    return {
        "ka_id": ka_id,
        "category": "Change of Control",
        "text": text,
        "interpretation": text,
        "source_contract_id": source,
        "confidence": confidence,
    }


def test_builds_typed_graph_and_pattern_cards():
    evidence = {"Change of Control": [
        _atom("KA-1", "A party may terminate upon a change of control.", "doc-a"),
        _atom("KA-2", "Upon a change of control, either party may terminate this agreement.", "doc-b"),
        _atom("KA-3", "Assignment requires prior written consent unless made to an affiliate.", "doc-c"),
    ]}
    graph, cards = build_graph_and_patterns(
        evidence, similarity_threshold=0.15, patterns_per_category=3,
    )
    node_types = {node["type"] for node in graph["nodes"]}
    edge_types = {edge["type"] for edge in graph["edges"]}
    assert {"KnowledgeAtom", "ClausePattern", "Category", "Contract"} <= node_types
    assert {"BELONGS_TO", "DERIVED_FROM", "INSTANCE_OF"} <= edge_types
    assert cards["Change of Control"]
    assert any(card["has_condition"] or card["has_exception"] for card in cards["Change of Control"])


def test_limits_atoms_and_preserves_source_diversity():
    evidence = {"Audit Rights": [
        _atom("KA-1", "Customer may inspect and audit all relevant records.", "doc-a", 1.0),
        _atom("KA-2", "Customer may inspect and audit the relevant books and records.", "doc-b", 0.95),
        _atom("KA-3", "Customer may inspect and audit relevant accounting records.", "doc-a", 0.90),
        _atom("KA-4", "Unrelated low confidence text.", "doc-c", 0.1),
    ]}
    graph, cards = build_graph_and_patterns(
        evidence, graph_ka_limit=3, similarity_threshold=0.10,
        patterns_per_category=1, examples_per_pattern=2,
    )
    atoms = [node for node in graph["nodes"] if node["type"] == "KnowledgeAtom"]
    examples = cards["Audit Rights"][0]["representative_examples"]
    assert len(atoms) == 3
    assert "KA-4" not in {node["id"] for node in atoms}
    assert len({item["source_contract_id"] for item in examples}) == 2


def test_select_case_range_returns_incremental_suffix():
    cases = ["first", "assignment_and_control", "revenue", "operational"]
    assert select_case_range(cases, start_case="assignment_and_control") == [
        "assignment_and_control", "revenue", "operational"
    ]
