# τ³-SkillBench 数据组织

```text
τ-bench/
├─ vendor/tau3-bench/                 # 冻结上游源码与数据（commit 668d3bc）
├─ data/
│  ├─ raw/source_manifest.json        # 来源、版本与哈希
│  └─ processed/<domain>/
│     ├─ documents/                   # policy sections、tool catalog、Banking KB
│     ├─ tasks/                       # all/train/test/base/full JSONL
│     └─ manifest.json                # 数量、编译源、held-out 边界
├─ skills/<method>/<domain>/
│  ├─ SKILL.md
│  ├─ evidence_index.json
│  ├─ security_policy.json
│  ├─ workflow_patterns.json
│  ├─ typed_atoms.json                 # 统一静态审计资产
│  ├─ tool_cards.json                  # 原子—工具编译中间产物
│  ├─ local_motifs.json                # 仅训练集支持的软局部模式
│  ├─ action_modules.json              # progressive runtime 的正式输入契约
│  ├─ knowledge_graph.json             # 仅图方法；G-A2SC 只在编译期读取
│  ├─ pattern_cards.json               # v1 graph baseline
│  └─ manifest.json
├─ config/experiment.json             # 冻结实验协议
├─ scripts/                            # 拉取、规范化、编译、runtime、评价与 mock
├─ results/
│  ├─ mock/
│  ├─ evaluation/                      # package audit、跨 run 汇总与统计
│  ├─ matrix/                          # 增量矩阵执行清单
│  └─ runs/<run-id>/
│     ├─ run_manifest.json
│     ├─ results.json
│     ├─ metrics.json
│     ├─ audit_trace.jsonl
│     ├─ audit_metrics.json
│     ├─ action_metrics.json
│     └─ extended_metrics.json
├─ docs/
├─ tests/
└─ legacy/tau-bench-original/         # 被替换的旧 τ-bench 链路，可恢复
```

## 关键 JSONL 契约

规范化 task 保留 `task_id/domain/split_memberships/user_instruction/initial_state`，评价标签统一放在 `gold` 下。该组织是为了离线审计，不表示 runtime 可以读取 `gold`。编译 source whitelist 写入各领域 manifest；生成器只按 whitelist 读取。

Banking 的 `knowledge_documents.jsonl` 是合法企业知识语料，`required_documents` 是任务级评价标签，两者必须分离。前者可编译/检索，后者只能在运行结束后计算 Recall@k/MRR。

## 复现顺序

```powershell
python scripts/fetch_resources.py
python scripts/prepare_dataset.py --force
python scripts/generate_skills.py --method all --domain all
python scripts/build_mock_case.py
python scripts/run_agent_runtime.py --method a2sc --domain telecom `
  --agent-model <model> --user-model <model> --num-tasks 1 --dry-run
```

移除 `--dry-run` 才会调用模型和官方 environment。正式运行后执行：

```powershell
python scripts/evaluate_results.py results/runs/<run-id>/results.json
python scripts/extract_audit_trace.py results/runs/<run-id>/results.json
python scripts/evaluate_action_metrics.py results/runs/<run-id>/results.json
```
