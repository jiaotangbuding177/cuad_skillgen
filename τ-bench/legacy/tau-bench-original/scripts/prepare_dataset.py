from __future__ import annotations

import argparse
import shutil
from collections import Counter
from pathlib import Path

from common import (
    PROCESSED_ROOT,
    ROOT,
    VENDOR_ROOT,
    parse_literal_assignment,
    parse_task_file,
    parse_tool_schema,
    sha256_file,
    split_markdown_sections,
    write_json,
    write_jsonl,
)


SPLIT_FILES = {
    "retail": {
        "train": "tasks_train.py",
        "dev": "tasks_dev.py",
        "test": "tasks_test.py",
    },
    "airline": {"test": "tasks_test.py"},
}


def normalize_tasks(domain: str, split: str, path: Path) -> list[dict]:
    tasks = parse_task_file(path)
    normalized = []
    for index, task in enumerate(tasks):
        actions = task.get("actions", [])
        normalized.append(
            {
                "task_id": f"{domain}-{split}-{index:04d}",
                "source_index": index,
                "domain": domain,
                "split": split,
                "user_id": task.get("user_id"),
                "user_instruction": task.get("instruction", ""),
                "gold": {
                    "actions": actions,
                    "outputs": task.get("outputs", []),
                },
                "metadata": {
                    "annotator": task.get("annotator", ""),
                    "source_file": str(path.relative_to(VENDOR_ROOT)).replace("\\", "/"),
                },
            }
        )
    return normalized


def prepare_domain(domain: str, force: bool) -> dict:
    source = VENDOR_ROOT / "tau_bench" / "envs" / domain
    target = PROCESSED_ROOT / domain
    done = target / "manifest.json"
    if done.exists() and not force:
        print(f"[{domain}] prepared output exists; skipping")
        return __import__("json").loads(done.read_text(encoding="utf-8"))

    policy_text = (source / "wiki.md").read_text(encoding="utf-8")
    rules = parse_literal_assignment(source / "rules.py", "RULES")
    tool_schemas = []
    for tool_file in sorted((source / "tools").glob("*.py")):
        if tool_file.name == "__init__.py":
            continue
        try:
            schema = parse_tool_schema(tool_file)
        except ValueError:
            continue
        schema["source"] = str(tool_file.relative_to(VENDOR_ROOT)).replace("\\", "/")
        tool_schemas.append(schema)

    documents = target / "documents"
    documents.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(source / "wiki.md", documents / "policy.md")
    write_jsonl(documents / "policy_sections.jsonl", split_markdown_sections(policy_text, domain))
    write_json(documents / "runtime_rules.json", {"domain": domain, "rules": rules})
    write_json(documents / "tool_catalog.json", {"domain": domain, "tools": tool_schemas})

    split_counts = {}
    action_counts: Counter[str] = Counter()
    for split, filename in SPLIT_FILES[domain].items():
        tasks = normalize_tasks(domain, split, source / filename)
        write_jsonl(target / "tasks" / f"{split}.jsonl", tasks)
        split_counts[split] = len(tasks)
        for task in tasks:
            action_counts.update(action["name"] for action in task["gold"]["actions"])

    manifest = {
        "domain": domain,
        "splits": split_counts,
        "training_task_use_allowed": "train" in split_counts,
        "compilation_sources": [
            "documents/policy.md",
            "documents/policy_sections.jsonl",
            "documents/runtime_rules.json",
            "documents/tool_catalog.json",
        ] + (["tasks/train.jsonl"] if "train" in split_counts else []),
        "held_out_from_compilation": [
            f"tasks/{split}.jsonl" for split in split_counts if split != "train"
        ],
        "policy_sha256": sha256_file(documents / "policy.md"),
        "policy_sections": len(split_markdown_sections(policy_text, domain)),
        "tools": len(tool_schemas),
        "gold_action_distribution_all_splits": dict(sorted(action_counts.items())),
    }
    write_json(done, manifest)
    print(f"[{domain}] {split_counts}, {len(tool_schemas)} tools, {manifest['policy_sections']} policy sections")
    return manifest


def main() -> None:
    parser = argparse.ArgumentParser(description="Normalize tau-bench into SOP-SkillBench records")
    parser.add_argument("--domain", choices=["retail", "airline", "all"], default="all")
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()
    if not (ROOT / "data" / "raw" / "source_manifest.json").exists():
        raise SystemExit("Run scripts/fetch_resources.py first")
    domains = ["retail", "airline"] if args.domain == "all" else [args.domain]
    manifests = [prepare_domain(domain, args.force) for domain in domains]
    write_json(PROCESSED_ROOT / "manifest.json", {"domains": manifests})


if __name__ == "__main__":
    main()

