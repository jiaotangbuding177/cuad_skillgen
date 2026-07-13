"""
Baseline 3: summary2skill

Summary-level knowledge extraction.
For each training contract, extract a structured summary per covered category.
Merge all summaries, then generate SKILL.md.

Input: 306 contracts (processed one at a time)
Output: SKILL.md + contract-level evidence_index
LLM calls: 306 (extract) + 2 (merge) + 1 (generate) = 309 per case
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

METHOD_NAME = "summary2skill"
MAX_CONTRACT_TOKENS = 13000
MERGE_BATCH_SIZE = 153  # Split 306 summaries into 2 batches


# ─── Prompts ───

EXTRACT_SYSTEM = """You are a contract review expert. Extract structured information from the following contract for the specified review categories.

For each category, determine:
1. Whether the category is present in the contract (found: true/false)
2. A one-sentence summary of what was found
3. Key terms mentioned
4. The source paragraph (direct quote from the contract)

If a category is not found, set found=false and leave other fields empty.
Return your response as valid JSON only."""


def build_extract_user_prompt(contract_id: str, contract_text: str,
                               category_descriptions: list) -> str:
    parts = []
    parts.append(f"=== CONTRACT ===")
    parts.append(f"Contract ID: {contract_id}")
    parts.append(truncate_to_tokens(contract_text, MAX_CONTRACT_TOKENS))
    parts.append("")
    parts.append("=== CATEGORIES TO EXTRACT ===")
    for cd in category_descriptions:
        parts.append(f"- {cd['category']}: {cd['description']} (Answer Format: {cd['answer_format']})")
    parts.append("")
    parts.append("=== OUTPUT SCHEMA ===")
    parts.append(json.dumps({
        "contract_id": contract_id,
        "extractions": [
            {
                "category": "category name",
                "found": True,
                "summary": "one-sentence summary",
                "key_terms": ["term1", "term2"],
                "source_paragraph": "direct quote from contract"
            }
        ]
    }, indent=2))
    return "\n".join(parts)


MERGE_SYSTEM = """You are a contract review knowledge aggregator. Below are structured summaries extracted from multiple contracts.

Merge and deduplicate these summaries. For each category:
1. Count how many contracts had this category (found_count)
2. Identify common patterns in the findings
3. Collect representative example summaries
4. Note any variations or edge cases

Return your response as valid JSON only."""


def build_merge_user_prompt(summaries: list, batch_label: str) -> str:
    parts = []
    parts.append(f"=== BATCH {batch_label} ===")
    parts.append(f"Number of summaries: {len(summaries)}")
    parts.append("")
    for i, s in enumerate(summaries):
        parts.append(f"[Summary {i+1}]")
        parts.append(json.dumps(s, ensure_ascii=False))
        parts.append("")
    parts.append("=== OUTPUT SCHEMA ===")
    parts.append(json.dumps({
        "category_stats": {
            "Category Name": {
                "found_count": 0,
                "total_contracts": 0,
                "common_patterns": ["pattern description"],
                "example_extractions": ["summary1", "summary2"],
                "variations": ["variation description"]
            }
        }
    }, indent=2))
    return "\n".join(parts)


GENERATE_SYSTEM = """You are a contract review skill designer. Based on the aggregated knowledge from multiple contracts, generate a SKILL.md file.

The SKILL.md must contain these sections:

## Covered Categories
List each category with: discovery frequency (X% of contracts), common patterns.

## Common Patterns
For each category, describe the 2-3 most common patterns found, with example phrasing.

## Review Checklist
For each category, a checklist item for what to look for.

## Evidence Extraction Rules
How to locate and extract evidence for each category.

## Output Format
JSON output schema: {status, answer, evidence_unit_ids, source_contract_ids, missing_inputs, human_review_required}

## Boundary Rules
Rules about what the skill should and should not do.

