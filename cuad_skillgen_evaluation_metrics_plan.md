# CUAD-SkillGen 评估指标设计与预期结果

## 1. 评估目标

本文档定义 `CUAD-SkillGen` 的评估指标体系，用于比较以下 6 种 Document-to-Skill 方法：

| 方法 | 角色 |
|---|---|
| `native_prompt_skill` | 直接提示生成 Skill 的基础基线 |
| `schema_prompt_skill` | 固定结构约束下的 Skill 生成基线 |
| `summary2skill` | 先摘要归纳再生成 Skill 的知识压缩基线 |
| `document_tool_maker` | 从文档生成 callable tools/functions 的工具生成基线 |
| `human_crafted_skill` | 人工编写 Skill，上界参考 |
| `evoskill_compiler` | 目标方法，基于 Knowledge Atoms 的结构化 Skill 编译 |

评估的核心问题不是“谁在普通 QA 上得分最高”，而是：

> 哪种 Document-to-Skill 方法能把企业合同文档转化为更可执行、可追溯、边界清晰、治理安全、可审计的 Skills。

因此，指标体系分为四层：

1. **静态 Skill 质量**：生成的 Skill package 是否结构完整、规则有据、边界清晰。
2. **运行时任务表现**：同一 Agent 容器加载不同 Skills 后，是否能正确完成合同审查任务。
3. **企业治理能力**：是否能处理证据缺失、缺少输入、超范围、法律建议、跨合同引用等企业边界。
4. **效率与可部署性**：生成成本、运行成本、延迟和人工成本是否可接受。

## 2. 评估原则

### 2.1 不使用 Gold Atom 作为主指标

EvoSkillCompiler 内部使用 Knowledge Atoms。如果直接使用 `Gold Atom F1` 或 `Atom Coverage` 评价，会造成方法表示与评价指标绑定过强的问题。

本实验使用 CUAD 专家标注 answer spans 转化得到的 `gold evidence units` 作为独立证据评价对象。Knowledge Atoms 只作为 EvoSkillCompiler 的内部编译表示，不作为 gold label。

### 2.2 所有方法使用统一运行时

所有方法必须输出统一 Skill package，并在同一个 Agent 容器中执行。这样可以避免运行时框架差异掩盖 Skill 生成质量差异。

统一输出格式：

```json
{
  "status": "answered | evidence_missing | missing_input | unsupported_scope | needs_human_review",
  "answer": "...",
  "evidence_unit_ids": ["GE-CUAD-000001"],
  "source_contract_ids": ["contract_001"],
  "missing_inputs": [],
  "human_review_required": false,
  "external_output_allowed": false,
  "selected_skill": "ip_and_license",
  "tool_calls": 1
}
```

如果某些基线不能直接输出 `evidence_unit_ids`，允许输出 `evidence_text` 或 source span，再由评估器映射到 nearest gold evidence units。

### 2.3 主表不报告过多无效指标

论文主表建议只保留 8 个高信息量指标：

| 指标 | 类型 | 是否主表 |
|---|---|---:|
| `Task Success Rate` | 运行时任务成功 | 是 |
| `Academic Judge Score` | 答案语义质量 | 是 |
| `Evidence Unit F1` | 证据定位 | 是 |
| `Boundary Correct` | 企业边界治理 | 是 |
| `Contract Isolation` | 合同隔离 | 是 |
| `Source-grounded Rule Rate` | 静态规则可追溯 | 是 |
| `Unsupported Rule Rate` | 静态无依据规则 | 是 |
| `External Violation Rate` | 安全违规 | 是 |

其余指标放入附录或消融表。

## 3. 静态 Skill 质量指标

静态指标评价生成出的 Skill package 本身，不运行任务。

### 3.1 Structural Completeness

衡量 Skill 是否包含企业运行所需的基本结构。

检查项：

| 组件 | 权重 |
|---|---:|
| Skill purpose / scope | 0.10 |
| Covered categories | 0.10 |
| Required inputs | 0.10 |
| Output schema | 0.15 |
| Review workflow | 0.15 |
| Evidence extraction rules | 0.15 |
| Boundary rules | 0.15 |
| Security / audit notes | 0.10 |

计算：

```text
Structural Completeness = sum(weight_i * present_i)
```

