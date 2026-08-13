from __future__ import annotations

import argparse
import shutil
from collections import Counter
from typing import Any

from common import (
    DOMAINS,
    PROCESSED_ROOT,
    ROOT,
    UPSTREAM_DATA,
    UPSTREAM_SRC,
    flatten_user_instructions,
    normalize_action,
    read_json,
    sha256_file,
    split_markdown_sections,
    write_json,
    write_jsonl,
)


PRIMARY_SPLITS = {
    "retail": {"train": 74, "test": 40, "base": 114},
    "airline": {"train": 30, "test": 20, "base": 50},
    "telecom": {"train": 74, "test": 40, "base": 114, "full": 2285, "small": 20},
    "banking_knowledge": {"base": 97},
}


def load_policies(domain: str) -> list[dict[str, Any]]:
    root = UPSTREAM_DATA / domain
    if domain in {"retail", "airline"}:
        paths = [root / "policy.md"]
    elif domain == "telecom":
        paths = [root / "main_policy.md", root / "tech_support_manual.md"]
    else:
        paths = [root / "prompts" / "components" / "policy_header.md"]
    sections = []
    for path_index, path in enumerate(paths, 1):
        source = str(path.relative_to(ROOT)).replace("\\", "/")
        sections.extend(
            split_markdown_sections(
                path.read_text(encoding="utf-8"), domain, source, f"policy{path_index}"
            )
        )
    return sections


def load_tools(domain: str) -> list[dict[str, Any]]:
    files = [UPSTREAM_SRC / "domains" / domain / "tools.py"]
    user_tools = UPSTREAM_SRC / "domains" / domain / "user_tools.py"
    if user_tools.exists():
        files.append(user_tools)
    rows = []
    for path in files:
        text = path.read_text(encoding="utf-8")
        import ast

        tree = ast.parse(text, filename=str(path))
        for node in tree.body:
            if not isinstance(node, ast.ClassDef) or not node.name.endswith(("Tools", "ToolKit")):
                continue
            for fn in node.body:
                decorators = {
                    decorator.func.id
                    for decorator in fn.decorator_list
                    if isinstance(decorator, ast.Call) and isinstance(decorator.func, ast.Name)
                } if isinstance(fn, (ast.FunctionDef, ast.AsyncFunctionDef)) else set()
                if (
                    isinstance(fn, (ast.FunctionDef, ast.AsyncFunctionDef))
                    and not fn.name.startswith("_")
                    and "is_tool" in decorators
                ):
                    doc = ast.get_docstring(fn) or ""
                    parameters = [
                        arg.arg
                        for arg in fn.args.args
                        if arg.arg not in {"self", "cls"}
                    ]
                    rows.append(
                        {
                            "name": fn.name,
                            "requestor": "user" if path.name == "user_tools.py" else "assistant",
                            "parameters": parameters,
                            "description": doc,
                            "source": str(path.relative_to(ROOT)).replace("\\", "/"),
                        }
                    )
    if domain == "banking_knowledge":
        # The primary protocol fixes the official task-independent BM25 variant.
        # Its retrieval tool is defined in a mixin rather than tools.py.
        rows.append(
            {
                "name": "KB_search",
                "requestor": "assistant",
                "parameters": ["query"],
                "description": "Search the Banking knowledge base with the fixed BM25 pipeline and return the top-k source documents.",
                "source": "vendor/tau3-bench/src/tau2/domains/banking_knowledge/retrieval_mixins.py",
            }
        )
    return rows


def normalize_task(domain: str, task: dict[str, Any], memberships: list[str]) -> dict[str, Any]:
    criteria = task.get("evaluation_criteria", {})
    description = task.get("description") or {}
    return {
        "task_id": f"{domain}-{task['id']}",
        "source_task_id": task["id"],
        "domain": domain,
        "split_memberships": memberships,
        "user_instruction": flatten_user_instructions(task),
        "purpose": description.get("purpose") if isinstance(description, dict) else None,
        "initial_state": task.get("initial_state"),
        "ticket": task.get("ticket"),
        "gold": {
            "reference_actions": [normalize_action(action) for action in criteria.get("actions", [])],
            "environment_assertions": criteria.get("env_assertions") or [],
            "communicate_info": criteria.get("communicate_info") or [],
            "nl_assertions": criteria.get("nl_assertions") or [],
            "reward_basis": criteria.get("reward_basis") or [],
            "required_documents": task.get("required_documents") or [],
        },
        "metadata": {
            "annotations": task.get("annotations"),
            "user_tools": task.get("user_tools") or [],
            "reference_actions_are_unique_path": "ACTION" in (criteria.get("reward_basis") or []),
        },
    }


