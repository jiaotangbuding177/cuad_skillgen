from __future__ import annotations

import argparse
import json
import os
import subprocess

from common import DOMAINS, ROOT, VENDOR_ROOT, read_json, write_json
from runtime.package_runtime import ProgressiveConfig, ProgressiveSkillPackage, RetrievalConfig, SkillPackage


def main() -> None:
    parser = argparse.ArgumentParser(description="Audit experimental readiness without exposing secret values")
    parser.add_argument("--require-live", action="store_true")
    parser.add_argument("--verbose", action="store_true")
    args = parser.parse_args()
    config = read_json(ROOT / "config" / "experiment.json")
    methods = config["methods"] + config.get("ablation_methods", [])
    checks = []
    def add(name, ok, detail):
        checks.append({"check": name, "ok": bool(ok), "detail": str(detail)})
    add("source_manifest", (ROOT / "data/raw/source_manifest.json").exists(), "frozen source manifest")
    commit = subprocess.run(["git", "-C", str(VENDOR_ROOT), "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip()
    add("upstream_commit", commit == "668d3bcd135c02aa3438f987ef45735b7c163ee3", commit)
    for domain in DOMAINS:
        manifest = ROOT / "data/processed" / domain / "manifest.json"
        add(f"data:{domain}", manifest.exists(), manifest)
    for method in methods:
        for domain in DOMAINS:
            package = ROOT / "skills" / method / domain
            manifest = package / "manifest.json"
            ok = (package / "SKILL.md").exists() and manifest.exists()
            if ok:
                meta = read_json(manifest)
                ok = not meta.get("uses_held_out_tasks", True)
            add(f"skill:{method}:{domain}", ok, package)
            if ok:
                try:
                    package_info = SkillPackage(package, domain, RetrievalConfig()).describe()
                    package_ok = bool(package_info["lane_counts"]["skill"]) and not package_info["graph_traversal_enabled"]
                    add(f"package_v1:{method}:{domain}", package_ok, package_info["lane_counts"])
                except Exception as exc:
                    add(f"package_v1:{method}:{domain}", False, f"{type(exc).__name__}: {exc}")
                try:
                    progressive = ProgressiveSkillPackage(
                        package, domain,
                        ProgressiveConfig(
                            max_catalog_chars=config["runtime"]["max_catalog_chars"],
                            max_module_chars=config["runtime"]["max_module_chars"],
                            max_active_modules=config["runtime"]["max_active_modules"],
                        ),
                    )
                    info = progressive.describe()
                    expected_modules = 0 if method == "no_skill" else 1
                    contract_ok = info["module_count"] >= expected_modules and not info["graph_traversal_enabled"]
                    add(f"progressive_v2:{method}:{domain}", contract_ok, info)
                except Exception as exc:
                    add(f"progressive_v2:{method}:{domain}", False, f"{type(exc).__name__}: {exc}")
    formal_root = ROOT / "skills_formal"
    formal_count = len(list(formal_root.glob("*/*/manifest.json"))) if formal_root.exists() else 0
    add("formal_skill_packages", formal_count == len(methods) * len(DOMAINS), f"{formal_count}/{len(methods) * len(DOMAINS)}")
    py312 = VENDOR_ROOT / ".venv" / "Scripts" / "python.exe"
    add("python_3_12_runtime", py312.exists(), py312)
    if py312.exists():
        probe = subprocess.run([str(py312), "-c", "import tau2; print('tau2-ok')"], cwd=VENDOR_ROOT, capture_output=True, text=True)
        add("tau3_import", probe.returncode == 0, probe.stdout.strip() or probe.stderr.strip())
    key_names = ["OPENAI_API_KEY", "ANTHROPIC_API_KEY", "GEMINI_API_KEY", "AZURE_API_KEY"]
    present = [name for name in key_names if os.environ.get(name)]
    add("live_model_credentials", bool(present), ", ".join(present) if present else "none detected")
    result_files = list((ROOT / "results" / "runs").glob("*/results.json")) if (ROOT / "results" / "runs").exists() else []
    add("live_results_exist", bool(result_files), f"{len(result_files)} results.json")
    optional = {"live_model_credentials", "live_results_exist", "formal_skill_packages"}
    required_ok = all(c["ok"] for c in checks if c["check"] not in optional)
    live_execution_ready = required_ok and any(c["ok"] for c in checks if c["check"] == "live_model_credentials")
    formal_results_ready = live_execution_ready and bool(result_files)
    report = {"offline_ready": required_ok, "live_execution_ready": live_execution_ready, "formal_results_ready": formal_results_ready, "checks": checks}
    write_json(ROOT / "results" / "preflight_report.json", report)
    rendered = report if args.verbose else {
        "offline_ready": required_ok,
        "live_execution_ready": live_execution_ready,
        "formal_results_ready": formal_results_ready,
        "checks": len(checks),
        "failed_required": [
            check["check"] for check in checks
            if not check["ok"] and check["check"] not in optional
        ],
        "unavailable_optional": [
            check["check"] for check in checks
            if not check["ok"] and check["check"] in optional
        ],
    }
    print(json.dumps(rendered, ensure_ascii=False, indent=2))
    if not required_ok or (args.require_live and not live_execution_ready):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
