"""
Target Method: evoskill_compiler

Atom-level knowledge extraction + security policy compilation.

Pipeline:
  Step 1: Extract Knowledge Atoms (KAs) from each contract (306 calls)
  Step 2: Build evidence_index.json (deterministic, no LLM)
  Step 3: Build security_policy.json (deterministic, from case.json)
  Step 4: Generate SKILL.md referencing KA IDs (1 call)
  Step 5: Compile & audit (1 call, optional)

Input: 306 contracts + case.json + category_descriptions
Output: SKILL.md + span-level evidence_index + structured security_policy
LLM calls: 306 + 1 + 1 = 308 per case
"""

import argparse
import json
import os
import sys
import time

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from common.loader import CUADSkillGenLoader
from common.writer import SkillOutputWriter
from common.llm_client import LLMClient, estimate_tokens, truncate_to_tokens

METHOD_NAME = "evoskill_compiler"
MAX_CONTRACT_TOKENS = 13000
MAX_KAS_IN_SKILL = 200  # Top K KAs to include in SKILL.md generation


# ─── Prompts ───

EXTRACT_SYSTEM = """You are a contract review expert. Extract Knowledge Atoms from the following contract.

A Knowledge Atom (KA) is an atomic unit of knowledge: a direct quote from the contract paired with its review interpretation.

Rules:
1. The 'text' field MUST be a DIRECT QUOTE from the contract. Do NOT rewrite, summarize, or paraphrase.
2. 'span_start' and 'span_end' must be the exact character offsets of the quote in the contract text.
3. Each KA must map to exactly one of the specified categories.
4. Extract ALL relevant atoms for each category (could be 0 or many).
5. If a category is not found in the contract, do NOT fabricate an atom for it.
6. 'confidence' should reflect how clearly the text matches the category.

Return your response as valid JSON only."""


def build_extract_user_prompt(contract_id: str, contract_text: str,
                               category_descriptions: list) -> str:
    parts = []
    parts.append(f"=== CONTRACT ===")
    parts.append(f"Contract ID: {contract_id}")
    parts.append(f"Text length: {len(contract_text)} characters")
    parts.append("")
    parts.append(truncate_to_tokens(contract_text, MAX_CONTRACT_TOKENS))
    parts.append("")
    parts.append("=== CATEGORIES TO EXTRACT ===")
    for cd in category_descriptions:
        parts.append(f"- {cd['category']}: {cd['description']} (Answer Format: {cd['answer_format']})")
    parts.append("")
    parts.append("=== KNOWLEDGE ATOM SCHEMA ===")
    parts.append(json.dumps([
        {
            "ka_id": "KA-0001",
            "category": "Must match one of the categories above",
            "text": "EXACT quote from contract (do not modify)",
            "span_start": 0,
            "span_end": 0,
            "interpretation": "One-sentence review interpretation",
            "confidence": 0.95
        }
    ], indent=2))
    return "\n".join(parts)


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


def build_generate_user_prompt(evidence_by_category: dict, security_policy: dict,
                                case_json: dict) -> str:
    parts = []
    parts.append("=== EVIDENCE INDEX ===")
    for cat, kas in evidence_by_category.items():
        parts.append(f"\n## {cat} ({len(kas)} KAs)")
        for ka in kas[:25]:  # Limit to 25 KAs per category for prompt size
            parts.append(f"  {ka['ka_id']}: \"{ka['text'][:100]}...\"")
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


COMPILE_SYSTEM = """You are a skill quality auditor. Review the following SKILL.md for:
1. Redundancy: Remove duplicate patterns
2. Consistency: Fix contradictions
3. Evidence: Verify all patterns reference valid KA IDs
4. Example Phrasing Quality: Ensure examples are actual quotes from KA texts (not fabricated), are at least 80 chars, and represent diverse phrasing styles
5. Security: Verify all boundary rules reference security policy

Return ONLY the corrected SKILL.md. Do not add commentary."""


def build_compile_user_prompt(skill_md: str, evidence_summary: dict) -> str:
    parts = []
    parts.append("=== SKILL.md DRAFT ===")
    parts.append(skill_md)
    parts.append("\n=== EVIDENCE SUMMARY ===")
    parts.append(json.dumps(evidence_summary, indent=2))
    parts.append("\n=== INSTRUCTION ===")
    parts.append("Review and correct the SKILL.md. Return only the corrected version.")
    return "\n".join(parts)


# ─── Deterministic Builders ───

def build_evidence_index(all_kas: list) -> dict:
    """Build evidence_index.json from all extracted KAs."""
    index = {}
    for ka in all_kas:
        cat = ka.get("category", "")
        if cat not in index:
            index[cat] = []
        index[cat].append(ka)
    return index


