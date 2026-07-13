"""
Baseline 2: schema_prompt_skill

Same as native_prompt but with a fixed SKILL.md schema.
Forces the LLM to produce 5 mandatory sections:
  ## Covered Categories
  ## Review Checklist
  ## Evidence Extraction Rules
  ## Output Format
  ## Boundary Rules

Input: case.json + category descriptions + 10 sampled contracts + schema template
Output: SKILL.md (structured), empty evidence_index, empty security_policy
LLM calls: 1 per case
"""

import argparse
import json
import os
import sys
import time

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from common.loader import CUADSkillGenLoader
from common.writer import SkillOutputWriter, create_empty_evidence_index, create_empty_security_policy
from common.llm_client import LLMClient, estimate_tokens, truncate_to_tokens
from common.sampler import ContractSampler


METHOD_NAME = "schema_prompt_skill"
N_CONTRACTS = 10
MAX_CONTRACT_TOKENS = 13000
SEED = 42


def build_schema_section(case_json: dict) -> str:
    """Build the schema constraint section from case.json."""
    reqs = case_json.get("capability_requirements", {})
    behaviors = reqs.get("required_behaviors", [])
    safety = reqs.get("safety_requirements", [])
    allowed_status = reqs.get("allowed_status", [])

    parts = []
    parts.append("The SKILL.md MUST contain the following sections in order:")
    parts.append("")
    parts.append("## Covered Categories")
    parts.append("List all covered categories with their descriptions and answer formats.")
    parts.append("")
    parts.append("## Review Checklist")
    parts.append("For each category, provide a checklist item describing what to look for.")
    parts.append("")
    parts.append("## Evidence Extraction Rules")
    parts.append("Describe how to locate and extract evidence from contracts.")
    parts.append("")
    parts.append("## Output Format")
    parts.append("The output must be a JSON object with these fields:")
    parts.append("  - status: one of " + ", ".join(f'"{s}"' for s in allowed_status))
    parts.append("  - answer: string")
    parts.append("  - evidence_unit_ids: list of strings")
    parts.append("  - source_contract_ids: list of strings")
    parts.append("  - missing_inputs: list of strings")
    parts.append("  - human_review_required: boolean")
    parts.append("")
    parts.append("## Boundary Rules")
    parts.append("Include ALL of the following rules:")
    for b in behaviors:
        parts.append(f"  - {b}")
    parts.append("Safety requirements:")
    for s in safety:
        parts.append(f"  - {s}")

    return "\n".join(parts)


SYSTEM_PROMPT_TEMPLATE = """You are a contract review expert. Based on the following contract documents and review categories, generate a SKILL.md file.

{schema_section}

Be practical and specific. Reference actual patterns you observe in the provided contracts.
Do not invent content that is not supported by the contract documents."""


def build_user_prompt(case_json: dict, category_descriptions: list, contracts: dict) -> str:
    """Build the user prompt (same structure as native_prompt)."""
    parts = []

    parts.append("=== CASE DEFINITION ===")
    parts.append(f"Case ID: {case_json['case_id']}")
    parts.append("Covered Categories:")
    for cat_desc in category_descriptions:
        parts.append(f"  - {cat_desc['category']}: {cat_desc['description']} (Answer Format: {cat_desc['answer_format']})")
    parts.append("")

    parts.append("=== CONTRACT DOCUMENTS ===")
    for cid, text in contracts.items():
        truncated = truncate_to_tokens(text, MAX_CONTRACT_TOKENS)
        parts.append(f"--- Contract: {cid} ---")
        parts.append(truncated)
        parts.append("")

    parts.append("=== INSTRUCTION ===")
    parts.append(f"Generate a SKILL.md for '{case_json['case_id']}' following the required schema above.")
    parts.append("Base your guidance on actual patterns from the provided contracts.")

    return "\n".join(parts)


def generate_skill_for_case(
    loader: CUADSkillGenLoader,
    case_id: str,
    llm: LLMClient,
    results_root: str,
    overwrite: bool = False,
) -> dict:
    """Generate SKILL.md for a single case using schema_prompt method."""
    writer = SkillOutputWriter(results_root, METHOD_NAME, case_id)

    if writer.output_exists() and not overwrite:
        print(f"  [{case_id}] Output already exists, skipping")
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

    # Build prompts
    schema_section = build_schema_section(case_json)
    system_prompt = SYSTEM_PROMPT_TEMPLATE.format(schema_section=schema_section)
    user_prompt = build_user_prompt(case_json, cat_descs, contracts)

    # Call LLM
    print(f"  [{case_id}] Calling LLM ({estimate_tokens(user_prompt)} tokens input)...")
    skill_md, usage = llm.call(system_prompt, user_prompt)

    duration = time.time() - start_time

    # Write outputs
    manifest = {
        "method": METHOD_NAME,
        "case_id": case_id,
        "model": llm.model,
        "schema_sections": [
            "Covered Categories",
            "Review Checklist",
            "Evidence Extraction Rules",
            "Output Format",
            "Boundary Rules",
        ],
        "input_summary": {
            "contracts_sampled": len(sampled_ids),
            "sampled_contract_ids": sampled_ids,
            "contracts_with_evidence_count": len(contracts_with_evidence),
            "category_count": len(cat_descs),
            "estimated_input_tokens": estimate_tokens(user_prompt),
        },
        "usage": usage,
        "duration_seconds": round(duration, 2),
    }

    generation_log = {
        "system_prompt": system_prompt,
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
    parser = argparse.ArgumentParser(description="Baseline 2: schema_prompt_skill")
    parser.add_argument("--data-root", default="data/cuad_skillgen")
    parser.add_argument("--results-root", default="results/skillgen/generated")
    parser.add_argument("--case-id", default=None)
    parser.add_argument("--model", default="claude-sonnet-4-20250514")
    parser.add_argument("--overwrite", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    loader = CUADSkillGenLoader(args.data_root)
    llm = LLMClient(model=args.model)
    case_ids = [args.case_id] if args.case_id else loader.get_all_case_ids()

    print(f"=== {METHOD_NAME} ===")
    print(f"Model: {llm.model}")
    print(f"Cases: {len(case_ids)}")
    print(f"Contracts per case: {N_CONTRACTS}")
    print(f"Schema sections: 5 (Covered Categories, Review Checklist, Evidence Extraction Rules, Output Format, Boundary Rules)")
    print()

    if args.dry_run:
        for case_id in case_ids:
            contracts_with_evidence = loader.get_contracts_with_evidence(case_id, "train")
            print(f"  [{case_id}] Would sample {N_CONTRACTS} contracts ({len(contracts_with_evidence)} with evidence)")
        return

    total_start = time.time()
    for case_id in case_ids:
        generate_skill_for_case(loader, case_id, llm, args.results_root, args.overwrite)

    total_duration = time.time() - total_start
    total_usage = llm.get_total_usage()
    print(f"\n=== Summary ===")
    print(f"Total calls: {total_usage['calls']}, Total tokens: {total_usage['total_tokens']}, Duration: {total_duration:.1f}s")


if __name__ == "__main__":
    main()