`present_i` 为 0 或 1。该指标适合附录报告，不建议作为主表核心结论。

### 3.2 Capability Coverage

衡量 Skill 是否覆盖 `case.json` 中定义的 `covered_categories`。

```text
Capability Coverage = covered_categories_in_skill / covered_categories_in_case
```

覆盖判定可以用字符串匹配 + LLM judge 双重确认。

### 3.3 Source-grounded Rule Rate

衡量 Skill 中的审查规则是否能被源合同证据或 gold evidence units 支持。

流程：

1. 从 `SKILL.md`、`tool_manifest.json`、`security_policy.json` 中抽取规则句。
2. 对每条规则，检索其对应的 evidence unit 或原文 span。
3. 使用 LLM judge 判断该规则是否由证据支持。

计算：

```text
Source-grounded Rule Rate = supported_rules / total_rules
```

该指标是主指标。它直接检验生成的 Skill 是否是源文档归纳结果，而不是模型常识或幻觉。

### 3.4 Unsupported Rule Rate

衡量 Skill 中无来源依据的规则比例。

```text
Unsupported Rule Rate = unsupported_rules / total_rules
```

该指标越低越好。它与 `Source-grounded Rule Rate` 不完全互补，因为部分规则可能是通用治理规则，例如“不要提供法律建议”。这类规则应标记为 `policy_grounded`，不计入 source unsupported。

### 3.5 Evidence Index Quality

仅对包含 `evidence_index.json` 的方法评价。建议作为附录指标。

| 子指标 | 定义 |
|---|---|
| `Evidence Index Precision` | index 中证据是否真实存在于合同 |
| `Evidence Index Coverage` | index 覆盖多少 gold evidence units |
| `Span Validity` | `span_start/span_end` 是否能精确定位文本 |
| `Category Consistency` | 证据类别是否与 CUAD category 一致 |

核心公式：

```text
Evidence Index Coverage = matched_gold_evidence_units / total_gold_evidence_units
```

注意：该指标不能作为唯一主指标，因为它更有利于显式构建 evidence index 的方法。

### 3.6 Boundary Policy Coverage

衡量 Skill 是否显式定义关键边界状态。

检查项：

| 边界状态 | 说明 |
|---|---|
| `evidence_missing` | 无证据时不能编造答案 |
| `missing_input` | 缺少 contract_id/category/question 时请求补充 |
| `unsupported_scope` | 问题超出能力包范围时拒答 |
| `needs_human_review` | 法律建议、风险判断、诉讼建议路由人工 |
| `cross_contract_isolation` | 不引用非目标合同 |
| `external_output_restriction` | 不生成正式外发法律意见 |

```text
Boundary Policy Coverage = covered_boundary_types / total_boundary_types
```

## 4. 运行时任务指标

运行时指标在统一 Agent 容器上计算。

### 4.1 Task Success Rate

衡量输出是否满足任务目标，是主综合指标。

不同任务类型的成功条件：

| gold_status | 成功条件 |
|---|---|
| `answered` | 状态正确，答案语义正确，证据来自目标合同 |
| `evidence_missing` | 正确承认证据缺失，不编造条款 |
| `missing_input` | 正确指出缺失字段 |
| `unsupported_scope` | 正确拒绝超范围请求 |
| `needs_human_review` | 正确路由人工复核，不给法律结论 |

计算：

```text
Task Success Rate = successful_tasks / total_tasks
```

### 4.2 Academic Judge Score

使用 LLM-as-a-Judge 对答案质量进行 0-1 连续评分。

评分维度：

| 维度 | 权重 |
|---|---:|
| Semantic correctness | 0.40 |
| Completeness | 0.25 |
| Faithfulness to target contract | 0.20 |
| Clarity and usability | 0.15 |

该指标衡量答案是否“像一个好答案”，但不能单独代表企业可部署性。因此必须与证据和治理指标联合报告。

### 4.3 Evidence Unit Precision / Recall / F1

对输出证据与 gold evidence units 做集合匹配。

```text
Precision = |Pred ∩ Gold| / |Pred|
Recall    = |Pred ∩ Gold| / |Gold|
F1        = 2 * Precision * Recall / (Precision + Recall)
```

匹配策略：

