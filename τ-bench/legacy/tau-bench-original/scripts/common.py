from __future__ import annotations

import ast
import hashlib
import json
import os
import tempfile
from collections import Counter
from pathlib import Path
from typing import Any, Iterable


ROOT = Path(__file__).resolve().parents[1]
VENDOR_ROOT = ROOT / "vendor" / "tau-bench"
PROCESSED_ROOT = ROOT / "data" / "processed"


def atomic_write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp_name = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as handle:
            handle.write(text)
        os.replace(tmp_name, path)
    finally:
        if os.path.exists(tmp_name):
            os.unlink(tmp_name)


def write_json(path: Path, value: Any) -> None:
    atomic_write_text(path, json.dumps(value, ensure_ascii=False, indent=2) + "\n")


def write_jsonl(path: Path, rows: Iterable[dict[str, Any]]) -> None:
    atomic_write_text(
        path,
        "".join(json.dumps(row, ensure_ascii=False) + "\n" for row in rows),
    )


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    with path.open("r", encoding="utf-8") as handle:
        return [json.loads(line) for line in handle if line.strip()]


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def git_head(path: Path) -> str:
    head = path / ".git" / "HEAD"
    if not head.exists():
        return "unknown"
    value = head.read_text(encoding="utf-8").strip()
    if value.startswith("ref: "):
        ref = path / ".git" / value[5:]
        return ref.read_text(encoding="utf-8").strip() if ref.exists() else value
    return value


def split_markdown_sections(text: str, domain: str) -> list[dict[str, Any]]:
    lines = text.splitlines()
    starts = [i for i, line in enumerate(lines) if line.startswith("#")]
    sections: list[dict[str, Any]] = []
    for index, start in enumerate(starts):
        end = starts[index + 1] if index + 1 < len(starts) else len(lines)
        heading = lines[start]
        level = len(heading) - len(heading.lstrip("#"))
        title = heading[level:].strip()
        body = "\n".join(lines[start + 1 : end]).strip()
        sections.append(
            {
                "section_id": f"{domain}-policy-{index + 1:03d}",
                "domain": domain,
                "title": title,
                "heading_level": level,
                "text": body,
                "source": f"tau_bench/envs/{domain}/wiki.md",
                "line_start": start + 1,
                "line_end": end,
            }
        )
    return sections


def _eval_task_node(node: ast.AST) -> Any:
    if isinstance(node, ast.Constant):
        return node.value
    if isinstance(node, ast.List):
        return [_eval_task_node(item) for item in node.elts]
    if isinstance(node, ast.Tuple):
        return [_eval_task_node(item) for item in node.elts]
    if isinstance(node, ast.Dict):
        return {
            _eval_task_node(key): _eval_task_node(value)
            for key, value in zip(node.keys, node.values)
        }
    if isinstance(node, ast.UnaryOp) and isinstance(node.op, ast.USub):
        return -_eval_task_node(node.operand)
    if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
        values = {item.arg: _eval_task_node(item.value) for item in node.keywords}
        if node.func.id == "Action":
            return {
                "name": values.get("name", ""),
                "arguments": values.get("kwargs", values.get("arguments", {})),
            }
        if node.func.id == "Task":
            values["actions"] = values.get("actions", [])
            return values
    raise ValueError(f"Unsupported task syntax: {ast.dump(node, include_attributes=False)[:300]}")


def parse_task_file(path: Path) -> list[dict[str, Any]]:
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    for statement in tree.body:
        if isinstance(statement, ast.Assign):
            names = [target.id for target in statement.targets if isinstance(target, ast.Name)]
            if any(name in {"tasks", "TASKS", "TASKS_TRAIN", "TASKS_DEV", "TASKS_TEST"} for name in names):
                rows = _eval_task_node(statement.value)
                normalized = []
                for row in rows:
                    actions = []
                    for action in row.get("actions", []):
                        actions.append(
                            {
                                "name": action.get("name", ""),
                                "arguments": action.get("arguments", action.get("kwargs", {})),
                            }
                        )
                    normalized.append({**row, "actions": actions})
                return normalized
    raise ValueError(f"No supported task assignment found in {path}")


def parse_literal_assignment(path: Path, variable: str) -> Any:
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    for statement in tree.body:
        if isinstance(statement, ast.Assign):
            if any(isinstance(target, ast.Name) and target.id == variable for target in statement.targets):
                return ast.literal_eval(statement.value)
    raise ValueError(f"{variable} not found in {path}")


def parse_tool_schema(path: Path) -> dict[str, Any]:
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name == "get_info":
            for statement in node.body:
                if isinstance(statement, ast.Return):
                    return ast.literal_eval(statement.value)
    raise ValueError(f"get_info return schema not found in {path}")


def action_signature(actions: list[dict[str, Any]]) -> str:
    return " -> ".join(action["name"] for action in actions) or "respond_only"


def workflow_counts(tasks: list[dict[str, Any]]) -> Counter[str]:
    return Counter(action_signature(task.get("gold", {}).get("actions", task.get("actions", []))) for task in tasks)

