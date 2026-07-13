# CUAD-SkillGen

**Document-to-Skill 生成基准数据集**：从 [CUAD v1](https://github.com/theattorneyproject/CUAD)（Contract Understanding Atticus Dataset）转化而来，用于评估企业合同审查智能体的 Skill 生成与运行时行为。

---

## 概述

CUAD-SkillGen 将 CUAD v1 的 510 份合同、20,910 个 QA 转化为 **Skill 生成 + 运行时评价** 标准格式：

| 维度 | 数据 |
|---|---|
| 合同数 | 510 |
| 审查类别 | 41（归纳为 9 个能力包） |
| Evidence Units | 13,823（CUAD 专家 span 标注） |
| 运行时 Tasks | 21,396（6,702 answered + 14,208 evidence_missing + 486 governance） |
| 数据划分 | train 306 / dev 102 / test 102（按合同划分，60/20/20） |

### 设计目标

- **Skill 生成评估**：评估不同方法从合同语料自动生成可调用 Skill 的能力
- **运行时行为评估**：评估 Skill 在实际审查任务中的正确性和安全性
- **治理边界测试**：测试智能体在能力边界外的拒绝、请求缺失信息、路由人工复核能力
- **可审计性**：每条任务有明确的 gold 标准、来源标注和约束条件

---

## 数据集结构

```
data/cuad_skillgen/
├── corpus/
│   ├── contracts/                          # 510 份合同全文 (.txt)
│   ├── contract_metadata.jsonl             # 合同元数据（510 条）
│   ├── category_descriptions.jsonl         # 41 个类别描述
│   └── category_to_case_mapping.json       # 类别 → 能力包映射
├── cases/                                  # 9 个能力包
│   ├── contract_basic_info/
│   │   ├── case.json                       # 能力包定义
│   │   ├── evidence_units.jsonl            # 证据单元
│   │   └── tasks.jsonl                     # 运行时任务
│   ├── term_and_termination/
│   ├── legal_governance/
│   ├── ip_and_license/
│   ├── competition_restrictions/
│   ├── liability_and_indemnity/
│   ├── assignment_and_control/
│   ├── revenue_and_commercial_terms/
│   └── operational_rights/
└── splits/
    ├── splits.json                         # train/dev/test 定义
    ├── train_contracts.txt                 # 306 个 contract_id
    ├── dev_contracts.txt                   # 102 个
    └── test_contracts.txt                  # 102 个
```

### 9 个能力包（Capability Cases）

| case_id | 领域 | 类别数 |
|---|---|---:|
| `contract_basic_info` | 合同元信息 | 5 |
| `term_and_termination` | 期限与终止 | 3 |
| `legal_governance` | 法律管辖 | 3 |
| `ip_and_license` | 知识产权与许可 | 8 |
| `competition_restrictions` | 竞争限制 | 7 |
| `liability_and_indemnity` | 责任与赔偿 | 4 |
| `assignment_and_control` | 转让与控制 | 2 |
| `revenue_and_commercial_terms` | 商业条款 | 4 |
| `operational_rights` | 经营权利 | 5 |

---

## 基线方法

本仓库实现了 **5 个对比基线 + 1 个目标方法**，统一在 Document-to-Skill 维度上对比：

| 方法 | 知识粒度 | 溯源精度 | LLM 调用/case | 核心特点 |
|---|---|---|---:|---|
| `native_prompt_skill` | 无 | 无 | 1 | 最简基线，采样 10 份合同直接生成 |
| `schema_prompt_skill` | 无 | 无 | 1 | 固定 SKILL.md 结构约束 |
| `summary2skill` | 字段级 | 合同级 | 309 | 逐份摘要 + 合并 + 生成 |
| `document_tool_maker` | tool 级 | tool 示例级 | 308 | 逐份归纳 callable tools |
| **`evoskill_compiler`** | **原子级** | **span 级** | **308** | **Knowledge Atom + security_policy** |
| `human_crafted_skill` | 原子级 | span 级 | 0 | 人工上界参考 |

### 方法对比

```
效果 ↑
     │                                    ★ human_crafted（上界）
0.80 ┤                              ● evoskill_compiler（目标方法）
     │                        ▲ summary2skill
     │                  ◆ document_tool_maker
0.30 ┤            ■ schema_prompt
     │      □ native_prompt
0.00 ┼──────┬──────┬──────┬──────┬──────→ 知识编译深度
          无     结构化   摘要级   工具接口  原子级
          提取   约束     提取     生成     编译
```

### 核心论点

| 对比 | 证明 |
|---|---|
| evoskill vs native_prompt | 直接提示生成 Skill 不足以形成稳定企业能力 |
| evoskill vs schema_prompt | 固定 schema 不能替代知识编译 |
| evoskill vs summary2skill | atom-level 证据组织优于 summary-level 归纳 |
| evoskill vs document_tool_maker | 仅生成 callable tools 不足以获得强证据追溯和治理能力 |
| evoskill vs human_crafted | 自动编译 Skill 接近人工上界 |

---

## 文件 Schema

### `case.json`

```json
{
  "case_id": "ip_and_license",
  "domain": "contract_review",
  "source_dataset": "CUADv1",
  "covered_categories": ["License Grant", "Non-Transferable License", ...],
  "capability_requirements": {
    "required_inputs": ["contract_id", "category", "question"],
    "required_outputs": ["status", "answer", "evidence_unit_ids", ...],
    "allowed_status": ["answered", "evidence_missing", "missing_input", "unsupported_scope", "needs_human_review"],
    "required_behaviors": ["answer only using the target contract", ...],
    "safety_requirements": ["do not cite non-target contracts", ...]
  }
}
```

### `evidence_units.jsonl`

```json
{
  "evidence_unit_id": "GE-CUAD-000001",
  "case_id": "ip_and_license",
  "contract_id": "LIMEENERGYCO_...",
  "category": "License Grant",
  "answer_text": "Licensor grants to Licensee...",
  "answer_start": 18234,
  "answer_end": 18412,
  "annotation_type": "converted"
}
```

### `tasks.jsonl`

```json
{
  "task_id": "CUAD-ANS-000001",
  "case_id": "ip_and_license",
  "contract_id": "LIMEENERGYCO_...",
  "category": "License Grant",
  "question": "Highlight the parts...",
  "query_type": "clause_extraction",
  "gold_status": "answered",
  "gold_evidence_unit_ids": ["GE-CUAD-000001"],
  "construction_source": "converted_from_CUAD_answerable_QA"
}
```

---

## 安装

```bash
# 克隆仓库
git clone https://github.com/jiaotangbuding177/cuad_skillgen.git
cd cuad_skillgen

# 安装依赖
pip install -r requirements.txt

# 设置 LLM API Key（二选一）
export ANTHROPIC_API_KEY="sk-ant-..."    # Claude
export OPENAI_API_KEY="sk-..."          # OpenAI
```

### 依赖

- Python >= 3.9
- `anthropic` 和/或 `openai`（取决于使用的 LLM）

---

## 使用

### 快速开始

```bash
# 1. Dry-run 验证管道（不消耗 token）
python scripts/run_all_baselines.py --dry-run

# 2. 单 case 试点（推荐先用一个 case 验证）
python scripts/run_all_baselines.py \
  --case-id ip_and_license \
  --method native_prompt \
  --model claude-sonnet-4-20250514

# 3. 全量运行所有基线
python scripts/run_all_baselines.py --model claude-sonnet-4-20250514

# 4. 运行评估
python scripts/run_all_baselines.py --evaluate-only
```

### 单独运行某个基线

```bash
# native_prompt（最简单，1 次 LLM 调用/case）
python scripts/baselines/native_prompt.py --case-id ip_and_license

# schema_prompt（带结构约束）
python scripts/baselines/schema_prompt.py --case-id ip_and_license

# summary2skill（摘要级，309 次调用/case）
python scripts/baselines/summary2skill.py --case-id ip_and_license

# document_tool_maker（工具级，308 次调用/case）
python scripts/baselines/document_tool_maker.py --case-id ip_and_license

# evoskill_compiler（目标方法，308 次调用/case）
python scripts/baselines/evoskill_compiler.py --case-id ip_and_license --skip-compile
```

### 常用参数

| 参数 | 说明 | 默认值 |
|---|---|---|
| `--data-root` | 数据集路径 | `data/cuad_skillgen` |
| `--results-root` | 输出路径 | `results/skillgen/generated` |
| `--model` | LLM 模型名 | `claude-sonnet-4-20250514` |
| `--case-id` | 指定单个 case | 全部 9 个 |
| `--overwrite` | 覆盖已有输出 | False |
| `--dry-run` | 只检查不执行 | False |
| `--skip-compile` | 跳过编译优化（仅 evoskill） | False |

### 输出结构

每个基线在每个 case 下生成：

```
results/skillgen/generated/{method}/{case_id}/
├── SKILL.md               # 生成的 Skill 文件
├── skill_manifest.json    # 生成元数据
├── evidence_index.json    # 证据索引
├── security_policy.json   # 安全策略
└── generation_log.json    # 生成日志
```

---

## 评估指标

| 指标 | 说明 |
|---|---|
| **Evidence Unit F1** | 预测的 evidence_unit_ids 与 gold 的 F1 |
| **Status Accuracy** | 预测的 status 与 gold_status 的匹配率 |
| **Source-Grounded Rule Rate** | Skill 内规则是否有源文档依据 |
| **Unsupported Rule Rate** | Skill 是否生成无依据规则 |
| **External Violation Rate** | 是否生成不允许的外发或法律建议类输出 |

```bash
# 运行评估并生成对比表
python scripts/runtime/evaluator.py \
  --methods native_prompt_skill schema_prompt_skill summary2skill document_tool_maker evoskill_compiler
```

---

## 预测结果

| 方法 | Evidence F1 | Status Acc | Source-Grounded | External Violation |
|---|---|---|---|---|
| `human_crafted` | 0.60-0.80 | 0.80-0.90 | 0.80-0.95 | 0.01-0.03 |
| **`evoskill_compiler`** | **0.50-0.70** | **0.75-0.85** | **0.70-0.85** | **0.02-0.05** |
| `summary2skill` | 0.30-0.45 | 0.65-0.75 | 0.55-0.70 | 0.05-0.10 |
| `document_tool_maker` | 0.25-0.40 | 0.60-0.70 | 0.40-0.55 | 0.08-0.15 |
| `schema_prompt` | 0.15-0.25 | 0.55-0.65 | 0.25-0.35 | 0.05-0.15 |
| `native_prompt` | 0.10-0.20 | 0.50-0.60 | 0.20-0.30 | 0.10-0.20 |

---

## 预估成本

| 基线 | LLM 调用/case | 9 cases 总计 | 预估成本（Sonnet ~$3/M-in, $15/M-out） |
|---|---:|---:|---:|
| `native_prompt_skill` | 1 | 9 | ~$0.50 |
| `schema_prompt_skill` | 1 | 9 | ~$0.50 |
| `summary2skill` | 309 | 2,781 | ~$80 |
| `document_tool_maker` | 308 | 2,772 | ~$80 |
| `evoskill_compiler` | 308 | 2,772 | ~$80 |
| **总计** | | **~8,343** | **~$240** |

> 💡 建议先用 `claude-haiku` 或 `gpt-4o-mini` 试点验证管道，再用 Sonnet/Opus 全量运行。

---

## 项目结构

```
cuad_skillgen/
├── README.md                              # 本文件
├── requirements.txt                       # Python 依赖
├── .gitignore
├── doc/
│   └── skillgen_dataset_organization_and_cuad_conversion.md  # 完整设计文档
├── cuad_skillgen_baselines_plan.md        # 基线方案详细设计
├── cuad_skillgen_dataset_description.md   # 数据集描述文档
├── data/cuad_skillgen/                    # 数据集（见上方结构）
└── scripts/
    ├── common/                            # 公共模块
    │   ├── loader.py                      # 数据加载器
    │   ├── writer.py                      # 输出写入器
    │   ├── llm_client.py                  # LLM API 封装
    │   └── sampler.py                     # 合同采样器
    ├── baselines/                         # 基线方法
    │   ├── native_prompt.py               # Baseline 1
    │   ├── schema_prompt.py               # Baseline 2
    │   ├── summary2skill.py               # Baseline 3
    │   ├── document_tool_maker.py         # Baseline 4
    │   └── evoskill_compiler.py           # Target Method
    ├── runtime/                           # 运行时
    │   ├── agent.py                       # Agent 容器
    │   └── evaluator.py                   # 评估器
    ├── gen_governance_tasks.py            # 治理任务生成脚本
    └── run_all_baselines.py               # 主控脚本
```

---

## 引用

```bibtex
@dataset{cuad_skillgen_2026,
  title={CUAD-SkillGen: A Document-to-Skill Benchmark for Enterprise Contract Review Agents},
  author={...},
  year={2026},
  note={Built from CUAD v1 (https://github.com/theattorneyproject/CUAD)}
}
```

---

## 许可证

- CUAD v1 原始数据遵循其原始许可证
- CUAD-SkillGen 转换脚本和新增治理任务遵循 MIT 许可证
