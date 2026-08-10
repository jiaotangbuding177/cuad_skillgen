"""
Regenerate EvoSkill SKILL.md with increased KA count per category.
Reuses existing evidence_index.json — NO KA re-extraction needed.

Usage:
  python scripts/regen_evoskill_more_kas.py [--ka-top-n 100]
"""

import argparse
import json
import os
import sys
import time

# Ensure scripts/ is on path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))

from common.llm_client import LLMClient
from common.loader import CUADSkillGenLoader
from common.writer import SkillOutputWriter

# ─── Prompts (same as evoskill_compiler.py) ───

GENERATE_SYSTEM = """You are a contract review skill compiler. Generate a SKILL.md from the Knowledge Atom evidence index.

CRITICAL RULES:
1. Every review rule / pattern in the SKILL.md MUST reference specific KA IDs as evidence.
2. Never fabricate clause patterns that are not supported by the evidence index.
3. Follow the security policy strictly.

The SKILL.md must contain these sections:

## Covered Categories
List each category with the number of evidence atoms available.

## Common Clause Patterns & Example Phrasing
For each category, instead of abstract review rules, derive 3-6 common clause PATTERNS
from the evidence KAs. For each pattern include:
- Pattern Name: a short label (e.g. "Termination Right with Notice Period")
- Description: what the pattern looks like in real contracts
- **Example Phrasing:** 1-2 actual full-length example quotes from KA texts
  showing how this clause is typically phrased in real contracts.
  These examples are SEARCH GUIDES — the runtime agent will look for similar language.
  Cite the KA IDs used.
- Variation Notes: how the pattern may differ across contracts (KA IDs as evidence)

## Review Checklist
Actionable checklist items for each category, referencing pattern names.

## Output Format
JSON: {status, answer, evidence_unit_ids, source_contract_ids, missing_inputs, human_review_required}

## Boundary Rules
Reference the security policy rules by ID (e.g., [RB-001], [SR-001]).
"""

COMPILE_SYSTEM = """You are a skill quality auditor. Review the following SKILL.md for:
1. Redundancy: Remove duplicate patterns
2. Consistency: Fix contradictions
3. Evidence: Verify all patterns reference valid KA IDs
4. Example Phrasing Quality: Ensure examples are actual quotes from KA texts (not fabricated), are at least 80 chars, and represent diverse phrasing styles
5. Security: Verify all boundary rules reference security policy

Return ONLY the corrected SKILL.md. Do not add commentary."""


def build_generate_user_prompt(evidence_by_category: dict, security_policy: dict,
                                case_json: dict, max_ka_per_cat_in_prompt: int = 50,
                                max_text_len: int = 200) -> str:
    parts = []
    parts.append("=== EVIDENCE INDEX ===")
    for cat, kas in evidence_by_category.items():
        parts.append(f"\n## {cat} ({len(kas)} KAs)")
        for ka in kas[:max_ka_per_cat_in_prompt]:
            text_preview = ka['text'][:max_text_len]
            if len(ka['text']) > max_text_len:
                text_preview += "..."
            parts.append(f"  {ka['ka_id']}: \"{text_preview}\"")
            parts.append(f"    -> Source: {ka['source_contract_id']}, span [{ka['span_start']}-{ka['span_end']}]")
            parts.append(f"    -> Interpretation: {ka['interpretation']}")

    parts.append("\n=== SECURITY POLICY ===")
    for rb in security_policy.get("required_behaviors", []):
        parts.append(f"  [{rb['rule_id']}] {rb['text']}")
    for sr in security_policy.get("safety_requirements", []):
        parts.append(f"  [{sr['rule_id']}] {sr['text']}")

    parts.append(f"\n=== CASE DEFINITION ===")
    parts.append(f"Case ID: {case_json['case_id']}")
    parts.append("Covered Categories:")
    for cat in case_json.get("covered_categories", []):
        parts.append(f"  - {cat}")

    parts.append("\n=== INSTRUCTION ===")
    parts.append("Generate a SKILL.md with Common Clause Patterns, each including concrete Example Phrasing drawn from KA texts.")
    parts.append("Provide full example quotes (up to 300 chars) — the runtime agent uses these as search templates.")
    parts.append("Reference specific KA IDs for every pattern.")
    return "\n".join(parts)


def build_compile_user_prompt(skill_md: str, evidence_summary: dict) -> str:
    parts = []
    parts.append("=== SKILL.md DRAFT ===")
    parts.append(skill_md)
    parts.append("\n=== EVIDENCE SUMMARY ===")
    parts.append(json.dumps(evidence_summary, indent=2))
    parts.append("\n=== INSTRUCTION ===")
    parts.append("Review and correct the SKILL.md. Return only the corrected version.")
    return "\n".join(parts)