def build_security_policy(case_json: dict) -> dict:
    """Build structured security_policy.json from case.json."""
    reqs = case_json.get("capability_requirements", {})

    required_behaviors = []
    for i, text in enumerate(reqs.get("required_behaviors", []), 1):
        required_behaviors.append({
            "rule_id": f"RB-{i:03d}",
            "text": text,
            "enforcement": "hard"
        })

    safety_requirements = []
    safety_checks = {
        "do not cite non-target contracts": "verify source_contract_ids == [target_contract_id]",
        "do not fabricate clauses": "verify evidence spans exist in target contract",
        "do not provide legal advice": "detect legal judgment language in answer",
        "do not generate externally sendable legal opinions": "detect formal document patterns",
    }
    for i, text in enumerate(reqs.get("safety_requirements", []), 1):
        check = ""
        for key, val in safety_checks.items():
            if key in text.lower():
                check = val
                break
        safety_requirements.append({
            "rule_id": f"SR-{i:03d}",
            "text": text,
            "enforcement": "hard",
            "check": check
        })

    return {
        "allowed_status": reqs.get("allowed_status", []),
        "required_behaviors": required_behaviors,
        "safety_requirements": safety_requirements,
        "boundary_rules": [
            {"covered_categories": case_json.get("covered_categories", [])},
            {"domain": case_json.get("domain", "contract_review")},
        ]
    }


# ─── Main Pipeline ───

def generate_skill_for_case(
    loader: CUADSkillGenLoader,
    case_id: str,
    llm: LLMClient,
    results_root: str,
    overwrite: bool = False,
    skip_compile: bool = False,
) -> dict:
    writer = SkillOutputWriter(results_root, METHOD_NAME, case_id)

    if writer.output_exists() and not overwrite:
        print(f"  [{case_id}] Output already exists, skipping")
        return {"skipped": True}

    start_time = time.time()

    # Load inputs
    case_json = loader.load_case_json(case_id)
    cat_descs = loader.get_category_descriptions_for_case(case_id)
    train_cids = loader.get_train_contract_ids()

    # ─── Step 1: Extract Knowledge Atoms ───
    print(f"  [{case_id}] Step 1: Extracting Knowledge Atoms from {len(train_cids)} contracts...")
    all_kas = []
    ka_counter = 0
    step1_usage = {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0}
    kas_by_contract = {}

    for i, cid in enumerate(train_cids):
        contract_text = loader.load_contract_text(cid)
        user_prompt = build_extract_user_prompt(cid, contract_text, cat_descs)
        try:
            kas_raw, usage = llm.call_json(EXTRACT_SYSTEM, user_prompt)
            for k in step1_usage:
                step1_usage[k] += usage[k]

            if isinstance(kas_raw, list):
                kas_list = kas_raw
            elif isinstance(kas_raw, dict):
                kas_list = kas_raw.get("knowledge_atoms", kas_raw.get("kas", []))
            else:
                kas_list = []

            contract_kas = []
            for ka in kas_list:
                ka_counter += 1
                ka["ka_id"] = f"KA-{ka_counter:04d}"
                ka["source_contract_id"] = cid
                # Verify span if possible
                text = ka.get("text", "")
                span_start = ka.get("span_start", -1)
                if text and span_start >= 0:
                    actual_span = contract_text[span_start:span_start + len(text)]
                    if actual_span != text:
                        # Try to find the text in the contract
                        found_pos = contract_text.find(text[:50])
                        if found_pos >= 0:
                            ka["span_start"] = found_pos
                            ka["span_end"] = found_pos + len(text)
                contract_kas.append(ka)

            all_kas.extend(contract_kas)
            kas_by_contract[cid] = len(contract_kas)

        except Exception as e:
            print(f"    Warning: Contract {cid[:40]}... failed: {e}")
            kas_by_contract[cid] = 0

        if (i + 1) % 50 == 0:
            print(f"    Progress: {i+1}/{len(train_cids)}, {len(all_kas)} KAs so far")

    print(f"    Step 1 done: {len(all_kas)} KAs from {len(train_cids)} contracts, {step1_usage['total_tokens']} tokens")

    # ─── Step 2: Build evidence_index (deterministic) ───
    print(f"  [{case_id}] Step 2: Building evidence index...")
    evidence_index = build_evidence_index(all_kas)

    # Build category-level summary for SKILL generation
    evidence_by_category = {}
    for cat, kas in evidence_index.items():
        # Sort by confidence, take top KAs
        sorted_kas = sorted(kas, key=lambda k: k.get("confidence", 0), reverse=True)
        evidence_by_category[cat] = sorted_kas[:30]  # Top 30 per category

    # ─── Step 3: Build security_policy (deterministic) ───
    security_policy = build_security_policy(case_json)
    print(f"    Step 2-3 done: {len(evidence_index)} categories, "
          f"{len(security_policy['required_behaviors'])} behaviors, "
          f"{len(security_policy['safety_requirements'])} safety rules")

    # ─── Step 4: Generate SKILL.md ───
    print(f"  [{case_id}] Step 4: Generating SKILL.md...")
    user_prompt = build_generate_user_prompt(evidence_by_category, security_policy, case_json)
    skill_md, step4_usage = llm.call(GENERATE_SYSTEM, user_prompt)
    print(f"    Step 4 done: {step4_usage['total_tokens']} tokens")

    # ─── Step 5: Compile & audit (optional) ───
    if not skip_compile:
        print(f"  [{case_id}] Step 5: Compiling and auditing...")
        evidence_summary = {
            cat: len(kas) for cat, kas in evidence_index.items()
        }
        compile_prompt = build_compile_user_prompt(skill_md, evidence_summary)
        skill_md_compiled, step5_usage = llm.call(COMPILE_SYSTEM, compile_prompt)
        if len(skill_md_compiled) > 100:  # Sanity check
            skill_md = skill_md_compiled
        print(f"    Step 5 done: {step5_usage['total_tokens']} tokens")
    else:
        step5_usage = {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0}

    duration = time.time() - start_time

    # ─── Write outputs ───
    total_usage = {
        "prompt_tokens": step1_usage["prompt_tokens"] + step4_usage["prompt_tokens"] + step5_usage["prompt_tokens"],
        "completion_tokens": step1_usage["completion_tokens"] + step4_usage["completion_tokens"] + step5_usage["completion_tokens"],
        "total_tokens": step1_usage["total_tokens"] + step4_usage["total_tokens"] + step5_usage["total_tokens"],
    }

    manifest = {
        "method": METHOD_NAME,
        "case_id": case_id,
        "model": llm.model,
        "pipeline": {
            "step1_extract": {
                "contracts_processed": len(train_cids),
                "total_kas_extracted": len(all_kas),
                "avg_kas_per_contract": round(len(all_kas) / max(len(train_cids), 1), 2),
                "kas_by_category": {cat: len(kas) for cat, kas in evidence_index.items()},
                "kas_by_contract_sample": dict(list(kas_by_contract.items())[:10]),
                "llm_calls": len(train_cids),
            },
            "step2_index": {
                "total_kas_in_index": len(all_kas),
                "categories_with_evidence": len(evidence_index),
            },
            "step3_security": {
                "required_behaviors_count": len(security_policy["required_behaviors"]),
                "safety_requirements_count": len(security_policy["safety_requirements"]),
            },
            "step4_generate": {"llm_calls": 1},
            "step5_compile": {"llm_calls": 0 if skip_compile else 1},
        },
        "usage": total_usage,
        "duration_seconds": round(duration, 2),
    }

    generation_log = {
        "step1_kas_sample": all_kas[:10],
        "step2_evidence_summary": {cat: len(kas) for cat, kas in evidence_index.items()},
        "step3_security_policy": security_policy,
        "step4_skill_md": skill_md,
    }

    writer.write_all(
        skill_md=skill_md,
        manifest=manifest,
        evidence_index=evidence_index,
        security_policy=security_policy,
        generation_log=generation_log,
    )

    print(f"  [{case_id}] Done in {duration:.1f}s, {total_usage['total_tokens']} total tokens, {len(all_kas)} KAs")
    return {"skipped": False, "usage": total_usage, "duration": duration, "kas": len(all_kas)}


