# τ³-SkillBench 评估方案

## 1. 研究目标与可证伪主张

本实验不以“换一个数据集后成功率更高”为充分结论，而检验以下可证伪主张：**相较于原始政策提示、摘要式 Skill 和工具包装式 Skill，EvoSkill 的原子化知识、显式治理与过程组织能在多领域企业 SOP 中提高全链路任务成功、决策均衡性、治理一致性与可追溯性；图增强编译进一步改善条件、例外和语义变体的组织，而收益不是由更多测试信息、更强运行模型或更大检索预算造成。**

τ-bench 首次把政策遵循、工具使用和用户交互置于同一动态环境中；τ²-bench 随后显式建模 agent、user 与 environment 的协作及双控制工具。本方案采用 τ³-bench v1.0.1 的修订任务、Telecom 和 Banking Knowledge 扩展，避免继续只在合同抽取这一单场景验证 Document-to-Skill 方法 [Yao et al., 2024](https://arxiv.org/abs/2406.12045); [Barres et al., 2025](https://arxiv.org/abs/2506.07982)。

研究问题如下：

- **RQ1：跨场景有效性。** Skill 编译能否同时迁移到交易办理、预订变更、技术排障和知识密集型咨询？
- **RQ2：全链路能力。** 改进是否发生在状态识别、规则决策、工具协作、结果验证与沟通，而非只发生在最终文本？
- **RQ3：治理与溯源。** 显式 policy/security/evidence 产物能否减少不合规动作并支持决定到来源的审计？
- **RQ4：结构贡献。** GESC 相对扁平 EvoSkill 的差异能否归因于编译组织，而非知识、Agent 或预算差异？
- **RQ5：成本收益。** 收益是否在生成成本、运行 token、时延和失败重试上仍有合理 Pareto 性？

## 2. 固定数据版本与样本口径

资源固定为仓库 `sierra-research/tau2-bench` 的 commit `668d3bcd135c02aa3438f987ef45735b7c163ee3`，对应 v1.0.1 之后的 τ³ 代码与 Banking grading 修订。所有报告必须记录 commit、任务文件 SHA-256、Skill 输入哈希和运行配置。

| 领域 | 场景能力 | 原始任务 | 编译用任务 | 主测试 | 扩展测试 | 文档/工具 |
|---|---|---:|---:|---:|---:|---:|
| Retail | 订单取消、退换、支付与地址修改 | 114 | train 74 | test 40 | base 114 仅兼容诊断 | 12 个政策段，16 个 assistant tools |
| Airline | 预订、改签、行李、取消与补偿 | 50 | train 30 | test 20 | base 50 仅兼容诊断 | 9 个政策段，14 个 assistant tools |
| Telecom | 账户操作与多轮技术排障 | 2,285 | train 74 | test 40 | full 2,285 | 51 个政策段，43 个双主体 tools |
| Banking Knowledge | 知识检索型银行客服 | 97 | 不使用任务；只用合法知识库 | base 97 | 检索配置消融 | 698 篇文档，20 个 tools |

主表的任务数为 `40 + 20 + 40 + 97 = 197`，不是 2,472。Telecom full 与 base/test 存在包含关系，只作为规模和组合泛化扩展，不能与主测试重复求和。官方 `base` 适合无训练的完整兼容评测；本研究的三个标准领域使用 train 轨迹编译，因此主因果结果必须使用互斥 test。Banking 无公开 train/test，故采用任务零样本：编译器可读取公开政策和 698 篇服务知识文档，但禁止读取 97 条任务、`required_documents` 和评价断言。

## 3. 信息边界与泄漏控制

编译阶段允许读取：政策文档、静态工具契约、Banking 的公开知识语料，以及 Retail/Airline/Telecom 的官方 train 任务。运行阶段只获得当前用户消息、当前环境工具、Skill 包与统一运行适配器。

以下信息不得进入编译器或运行提示：test/base 任务文本、initial state、reference actions、environment assertions、communication assertions、reward basis、Banking `required_documents`、评价器结果。参考 action 表示目标状态的一条参考轨迹；只有 reward basis 显式包含 `ACTION` 时才把路径匹配解释为目标。否则不得用 reference action imitation 代替任务成功。

每个 Skill manifest 必须满足：`uses_held_out_tasks=false`、输入文件哈希可复算、编译后不得因 test 结果返工默认参数。若调参，仅在 train 的内部划分或静态覆盖诊断上完成，并在正式运行前冻结。

## 4. 对照方法与公平控制

主实验包含七种方法：

1. `raw_policy_rag`：原政策/知识检索，不做过程化编译；
2. `native_prompt_skill`：原生长提示 Skill；
3. `schema_prompt_skill`：固定 SOP schema 的提示式 Skill；
4. `summary2skill`：政策与训练流程摘要；
5. `document_tool_maker`：以 actor-aware 工具契约组织文档；
6. `evoskill_compiler`：Knowledge Atom、治理规则、工作流与证据索引；
7. `graph_evoskill_compiler`：复用相同 atoms/policy/runtime，仅以图归纳 Pattern Card。

所有方法固定相同 runtime model、user simulator、任务顺序、trial/seed、温度、最大轮数、工具 schema、Telecom manual policy、Banking retrieval backend/top-k、上下文预算、超时与重试策略。主实验采用 oracle domain routing，因为研究问题是 Skill 质量而非路由质量；自主路由另列扩展实验，不能混入主结论。

建议正式配置使用 seeds `11/23/42`，每个 seed 运行 1 trial，并对全部方法复用相同 task × seed。这样每个任务共有三次独立重复，而不是 3 seeds × 3 trials 的九次重复。模型选择应在预实验后一次性冻结；如预算不足，可先运行 seed 42 的全方法 pilot，但不得把 pilot 当作最终显著性结论。

## 5. 指标体系

### 5.1 一级终点：原生任务结果

- **Native Reward**：τ³ evaluator 给出的任务 reward，按领域宏平均作为总指标；
- **Strict Task Success**：`reward = 1` 的比例；
- **Reward Breakdown**：分别报告 `DB`、`ENV_ASSERTION`、`COMMUNICATE`、`NL_ASSERTION`、`ACTION`；
- **pass@k / pass^k**：同一任务 k 次尝试至少一次全部成功，以及 k 次全部成功，分别描述能力上界和可靠性；
- **Domain Macro Success**：四个领域成功率等权平均，防止 Telecom full 或 Banking 数量支配结果。

最终论文主结论以 Native Reward、Strict Success、Domain Macro Success 为主，不另造一个取代官方 evaluator 的混合总分。

### 5.2 二级终点：论文主张对应指标

| 论文维度 | 指标 | 计算与用途 |
|---|---|---|
| 决策均衡性 | Status Macro-F1 / Balanced Accuracy | 在人工标注 trace 子集上评估 `observe/clarify/execute/instruct_user/deny/escalate/complete/failed`，避免多数类成功掩盖少数治理状态 |
| 治理一致性 | Policy Compliance Rate | 符合适用前提、禁止项、确认与转人工规则的 consequential decisions / 全部 consequential decisions |
| 双控制协作 | Actor Ownership Accuracy | 工具或动作分派给正确 requestor 的比例 |
| 双控制安全 | Illegal Cross-Actor Tool Rate | assistant 越权调用 user tool 或反向越权次数 / 可执行动作数，越低越好 |
| 过程完整性 | Preconditions / Exceptions / Verification Recall | 对任务所需前提、例外分支和后置验证的覆盖率；由盲评 trace 标注获得 |
| 可追溯性 | Decision Provenance Coverage | 需要政策/知识支撑的决定中，存在有效 source/KA/document 记录的比例 |
| 证据精度 | Provenance Precision | 所引来源确实支持对应决定的比例；抽样双人标注并报告一致性 |
| Banking 检索 | Required-document Recall@k / MRR | `required_documents` 仅在离线评价时使用，不进入查询、Skill 或 reranker |
| 效率 | tokens、agent cost、wall time、turns、tool calls | 同时报告均值、中位数与 P95，构建质量—成本 Pareto frontier |

Status 和 provenance 不是 τ³ 原生 gold，必须在预注册的分层样本上人工标注：建议每领域随机抽取 50 条 task-trial，覆盖成功/失败、读/写工具及不同 reward basis；两位标注者独立标注，冲突由第三人裁决，报告 Cohen's κ 或 Krippendorff's α。LLM judge 只能作为 proxy，并需在人类样本上校准。

### 5.3 静态 Skill 质量

静态指标用于解释机制而非替代 runtime 成功率：Source-grounded Rule Rate、政策/工具覆盖率、冲突规则数、重复 atom 比例、图 pattern 覆盖与纯度、Skill token 长度、编译 token/费用/耗时。Banking 的 698 篇全文保存在 `evidence_index.json`，`SKILL.md` 只保留可检索引用，防止上下文长度成为不公平优势。

## 6. 统计分析

分析单位是相同 task × trial 的配对结果。对每个方法相对 EvoSkill、GESC 的比较执行：

- task-level paired bootstrap 10,000 次，报告差值与 95% CI；
- Strict Success 使用配对 McNemar 检验；连续 reward、成本和长度可用配对 permutation test；
- 四领域分别报告，再按领域宏平均；
- 多重比较采用 Holm 校正；同时报告效应量，不以 `p < .05` 代替实际收益；
- full Telecom 的任务族可能高度相关，需按任务模板/目的进行 cluster bootstrap，不能把近重复任务当作独立样本放大显著性。

缺失或基础设施失败不得记为模型失败后静默混入分母。主表同时给出 ITT（所有计划任务）与 valid-run（排除预定义 infrastructure error）结果，并报告排除数量与原因。

## 7. 消融与扩展实验

核心消融按优先级执行：`No Security Policy`、`No Workflow Patterns`、`No Evidence Index`、`No Actor Controller`、`Flat Atoms vs Graph Patterns`、GESC 的 random patterns/no centrality/no source diversity。每项只改变一个组件，其余配置复用主实验。

扩展实验包括：Telecom full 的组合泛化；Banking `rag top-k ∈ {5,10,20}` 敏感性；自主 Skill routing；第二 runtime model 复现；噪声用户或 voice full-duplex。它们用于外部效度，不能替代 197 条冻结主协议。

## 8. 结论判据

论文主张获得支持需同时满足：

1. EvoSkill 或 GESC 在 Domain Macro Native Reward/Strict Success 上相对强结构化基线呈稳定正效应，而非只胜过 raw policy；
2. 至少三个不同类型领域方向一致，且不是 Banking 单域驱动；
3. 治理、actor ownership 或过程完整性至少一项显著改善，支撑“多维度 Skill”而非纯文本优化；
4. GESC 相对 EvoSkill 的结论只在共享 atoms、policy、runtime 和预算的配对实验中陈述；
5. 所有负结果、置信区间和成本均报告。若只改善治理而不改善成功率，应陈述为安全—效用权衡，不宣称全面优越。

---

## 9. A2SC/G-A2SC 评估协议（v2）

本节覆盖前述 EvoSkill/GESC 表述。正式主比较增加 `no_skill`、`tool_schema_compiler`、`a2sc` 和 `g_a2sc`。A2SC 使用类型化 Knowledge Atoms、直接 Tool Binding 与局部动作约束；G-A2SC 与 A2SC 共享输入、模块预算和 Runtime，只增加编译期语义图。

主 Runtime 统一为：

```text
module catalog → activate_skill(module_id)
→ Runtime 强制加载完整 Action Module → τ³ 原生工具执行
```

主实验使用 `hard_progressive_advisory`：强制加载模块但只审计违规，不阻止业务工具调用。所有方法看到相同 τ³ 工具，不因 Skill 方法动态增加或删除工具。

### 9.1 新增基线

| 方法 | 定义 |
|---|---|
| `no_skill` | 仅统一 Runtime adapter 与 τ³ 原生工具 |
| `tool_schema_compiler` | 只将官方工具 schema 渲染为 Tool Cards，不读取训练轨迹、不绑定政策原子 |
| `a2sc` | 类型化 atoms + Tool Binding + 局部 `BEFORE/REQUIRES/VERIFIES` 约束 |
| `g_a2sc` | 与 A2SC 完全相同，仅使用编译期语义图组织条件、例外和变体 |

旧 `evoskill_compiler` 与 `graph_evoskill_compiler` 作为 v1 兼容实现保留，不直接等同于完整 A2SC/G-A2SC。

### 9.2 新增指标

对每个激活模块记录适用的原子集合：前置条件 `P`、顺序约束 `O`、治理约束 `G`、后置验证 `V`。

```text
Atom Execution Coverage
= (satisfied(P)+satisfied(O)+satisfied(G)+satisfied(V))
  / (|P|+|O|+|G|+|V|)

Tool Binding Accuracy
= 正确使用 module 绑定工具的调用数 / 相关工具调用数

Precondition Satisfaction
= 满足前置条件后执行的动作数 / 需要前置条件的动作数

Verification Recall
= 完成的后置验证数 / 应完成的后置验证数

Provenance Coverage
= 能回溯到有效 atom 的决定数 / 需要来源的决定数
```

另报告 `Trigger Recall`、`Route@1`、`Unnecessary Activation Rate` 和 `Skill Tokens per Task`。这些指标必须由激活日志、工具轨迹和预先标注的适用原子计算，不能由模型自报。

实现中将自动轨迹可计算的 `activated_required_tool_recall_proxy` 与 `business_tool_grounding_precision_proxy` 明确标记为代理指标。它们只说明已激活模块声明的工具与实际调用是否重合，不能替代人工标注的 Tool Binding Accuracy，因为合法支持工具可能不在当前模块的声明集合中。`make_annotation_template.py` 自动写入预测激活，`evaluate_annotations.py` 使用预注册的 `gold_requires_skill` 与 `gold_applicable_module_ids` 计算 Trigger Recall、Route@1、无效激活率和正式绑定准确率。

### 9.3 核心消融

1. `a2sc_no_typed_atoms`：退回 policy section-level chunks；
2. `a2sc_no_tool_binding`：保留 atoms，但不生成工具绑定；
3. `a2sc_no_local_motifs`：不使用训练轨迹局部约束；
4. `g_a2sc_no_graph`：即 A2SC，作为图增量直接对照。

第一阶段不加入 Runtime Graph-RAG、任意脚本生成、动态 tool allowlist 或强制 policy guard。

### 9.4 结果判据

A2SC 只有在 Domain Macro Strict Success 相对最强非提出基线为正、至少三个领域方向一致、前置条件满足率或验证召回率有实质改善、成本不高于 Native Prompt 且违规不恶化时，才支持其主张。

G-A2SC 只有在多条件/例外子集相对 A2SC 改善，或以更低成本达到相同性能时，才支持图编译贡献。若 G-A2SC 与 A2SC 持平，应采用更简单的 A2SC。
