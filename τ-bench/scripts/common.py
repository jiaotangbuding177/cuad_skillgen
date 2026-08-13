from __future__ import annotations

import hashlib
import json
import os
import tempfile
from pathlib import Path
from typing import Any, Iterable


ROOT = Path(__file__).resolve().parents[1]
VENDOR_ROOT = ROOT / "vendor" / "tau3-bench"
UPSTREAM_DATA = VENDOR_ROOT / "data" / "tau2" / "domains"
UPSTREAM_SRC = VENDOR_ROOT / "src" / "tau2"
PROCESSED_ROOT = ROOT / "data" / "processed"
DOMAINS = ("retail", "airline", "telecom", "banking_knowledge")


def load_env_file(path: Path) -> None:
    """Load KEY=VALUE entries from a .env file into os.environ without overriding
    already-set variables (standard dotenv semantics)."""
    if not path.exists():
        return
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if key and key not in os.environ:
            os.environ[key] = value


def default_model_name() -> str | None:
    """The model name configured in τ-bench/.env (TAU3_MODEL_NAME)."""
    return os.environ.get("TAU3_MODEL_NAME")


def resolve_litellm_model(name: str) -> str:
    """Prefix a bare model name with openai/ so LiteLLM routes it to the
    OpenAI-compatible gateway configured via OPENAI_BASE_URL in .env."""
    name = (name or "").strip()
    if not name:
        return name
    return name if "/" in name else f"openai/{name}"


# Load τ-bench/.env once, at import time, so every script that imports common
# automatically picks up the configured LLM credentials.
load_env_file(ROOT / ".env")

# Bridge LiteLLM standard names → τ³ compiler names.
# generate_skills.py reads TAU3_LLM_API_KEY / TAU3_LLM_BASE_URL for the
# OpenAI-compatible formal compiler, while the runtime (via LiteLLM) reads
# OPENAI_API_KEY / OPENAI_BASE_URL. One .env should serve both; if the user
# set the LiteLLM standard names but not the τ³ ones, fill the latter from
# the former.
if os.environ.get("OPENAI_API_KEY") and not os.environ.get("TAU3_LLM_API_KEY"):
    os.environ["TAU3_LLM_API_KEY"] = os.environ["OPENAI_API_KEY"]
if os.environ.get("OPENAI_BASE_URL") and not os.environ.get("TAU3_LLM_BASE_URL"):
    os.environ["TAU3_LLM_BASE_URL"] = os.environ["OPENAI_BASE_URL"]


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


def split_markdown_sections(
    text: str, domain: str, source: str, prefix: str = "policy"
) -> list[dict[str, Any]]:
    lines = text.splitlines()
    starts = [i for i, line in enumerate(lines) if line.startswith("#")]
    if not starts:
        return [
            {
                "section_id": f"{domain}-{prefix}-001",
                "domain": domain,
                "title": Path(source).stem,
                "heading_level": 0,
                "text": text.strip(),
                "source": source,
                "line_start": 1,
                "line_end": len(lines),
            }
        ]
    sections = []
    for index, start in enumerate(starts):
        end = starts[index + 1] if index + 1 < len(starts) else len(lines)
        heading = lines[start]
        level = len(heading) - len(heading.lstrip("#"))
        sections.append(
            {
                "section_id": f"{domain}-{prefix}-{index + 1:03d}",
                "domain": domain,
                "title": heading[level:].strip(),
                "heading_level": level,
                "text": "\n".join(lines[start + 1 : end]).strip(),
                "source": source,
                "line_start": start + 1,
                "line_end": end,
            }
        )
    return sections


def flatten_user_instructions(task: dict[str, Any]) -> str:
    instructions = task.get("user_scenario", {}).get("instructions", "")
    if isinstance(instructions, str):
        return instructions
    fields = [
        instructions.get("reason_for_call"),
        instructions.get("known_info"),
        instructions.get("unknown_info"),
        instructions.get("task_instructions"),
    ]
    return "\n\n".join(value for value in fields if value)


def normalize_action(action: dict[str, Any]) -> dict[str, Any]:
    return {
        "action_id": action.get("action_id"),
        "requestor": action.get("requestor", "assistant"),
        "name": action.get("name", ""),
        "arguments": action.get("arguments", {}),
        "compare_args": action.get("compare_args"),
        "info": action.get("info"),
    }

