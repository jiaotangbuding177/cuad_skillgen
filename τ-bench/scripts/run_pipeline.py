from __future__ import annotations

import argparse
import subprocess
import sys

from common import ROOT


def run(args: list[str]) -> None:
    print("+", " ".join(args))
    subprocess.run(args, cwd=ROOT, check=True)


def main() -> None:
    parser = argparse.ArgumentParser(description="Incremental tau3 data-to-skill pipeline")
    parser.add_argument("--force-prepare", action="store_true")
    parser.add_argument("--force-skills", action="store_true")
    parser.add_argument("--formal", action="store_true", help="Use the configured OpenAI-compatible compiler")
    parser.add_argument("--compiler-model")
    args = parser.parse_args()
    py = sys.executable
    run([py, "scripts/fetch_resources.py"])
    prepare = [py, "scripts/prepare_dataset.py"] + (["--force"] if args.force_prepare else [])
    run(prepare)
    generate = [py, "scripts/generate_skills.py", "--method", "all", "--domain", "all"]
    if args.force_skills:
        generate.append("--force")
    if args.formal:
        if not args.compiler_model:
            raise SystemExit("--formal requires --compiler-model")
        generate += ["--backend", "openai_compatible", "--model", args.compiler_model]
    run(generate)
    run([py, "scripts/audit_action_packages.py"])
    run([py, "scripts/build_mock_case.py"])
    run([py, "scripts/preflight.py"])


if __name__ == "__main__":
    main()
