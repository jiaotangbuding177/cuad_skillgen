from __future__ import annotations

import argparse
import hashlib
import json
import subprocess

from common import ROOT, default_model_name, read_json, resolve_litellm_model, sha256_file, write_json
from run_agent_runtime import RUNTIME_ADAPTER


def command_for(method: str, domain: str, seed: int, config: dict, args) -> list[str]:
    run_id = f"{args.run_prefix}-{method}-{domain}-s{seed}"
    command = [
        str(ROOT / "vendor" / "tau3-bench" / ".venv" / "Scripts" / "python.exe"),
        str(ROOT / "scripts" / "run_agent_runtime.py"),
        "--method", method, "--domain", domain,
        "--agent-model", args.agent_model, "--user-model", args.user_model,
        "--split", config["main_protocol"][domain], "--seed", str(seed),
        "--num-trials", str(config["num_trials"]), "--max-concurrency", str(args.max_concurrency),
        "--max-steps", str(config["max_steps"]),
        "--run-id", run_id,
    ]
    runtime = config["runtime"]
    command += ["--runtime-mode", runtime["mode"]]
    if runtime["mode"] == "package_v1":
        command += [
            "--package-skill-top-k", str(runtime["skill_top_k"]),
            "--package-atom-top-k", str(runtime["atom_top_k"]),
            "--package-rule-top-k", str(runtime["rule_top_k"]),
            "--package-workflow-top-k", str(runtime["workflow_top_k"]),
            "--package-pattern-top-k", str(runtime["pattern_top_k"]),
            "--package-max-context-chars", str(runtime["max_context_chars"]),
            "--package-max-item-chars", str(runtime["max_item_chars"]),
            "--package-history-messages", str(runtime["history_messages"]),
        ]
    if runtime["mode"] in {"hard_progressive_advisory", "full_injection"}:
        command += [
            "--progressive-max-catalog-chars", str(runtime["max_catalog_chars"]),
            "--progressive-max-module-chars", str(runtime["max_module_chars"]),
            "--progressive-max-active-modules", str(runtime["max_active_modules"]),
        ]
    if domain == "banking_knowledge":
        banking = config["banking_retrieval"]
        command += ["--retrieval-config", banking["config"], "--retrieval-top-k", str(banking["top_k"])]
    if args.num_tasks:
        command += ["--num-tasks", str(args.num_tasks)]
    if args.dry_run:
        command.append("--dry-run")
    return command


def main() -> None:
    parser = argparse.ArgumentParser(description="Incremental tau3 main/ablation experiment matrix")
    parser.add_argument("--agent-model")
    parser.add_argument("--user-model")
    parser.add_argument("--method", action="append")
    parser.add_argument("--domain", action="append")
    parser.add_argument("--seed", action="append", type=int)
    parser.add_argument("--num-tasks", type=int)
    parser.add_argument("--max-concurrency", type=int, default=4)
    parser.add_argument("--run-prefix", default="main")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--include-ablations", action="store_true")
    args = parser.parse_args()
    agent_model = args.agent_model or default_model_name()
    if not agent_model:
        raise SystemExit(
            "No model configured. Pass --agent-model/--user-model or set "
            "TAU3_MODEL_NAME in τ-bench/.env."
        )
    args.agent_model = resolve_litellm_model(agent_model)
    args.user_model = resolve_litellm_model(args.user_model or agent_model)
    config = read_json(ROOT / "config" / "experiment.json")
    default_methods = list(config["methods"])
    if args.include_ablations:
        default_methods.extend(config.get("ablation_methods", []))
    methods = args.method or default_methods
    domains = args.domain or list(config["main_protocol"])
    seeds = args.seed or config["seeds"]
    units = []
    for method in methods:
        for domain in domains:
            for seed in seeds:
                command = command_for(method, domain, seed, config, args)
                run_id = command[command.index("--run-id") + 1]
                manifest = ROOT / "results" / "runs" / run_id / "run_manifest.json"
                if manifest.exists() and read_json(manifest).get("status") == "complete":
                    existing = read_json(manifest)
                    expected = {
                        "method": method, "domain": domain, "seed": seed,
                        "agent_model": args.agent_model, "user_model": args.user_model,
                        "split": config["main_protocol"][domain],
                        "runtime_mode": config["runtime"]["mode"],
                        "num_trials": config["num_trials"], "num_tasks": args.num_tasks,
                        "max_concurrency": args.max_concurrency, "max_steps": config["max_steps"],
                        "skill_sha256": sha256_file(ROOT / "skills" / method / domain / "SKILL.md"),
                        "runtime_adapter_sha256": hashlib.sha256(RUNTIME_ADAPTER.encode()).hexdigest(),
                        "retrieval_config": (
                            config["banking_retrieval"]["config"] if domain == "banking_knowledge" else None
                        ),
                        "retrieval_top_k": (
                            config["banking_retrieval"]["top_k"] if domain == "banking_knowledge" else None
                        ),
                    }
                    mismatches = {
                        key: {"existing": existing.get(key), "requested": value}
                        for key, value in expected.items() if existing.get(key) != value
                    }
                    if config["runtime"]["mode"] in {"hard_progressive_advisory", "full_injection"}:
                        expected_package_config = {
                            "max_catalog_chars": config["runtime"]["max_catalog_chars"],
                            "max_module_chars": config["runtime"]["max_module_chars"],
                            "max_active_modules": config["runtime"]["max_active_modules"],
                        }
                        existing_package_config = (existing.get("package") or {}).get("config")
                        if existing_package_config != expected_package_config:
                            mismatches["package.config"] = {
                                "existing": existing_package_config,
                                "requested": expected_package_config,
                            }
                    if mismatches:
                        raise SystemExit(
                            f"Completed run {run_id!r} has incompatible configuration; use a new --run-prefix: "
                            + json.dumps(mismatches, ensure_ascii=False)
                        )
                    units.append({"run_id": run_id, "status": "skipped_complete"})
                    continue
                completed = subprocess.run(command, cwd=ROOT, check=False)
                status = "planned" if args.dry_run and completed.returncode == 0 else "complete" if completed.returncode == 0 else "failed"
                units.append({"run_id": run_id, "status": status, "returncode": completed.returncode, "command": command})
                write_json(ROOT / "results" / "matrix" / f"{args.run_prefix}.json", {"units": units})
                if completed.returncode != 0:
                    raise SystemExit(completed.returncode)
    print(json.dumps({"units": len(units), "status_counts": {s: sum(u["status"] == s for u in units) for s in set(u["status"] for u in units)}}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
