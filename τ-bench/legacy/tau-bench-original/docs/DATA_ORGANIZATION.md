# 数据组织

## 目录结构

```text
τ-bench/
├── vendor/tau-bench/                 # 冻结的官方原版仓库，不在其中写实验产物
├── config/experiment.json            # 正式实验冻结参数
├── data/
│   ├── raw/source_manifest.json      # 上游提交、许可、文件哈希
│   └── processed/
│       ├── manifest.json
│       ├── retail/
│       │   ├── manifest.json
│       │   ├── documents/
│       │   │   ├── policy.md
│       │   │   ├── policy_sections.jsonl
│       │   │   ├── runtime_rules.json
│       │   │   └── tool_catalog.json
│       │   └── tasks/{train,dev,test}.jsonl
│       └── airline/
│           ├── manifest.json
│           ├── documents/...
│           └── tasks/test.jsonl
├── skills/<method>/<domain>/         # 每种基线的 Skill package
├── results/
│   ├── mock/                         # 确定性工程 mock
│   ├── evaluation/                   # mock 聚合
│   └── runs/<run-id>/                # 正式 task×trial 增量结果
├── scripts/                          # 拉取、转换、生成、运行、评测
├── docs/                             # 论文实验协议
└── tests/                            # 泄漏边界与产物测试
```

## 数据规模

| Domain | Train | Dev | Test | Policy sections | Tools |
|---|---:|---:|---:|---:|---:|
| Retail | 500 | 20 | 115 | 8 | 16 |
| Airline | — | — | 50 | 6 | 14 |

上述数字来自冻结提交的本地转换结果，而不是推测值。

## 统一任务记录

```json
{
  "task_id": "retail-dev-0000",
  "source_index": 0,
  "domain": "retail",
  "split": "dev",
  "user_id": "olivia_ito_3591",
  "user_instruction": "...",
  "gold": {
    "actions": [
      {
        "name": "cancel_pending_order",
        "arguments": {
          "order_id": "#W5442520",
          "reason": "no longer needed"
        }
      }
    ],
    "outputs": []
  },
  "metadata": {
    "annotator": "",
    "source_file": "tau_bench/envs/retail/tasks_dev.py"
  }
}
```

## Skill package 协议

所有方法均输出：

- `SKILL.md`：运行时 system policy；
- `manifest.json`：输入哈希、方法、后端、数据使用边界和产物计数；
- `evidence_index.json`：政策段、运行规则和工具契约的可追溯知识单元；
- `security_policy.json`：显式治理规则；
- `workflow_patterns.json`：仅从 train 动作序列统计的工作流模式。

GESC额外输出：

- `knowledge_graph.json`；
- `pattern_cards.json`。

## 泄漏控制

Retail 编译可使用 `policy + runtime rules + tool contracts + train tasks`，但禁止读取 dev/test。Airline 原版没有 train/dev，因此只能使用 `policy + runtime rules + tool contracts`。不得用 airline test 动作、historical trajectories 或模型失败轨迹生成 Skill。

这一不对称必须保留在主表中：airline 更接近零样本 SOP 编译，retail 同时支持从训练工作流归纳模式。不能把二者混成同一种监督条件。

