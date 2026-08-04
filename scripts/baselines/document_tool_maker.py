"""
Baseline 4: document_tool_maker

Document-to-Tool generation baseline.
For each training contract, extract callable tool/function specs.
Merge all tool specs, then generate SKILL.md + tool_manifest.json.

Input: 306 contracts (processed one at a time)
Output: SKILL.md + tool_manifest.json + tool-level evidence_index
LLM calls: 306 (extract) + 1 (merge) + 1 (generate) = 308 per case
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

METHOD_NAME = "document_tool_maker"
MAX_CONTRACT_TOKENS = 13000
REQUIRED_OUTPUT_FILES = (
    "SKILL.md",
    "skill_manifest.json",
    "evidence_index.json",
    "security_policy.json",
    "generation_log.json",
    "tool_manifest.json",
)


EXTRACT_SYSTEM = """You are a contract review tool designer. From the following contract, extract reusable review tools (callable functions).

Each tool should:
1. Have a clear name (snake_case, prefixed with "check_")
2. Map to one of the specified review categories
3. Have a clear description of what it does
4. Define input parameters and return values
5. Include a real example from the current contract

Return your response as valid JSON only."""


def build_extract_user_prompt(contract_id: str, contract_text: str,
                               category_descriptions: list) -> str:
    parts = []
    parts.append(f"=== CONTRACT ===")
    parts.append(f"Contract ID: {contract_id}")
    parts.append(truncate_to_tokens(contract_text, MAX_CONTRACT_TOKENS))
    parts.append("")
    parts.append("=== CATEGORIES ===")
    for cd in category_descriptions:
        parts.append(f"- {cd['category']}: {cd['description']}")
    parts.append("")
    parts.append("=== TOOL SCHEMA ===")
    parts.append(json.dumps([
        {
            "tool_id": "tool_001",
            "name": "check_category_snake_case",
            "description": "One-sentence description of what this tool does",
            "category": "Must match one of the categories above",
            "parameters": {
                "contract_text": "string - Full contract text or relevant section",
                "target_clause": "string (optional) - Specific clause to examine"
            },
            "returns": {
                "found": "boolean - Whether the relevant clause was found",
                "extracted_text": "string - The exact text found in the contract",
                "confidence": "float 0.0-1.0",
                "explanation": "string - Review conclusion"
            },
            "example": {
                "input": "Example input from this contract",
                "output": {"found": True, "extracted_text": "Exact quote from contract",
                           "confidence": 0.95, "explanation": "Brief conclusion"}
            }
        }
    ], indent=2))
    parts.append("")
    parts.append("Extract ALL relevant tools from this contract. Each tool must have a real example from the contract text.")
    return "\n".join(parts)


MERGE_SYSTEM = """You are a contract review tool architect. Below are tool specifications extracted from multiple contracts.

Merge and deduplicate these tools:
1. Group tools by category
2. Remove duplicate tools (same name or same function)
3. For each unique tool, collect all source contracts and examples
4. Select the best example for each tool

Return your response as valid JSON only."""


def build_merge_user_prompt(all_tools: list) -> str:
    parts = []
    parts.append(f"=== ALL TOOLS ===")
    parts.append(f"Total tool specifications: {len(all_tools)}")
    parts.append("")
    for i, tools in enumerate(all_tools):
        parts.append(f"[Contract {i+1} Tools]")
        parts.append(json.dumps(tools, ensure_ascii=False))
        parts.append("")
    parts.append("=== OUTPUT SCHEMA ===")
    parts.append(json.dumps({
        "merged_tools": [
            {
                "tool_id": "tool_001",
                "name": "check_license_grant",
                "category": "License Grant",
                "description": "Checks for license grant clauses",
                "source_contracts": ["contract_id_1", "contract_id_2"],
                "best_example": {
                    "input": "...",
                    "output": {"found": True, "extracted_text": "...", "confidence": 0.95}
                }
            }
        ],
        "tool_stats": {
            "total_unique_tools": 0,
            "tools_by_category": {"Category": 0}
        }
    }, indent=2))
    return "\n".join(parts)


GENERATE_SYSTEM = """You are a contract review skill designer. Based on the merged tool specifications, generate a SKILL.md file.

