from __future__ import annotations

import argparse
import subprocess

from common import ROOT, UPSTREAM_DATA, VENDOR_ROOT, git_head, sha256_file, write_json


UPSTREAM_URL = "https://github.com/sierra-research/tau2-bench.git"
PINNED_COMMIT = "668d3bcd135c02aa3438f987ef45735b7c163ee3"


def run(command: list[str]) -> None:
    subprocess.run(command, cwd=VENDOR_ROOT, check=True)


def main() -> None:
    parser = argparse.ArgumentParser(description="Verify and freeze tau3-bench resources")
    parser.add_argument("--force-fetch", action="store_true")
    args = parser.parse_args()
    if not (VENDOR_ROOT / ".git").exists():
        raise SystemExit(
            f"Missing {VENDOR_ROOT}. Clone {UPSTREAM_URL} at {PINNED_COMMIT} first."
        )
    if args.force_fetch:
        run(["git", "fetch", "origin", PINNED_COMMIT])
    if git_head(VENDOR_ROOT) != PINNED_COMMIT:
        run(["git", "checkout", PINNED_COMMIT])

    tracked = [
        VENDOR_ROOT / "LICENSE",
        VENDOR_ROOT / "README.md",
        VENDOR_ROOT / "pyproject.toml",
    ]
    for domain in ("retail", "airline", "telecom", "banking_knowledge"):
        domain_root = UPSTREAM_DATA / domain
        tracked.append(domain_root / "tasks.json")
        if (domain_root / "split_tasks.json").exists():
            tracked.append(domain_root / "split_tasks.json")
    tracked.extend(
        [
            UPSTREAM_DATA / "retail" / "policy.md",
            UPSTREAM_DATA / "airline" / "policy.md",
            UPSTREAM_DATA / "telecom" / "main_policy.md",
            UPSTREAM_DATA / "telecom" / "tech_support_manual.md",
            UPSTREAM_DATA / "banking_knowledge" / "prompts" / "components" / "policy_header.md",
        ]
    )
    manifest = {
        "dataset": "tau3-bench",
        "package_version": "1.0.1",
        "upstream_url": UPSTREAM_URL,
        "pinned_commit": PINNED_COMMIT,
        "checked_out_commit": git_head(VENDOR_ROOT),
        "license": "MIT",
        "primary_paper": "https://arxiv.org/abs/2506.07982",
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
    print(f"Frozen tau3-bench v1.0.1 at {manifest['checked_out_commit']}")


if __name__ == "__main__":
    main()