def prepare_domain(domain: str, force: bool) -> dict[str, Any]:
    target = PROCESSED_ROOT / domain
    done = target / "manifest.json"
    if done.exists() and not force:
        print(f"[{domain}] prepared output exists; skipping")
        return read_json(done)

    upstream = UPSTREAM_DATA / domain
    tasks = read_json(upstream / "tasks.json")
    split_map = (
        read_json(upstream / "split_tasks.json")
        if (upstream / "split_tasks.json").exists()
        else {"base": [task["id"] for task in tasks]}
    )
    memberships: dict[str, list[str]] = {str(task["id"]): [] for task in tasks}
    for split, ids in split_map.items():
        for task_id in ids:
            memberships.setdefault(str(task_id), []).append(split)
    normalized = [
        normalize_task(domain, task, memberships.get(str(task["id"]), []))
        for task in tasks
    ]

    documents = target / "documents"
    documents.mkdir(parents=True, exist_ok=True)
    policy_sections = load_policies(domain)
    write_jsonl(documents / "policy_sections.jsonl", policy_sections)
    write_json(documents / "tool_catalog.json", {"domain": domain, "tools": load_tools(domain)})
    for path in (
        [upstream / "policy.md"]
        if domain in {"retail", "airline"}
        else [upstream / "main_policy.md", upstream / "tech_support_manual.md"]
        if domain == "telecom"
        else [upstream / "prompts" / "components" / "policy_header.md"]
    ):
        shutil.copyfile(path, documents / path.name)

    if domain == "banking_knowledge":
        knowledge_rows = []
        for path in sorted((upstream / "documents").glob("*.json")):
            document = read_json(path)
            knowledge_rows.append(
                {
                    "document_id": document["id"],
                    "title": document.get("title", ""),
                    "content": document.get("content", ""),
                    "source": str(path.relative_to(ROOT)).replace("\\", "/"),
                }
            )
        write_jsonl(documents / "knowledge_documents.jsonl", knowledge_rows)
    else:
        knowledge_rows = []

    write_jsonl(target / "tasks" / "all.jsonl", normalized)
    for split, ids in split_map.items():
        selected = [task for task in normalized if str(task["source_task_id"]) in {str(i) for i in ids}]
        write_jsonl(target / "tasks" / f"{split}.jsonl", selected)

    action_counts: Counter[str] = Counter()
    reward_counts: Counter[str] = Counter()
    for task in normalized:
        action_counts.update(action["name"] for action in task["gold"]["reference_actions"])
        reward_counts.update(task["gold"]["reward_basis"])
    compilation_sources = [
        "documents/policy_sections.jsonl",
        "documents/tool_catalog.json",
    ]
    if domain == "banking_knowledge":
        compilation_sources.append("documents/knowledge_documents.jsonl")
    if "train" in split_map:
        compilation_sources.append("tasks/train.jsonl")
    manifest = {
        "benchmark": "tau3-bench",
        "domain": domain,
        "task_counts": {key: len(value) for key, value in split_map.items()},
        "primary_protocol": "base" if domain == "banking_knowledge" else "test",
        "compilation_sources": compilation_sources,
        "held_out_from_compilation": [
            f"tasks/{name}.jsonl" for name in split_map if name in {"test", "base"}
        ],
        "policy_sections": len(policy_sections),
        "tools": len(load_tools(domain)),
        "knowledge_documents": len(knowledge_rows),
        "reference_action_distribution": dict(sorted(action_counts.items())),
        "reward_basis_distribution": dict(sorted(reward_counts.items())),
        "task_source_sha256": sha256_file(upstream / "tasks.json"),
        "warning": "Reference actions define a target state, not a unique required trajectory, unless ACTION is in reward_basis.",
    }
    write_json(done, manifest)
    print(
        f"[{domain}] tasks={len(normalized)}, splits={manifest['task_counts']}, "
        f"policy={len(policy_sections)}, tools={manifest['tools']}, kb={len(knowledge_rows)}"
    )
    return manifest


def main() -> None:
    parser = argparse.ArgumentParser(description="Normalize tau3-bench into SOP-SkillBench")
    parser.add_argument("--domain", choices=[*DOMAINS, "all"], default="all")
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()
    if not (ROOT / "data" / "raw" / "source_manifest.json").exists():
        raise SystemExit("Run scripts/fetch_resources.py first")
    domains = DOMAINS if args.domain == "all" else (args.domain,)
    manifests = [prepare_domain(domain, args.force) for domain in domains]
    write_json(PROCESSED_ROOT / "manifest.json", {"benchmark": "tau3-bench", "domains": manifests})


if __name__ == "__main__":
    main()