Be specific and reference the patterns observed in the aggregated knowledge."""


def build_generate_user_prompt(merged_knowledge: dict, case_json: dict,
                                category_descriptions: list) -> str:
    parts = []
    parts.append("=== AGGREGATED KNOWLEDGE ===")
    parts.append(json.dumps(merged_knowledge, indent=2, ensure_ascii=False))
    parts.append("")
    parts.append("=== CASE DEFINITION ===")
    parts.append(f"Case ID: {case_json['case_id']}")
    parts.append("Covered Categories:")
    for cd in category_descriptions:
        parts.append(f"  - {cd['category']}: {cd['description']}")
    parts.append("")
    parts.append("=== INSTRUCTION ===")
    parts.append("Generate a SKILL.md based on the aggregated knowledge above.")
    return "\n".join(parts)


# ─── Main Pipeline ───

def generate_skill_for_case(
    loader: CUADSkillGenLoader,
    case_id: str,
    llm: LLMClient,
    results_root: str,
    overwrite: bool = False,
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

    # ─── Step 1: Extract summaries from each contract ───
    print(f"  [{case_id}] Step 1: Extracting summaries from {len(train_cids)} contracts...")
    all_summaries = []
    step1_usage = {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0}

    for i, cid in enumerate(train_cids):
        contract_text = loader.load_contract_text(cid)
        user_prompt = build_extract_user_prompt(cid, contract_text, cat_descs)
        try:
            summary, usage = llm.call_json(EXTRACT_SYSTEM, user_prompt)
            all_summaries.append(summary)
            for k in step1_usage:
                step1_usage[k] += usage[k]
        except Exception as e:
            print(f"    Warning: Contract {cid[:40]}... failed: {e}")
            # Add a minimal fallback summary
            all_summaries.append({
                "contract_id": cid,
                "extractions": [{"category": cd["category"], "found": False,
                                  "summary": "", "key_terms": [], "source_paragraph": ""}
                                 for cd in cat_descs]
            })

        if (i + 1) % 50 == 0:
            print(f"    Progress: {i+1}/{len(train_cids)}")

    print(f"    Step 1 done: {len(all_summaries)} summaries, {step1_usage['total_tokens']} tokens")

    # ─── Step 2: Merge summaries in batches ───
    print(f"  [{case_id}] Step 2: Merging summaries...")
    batch1 = all_summaries[:MERGE_BATCH_SIZE]
    batch2 = all_summaries[MERGE_BATCH_SIZE:]

    merged_results = []
    step2_usage = {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0}

    for batch, label in [(batch1, "1/2"), (batch2, "2/2")]:
        if not batch:
            continue
        user_prompt = build_merge_user_prompt(batch, label)
        merged, usage = llm.call_json(MERGE_SYSTEM, user_prompt)
        merged_results.append(merged)
        for k in step2_usage:
            step2_usage[k] += usage[k]

    # Combine batch results
    combined_stats = {}
    for mr in merged_results:
        for cat, stats in mr.get("category_stats", {}).items():
            if cat not in combined_stats:
                combined_stats[cat] = stats
            else:
                combined_stats[cat]["found_count"] = (
                    combined_stats[cat].get("found_count", 0) + stats.get("found_count", 0)
                )
                combined_stats[cat]["total_contracts"] = (
                    combined_stats[cat].get("total_contracts", 0) + stats.get("total_contracts", 0)
                )
                combined_stats[cat]["common_patterns"] = list(set(
                    combined_stats[cat].get("common_patterns", []) + stats.get("common_patterns", [])
                ))[:5]
                combined_stats[cat]["example_extractions"] = (
                    combined_stats[cat].get("example_extractions", []) + stats.get("example_extractions", [])
                )[:6]

    print(f"    Step 2 done: {step2_usage['total_tokens']} tokens")

    # ─── Step 3: Generate SKILL.md ───
    print(f"  [{case_id}] Step 3: Generating SKILL.md...")
    user_prompt = build_generate_user_prompt(combined_stats, case_json, cat_descs)
    skill_md, step3_usage = llm.call(GENERATE_SYSTEM, user_prompt)
    print(f"    Step 3 done: {step3_usage['total_tokens']} tokens")

    duration = time.time() - start_time

    # ─── Build evidence_index (contract-level) ───
    evidence_index = {}
    for summary in all_summaries:
        cid = summary.get("contract_id", "")
        for ext in summary.get("extractions", []):
            if ext.get("found"):
                cat = ext.get("category", "")
                if cat not in evidence_index:
                    evidence_index[cat] = {
                        "found_in_contracts": 0,
                        "total_contracts": len(train_cids),
                        "source_paragraphs": []
                    }
                evidence_index[cat]["found_in_contracts"] += 1
                if ext.get("source_paragraph"):
                    evidence_index[cat]["source_paragraphs"].append({
                        "contract_id": cid,
                        "paragraph_snippet": ext["source_paragraph"][:200]
                    })

    # Trim source_paragraphs to keep file manageable
    for cat in evidence_index:
        evidence_index[cat]["source_paragraphs"] = evidence_index[cat]["source_paragraphs"][:10]

    # ─── Write outputs ───
    total_usage = {
        "prompt_tokens": step1_usage["prompt_tokens"] + step2_usage["prompt_tokens"] + step3_usage["prompt_tokens"],
        "completion_tokens": step1_usage["completion_tokens"] + step2_usage["completion_tokens"] + step3_usage["completion_tokens"],
        "total_tokens": step1_usage["total_tokens"] + step2_usage["total_tokens"] + step3_usage["total_tokens"],
    }

    manifest = {
        "method": METHOD_NAME,
        "case_id": case_id,
        "model": llm.model,
        "pipeline": {
            "step1_extract": {
                "contracts_processed": len(all_summaries),
                "llm_calls": len(all_summaries),
            },
            "step2_merge": {
                "batches": len(merged_results),
                "llm_calls": len(merged_results),
            },
            "step3_generate": {"llm_calls": 1},
        },
        "usage": total_usage,
        "duration_seconds": round(duration, 2),
    }

    generation_log = {
        "step1_summaries": all_summaries[:5],  # Keep first 5 for reference
        "step2_merged": combined_stats,
        "step3_skill_md": skill_md,
    }

    writer.write_all(
        skill_md=skill_md,
        manifest=manifest,
        evidence_index=evidence_index,
        security_policy={},
        generation_log=generation_log,
    )

    print(f"  [{case_id}] Done in {duration:.1f}s, {total_usage['total_tokens']} total tokens")
    return {"skipped": False, "usage": total_usage, "duration": duration}


def main():
    parser = argparse.ArgumentParser(description="Baseline 3: summary2skill")
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
    print(f"Pipeline: 306 extract + 2 merge + 1 generate = 309 LLM calls/case")
    print()

    if args.dry_run:
        for case_id in case_ids:
            print(f"  [{case_id}] Would process 306 contracts")
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
