from __future__ import annotations

import argparse
import subprocess
from pathlib import Path

from common import ROOT, VENDOR_ROOT, git_head, sha256_file, write_json


UPSTREAM_URL = "https://github.com/sierra-research/tau-bench.git"
PINNED_COMMIT = "59a200c6d575d595120f1cb70fea53cef0632f6b"


def run(command: list[str], cwd: Path | None = None) -> None:
    subprocess.run(command, cwd=cwd, check=True)


def main() -> None:
    parser = argparse.ArgumentParser(description="Fetch and freeze the original tau-bench resources")
    parser.add_argument("--force-fetch", action="store_true", help="Fetch remote objects even when the pinned checkout exists")
    args = parser.parse_args()

    if not (VENDOR_ROOT / ".git").exists():
        VENDOR_ROOT.parent.mkdir(parents=True, exist_ok=True)
        run(["git", "clone", "--filter=blob:none", UPSTREAM_URL, str(VENDOR_ROOT)])
    if args.force_fetch:
        run(["git", "fetch", "origin", PINNED_COMMIT], cwd=VENDOR_ROOT)
    if git_head(VENDOR_ROOT) != PINNED_COMMIT:
        run(["git", "checkout", PINNED_COMMIT], cwd=VENDOR_ROOT)

    tracked = [
        VENDOR_ROOT / "LICENSE",
        VENDOR_ROOT / "README.md",
        VENDOR_ROOT / "tau_bench" / "envs" / "retail" / "wiki.md",
        VENDOR_ROOT / "tau_bench" / "envs" / "airline" / "wiki.md",
        VENDOR_ROOT / "tau_bench" / "envs" / "retail" / "tasks_train.py",
        VENDOR_ROOT / "tau_bench" / "envs" / "retail" / "tasks_dev.py",
        VENDOR_ROOT / "tau_bench" / "envs" / "retail" / "tasks_test.py",
        VENDOR_ROOT / "tau_bench" / "envs" / "airline" / "tasks_test.py",
    ]
    manifest = {
        "dataset": "tau-bench-original",
        "upstream_url": UPSTREAM_URL,
        "pinned_commit": PINNED_COMMIT,
        "checked_out_commit": git_head(VENDOR_ROOT),
        "license": "MIT",
        "upstream_status": "deprecated_by_upstream_in_favor_of_tau3_bench",
        "paper": "https://arxiv.org/abs/2406.12045",
        "files": [
            {
                "path": str(path.relative_to(ROOT)).replace("\\", "/"),
                "sha256": sha256_file(path),
                "bytes": path.stat().st_size,
            }
            for path in tracked
        ],
    }
    write_json(ROOT / "data" / "raw" / "source_manifest.json", manifest)
    print(f"Frozen tau-bench at {manifest['checked_out_commit']}")


if __name__ == "__main__":
    main()

