from __future__ import annotations

import argparse
import json
from pathlib import Path

from common import DOMAINS, ROOT, read_json, write_json
from runtime.package_runtime import ProgressiveConfig, ProgressiveSkillPackage


def audit_package(root: Path, method: str, domain: str, config: ProgressiveConfig) -> dict:
    package = ProgressiveSkillPackage(root, domain, config)
    tools = read_json(ROOT / "data" / "processed" / domain / "documents" / "tool_catalog.json")["tools"]
    valid_tools = {tool["name"] for tool in tools}
    atom_ids = {atom["atom_id"] for atom in read_json(root / "typed_atoms.json").get("atoms", [])}
    atom_map = {atom["atom_id"]: atom for atom in read_json(root / "typed_atoms.json").get("atoms", [])}
    tool_cards = read_json(root / "tool_cards.json").get("tools", [])
    motifs = read_json(root / "local_motifs.json").get("motifs", [])
    module_ids = list(package.modules)
    errors: list[str] = []
    if len(module_ids) != len(set(module_ids)):
        errors.append("duplicate_module_ids")
    for card in tool_cards:
        for atom_id in card.get("bound_atom_ids") or []:
            atom = atom_map.get(atom_id)
            if atom and atom.get("origin") in {"tool_schema", "tool_description"} and atom.get("subject") != card["tool"]:
                errors.append(f"{card['tool']}:cross_tool_schema_binding={atom_id}")
    for motif in motifs:
        if motif.get("support", 0) < 2:
            errors.append(f"{motif.get('motif_id')}:unsupported_singleton_motif")
        if motif.get("before_tool") == motif.get("after_tool"):
            errors.append(f"{motif.get('motif_id')}:self_loop_motif")
    for module_id, module in package.modules.items():
        unknown_tools = sorted(set(module.get("required_tools") or []) - valid_tools)
        if unknown_tools:
            errors.append(f"{module_id}:unknown_tools={unknown_tools}")
        unknown_atoms = sorted(set(module.get("source_atom_ids") or []) - atom_ids)
        if unknown_atoms:
            errors.append(f"{module_id}:unknown_atoms={unknown_atoms[:5]}")
        if len(module.get("instructions", "")) > config.max_module_chars:
            errors.append(f"{module_id}:module_over_budget")
        for requirement in module.get("trace_requirements") or []:
            for key in ("tool", "before_tool", "after_tool"):
                if requirement.get(key) and requirement[key] not in valid_tools:
                    errors.append(f"{module_id}:unknown_trace_tool={requirement[key]}")
        if method in {"a2sc", "g_a2sc", "a2sc_no_local_motifs"} and not module.get("primary_tool"):
            errors.append(f"{module_id}:missing_primary_tool")
        if method in {"a2sc", "g_a2sc", "a2sc_no_local_motifs"}:
            actor_requirements = [
                requirement for requirement in module.get("trace_requirements") or []
                if requirement.get("kind") == "actor"
            ]
            if len(actor_requirements) != 1:
                errors.append(f"{module_id}:actor_requirement_count={len(actor_requirements)}")
        if method in {"evoskill_compiler", "graph_evoskill_compiler"} and module.get("primary_tool"):
            errors.append(f"{module_id}:v1_baseline_inherits_a2sc_tool_binding")
        if method == "a2sc_no_typed_atoms" and module.get("source_atom_ids"):
            errors.append(f"{module_id}:typed_atoms_not_removed")
        if method == "a2sc_no_tool_binding" and (module.get("required_tools") or module.get("primary_tool")):
            errors.append(f"{module_id}:tool_binding_not_removed")
        if method == "a2sc_no_local_motifs" and any(
            requirement.get("kind") in {"ordering", "precondition", "verification"}
            for requirement in module.get("trace_requirements") or []
        ):
            errors.append(f"{module_id}:local_motif_trace_not_removed")
    if package.describe()["graph_traversal_enabled"]:
        errors.append("runtime_graph_traversal_enabled")
    return {
        "method": method, "domain": domain, "ok": not errors, "errors": errors,
        "module_count": len(package.modules), "catalog_chars": len(package.catalog()),
        "source_atom_coverage": (
            len({atom for module in package.modules.values() for atom in module.get("source_atom_ids") or []}) / len(atom_ids)
            if atom_ids else None
        ),
        "ignored_compile_time_files": package.describe()["ignored_compile_time_files"],
    }


def aligned_a2sc(domain: str) -> dict:
    flat = read_json(ROOT / "skills" / "a2sc" / domain / "action_modules.json").get("modules", [])
    graph = read_json(ROOT / "skills" / "g_a2sc" / domain / "action_modules.json").get("modules", [])
    flat_map = {module["module_id"]: module for module in flat}
    graph_map = {module["module_id"]: module for module in graph}
    same_ids = set(flat_map) == set(graph_map)
    same_primary_tools = same_ids and all(
        flat_map[key].get("primary_tool") == graph_map[key].get("primary_tool") for key in flat_map
    )
    same_required_tools = same_ids and all(
        flat_map[key].get("required_tools") == graph_map[key].get("required_tools") for key in flat_map
    )
    graph_has_expansion = any(
        set(graph_map[key].get("source_atom_ids") or []) - set(flat_map[key].get("source_atom_ids") or [])
        for key in set(flat_map) & set(graph_map)
    )
    runtime_instruction_diff_modules = sum(
        flat_map[key].get("instructions") != graph_map[key].get("instructions")
        for key in set(flat_map) & set(graph_map)
    )
    return {
        "domain": domain, "same_module_ids": same_ids,
        "same_primary_tools": same_primary_tools, "same_required_tools": same_required_tools,
        "graph_has_compile_time_atom_expansion": graph_has_expansion,
        "runtime_instruction_diff_modules": runtime_instruction_diff_modules,
        "ok": same_ids and same_primary_tools and same_required_tools,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Static audit for Action Module v2 packages")
    parser.add_argument("--output", type=Path, default=ROOT / "results" / "evaluation" / "action_package_audit.json")
    args = parser.parse_args()
    experiment = read_json(ROOT / "config" / "experiment.json")
    runtime = experiment["runtime"]
    config = ProgressiveConfig(
        max_catalog_chars=runtime["max_catalog_chars"],
        max_module_chars=runtime["max_module_chars"],
        max_active_modules=runtime["max_active_modules"],
    )
    methods = experiment["methods"] + experiment.get("ablation_methods", [])
    rows = [
        audit_package(ROOT / "skills" / method / domain, method, domain, config)
        for method in methods for domain in DOMAINS
    ]
    alignments = [aligned_a2sc(domain) for domain in DOMAINS]
    output = {
        "status": "pass" if all(row["ok"] for row in rows) and all(row["ok"] for row in alignments) else "fail",
        "packages": rows, "a2sc_graph_alignment": alignments,
        "note": "Static compile/runtime-contract audit only; it is not an Agent benchmark result.",
    }
    write_json(args.output, output)
    print(json.dumps({
        "status": output["status"], "packages": len(rows),
        "failed_packages": [f"{row['method']}/{row['domain']}" for row in rows if not row["ok"]],
        "alignments": alignments,
    }, ensure_ascii=False, indent=2))
    if output["status"] != "pass":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
