from __future__ import annotations

import argparse
import json
import sys
import subprocess
from datetime import datetime, timezone
from pathlib import Path

from common import ROOT, default_model_name, resolve_litellm_model, sha256_file, write_json
from runtime.package_runtime import ProgressiveConfig, ProgressiveSkillPackage, RetrievalConfig, SkillPackage


VENDOR_SRC = ROOT / "vendor" / "tau3-bench" / "src"
RUNTIME_ADAPTER = """# Fixed SkillGen runtime contract

The following contract is identical for every experimental method.
- Use only tools exposed by the current tau3 environment.
- Respect tool actor ownership. Never call a user tool as the assistant; explain the action and let the simulated user perform it.
- Check policy preconditions before consequential writes and verify the resulting state.
- A reference trajectory, when one exists, is not visible to you and is not necessarily the only valid trajectory.
- Do not claim completion until required state and communication outcomes are supported by observations.
"""


def main() -> None:
    parser = argparse.ArgumentParser(description="Run one Skill package in the official tau3 runtime")
    parser.add_argument("--method", required=True)
    parser.add_argument("--domain", choices=["retail", "airline", "telecom", "banking_knowledge"], required=True)
    parser.add_argument("--agent-model")
    parser.add_argument("--user-model")
    parser.add_argument("--split")
    parser.add_argument("--task-set")
    parser.add_argument("--task-id", action="append")
    parser.add_argument("--num-tasks", type=int)
    parser.add_argument("--num-trials", type=int, default=1)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--max-concurrency", type=int, default=4)
    parser.add_argument("--max-steps", type=int, default=100)
    parser.add_argument("--run-id")
    parser.add_argument("--retrieval-config")
    parser.add_argument("--retrieval-top-k", type=int)
    parser.add_argument("--skill-root", default=str(ROOT / "skills"))
    parser.add_argument(
        "--runtime-mode",
        choices=["prompt_only", "package_v1", "full_injection", "hard_progressive_advisory"],
        default="hard_progressive_advisory",
    )
    parser.add_argument("--package-atom-top-k", type=int, default=6)
    parser.add_argument("--package-skill-top-k", type=int, default=4)
    parser.add_argument("--package-rule-top-k", type=int, default=3)
    parser.add_argument("--package-workflow-top-k", type=int, default=3)
    parser.add_argument("--package-pattern-top-k", type=int, default=3)
    parser.add_argument("--package-max-context-chars", type=int, default=12000)
    parser.add_argument("--package-max-item-chars", type=int, default=1800)
    parser.add_argument("--package-history-messages", type=int, default=6)
    parser.add_argument("--progressive-max-catalog-chars", type=int, default=12000)
    parser.add_argument("--progressive-max-module-chars", type=int, default=9000)
    parser.add_argument("--progressive-max-active-modules", type=int, default=2)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    agent_model = args.agent_model or default_model_name()
    if not agent_model:
        raise SystemExit(
            "No model configured. Pass --agent-model/--user-model or set "
            "TAU3_MODEL_NAME in τ-bench/.env."
        )
    args.agent_model = resolve_litellm_model(agent_model)
    args.user_model = resolve_litellm_model(args.user_model or agent_model)

    skill_path = Path(args.skill_root) / args.method / args.domain / "SKILL.md"
    if not skill_path.exists():
        raise SystemExit(f"Missing Skill package: {skill_path}")
    skill = skill_path.read_text(encoding="utf-8")
    retrieval_config = RetrievalConfig(
        skill_top_k=args.package_skill_top_k,
        atom_top_k=args.package_atom_top_k,
        rule_top_k=args.package_rule_top_k,
        workflow_top_k=args.package_workflow_top_k,
        pattern_top_k=args.package_pattern_top_k,
        max_context_chars=args.package_max_context_chars,
        max_item_chars=args.package_max_item_chars,
        history_messages=args.package_history_messages,
    )
    package = SkillPackage(skill_path.parent, args.domain, retrieval_config)
    progressive_package = ProgressiveSkillPackage(
        skill_path.parent, args.domain,
        ProgressiveConfig(
            max_catalog_chars=args.progressive_max_catalog_chars,
            max_module_chars=args.progressive_max_module_chars,
            max_active_modules=args.progressive_max_active_modules,
        ),
    )
    run_id = args.run_id or f"{args.method}-{args.domain}-{args.seed}"
    output = ROOT / "results" / "runs" / run_id
    output.mkdir(parents=True, exist_ok=True)
    split = args.split or ("base" if args.domain == "banking_knowledge" else "test")
    manifest = {
        "benchmark": "tau3-bench",
        "run_id": run_id,
        "method": args.method,
        "domain": args.domain,
        "split": split,
        "task_set": args.task_set,
        "task_ids": args.task_id,
        "num_tasks": args.num_tasks,
        "num_trials": args.num_trials,
        "seed": args.seed,
        "max_concurrency": args.max_concurrency,
        "max_steps": args.max_steps,
        "agent_model": args.agent_model,
        "user_model": args.user_model,
        "skill_path": str(skill_path),
        "skill_sha256": sha256_file(skill_path),
        "runtime_adapter_sha256": __import__("hashlib").sha256(RUNTIME_ADAPTER.encode()).hexdigest(),
        "runtime_mode": args.runtime_mode,
        "package": progressive_package.describe() if args.runtime_mode in {"full_injection", "hard_progressive_advisory"} else package.describe(),
        "retrieval_config": args.retrieval_config,
        "retrieval_top_k": args.retrieval_top_k,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "dry_run": args.dry_run,
        "status": "planned" if args.dry_run else "running",
    }
    manifest_path = output / "run_manifest.json"
    if manifest_path.exists():
        existing = json.loads(manifest_path.read_text(encoding="utf-8"))
        if existing.get("status") == "complete":
            identity_keys = [
                "method", "domain", "split", "task_set", "task_ids", "num_tasks",
                "num_trials", "seed", "max_concurrency", "max_steps",
                "agent_model", "user_model", "retrieval_config", "retrieval_top_k",
                "skill_sha256", "runtime_adapter_sha256", "runtime_mode",
                "package",
            ]
            mismatches = {
                key: {"existing": existing.get(key), "requested": manifest.get(key)}
                for key in identity_keys if existing.get(key) != manifest.get(key)
            }
            if mismatches:
                raise SystemExit(
                    f"Run id {run_id!r} already completed with incompatible configuration: "
                    + json.dumps(mismatches, ensure_ascii=False)
                )
            print(json.dumps({"run_id": run_id, "status": "already_complete"}, ensure_ascii=False, indent=2))
            return
    write_json(manifest_path, manifest)
    if args.dry_run:
        print(json.dumps(manifest, ensure_ascii=False, indent=2))
        return

    sys.path.insert(0, str(VENDOR_SRC))
    from tau2.agent.llm_agent import LLMAgent
    from tau2.data_model.simulation import TextRunConfig
    from tau2.registry import registry
    from tau2.runner.batch import run_domain
    from runtime.package_agent import PackageAwareAgent, ProgressiveSkillAgent

    # Route the optional NL-assertion / env-interface judge LLMs through the same
    # gateway as the agent. Their defaults are hardcoded gpt-4.1, which a private
    # OpenAI-compatible gateway may not serve. Patch before the evaluator imports.
    import tau2.config as _tau2_config
    _tau2_config.DEFAULT_LLM_NL_ASSERTIONS = args.agent_model
    _tau2_config.DEFAULT_LLM_ENV_INTERFACE = args.agent_model

    def create_skillgen_agent(tools, domain_policy, **kwargs):
        del domain_policy  # Each package already contains its allowed policy source.
        retrieval_adapter = ""
        if args.domain == "banking_knowledge":
            retrieval_adapter = (
                "\n# Banking retrieval interface\n"
                "The service knowledge corpus is external to the prompt. Use the available "
                "`KB_search` tool before making product or policy claims; cite retrieved document IDs "
                "internally and do not invent an answer when retrieval is insufficient.\n"
            )
        if args.runtime_mode == "package_v1":
            return PackageAwareAgent(
                tools=tools, fixed_adapter=RUNTIME_ADAPTER,
                retrieval_adapter=retrieval_adapter, package=package,
                llm=kwargs.get("llm"), llm_args=kwargs.get("llm_args"),
            )
        if args.runtime_mode == "hard_progressive_advisory":
            return ProgressiveSkillAgent(
                tools=tools, fixed_adapter=RUNTIME_ADAPTER,
                retrieval_adapter=retrieval_adapter, package=progressive_package,
                llm=kwargs.get("llm"), llm_args=kwargs.get("llm_args"),
            )
        if args.runtime_mode == "full_injection":
            modules = "\n\n".join(
                module.get("instructions", "") for module in progressive_package.modules.values()
            )
            return LLMAgent(
                tools=tools,
                domain_policy=RUNTIME_ADAPTER + retrieval_adapter + "\n\n" + modules,
                llm=kwargs.get("llm"), llm_args=kwargs.get("llm_args"),
            )
        return LLMAgent(tools=tools, domain_policy=RUNTIME_ADAPTER + retrieval_adapter + "\n\n" + skill, llm=kwargs.get("llm"), llm_args=kwargs.get("llm_args"))

    registry.register_agent_factory(create_skillgen_agent, f"skillgen:{run_id}")
    retrieval_kwargs = {"top_k": args.retrieval_top_k} if args.retrieval_top_k else None
    config = TextRunConfig(
        domain=args.domain,
        task_set_name=args.task_set,
        task_split_name=split,
        task_ids=args.task_id,
        num_tasks=args.num_tasks,
        num_trials=args.num_trials,
        seed=args.seed,
        max_concurrency=args.max_concurrency,
        max_steps=args.max_steps,
        agent=f"skillgen:{run_id}",
        llm_agent=args.agent_model,
        llm_user=args.user_model,
        llm_args_agent={"temperature": 0.0},
        llm_args_user={"temperature": 0.0},
        retrieval_config=args.retrieval_config,
        retrieval_config_kwargs=retrieval_kwargs,
        save_to=f"skillgen-{run_id}",
        auto_resume=True,
    )
    try:
        results = run_domain(config)
        results_path = output / "results.json"
        results.save(results_path)
        subprocess.run([sys.executable, str(ROOT / "scripts" / "evaluate_results.py"), str(results_path)], cwd=ROOT, check=True)
        subprocess.run([sys.executable, str(ROOT / "scripts" / "extract_audit_trace.py"), str(results_path)], cwd=ROOT, check=True)
        subprocess.run([sys.executable, str(ROOT / "scripts" / "evaluate_action_metrics.py"), str(results_path)], cwd=ROOT, check=True)
        subprocess.run([sys.executable, str(ROOT / "scripts" / "evaluate_extended_metrics.py"), str(results_path), "--domain", args.domain], cwd=ROOT, check=True)
        manifest["dry_run"] = False
        manifest["status"] = "complete"
        manifest["completed_simulations"] = len(results.simulations)
        write_json(manifest_path, manifest)
    except Exception as exc:
        manifest["status"] = "failed"
        manifest["error"] = {"type": type(exc).__name__, "message": str(exc)}
        write_json(manifest_path, manifest)
        raise


if __name__ == "__main__":
    main()
