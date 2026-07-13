"""
Baseline 1: native_prompt_skill

The simplest baseline. No knowledge extraction, no structure.
Samples 10 contracts and asks LLM to generate a SKILL.md.

Input: case.json + category descriptions + 10 sampled contracts
Output: SKILL.md (free-form), empty evidence_index, empty security_policy
LLM calls: 1 per case
"""

import argparse
import json
import os
import sys
import time

# Add scripts/ to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from common.loader import CUADSkillGenLoader
from common.writer import SkillOutputWriter, create_empty_evidence_index, create_empty_security_policy
from common.llm_client import LLMClient, estimate_tokens, truncate_to_tokens
from common.sampler import ContractSampler


# ─── Constants ───

METHOD_NAME = "native_prompt_skill"
N_CONTRACTS = 10
MAX_CONTRACT_TOKENS = 13000  # ~13K tokens per contract, 10 contracts = ~130K total
SEED = 42

SYSTEM_PROMPT = """You are a contract review expert. Based on the following contract documents and review categories, generate a SKILL.md file that describes how to review contracts for the specified capability case.

The SKILL.md should include:
- An overview of what this skill does
- Review steps for each covered category
- What to look for in contracts
- Output format for review results

Be practical and specific. Reference actual patterns you observe in the provided contracts."""


def build_user_prompt(case_json: dict, category_descriptions: list, contracts: dict) -> str:
    """
    Build the user prompt.

    Args:
        case_json: case.json content
        category_descriptions: list of {category, description, answer_format} for this case
        contracts: dict of {contract_id: contract_text}
    """
    parts = []

    # Case definition
    parts.append("=== CASE DEFINITION ===")
    parts.append(f"Case ID: {case_json['case_id']}")
    parts.append("Covered Categories:")
    for cat_desc in category_descriptions:
        parts.append(f"  - {cat_desc['category']}: {cat_desc['description']} (Answer Format: {cat_desc['answer_format']})")
    parts.append("")

    # Contract documents
    parts.append("=== CONTRACT DOCUMENTS ===")
    for cid, text in contracts.items():
        truncated = truncate_to_tokens(text, MAX_CONTRACT_TOKENS)
        parts.append(f"--- Contract: {cid} ---")
        parts.append(truncated)
        parts.append("")

    # Instruction
    parts.append("=== INSTRUCTION ===")
    parts.append(f"Please generate a SKILL.md file for the '{case_json['case_id']}' capability case.")
    parts.append("The skill should describe how to review contracts for the covered categories listed above.")
    parts.append("Base your guidance on the actual patterns you observe in the provided contract documents.")

    return "\n".join(parts)


def generate_skill_for_case(
    loader: CUADSkillGenLoader,
    case_id: str,
    llm: LLMClient,
    results_root: str,
    overwrite: bool = False,
) -> dict:
    """
    Generate SKILL.md for a single case using native_prompt method.

    Returns:
        dict with generation stats
    """
    writer = SkillOutputWriter(results_root, METHOD_NAME, case_id)

    if writer.output_exists() and not overwrite:
        print(f"  [{case_id}] Output already exists, skipping (use --overwrite to regenerate)")
        return {"skipped": True}

    start_time = time.time()

    # Load inputs
    case_json = loader.load_case_json(case_id)
    cat_descs = loader.get_category_descriptions_for_case(case_id)
    train_cids = loader.get_train_contract_ids()
    contracts_with_evidence = loader.get_contracts_with_evidence(case_id, "train")

    # Sample contracts
    sampler = ContractSampler(seed=SEED)
    sampled_ids = sampler.sample_contracts_for_case(train_cids, N_CONTRACTS, contracts_with_evidence)
    contracts = loader.load_contract_texts(sampled_ids)

    # Build prompt
    user_prompt = build_user_prompt(case_json, cat_descs, contracts)

    # Call LLM
    print(f"  [{case_id}] Calling LLM ({estimate_tokens(user_prompt)} tokens input)...")
    skill_md, usage = llm.call(SYSTEM_PROMPT, user_prompt)

    duration = time.time() - start_time

    # Write outputs
    manifest = {
        "method": METHOD_NAME,
        "case_id": case_id,
        "model": llm.model,
        "input_summary": {
            "contracts_sampled": len(sampled_ids),
            "sampled_contract_ids": sampled_ids,
            "contracts_with_evidence_count": len(contracts_with_evidence),
            "category_count": len(cat_descs),
            "estimated_input_tokens": estimate_tokens(user_prompt),
        },
        "output_summary": {
            "skill_md_chars": len(skill_md),
            "skill_md_estimated_tokens": estimate_tokens(skill_md),
        },
        "usage": usage,
        "duration_seconds": round(duration, 2),
    }

    generation_log = {
        "system_prompt": SYSTEM_PROMPT,
        "user_prompt": user_prompt,
        "llm_response": skill_md,
        "model": llm.model,
        "temperature": llm.temperature,
        "sampled_contracts": sampled_ids,
    }

    writer.write_all(
        skill_md=skill_md,
        manifest=manifest,
        evidence_index=create_empty_evidence_index(),
        security_policy=create_empty_security_policy(),
        generation_log=generation_log,
    )

    print(f"  [{case_id}] Done in {duration:.1f}s, {usage['total_tokens']} tokens")
    return {"skipped": False, "usage": usage, "duration": duration}


def main():
    parser = argparse.ArgumentParser(description="Baseline 1: native_prompt_skill")
    parser.add_argument("--data-root", default="data/cuad_skillgen",
                        help="Path to CUAD-SkillGen data root")
    parser.add_argument("--results-root", default="results/skillgen/generated",
                        help="Path to results output root")
    parser.add_argument("--case-id", default=None,
                        help="Generate for a single case (default: all 9 cases)")
    parser.add_argument("--model", default="claude-sonnet-4-20250514",
                        help="LLM model name")
    parser.add_argument("--overwrite", action="store_true",
                        help="Overwrite existing output")
    parser.add_argument("--dry-run", action="store_true",
                        help="Show what would be done without calling LLM")
    args = parser.parse_args()

    loader = CUADSkillGenLoader(args.data_root)
    llm = LLMClient(model=args.model)

    case_ids = [args.case_id] if args.case_id else loader.get_all_case_ids()

    print(f"=== {METHOD_NAME} ===")
    print(f"Model: {llm.model}")
    print(f"Cases: {len(case_ids)}")
    print(f"Contracts per case: {N_CONTRACTS}")
    print()

    if args.dry_run:
        for case_id in case_ids:
            contracts_with_evidence = loader.get_contracts_with_evidence(case_id, "train")
            sampler = ContractSampler(seed=SEED)
            sampled = sampler.sample_contracts_for_case(
                loader.get_train_contract_ids(), N_CONTRACTS, contracts_with_evidence
            )
            print(f"  [{case_id}] Would sample {len(sampled)} contracts "
                  f"({len(contracts_with_evidence)} with evidence)")
        return

    total_start = time.time()
    results = {}
    for case_id in case_ids:
        results[case_id] = generate_skill_for_case(
            loader, case_id, llm, args.results_root, args.overwrite
        )

    total_duration = time.time() - total_start
    total_usage = llm.get_total_usage()

    print(f"\n=== Summary ===")
    print(f"Total cases: {len(case_ids)}")
    print(f"Total LLM calls: {total_usage['calls']}")
    print(f"Total tokens: {total_usage['total_tokens']}")
    print(f"Total duration: {total_duration:.1f}s")


if __name__ == "__main__":
    main()
