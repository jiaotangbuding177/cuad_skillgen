# τ-bench Document-to-Skill 实验子工程

本目录保存原始 τ-bench 资源、规范化数据、七种 Skill 基线、增量运行脚本、实验结果和论文协议。它与现有 CUAD 实验隔离，不修改 `D:\skillgen\scripts` 或原结果。

## 当前状态

- 已冻结官方原版仓库提交：`59a200c6d575d595120f1cb70fea53cef0632f6b`。
- 原版上游已标记任务过时并推荐 τ³-bench；本目录保留原版用于复现 2024 年 τ-bench 论文，后续适配必须作为独立版本报告。
- 已规范化 retail 的 500/20/115 个 train/dev/test 任务和 airline 的 50 个 test 任务。
- 已生成七种方法、两个领域的 deterministic bootstrap Skill package。
- 已运行一个真实 retail dev 任务的全链路 mock；它是工程校验，不是论文结果。
- live runner 已实现，但尚未安装或调用付费模型依赖。

## 一键增量执行

```powershell
cd D:\skillgen\τ-bench
python scripts/run_pipeline.py --skip-fetch
```

各阶段默认根据 manifest 和输入哈希跳过已完成产物；仅在明确需要重建时使用 `--force`。

```powershell
python scripts/fetch_resources.py
python scripts/prepare_dataset.py --domain all
python scripts/generate_skills.py --method all --domain all
python scripts/run_mock_case.py --method graph_evoskill_compiler
python scripts/evaluate_runs.py
python -m unittest discover -s tests -v
```

## 正式统一模型生成

Bootstrap 与正式生成分目录保存。正式生成要求所有方法使用同一个 OpenAI-compatible 模型：

```powershell
$env:TAU_LLM_BASE_URL="https://YOUR-ENDPOINT/v1"
$env:TAU_LLM_API_KEY="..."
python scripts/generate_skills.py `
  --backend openai_compatible `
  --model YOUR_FROZEN_MODEL `
  --method all `
  --domain all
```

正式产物默认进入 `skills_formal/<method>/<domain>`，不会覆盖 `skills/` 下的 bootstrap。缓存键包含输入哈希、后端和模型。

## 正式 live 运行

先在独立 Python 环境安装冻结的上游依赖：

```powershell
python -m pip install -e vendor/tau-bench
```

示例仅展示接口；模型和 provider 必须在所有方法间冻结一致：

```powershell
python scripts/run_live_tau.py `
  --method graph_evoskill_compiler `
  --skills-root skills_formal `
  --domain retail `
  --split test `
  --model YOUR_MODEL `
  --model-provider YOUR_PROVIDER `
  --user-model YOUR_USER_MODEL `
  --user-model-provider YOUR_USER_PROVIDER `
  --run-id retail-test-v1 `
  --num-trials 4
```

每个 `task_id × trial` 单独写入结果文件，重启后自动跳过。聚合命令：

```powershell
python scripts/evaluate_live_runs.py --run-root results/runs/retail-test-v1
```

## 文档

- [数据组织](docs/DATA_ORGANIZATION.md)
- [实验协议](docs/EXPERIMENT_PROTOCOL.md)
- [完整 Mock 案例](docs/MOCK_CASE.md)
- [指标设计](docs/METRICS.md)