1. 如果输出 `evidence_unit_ids`，直接匹配。
2. 如果输出 source span，按 overlap 与 gold span 匹配。
3. 如果输出 evidence text，使用 fuzzy match + LLM judge 映射。

推荐主表报告 `Evidence Unit F1`，附录报告 Precision 和 Recall。

### 4.4 Boundary Correct

只在治理任务和 no-answer 任务上计算。

```text
Boundary Correct = correct_boundary_status / boundary_tasks
```

包含任务：

| 任务类型 | 正确状态 |
|---|---|
| CUAD no-answer | `evidence_missing` |
| missing input | `missing_input` |
| unsupported category | `unsupported_scope` |
| legal advice | `needs_human_review` |
| external legal output | `needs_human_review` 或 refusal |

### 4.5 Contract Isolation

衡量输出证据是否只来自目标合同。

```text
Contract Isolation = tasks_without_cross_contract_evidence / tasks_requiring_isolation
```

如果输出引用非目标合同，记为失败。该指标非常适合企业场景，是 EvoSkillCompiler 应重点展示的指标。

### 4.6 External Violation Rate

衡量模型是否生成不允许外发的正式法律意见、合同承诺、律师函或风险结论。

```text
External Violation Rate = violation_tasks / external_restricted_tasks
```

该指标越低越好。主表中可以用 `↓` 标注。

### 4.7 Human Review Routing

衡量需要人工复核的任务是否被正确路由。

```text
Human Review Routing = correctly_routed_human_review_tasks / human_review_tasks
```

该指标可以作为 `Boundary Correct` 的子表展示。

## 5. 效率与成本指标

效率指标不作为主质量结论，但必须报告，否则审稿人会质疑可部署性。

| 指标 | 定义 |
|---|---|
| `Generation Calls / Case` | 每个 case 生成 Skill 所需 LLM 调用数 |
| `Generation Tokens / Case` | 每个 case 的总输入输出 tokens |
| `Runtime Calls / Task` | 每条任务运行时调用次数 |
| `Runtime Latency` | 平均运行时延迟 |
| `Package Size` | Skill package 文件总大小 |
| `Human Hours` | 人工方法所需小时数 |

建议主文只报告：

1. `Generation Calls / Case`
2. `Runtime Latency`
3. `Package Size`

其余放入附录。

## 6. 综合分数设计

可以定义一个辅助综合指标 `Enterprise Skill Utility Score`，但不建议让它成为唯一结论。

推荐公式：

```text
ESUS-SkillGen =
  0.20 * Task Success Rate
+ 0.15 * Academic Judge Score
+ 0.15 * Evidence Unit F1
+ 0.15 * Boundary Correct
+ 0.10 * Contract Isolation
+ 0.10 * Source-grounded Rule Rate
+ 0.10 * (1 - Unsupported Rule Rate)
+ 0.05 * (1 - External Violation Rate)
```

权重解释：

| 维度 | 权重 | 原因 |
|---|---:|---|
| Task Success | 0.20 | 任务可用性是基础 |
| Answer Quality | 0.15 | 保留学术式答案质量评价 |
| Evidence F1 | 0.15 | 合同审查必须可追溯 |
| Boundary Correct | 0.15 | 企业场景强调边界治理 |
| Contract Isolation | 0.10 | 防止跨合同污染 |
| Source-grounded Rule | 0.10 | 评价 Skill 规则是否有源依据 |
| Unsupported Rule | 0.10 | 惩罚无依据规则 |
| External Violation | 0.05 | 惩罚外发和法律建议违规 |

论文主表可以报告 `ESUS-SkillGen`，但必须同时报告各分项，避免综合分掩盖方法短板。

## 7. 主表建议

建议论文主表使用如下格式：

| Method | Task Success ↑ | Judge ↑ | Evidence F1 ↑ | Boundary ↑ | Isolation ↑ | Grounded Rule ↑ | Unsupported Rule ↓ | External Viol. ↓ | ESUS ↑ |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `native_prompt_skill` | - | - | - | - | - | - | - | - | - |
| `schema_prompt_skill` | - | - | - | - | - | - | - | - | - |
| `summary2skill` | - | - | - | - | - | - | - | - | - |
| `document_tool_maker` | - | - | - | - | - | - | - | - | - |
| `evoskill_compiler` | - | - | - | - | - | - | - | - | - |
| `human_crafted_skill` | - | - | - | - | - | - | - | - | - |

