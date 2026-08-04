"""
Skill Generation Quality Evaluator.

Evaluates the quality of generated SKILL.md files without runtime execution.

Metrics:
1. Structure Completeness - Does SKILL.md have required sections?
2. Evidence Grounding - Are rules backed by evidence references?
3. Safety Compliance - Does it include boundary/safety rules?
4. Category Coverage - Does it cover all required categories?

Usage:
  python scripts/evaluate_skill_quality.py
  python scripts/evaluate_skill_quality.py --method evoskill_compiler
"""

import argparse
import json
import os
import re
import sys
from typing import Dict, List

sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

from common.loader import CUADSkillGenLoader


METHODS = [
    "native_prompt_skill",
    "schema_prompt_skill",
    "summary2skill",
    "document_tool_maker",
    "evoskill_compiler",
]

REQUIRED_SECTIONS = [
    "overview",
    "covered categories",
    "review",
    "output format",
]

EVIDENCE_PATTERNS = [
    r"\[KA-\d+\]",
    r"\[E\d+\]",
    r"\[RB-\d+\]",
    r"\[SR-\d+\]",
    r"evidence",
    r"source",
    r"contract",
]


def check_structure(skill_md: str) -> Dict:
    skill_lower = skill_md.lower()
    found_sections = []
    missing_sections = []
    
    for section in REQUIRED_SECTIONS:
        if section in skill_lower:
            found_sections.append(section)
        else:
            missing_sections.append(section)
    
    return {
        "completeness": len(found_sections) / len(REQUIRED_SECTIONS),
        "found": found_sections,
        "missing": missing_sections,
    }


def check_evidence_grounding(skill_md: str) -> Dict:
    evidence_refs = []
    for pattern in EVIDENCE_PATTERNS:
        matches = re.findall(pattern, skill_md, re.IGNORECASE)
        evidence_refs.extend(matches)
    
    unique_refs = set(evidence_refs)
    
    return {
        "has_evidence": len(evidence_refs) > 0,
        "total_references": len(evidence_refs),
        "unique_references": len(unique_refs),
        "sample_refs": list(unique_refs)[:10],
    }


def check_safety_compliance(skill_md: str, case_json: dict) -> Dict:
    skill_lower = skill_md.lower()
    
    safety_keywords = [
        "boundary",
        "safety",
        "constraint",
        "limitation",
        "do not",
        "must not",
        "should not",
        "only use",
        "evidence_missing",
        "missing_input",
        "unsupported_scope",
        "needs_human_review",
    ]
    
    found_keywords = [kw for kw in safety_keywords if kw in skill_lower]
    
    required_behaviors = case_json.get("capability_requirements", {}).get("required_behaviors", [])
    behavior_coverage = sum(1 for rb in required_behaviors if any(word in skill_lower for word in rb.lower().split()))
    
    return {
        "safety_keywords_found": len(found_keywords),
        "safety_keywords": found_keywords,
        "behavior_coverage": behavior_coverage / max(len(required_behaviors), 1),
    }


def check_category_coverage(skill_md: str, case_json: dict) -> Dict:
    covered_categories = case_json.get("covered_categories", [])
    skill_lower = skill_md.lower()
    
    found_categories = []
    missing_categories = []
    
    for cat in covered_categories:
        if cat.lower() in skill_lower:
            found_categories.append(cat)
        else:
            missing_categories.append(cat)
    
    return {
        "coverage": len(found_categories) / max(len(covered_categories), 1),
        "found": found_categories,
        "missing": missing_categories,
    }


def evaluate_skill(method: str, case_id: str, results_root: str, 
                   loader: CUADSkillGenLoader) -> Dict:
    skill_path = os.path.join(results_root, method, case_id, "SKILL.md")
    
    if not os.path.exists(skill_path):
        return {"error": "SKILL.md not found"}
    
    with open(skill_path, "r", encoding="utf-8") as f:
        skill_md = f.read()
    
    case_json = loader.load_case_json(case_id)
    
    structure = check_structure(skill_md)
    evidence = check_evidence_grounding(skill_md)
    safety = check_safety_compliance(skill_md, case_json)
    categories = check_category_coverage(skill_md, case_json)
    
    manifest_path = os.path.join(results_root, method, case_id, "skill_manifest.json")
    manifest = {}
    if os.path.exists(manifest_path):
        with open(manifest_path, "r", encoding="utf-8") as f:
            manifest = json.load(f)
    
    return {
        "method": method,
        "case_id": case_id,
        "skill_md_chars": len(skill_md),
        "structure": structure,
        "evidence": evidence,
        "safety": safety,
        "categories": categories,
        "usage": manifest.get("usage", {}),
    }


def print_summary(evaluations: List[Dict]):
    print(f"\n{'='*100}")
    print(f"{'Method':<25} {'Case':<25} {'Structure':<12} {'Evidence':<12} {'Safety':<12} {'Categories':<12}")
    print(f"{'-'*100}")
    
    for ev in evaluations:
        if "error" in ev:
            method = ev.get('method', 'unknown')
            case_id = ev.get('case_id', 'unknown')
            print(f"{method:<25} {case_id:<25} ERROR: {ev['error']}")
            continue
        
        struct_score = f"{ev['structure']['completeness']:.0%}"
        evidence_score = f"{ev['evidence']['unique_references']} refs"
        safety_score = f"{ev['safety']['behavior_coverage']:.0%}"
        cat_score = f"{ev['categories']['coverage']:.0%}"
        
        print(f"{ev['method']:<25} {ev['case_id']:<25} {struct_score:<12} {evidence_score:<12} {safety_score:<12} {cat_score:<12}")
    
    print(f"{'='*100}")


def main():
    parser = argparse.ArgumentParser(description="Evaluate SKILL.md generation quality")
    parser.add_argument("--data-root", default="data/cuad_skillgen")
    parser.add_argument("--results-root", default="results/skillgen/generated")
    parser.add_argument("--method", default=None, help="Evaluate only this method")
    parser.add_argument("--case-id", default=None, help="Evaluate only this case")
    parser.add_argument("--output", default="results/skillgen/generated/skill_quality_evaluation.json")
    args = parser.parse_args()
    
    loader = CUADSkillGenLoader(args.data_root)
    
    methods_to_eval = [args.method] if args.method else METHODS
    case_ids = [args.case_id] if args.case_id else loader.get_all_case_ids()
    
    print(f"=== Skill Generation Quality Evaluation ===")
    print(f"Methods: {len(methods_to_eval)}")
    print(f"Cases: {len(case_ids)}")
    print()
    
    evaluations = []
    for method in methods_to_eval:
        for case_id in case_ids:
            ev = evaluate_skill(method, case_id, args.results_root, loader)
            evaluations.append(ev)
    
    print_summary(evaluations)
    
    with open(args.output, "w", encoding="utf-8") as f:
        json.dump(evaluations, f, indent=2, ensure_ascii=False)
    
    print(f"\nDetailed results saved to {args.output}")


if __name__ == "__main__":
    main()
