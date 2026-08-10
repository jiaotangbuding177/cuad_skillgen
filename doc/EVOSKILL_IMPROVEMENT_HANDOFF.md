# EvoSkill 改进实验交接文档

## 概述

本文档记录了 2026-08-06 至 2026-08-10 期间，为了提升 EvoSkill Compiler 算法性能所做的全部实验、思考和结果。

**核心结论**：三个改进方向中，只有 P2-1（SKILL.md 增加 Example Phrasing）有正向效果。

---

## 一、背景与问题诊断

### 1.1 EvoSkill 的瓶颈定位

v1（原始 EvoSkill）在 5 个基线中的表现：

| 指标 | EvoSkill v1 | Summary2Skill | 差距 | 诊断 |
|------|:-:|:-:|:-:|---|
| Task Success | 0.6435 (#1) | 0.6407 | +0.28pp | 已领先 |
| Status Macro-F1 | 0.8477 (#1) | 0.7696 | +7.81pp | 已领先 |
| Governance Boundary | 0.8916 (#1) | 0.7328 | +15.88pp | 已领先 |
| Academic Judge | 0.9545 (#2) | 0.9660 | -1.15pp | **落后** |
| Containment Evidence F1 | 0.6348 (#6, 最差) | 0.6638 | -2.90pp | **落后** |
| Strict Evidence F1 | 0.4315 (#5) | 0.4329 | -0.14pp | 持平但都差 |

**根因诊断**（来自 200 条抽样分析）：

- 检索失败或 query drift：4.5%（很少）
- Gold chunk 已召回但引用抽取失败：7.5%
- 接近 Gold 但未通过严格阈值：11.0%
- **替代或错误证据**：24.0%（43/48 实际是 valid alternative, Gold span 有限导致的误判）

核心问题：EvoSkill 的 Knowledge Atom 是字符级原子，检索后 LLM 抽取碎片化引用。Summary2Skill 保留段落级原文片段，更有利于答案生成和证据定位。

### 1.2 思考过程

**应该试什么**：

1. 增加 evidence_index 的 KA 数量（30 → 100），提高 BM25 覆盖度
2. 扩展 chunk 上下文窗口（±1200 chars），减少碎片引用
3. **改 SKILL.md 的生成方式**——从"规则驱动"变为"模式驱动"，让 LLM 在匹配证据时有具体语言模板

**不应该试什么**：

- 图结构组织 KA：当前场景全是单跳问答，不需要多跳推理。瓶颈是 KA 粒度过细，不是知识之间缺乏关系
- 换更强的 LLM（ecnu-plus 是固定约束）
- 重新标注 Gold span（不现实）

---

## 二、三次改进实验

### 2.1 v2：P0-2 增加 KA 数量（top-30 → top-100）

**改动位置**：`scripts/baselines/evoskill_compiler.py` 第 293 行 `build_evidence_index()` 截断逻辑 + `scripts/regen_evoskill_more_kas.py`（新建）

**改动内容**：`sorted_kas[:30]` → `sorted_kas[:100]`，重新生成 9 个 SKILL.md（不重跑 306 次 KA 提取，直接从已有 `evidence_index.json` 加载全量 KA）

**结果**：❌ FAILED

| 指标 | v1 | v2 | Δ |
|---|---|:-:|:-:|
| Task Success | 0.6435 | 0.6300 | -1.35pp |
| Status Macro-F1 | 0.8477 | 0.8390 | -0.87pp |
| Evidence F1 | 0.4315 | 0.4385 | +0.70pp |

**根因**：低 confidence KA 引入噪声 → em→ans 误判增加，agent 在有 noise 的情况下更容易错误回答而不是正确拒答。

**结论**：top-30 是有效的隐式 quality gate，不应增加。

---

### 2.2 v3：P0-1 扩展 chunk 上下文窗口（±1200 chars）

**改动位置**：`scripts/runtime/package_agent.py`

**改动内容**：新增 `expand_chunk_context()` 函数，在 `process_task()` 检索合同 chunks 后，将每个 chunk 向两侧扩展 ±1200 字符

**结果**：❌ FAILED

| 指标 | v1 | v3 | Δ |
|---|---|:-:|:-:|
| Task Success | 0.6435 | 0.6341 | -0.94pp |
| Evidence F1 | 0.4315 | 0.4295 | -0.20pp |
| Containment F1 | 0.6348 | 0.6466 | +1.18pp |

**根因**：更大的窗口引入了无关条款，稀释了 BM25 检索精度。Containment 改善不足以抵消其他指标的下降。

**结论**：原始 4800 字符的 chunk 大小已经接近最优。

---

### 2.3 v4：P2-1 SKILL.md 增加 Example Phrasing（规则驱动 → 模式驱动）

**改动位置**：`scripts/baselines/evoskill_compiler.py` — `GENERATE_SYSTEM` prompt 变量

**改动内容**：

改之前 (v1) prompt 要求生成：
```
## Evidence-Based Review Rules
For each category, describe review rules with [KA-XXXX] references.
Example: "Look for explicit grant language such as 'hereby grants' [KA-0001]"
```

LLM 生成的 SKILL.md 是抽象规则列表：
```markdown
### 1. Renewal Term
* Identify Automatic Renewal Mechanisms: Look for language indicating
  automatic renewal upon expiration [KA-0077, KA-0111].
* Determine Renewal Duration: Check if renewal term matches initial
  term. Variations include one-year [KA-0001], two-year [KA-0327].
```

改之后 (v4) prompt 要求生成：
```
## Common Clause Patterns & Example Phrasing
For each category, derive 3-6 common clause PATTERNS from the evidence KAs.
For each pattern include:
- Pattern Name / Description
- **Example Phrasing:** 1-2 actual full-length example quotes from KA texts
- Variation Notes
```

LLM 生成的 SKILL.md 变成模式+真实例句：
```markdown
#### Pattern 1: Automatic Annual Renewal
- Description: Agreement automatically extends for successive one-year
  periods unless terminated by notice.
- Example Phrasing:
  > "will renew automatically from year to year unless cancelled
     in writing by either Party..." [KA-0016]
  > "shall be automatically renewed for successive one (1) year
     periods" [KA-0111]
- Variation Notes: Some specify month-to-month [KA-0164]
```

**其他文件完全不变**：`evidence_index.json`、`security_policy.json`、`skill_manifest.json` 均与 v1 相同。

**结果**：✅ CONFIRMED — 唯一有正向信号的改进

| 指标 | v1 | v4 | Δ | v4 排名 |
|---|---|:-:|:-:|:-:|
| Task Success | 0.6435 | **0.6952** | **+5.17pp** | #1 |
| Status Macro-F1 | 0.8477 | **0.8714** | **+2.37pp** | #1 |
| Containment Ev F1 | 0.6348 | **0.6536** | **+1.88pp** | #2 (was #6) |
| Boundary Correct | 0.6905 | **0.7662** | **+7.57pp** | #1 |
| Governance Boundary | 0.8916 | 0.8863 | -0.53pp | #2 (was #1) |
| Strict Evidence F1 | 0.4315 | 0.4310 | -0.05pp | 持平 |

**核心机制**：evidence_missing → answered 误判从 956 降到 710（**-246, -26%**），其中 ip_and_license 从 356 降到 163（**-193, -54%**）。Example Phrasing 给了 LLM 具体的语言模板，让它更准确地判断何时应该拒答。

**本质原因**：v1 的规则式指引告诉 LLM "去检查有没有 X"，v4 的模式式指引告诉 LLM "你要找的条款长这个样子：[真实原文]"。后者让 LLM 在目标合同中有了具体的匹配锚点，同时在没有找到类似表述时更有信心拒答。

---

## 三、完整数据文件清单

### 3.1 实验结果 JSON（汇总）

| 文件 | 说明 |
|------|------|
| `results/skillgen/generated/package_runtime_evaluation_test_final-k10-k6.json` | **v1 原始 5 基线结果**（含 native/schema/summary/document/evoskill） |
| `results/skillgen/generated/package_runtime_evaluation_test_final-k10-k6-v2.json` | v2 结果（KA top-100） |
| `results/skillgen/generated/package_runtime_evaluation_test_final-k10-k6-v3-expand-chunks.json` | v3 结果（chunk expand ±1200） |
| `results/skillgen/generated/package_runtime_evaluation_test_final-k10-k6-v4-example-phrasing.json` | **v4 结果**（Example Phrasing，唯一成功的改进） |

### 3.2 运行时评测详情（JSONL，每个 task 一行）

| 目录 | 说明 |
|------|------|
| `results/skillgen/generated/evoskill_compiler/package_runtime_results/test/final-k10-k6/` | v1 原始结果 |
| `results/skillgen/generated/evoskill_compiler/package_runtime_results/test/final-k10-k6-v2/` | v2 结果 |
| `results/skillgen/generated/evoskill_compiler/package_runtime_results/test/final-k10-k6-v3-expand-chunks/` | v3 结果 |
| `results/skillgen/generated/evoskill_compiler/package_runtime_results/test/final-k10-k6-v4-example-phrasing/` | **v4 结果** |

### 3.3 生成的 SKILL.md（9 个 case × 多种版本）

| 目录 | 版本 |
|------|------|
| `results/skillgen/generated/evoskill_compiler/{case_id}/SKILL.md` | **当前为 v1**（Evidence-Based Review Rules） |
| 注：v4 SKILL.md 文件在当前状态可能被 v1 覆盖，通过 `scripts/regen_evoskill_more_kas.py --ka-top-n 30` 可重新生成 |

### 3.4 数据报告

| 文件 | 说明 |
|------|------|
| `results/skillgen/generated/experiment_data_report.md` | **完整实验数据报告**（6 方法 × 13 指标，含分 case 明细和排名） |
| `results/skillgen/generated/academic_judge_evaluation_test_final-k10-k6.jsonl` | Academic Judge 盲化评分明细 |
| `results/skillgen/generated/academic_judge_evaluation_test_final-k10-k6_summary.json` | Academic Judge 汇总 |

### 3.5 新建/修改的脚本

| 文件 | 说明 |
|------|------|
| `scripts/regen_evoskill_more_kas.py` | 从已有 evidence_index.json 重新生成 SKILL.md（不需重跑 KA 提取） |
| `scripts/gen_report.py` | 生成 experiment_data_report.md 报告 |
| `scripts/baselines/evoskill_compiler.py` | **已修改** — GENERATE_SYSTEM、COMPILE_SYSTEM prompt |
| `scripts/runtime/package_agent.py` | **已修改** — 新增 expand_chunk_context() 函数（v3 改动，已废弃但代码保留） |
| `scripts/common/llm_client.py` | **已修改** — 新增 .env 自动加载、_repair_truncated_json() |
| `scripts/evaluate_academic_judge.py` | **已修改** — max_tokens 1024→4096 |
| `.env` | 环境变量（ECNU_API_KEY），已加入 .gitignore |

---

## 四、关键数据速查

### 4.1 全方法排名（v4 加入后）

**Task Success**：
1. EvoSkill v4: **0.6952**
2. EvoSkill v1: 0.6435
3. Summary2Skill: 0.6407
4. DocToolMaker: 0.6345
5. Schema Prompt: 0.6298
6. Native Prompt: 0.4994

**Status Macro-F1**：
1. EvoSkill v4: **0.8714**
2. EvoSkill v1: 0.8477
3. Schema Prompt: 0.8380
4. Summary2Skill: 0.7696
5. DocToolMaker: 0.7451
6. Native Prompt: 0.5824

**Containment Evidence F1**：
1. Summary2Skill: 0.6638
2. EvoSkill v4: **0.6536** (v1 是 #6 最差)
3. Schema Prompt: 0.6508
4. Native Prompt: 0.6455
5. DocToolMaker: 0.6447
6. EvoSkill v1: 0.6348

**Governance Boundary**：
1. EvoSkill v1: 0.8916
2. EvoSkill v4: 0.8863
3. Schema Prompt: 0.8810
4. Summary2Skill: 0.7328
5. DocToolMaker: 0.6984
6. Native Prompt: 0.5714

### 4.2 v4 分 case Task Success

| Case | v1 | v4 | Δ |
|---|---|:-:|:-:|
| ip_and_license | 0.5322 | **0.7552** | **+22.30pp** |
| term_and_termination | 0.6139 | **0.6639** | +5.00pp |
| liability_and_indemnity | 0.6645 | **0.6991** | +3.46pp |
| assignment_and_control | 0.6860 | 0.6589 | -2.71pp |
| competition_restrictions | 0.7747 | **0.7839** | +0.92pp |
| revenue_and_commercial_terms | 0.7208 | **0.7359** | +1.51pp |
| operational_rights | 0.6950 | **0.7004** | +0.54pp |
| contract_basic_info | 0.3599 | **0.3652** | +0.53pp |
| legal_governance | 0.8694 | 0.8694 | 0.00pp |

---

## 五、踩坑记录

1. **ECNU API 限流（429）**：长时间连续调用被限，需要加入更长的 retry delay 或分批执行
2. **`SkillOutputWriter` 构造函数签名**：是 `(results_root, method, case_id)` 三个参数，不是 `(pkg_dir)` 一个参数
3. **`.env` 文件不生效**：`llm_client.py` 原本不会自动加载环境变量，已通过模块级 import 时读取 `.env` 修复
4. **`ContractChunk` 字段名**：是 `chunk_id` 不是 `id`
5. **v4 SKILL.md 被误覆盖**：`git checkout` 恢复了 v1 的 SKILL.md，v4 版本需通过 `regen_evoskill_more_kas.py` 重新生成
6. **评测结果不可简单对比不同 case 集合**：v4 曾经只跑了 3 个 case，不能用 3-case 平均和 v1 的 9-case 全量对比——得出的排名完全是误导

---

## 六、下一步建议

1. **采纳 v4**：将 Example Phrasing 融入 evoskill_compiler 的标准生成流程
2. **P0-3（未执行）**：BM25 检索只用 KA text 不用 interpretation，减少 query drift
3. **P1-1（未充分执行）**：在 dev 集上做 top-k 参数 grid search（当前 k=10, k=6 仅冒烟测试）
4. **消融实验**（论文后续）：No Policy / No KA Retrieval / KA 仅用于推理 / Minimal Sufficient Quote / 等生成模型
5. **不推荐方向**：图结构组织 KA、增加 KA 数量、扩展 chunk 窗口——三个都已证伪