def regen_case(case_id: str, loader: CUADSkillGenLoader, llm: LLMClient,
               ka_top_n: int, output_root: str, skip_compile: bool = False):
    """Regenerate SKILL.md for one case using existing evidence_index.json."""
    method = "evoskill_compiler"

    # Load existing files
    pkg_dir = os.path.join(output_root, method, case_id)
    evidence_path = os.path.join(pkg_dir, "evidence_index.json")
    policy_path = os.path.join(pkg_dir, "security_policy.json")

    if not os.path.exists(evidence_path):
        print(f"  SKIP: {evidence_path} not found")
        return

    with open(evidence_path, encoding="utf-8") as f:
        evidence_index = json.load(f)

    with open(policy_path, encoding="utf-8") as f:
        security_policy = json.load(f)

    case_json = loader.load_case_json(case_id)

    # Build evidence_by_category with NEW threshold (top-N per category)
    evidence_by_category = {}
    for cat, kas in evidence_index.items():
        sorted_kas = sorted(kas, key=lambda k: k.get("confidence", 0), reverse=True)
        evidence_by_category[cat] = sorted_kas[:ka_top_n]

    total_kas = sum(len(v) for v in evidence_by_category.values())
    print(f"  Evidence by category (top-{ka_top_n}): "
          f"{', '.join(f'{c}={len(v)}' for c, v in evidence_by_category.items())} "
          f"= {total_kas} total KAs in prompt")

    # Step 4: Generate SKILL.md with larger KA set
    print(f"  Step 4: Generating SKILL.md...")
    user_prompt = build_generate_user_prompt(evidence_by_category, security_policy, case_json)
    skill_md, step4_usage = llm.call(GENERATE_SYSTEM, user_prompt)
    print(f"    Step 4 done: {step4_usage['total_tokens']} tokens, {len(skill_md)} chars")

    # Step 5: Compile & audit
    if not skip_compile:
        print(f"  Step 5: Compiling and auditing...")
        evidence_summary = {cat: len(kas) for cat, kas in evidence_index.items()}
        compile_prompt = build_compile_user_prompt(skill_md, evidence_summary)
        skill_md_compiled, step5_usage = llm.call(COMPILE_SYSTEM, compile_prompt)
        if len(skill_md_compiled) > 100:
            skill_md = skill_md_compiled
        print(f"    Step 5 done: {step5_usage['total_tokens']} tokens, {len(skill_md)} chars")

    # Write outputs
    writer = SkillOutputWriter(output_root, method, case_id)
    manifest = {
        "method": method,
        "case_id": case_id,
        "model": llm.model,
        "ka_top_n": ka_top_n,
        "regenerated_at": time.strftime("%Y-%m-%d %H:%M:%S"),
        "generation_notes": f"Regenerated with top-{ka_top_n} KAs per category",
        "categories": {cat: len(kas) for cat, kas in evidence_by_category.items()},
    }
    generation_log = {
        "evidence_by_category_counts": {cat: len(kas) for cat, kas in evidence_by_category.items()},
        "ka_top_n": ka_top_n,
        "step4_tokens": step4_usage["total_tokens"],
    }
    writer.write_all(
        skill_md=skill_md,
        manifest=manifest,
        evidence_index=evidence_index,  # unchanged
        security_policy=security_policy,  # unchanged
        generation_log=generation_log,
    )
    print(f"  Wrote: {pkg_dir}")


def main():
    parser = argparse.ArgumentParser(description="Regenerate EvoSkill SKILL.md with more KAs")
    parser.add_argument("--ka-top-n", type=int, default=100,
                        help="Number of top-KAs per category to include in SKILL.md generation (default: 100)")
    parser.add_argument("--model", default="ecnu-plus",
                        help="LLM model for generation (default: ecnu-plus)")
    parser.add_argument("--case-id", default=None,
                        help="Regenerate only this case (default: all 9)")
    parser.add_argument("--skip-compile", action="store_true",
                        help="Skip Step 5 (compile audit)")
    parser.add_argument("--output-root", default="results/skillgen/generated",
                        help="Root directory for generated skill packages")
    parser.add_argument("--dry-run", action="store_true",
                        help="Show what would be done without generating")
    args = parser.parse_args()

    repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    os.chdir(repo_root)

    loader = CUADSkillGenLoader("data/cuad_skillgen")
    case_ids = [args.case_id] if args.case_id else loader.get_all_case_ids()

    if args.dry_run:
        print(f"Would regenerate SKILL.md for {len(case_ids)} cases with ka_top_n={args.ka_top_n}")
        for case_id in case_ids:
            pkg_dir = os.path.join(args.output_root, "evoskill_compiler", case_id)
            evidence_path = os.path.join(pkg_dir, "evidence_index.json")
            if os.path.exists(evidence_path):
                with open(evidence_path, encoding="utf-8") as f:
                    ei = json.load(f)
                for cat, kas in ei.items():
                    sorted_kas = sorted(kas, key=lambda k: k.get("confidence", 0), reverse=True)
                    print(f"  {case_id}/{cat}: {len(sorted_kas)} total KAs → top-{min(args.ka_top_n, len(sorted_kas))} used")
            else:
                print(f"  {case_id}: evidence_index.json NOT FOUND")
        return

    llm = LLMClient(model=args.model, temperature=0.2, max_tokens=8192)

    for i, case_id in enumerate(case_ids, 1):
        print(f"\n[{i}/{len(case_ids)}] Regenerating: {case_id}")
        try:
            regen_case(case_id, loader, llm, args.ka_top_n, args.output_root, args.skip_compile)
        except Exception as e:
            print(f"  ERROR: {e}")
            import traceback
            traceback.print_exc()

    print("\nDone. To evaluate, run:")
    print(f"  python scripts/run_package_runtime.py --method evoskill_compiler --split test --run-id final-k10-k6-v2")


if __name__ == "__main__":
    main()
