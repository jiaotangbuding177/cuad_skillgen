from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

from common import ROOT


def run(script: str, *arguments: str) -> None:
    command = [sys.executable, str(ROOT / "scripts" / script), *arguments]
    print("+", " ".join(command), flush=True)
    subprocess.run(command, cwd=ROOT, check=True)


def main() -> None:
    parser = argparse.ArgumentParser(description="End-to-end incremental tau-bench Skill pipeline")
    parser.add_argument("--skip-fetch", action="store_true")
    parser.add_argument("--force", action="store_true")
    parser.add_argument("--domain", choices=["retail", "airline", "all"], default="all")
    parser.add_argument("--method", default="all")
    parser.add_argument("--skip-mock", action="store_true")
    parser.add_argument("--backend", choices=["deterministic_bootstrap", "openai_compatible"], default="deterministic_bootstrap")
    parser.add_argument("--model")
    parser.add_argument("--base-url")
    parser.add_argument("--output-root")
    args = parser.parse_args()
    force = ["--force"] if args.force else []
    if not args.skip_fetch:
        run("fetch_resources.py")
    run("prepare_dataset.py", "--domain", args.domain, *force)
    generation_args = ["--domain", args.domain, "--method", args.method, "--backend", args.backend]
    if args.model:
        generation_args.extend(["--model", args.model])
    if args.base_url:
        generation_args.extend(["--base-url", args.base_url])
    if args.output_root:
        generation_args.extend(["--output-root", args.output_root])
    run("generate_skills.py", *generation_args, *force)
    if not args.skip_mock and args.backend == "deterministic_bootstrap" and args.domain in {"retail", "all"}:
        mock_method = "graph_evoskill_compiler" if args.method == "all" else args.method
        run("run_mock_case.py", "--method", mock_method, *force)
        run("evaluate_runs.py")


if __name__ == "__main__":
    main()
