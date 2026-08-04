# Package-Aware Runtime Experiment

This track evaluates each generated skill package with the same runtime while
keeping training-derived knowledge separate from target-contract evidence.

## Protocol

1. Generate skills from the 306 training contracts.
2. Tune chunk size and retrieval top-k on the 102 development contracts.
3. Freeze runtime settings.
4. Evaluate once on the 102 test contracts plus the shared governance tasks.
5. Map verified target-contract spans to CUAD gold evidence units offline.

Runtime outputs are written to:

```text
results/skillgen/generated/{method}/package_runtime_results/{split}/{run-id}/
```

Files are append-only and flushed after every task. On resume, the latest row
for each `_task_id` is authoritative; successful tasks are skipped and errors
are retried.

## Commands

Small development smoke run:

```powershell
$env:ECNU_API_KEY="..."
python scripts/run_package_runtime.py --model ecnu-plus `
  --method evoskill_compiler --case-id assignment_and_control `
  --split dev --run-id dev-k10-k6 --max-tasks 20
```

Resume the same development run:

```powershell
python scripts/run_package_runtime.py --model ecnu-plus `
  --method evoskill_compiler --case-id assignment_and_control `
  --split dev --run-id dev-k10-k6
```

After choosing retrieval settings, run the frozen test track:

```powershell
python scripts/run_package_runtime.py --model ecnu-plus `
  --split test --run-id final-k10-k6
```

Recompute metrics without calling an LLM:

```powershell
python scripts/run_package_runtime.py --split test `
  --run-id final-k10-k6 --evaluate-only
```

The main deterministic metrics are task success, status accuracy, evidence
precision/recall/F1, boundary correctness, contract isolation, human-review
routing, external violation rate, validation failure rate, and API error rate.

Each run directory contains `run_config.json`. Incremental execution refuses to
mix a different model or retrieval configuration into an existing run ID.

## Fairness Rules

- All methods use the same chunker, retriever, prompt budget, target evidence
  validator, and gold mapper.
- Training evidence, summaries, and tool examples are search guidance only.
- Only exact spans verified in the target contract count as runtime evidence.
- Gold status, reference answers, and gold evidence are never exposed to the
  runtime agent.