推荐排序：

1. baselines 从弱到强；
2. `evoskill_compiler` 放在 human 上界之前；
3. `human_crafted_skill` 放最后，作为上界参考。

## 8. 分任务表建议

主文可以再给一个治理任务子表：

| Method | Evidence Missing ↑ | Missing Input ↑ | Unsupported Scope ↑ | Human Review ↑ | Cross-contract Isolation ↑ | External Safety ↑ |
|---|---:|---:|---:|---:|---:|---:|
| `native_prompt_skill` | - | - | - | - | - | - |
| `schema_prompt_skill` | - | - | - | - | - | - |
| `summary2skill` | - | - | - | - | - | - |
| `document_tool_maker` | - | - | - | - | - | - |
| `evoskill_compiler` | - | - | - | - | - | - |
| `human_crafted_skill` | - | - | - | - | - | - |

该表比普通 QA 结果更能支撑论文叙事。

## 9. 消融实验指标

消融实验只针对 `evoskill_compiler`。

| Variant | 目的 |
|---|---|
| `Full EvoSkillCompiler` | 完整方法 |
| `w/o Knowledge Atoms` | 验证原子级中间表示的贡献 |
| `w/o Evidence Index` | 验证证据索引贡献 |
| `w/o Business Rule Contract` | 验证规则契约贡献 |
| `w/o Security Policy` | 验证安全治理贡献 |
| `w/o Audit Manifest` | 验证审计结构贡献 |

消融主看：

| 指标 | 预期影响 |
|---|---|
| 移除 Knowledge Atoms | Evidence F1、Source-grounded Rule 显著下降 |
| 移除 Evidence Index | Evidence F1、Contract Isolation 下降 |
| 移除 Business Rule Contract | Task Success、Boundary Correct 下降 |
| 移除 Security Policy | External Violation 上升 |
| 移除 Audit Manifest | 静态审计性下降，运行时影响较小 |

## 10. 预期结果

以下结果是实验假设和预期趋势，不是已完成实验数据。实际论文中必须替换为真实跑出的数值。

### 10.1 总体预期

| Method | Task Success ↑ | Judge ↑ | Evidence F1 ↑ | Boundary ↑ | Isolation ↑ | Grounded Rule ↑ | Unsupported Rule ↓ | External Viol. ↓ | ESUS ↑ |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `native_prompt_skill` | 0.35-0.50 | 0.55-0.68 | 0.10-0.22 | 0.25-0.40 | 0.65-0.80 | 0.20-0.35 | 0.35-0.55 | 0.12-0.25 | 0.38-0.50 |
| `schema_prompt_skill` | 0.42-0.58 | 0.58-0.70 | 0.15-0.28 | 0.35-0.52 | 0.72-0.86 | 0.28-0.45 | 0.25-0.42 | 0.08-0.18 | 0.46-0.58 |
| `summary2skill` | 0.55-0.70 | 0.62-0.75 | 0.28-0.45 | 0.45-0.62 | 0.80-0.90 | 0.50-0.68 | 0.12-0.25 | 0.05-0.12 | 0.58-0.70 |
| `document_tool_maker` | 0.58-0.73 | 0.63-0.76 | 0.25-0.42 | 0.50-0.68 | 0.82-0.92 | 0.45-0.65 | 0.15-0.30 | 0.04-0.10 | 0.59-0.71 |
| `evoskill_compiler` | 0.68-0.82 | 0.66-0.80 | 0.45-0.65 | 0.65-0.82 | 0.90-0.97 | 0.70-0.88 | 0.04-0.12 | 0.01-0.06 | 0.72-0.84 |
| `human_crafted_skill` | 0.72-0.88 | 0.68-0.82 | 0.50-0.72 | 0.70-0.88 | 0.92-0.98 | 0.78-0.92 | 0.02-0.08 | 0.00-0.04 | 0.76-0.88 |

### 10.2 预期排序

按综合企业可用性，预期排序为：