def main():
    parser = argparse.ArgumentParser(description="Target Method: evoskill_compiler")
    parser.add_argument("--data-root", default="data/cuad_skillgen")
    parser.add_argument("--results-root", default="results/skillgen/generated")
    parser.add_argument("--case-id", default=None)
    parser.add_argument("--model", default="claude-sonnet-4-20250514")
    parser.add_argument("--overwrite", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--skip-compile", action="store_true",
                        help="Skip Step 5 (compile & audit)")
    args = parser.parse_args()

    loader = CUADSkillGenLoader(args.data_root)
    llm = LLMClient(model=args.model)
    case_ids = [args.case_id] if args.case_id else loader.get_all_case_ids()

    print(f"=== {METHOD_NAME} ===")
    print(f"Model: {llm.model}")
    print(f"Cases: {len(case_ids)}")
    print(f"Pipeline: 306 extract + 1 generate + 1 compile = 308 LLM calls/case")
    print()

    if args.dry_run:
        for case_id in case_ids:
            eu_count = len(loader.get_train_evidence_units(case_id))
            print(f"  [{case_id}] Would extract KAs from 306 contracts "
                  f"(reference: {eu_count} expert evidence units)")
        return

    total_start = time.time()
    all_results = {}
    for case_id in case_ids:
        all_results[case_id] = generate_skill_for_case(
            loader, case_id, llm, args.results_root, args.overwrite, args.skip_compile
        )

    total_duration = time.time() - total_start
    total_usage = llm.get_total_usage()
    total_kas = sum(r.get("kas", 0) for r in all_results.values() if not r.get("skipped"))

    print(f"\n=== Summary ===")
    print(f"Total calls: {total_usage['calls']}")
    print(f"Total tokens: {total_usage['total_tokens']}")
    print(f"Total KAs extracted: {total_kas}")
    print(f"Total duration: {total_duration:.1f}s")


if __name__ == "__main__":
    main()