The SKILL.md must contain these sections:

## Overview
Brief description of this skill and its available tools.

## Available Tools
For each tool: name, category, description, parameters, returns, and usage notes.

## Review Workflow
Step-by-step: how to select and use tools for a given review task.

## Output Format
JSON schema: {status, answer, evidence_unit_ids, source_contract_ids, missing_inputs, human_review_required}

## Boundary Rules
What the skill should and should not do.

Write clear, actionable tool descriptions. Reference the examples from real contracts."""


def _output_complete(output_dir: str) -> bool:
    return all(
        os.path.isfile(os.path.join(output_dir, name))
        and os.path.getsize(os.path.join(output_dir, name)) > 0
        for name in REQUIRED_OUTPUT_FILES
    )


def _load_step1_checkpoint(path: str, case_id: str, model: str) -> dict:
    latest = {}
    if not os.path.exists(path):
        return latest
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                continue
            record = json.loads(line)
            if record.get("type") == "metadata":
                if record.get("case_id") != case_id or record.get("model") != model:
                    raise RuntimeError(
                        f"Checkpoint {path} belongs to a different case or model. "
                        "Use --overwrite to start a new generation."
                    )
            elif record.get("contract_id"):
                latest[record["contract_id"]] = record
    return latest


def _initialize_step1_checkpoint(path: str, case_id: str, model: str) -> None:
    if os.path.exists(path):
        return
    with open(path, "w", encoding="utf-8") as f:
        f.write(json.dumps({
            "type": "metadata",
            "version": 1,
            "case_id": case_id,
            "model": model,
        }, ensure_ascii=False) + "\n")
        f.flush()


def _append_checkpoint(path: str, record: dict) -> None:
    with open(path, "a", encoding="utf-8", buffering=1) as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")
        f.flush()


def build_generate_user_prompt(merged_tools: dict, case_json: dict,
                                category_descriptions: list) -> str:
    parts = []
    parts.append("=== MERGED TOOL SPECIFICATIONS ===")
    parts.append(json.dumps(merged_tools, indent=2, ensure_ascii=False))
    parts.append("")
    parts.append("=== CASE DEFINITION ===")
    parts.append(f"Case ID: {case_json['case_id']}")
    parts.append("Covered Categories:")
    for cd in category_descriptions:
        parts.append(f"  - {cd['category']}: {cd['description']}")
    parts.append("")
    parts.append("=== INSTRUCTION ===")
    parts.append("Generate a SKILL.md based on the merged tool specifications above.")
    return "\n".join(parts)


def generate_skill_for_case(
    loader: CUADSkillGenLoader,
    case_id: str,
    llm: LLMClient,
    results_root: str,
    overwrite: bool = False,
) -> dict:
    writer = SkillOutputWriter(results_root, METHOD_NAME, case_id)

    if _output_complete(writer.output_dir) and not overwrite:
        print(f"  [{case_id}] Output already exists, skipping")
        return {"skipped": True}

    checkpoint_path = os.path.join(writer.output_dir, "step1_checkpoint.jsonl")
    if overwrite and os.path.exists(checkpoint_path):
        os.remove(checkpoint_path)

    start_time = time.time()

    # Load inputs
    case_json = loader.load_case_json(case_id)
    cat_descs = loader.get_category_descriptions_for_case(case_id)
    train_cids = loader.get_train_contract_ids()

    # ─── Step 1: Extract tool specs from each contract ───
    print(f"  [{case_id}] Step 1: Extracting tool specs from {len(train_cids)} contracts...")
    checkpoint = _load_step1_checkpoint(checkpoint_path, case_id, llm.model)
    _initialize_step1_checkpoint(checkpoint_path, case_id, llm.model)
    successful = sum(1 for item in checkpoint.values() if item.get("status") == "ok")
    failed = sum(1 for item in checkpoint.values() if item.get("status") == "error")
    if checkpoint:
        print(
            f"    Resuming checkpoint: successful={successful}, failed={failed}, "
            f"pending={len(train_cids) - successful}"
        )

    for i, cid in enumerate(train_cids):
        previous = checkpoint.get(cid)
        if previous and previous.get("status") == "ok":
            continue
        contract_text = loader.load_contract_text(cid)
        user_prompt = build_extract_user_prompt(cid, contract_text, cat_descs)
        try:
            tools, usage = llm.call_json(EXTRACT_SYSTEM, user_prompt)
            if isinstance(tools, list):
                normalized_tools = tools
            elif isinstance(tools, dict) and "tools" in tools:
                normalized_tools = tools["tools"]
            else:
                normalized_tools = []
            record = {
                "contract_id": cid,
                "status": "ok",
                "tools": normalized_tools,
                "usage": usage,
            }
        except Exception as e:
            print(f"    Warning: Contract {cid[:40]}... failed: {e}")
            record = {
                "contract_id": cid,
                "status": "error",
                "tools": [],
                "usage": {},
                "error": str(e),
            }
        checkpoint[cid] = record
        _append_checkpoint(checkpoint_path, record)

        if (i + 1) % 50 == 0:
            print(f"    Progress: {i+1}/{len(train_cids)}")

    failed_contracts = [
        cid for cid in train_cids
        if checkpoint.get(cid, {}).get("status") != "ok"
    ]
    if failed_contracts:
        raise RuntimeError(
            f"Step 1 incomplete for {len(failed_contracts)} contracts. "
            f"Re-run the same command to retry only failed contracts. "
            f"Checkpoint: {checkpoint_path}"
        )

    all_tools = [
        {"contract_id": cid, "tools": checkpoint[cid].get("tools", [])}
        for cid in train_cids
    ]
    step1_usage = {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0}
    for cid in train_cids:
        usage = checkpoint[cid].get("usage", {})
        for key in step1_usage:
            step1_usage[key] += usage.get(key, 0)

    total_tools_extracted = sum(len(t["tools"]) for t in all_tools)
    print(f"    Step 1 done: {total_tools_extracted} tools from {len(all_tools)} contracts, {step1_usage['total_tokens']} tokens")

    # ??? Step 2: Merge tool specs (by category to avoid truncation) ???
    print(f"  [{case_id}] Step 2: Merging tool specs by category...")
    
    # Collect all tools and group by category
    tools_by_category = {}
    for t in all_tools:
        if t["tools"]:
            for tool in t["tools"]:
                cat = tool.get("category", "Unknown")
                if cat not in tools_by_category:
                    tools_by_category[cat] = []
                tools_by_category[cat].append({
                    "name": tool.get("name", ""),
                    "category": cat,
                    "description": tool.get("description", ""),
                    "contract_id": t["contract_id"],
                })
    
    # Merge each category separately
    all_merged_tools = []
    step2_total_usage = {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0}
    
    for category, tools in tools_by_category.items():
        print(f"      Merging {category}: {len(tools)} tools...")
        
        # If too many tools in one category, batch them
        BATCH_SIZE = 100
        if len(tools) > BATCH_SIZE:
            # Split into batches
            batches = [tools[i:i+BATCH_SIZE] for i in range(0, len(tools), BATCH_SIZE)]
            category_merged = []
            
            for batch_idx, batch in enumerate(batches):
                tools_for_merge = [batch]  # Wrap in list for build_merge_user_prompt
                user_prompt = build_merge_user_prompt(tools_for_merge)
                try:
                    merged_batch, usage = llm.call_json(MERGE_SYSTEM, user_prompt)
                    for k in step2_total_usage:
                        step2_total_usage[k] += usage.get(k, 0)
                    category_merged.extend(merged_batch.get("merged_tools", []))
                except Exception as e:
                    print(f"        Warning: Batch {batch_idx+1} failed: {e}")
            
            # Final merge of all batches for this category
            if len(category_merged) > BATCH_SIZE:
                tools_for_merge = [category_merged]
                user_prompt = build_merge_user_prompt(tools_for_merge)
                try:
                    merged_category, usage = llm.call_json(MERGE_SYSTEM, user_prompt)
                    for k in step2_total_usage:
                        step2_total_usage[k] += usage.get(k, 0)
                    all_merged_tools.extend(merged_category.get("merged_tools", []))
                except Exception as e:
                    print(f"        Warning: Final merge for {category} failed: {e}")
                    all_merged_tools.extend(category_merged)
            else:
                all_merged_tools.extend(category_merged)
        else:
            # Small category, merge directly
            tools_for_merge = [tools]
            user_prompt = build_merge_user_prompt(tools_for_merge)
            try:
                merged_category, usage = llm.call_json(MERGE_SYSTEM, user_prompt)
                for k in step2_total_usage:
                    step2_total_usage[k] += usage.get(k, 0)
                all_merged_tools.extend(merged_category.get("merged_tools", []))
            except Exception as e:
                print(f"        Warning: Merge for {category} failed: {e}")
    
    # Build final merged result
    merged = {
        "merged_tools": all_merged_tools,
        "tool_stats": {
            "total_unique_tools": len(all_merged_tools),
            "tools_by_category": {cat: len([t for t in all_merged_tools if t.get("category") == cat]) for cat in tools_by_category.keys()}
        }
    }
    step2_usage = step2_total_usage
    print(f"    Step 2 done: {len(all_merged_tools)} unique tools, {step2_usage['total_tokens']} tokens")

    # ─── Step 3: Generate SKILL.md ───
    print(f"  [{case_id}] Step 3: Generating SKILL.md...")
    user_prompt = build_generate_user_prompt(merged, case_json, cat_descs)
    skill_md, step3_usage = llm.call(GENERATE_SYSTEM, user_prompt)
    if not isinstance(skill_md, str) or not skill_md.strip():
        raise RuntimeError("Step 3 returned an empty SKILL.md")
    print(f"    Step 3 done: {step3_usage['total_tokens']} tokens")

    duration = time.time() - start_time

    # ─── Build outputs ───
    # tool_manifest.json content (stored in manifest)
    merged_tools_list = merged.get("merged_tools", [])
    tool_stats = merged.get("tool_stats", {})

    # evidence_index: tool/example level
    evidence_index = {}
    for tool in merged_tools_list:
        tid = tool.get("tool_id", tool.get("name", ""))
        evidence_index[tid] = {
            "name": tool.get("name", ""),
            "category": tool.get("category", ""),
            "source_contracts": tool.get("source_contracts", []),
            "example": tool.get("best_example", {}),
        }

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
                "contracts_processed": len(all_tools),
                "total_tools_extracted": total_tools_extracted,
                "llm_calls": len(all_tools),
            },
            "step2_merge": {"llm_calls": 1},
            "step3_generate": {"llm_calls": 1},
        },
        "tool_manifest": {
            "total_unique_tools": len(merged_tools_list),
            "tools_by_category": tool_stats.get("tools_by_category", {}),
            "tools": merged_tools_list,
        },
        "usage": total_usage,
        "duration_seconds": round(duration, 2),
    }

    generation_log = {
        "step1_tools_sample": all_tools[:3],
        "step2_merged": merged,
        "step3_skill_md": skill_md,
    }

    writer.write_all(
        skill_md=skill_md,
        manifest=manifest,
        evidence_index=evidence_index,
        security_policy={},
        generation_log=generation_log,
    )

    # Also write tool_manifest.json as a separate file
    tool_manifest_path = os.path.join(writer.output_dir, "tool_manifest.json")
    with open(tool_manifest_path, "w", encoding="utf-8") as f:
        json.dump({
            "method": METHOD_NAME,
            "case_id": case_id,
            "total_tools": len(merged_tools_list),
            "tools": merged_tools_list,
        }, f, indent=2, ensure_ascii=False)

    if not _output_complete(writer.output_dir):
        missing = [
            name for name in REQUIRED_OUTPUT_FILES
            if not os.path.isfile(os.path.join(writer.output_dir, name))
            or os.path.getsize(os.path.join(writer.output_dir, name)) == 0
        ]
        raise RuntimeError(f"Generated package is incomplete: {missing}")

    print(f"  [{case_id}] Done in {duration:.1f}s, {total_usage['total_tokens']} total tokens, {len(merged_tools_list)} unique tools")
    return {"skipped": False, "usage": total_usage, "duration": duration}


def main():
    parser = argparse.ArgumentParser(description="Baseline 4: document_tool_maker")
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
    print(f"Pipeline: 306 extract + 1 merge + 1 generate = 308 LLM calls/case")
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