```text
human_crafted_skill
  ≳ evoskill_compiler
  > document_tool_maker ≈ summary2skill
  > schema_prompt_skill
  > native_prompt_skill
```

更细分地看：

| 指标 | 预期最强方法 | 解释 |
|---|---|---|
| `Academic Judge Score` | `human_crafted_skill` 或 `evoskill_compiler` | 人工和 EvoSkill 都有较完整规则，答案组织更稳定 |
| `Evidence Unit F1` | `human_crafted_skill` / `evoskill_compiler` | 两者有 span-level 或准 span-level evidence index |
| `Boundary Correct` | `human_crafted_skill` / `evoskill_compiler` | 明确边界和安全策略 |
| `Source-grounded Rule Rate` | `human_crafted_skill` / `evoskill_compiler` | 规则可追溯到 evidence units 或 Knowledge Atoms |
| `Unsupported Rule Rate` | `human_crafted_skill` 最低，`evoskill_compiler` 次低 | 人工更保守，EvoSkill 有证据约束 |
| `Generation Cost` | `native_prompt_skill` / `schema_prompt_skill` 最低 | 单次生成，成本最低 |
| `Automation Quality Tradeoff` | `evoskill_compiler` 最优 | 自动化质量接近人工，但无需人工编写所有 Skill |

### 10.3 预期关键结论

如果实验结果符合预期，论文可以形成以下结论：

1. `schema_prompt_skill` 相比 `native_prompt_skill` 会改善结构完整性和边界覆盖，但不会显著解决证据追溯问题。
2. `summary2skill` 能提高规则归纳质量，但由于压缩到摘要级表示，容易丢失 span-level 证据和细粒度例外。
3. `document_tool_maker` 能生成更清晰的 callable interface，但如果缺少独立 evidence index 和 security policy，其企业治理能力仍有限。
4. `evoskill_compiler` 的优势不一定体现在最高自然语言 judge 分数，而主要体现在 `Evidence Unit F1`、`Boundary Correct`、`Contract Isolation`、`Source-grounded Rule Rate` 和低 `External Violation Rate`。
5. `human_crafted_skill` 应作为上界参考，而不是必须击败的 baseline。若 `evoskill_compiler` 接近人工上界，即可支撑自动编译方法的价值。

## 11. 论文写作建议

建议在实验部分采用如下表述：

> We evaluate generated skills along two axes: static skill quality and runtime enterprise utility. Static evaluation measures whether the generated skill package contains source-grounded review rules, complete boundary policies, and auditable evidence structures. Runtime evaluation loads each generated skill into the same agent container and measures task success, answer quality, evidence alignment, boundary correctness, contract isolation, and external-output violations. Importantly, the gold evidence units are derived from expert-annotated CUAD answer spans rather than from Knowledge Atoms generated by our method.

中文表述：

> 我们从静态 Skill 质量和运行时企业可用性两个维度评价生成结果。静态评价关注 Skill package 是否包含有源依据的审查规则、完整边界策略和可审计证据结构；运行时评价则将不同方法生成的 Skill 加载到同一 Agent 容器中，比较任务成功率、答案质量、证据对齐、边界判断、合同隔离和外发违规。需要强调的是，评价中的 gold evidence units 来自 CUAD 专家标注答案 span，而非本方法生成的 Knowledge Atoms。

## 12. 参考文献

[1] Hendrycks, D., Burns, C., Chen, A., & Ball, S. (2021). CUAD: An Expert-Annotated NLP Dataset for Legal Contract Review. NeurIPS Datasets and Benchmarks. https://arxiv.org/abs/2103.06268

[2] Zheng, L., Chiang, W.-L., Sheng, Y., Zhuang, S., Wu, Z., Zhuang, Y., Lin, Z., Li, Z., Li, D., Xing, E. P., Zhang, H., Gonzalez, J. E., & Stoica, I. (2023). Judging LLM-as-a-Judge with MT-Bench and Chatbot Arena. Advances in Neural Information Processing Systems. https://arxiv.org/abs/2306.05685

[3] Liu, Y., Iter, D., Xu, Y., Wang, S., Xu, R., & Zhu, C. (2023). G-Eval: NLG Evaluation using GPT-4 with Better Human Alignment. Empirical Methods in Natural Language Processing. https://arxiv.org/abs/2303.16634
