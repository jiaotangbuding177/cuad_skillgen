# Atom-to-Action Skill Compilation：算法与渐进式 Runtime 修改设计

> 文档状态：设计稿，不代表已实现或已获得实验提升  
> 日期：2026-08-13  
> 适用范围：`D:\skillgen\τ-bench` 的 Skill 生成、注入和评估链路  
> 本文不修改既有结果；所有数值预测均为待验证假设，不是实验观测。

## 1. 结论先行

当前路线应当升级，但不应扩展成一个包含任意脚本生成、运行时图检索、动态工具生成和复杂安全中间件的庞大系统。最有可能产生实际收益的修改只有三项：

1. 把粗粒度政策段真正分解为可执行的类型化原子；
2. 在编译期把政策条件与现有 τ³ 工具的主体、参数、前置条件和验证动作直接绑定；
3. 把完整轨迹记忆改成可迁移的局部动作约束，并编译为少量聚焦的 Action Skill Modules。

据此，建议将原 `evoskill_compiler` 重命名和升级为：

> **Atom-to-Action Skill Compiler（A2SC）**：不使用图，通过类型化知识原子与工具契约的直接绑定，编译可执行 Action Modules。

将原 `graph_evoskill_compiler` 对齐升级为：

> **Graph-enhanced Atom-to-Action Skill Compiler（G-A2SC）**：与 A2SC 共享原子、工具绑定、输出契约、Runtime 和预算，只用编译期图改进条件、例外和语义变体的组合。

论文主方法可以是 G-A2SC，A2SC 是必须保留的非图前驱与核心强对照。二者不生成 τ³ 业务工具代码，只生成如何正确使用既有工具的可执行 Skill 语义。

## 2. 对当前设计的客观审查

### 2.1 当前方法尚未真正完成“知识原子化”

当前 bootstrap 的 `build_atoms()` 将一个完整 policy section 直接作为一个 `policy_section` atom，将完整 tool description 作为一个 `tool_contract` atom。这提供了 ID 和来源，但通常没有把一个段落中的多个条件拆成最小命题。因此当前产物更接近“带编号的文档分段”，还不是严格的 Knowledge Atom 编译。

真正有用的原子至少应区分：

- 适用条件；
- 必填信息；
- 允许动作；
- 禁止动作；
- 确认要求；
- 行为主体；
- 工具效果；
- 后置验证；
- 失败与升级路径。

### 2.2 当前 workflow 记忆过细，泛化线索不足

现有 `workflow_patterns.json` 对训练集 reference action 的完整序列计数。静态统计显示：

| 领域 | 有动作序列的训练任务 | 唯一完整序列 | 唯一比例 | 唯一二元动作片段 |
|---|---:|---:|---:|---:|
| Retail | 72 | 52 | 72.2% | 57 |
| Airline | 25 | 19 | 76.0% | 18 |
| Telecom | 74 | 67 | 90.5% | 49 |

完整序列高度稀疏，尤其 Telecom 中 74 条序列有 67 条不同。直接记忆整条 reference trajectory 容易过拟合，而且 reference action 并不必然是唯一正确路径。相较之下，局部动作片段、前后依赖和确认边更可能跨任务复用。

### 2.3 工具落地有真实信号，但当前未被结构化利用

使用不读取 held-out task 的编译侧资产统计，工具描述中含 `must`、`only`、`before`、`confirm`、`cannot`、`required`、`if` 等约束词的比例为：

| 领域 | 工具数 | 含显式条件/限制的工具 | 比例 |
|---|---:|---:|---:|
| Retail | 16 | 16 | 100.0% |
| Airline | 14 | 10 | 71.4% |
| Telecom | 43 | 22 | 51.2% |
| Banking Knowledge | 21 | 6 | 28.6% |

这说明在前三个交互领域，Tool Schema 本身已经包含大量前置、确认和主体线索。把这些线索编译为 Tool-grounded Action Card 有合理的收益依据；在 Banking Knowledge 中则不应预期同等提升，因为其主要瓶颈更可能是文档检索。

### 2.4 当前 Package-aware v1 存在重复上下文

Telecom 离线检索审计中，`evoskill_compiler` 一轮注入 9,188 字符；同一“移动数据问题”内容分别从 `skill`、`rule`、`atom` 通道重复出现，并且该查询没有命中 `workflow`。GESC 又同时检索 Pattern Card 和 SKILL 中的 Pattern 段，仍存在重复。

因此，多通道检索数量本身不能作为 Package-aware 的价值。下一版应在编译期把相关政策、工具与流程融合为一个 Action Module，Runtime 只检索或激活模块，不再分别检索五个语义重叠通道。

### 2.5 当前图产物不具备足够的可执行语义

现有图以 token Jaccard 阈值生成统一类型的 `SEMANTIC_VARIANT_OR_DEPENDENCY` 边，Pattern Card 主要列出中心 atom 和相邻 ID。这类结构适合证明图文件能够构建，但不足以证明模型能据此选择正确工具、满足确认要求或完成后置验证。

因此，G-A2SC 的图必须使用有语义的边，并输出自然语言可消费的 Action Module；仅输出节点 ID 不应被视为有效图增强。

## 3. 研究问题和因果边界

### 3.1 核心研究问题

- **RQ1**：类型化 Atom-to-Action 编译是否比原始政策、摘要、模板和工具列表更能提高端到端 SOP 成功率？
- **RQ2**：改进是否来自工具前置条件、确认、行为主体和后置验证的正确表达？
- **RQ3**：在保持相同 atoms、工具绑定、模块预算和 Runtime 时，编译期图是否额外改善条件、例外与变体组合？
- **RQ4**：渐进式 Skill 激活能否降低上下文成本，同时保持或提高任务成功率？

### 3.2 明确保留的因果边界

- 不生成或修改 τ³ 业务工具；
- 不修改工具 schema、环境、user simulator 或 evaluator；
- 主实验采用 oracle domain routing；
- G-A2SC 的 `knowledge_graph.json` 不进入 Runtime；
- Runtime 不执行 Graph-RAG；
- test/base 任务、gold action、assertion 和 `required_documents` 不进入编译；
- A2SC 与 G-A2SC 使用同一个类型化 atom 集和相同输出预算；
- 图方法只改变 atoms 到 modules 的组织与选择。

## 4. A2SC：非图 Atom-to-Action Skill Compiler

### 4.1 输入

\[
\mathcal{X}=\{P,K,T,R_{train}\}
\]

其中：

- \(P\)：政策与 SOP；
- \(K\)：合法的知识文档；
- \(T\)：τ³ 工具 schema，包括名称、描述、参数和 requestor；
- \(R_{train}\)：仅在存在官方 train split 时使用的训练动作轨迹。

### 4.2 步骤一：最小类型化原子抽取

每个原子只表达一个可验证命题：

```json
{
  "atom_id": "A-0017",
  "type": "precondition",
  "subject": "modify_pending_order_address",
  "predicate": "requires",
  "object": "order.status == pending",
  "polarity": "required",
  "source": {
    "file": "policy.md",
    "section": "Modify order",
    "span": "..."
  },
  "confidence": 0.94
}
```

冻结的原子类型为：

```text
fact
precondition
required_input
permission
prohibition
confirmation
actor_constraint
tool_effect
postcondition
exception
escalation
communication_requirement
```

不建议继续增加更多类型，除非 dev 静态审计证明现有类型无法表达重要规则。

### 4.3 步骤二：确定性 Tool Grounding

每个工具从官方 schema 直接建立 `ToolCard`：

```json
{
  "tool": "modify_pending_order_address",
  "actor": "assistant",
  "parameters": ["order_id", "new_address"],
  "observes": [],
  "changes": ["order.shipping_address"],
  "bound_atom_ids": ["A-0017", "A-0018", "A-0019"],
  "must_check_before": ["order.status", "identity", "confirmation"],
  "must_verify_after": ["returned shipping address"],
  "forbidden_when": ["order.status != pending"]
}
```

绑定分两步完成：

1. 工具名、参数名、政策显式引用和标题匹配产生候选；
2. 受约束模型只判断“该 atom 是否约束该 tool”，不得重写工具或政策。

未绑定 atom 保留为领域规则，不强迫绑定；低置信绑定不进入 Action Module。

### 4.4 步骤三：从完整轨迹改为局部动作约束

训练轨迹只归纳以下局部结构：

- `A BEFORE B`：稳定的先后关系；
- `A REQUIRES OBSERVATION X`：动作前观察；
- `A REQUIRES CONFIRMATION`：写操作确认；
- `A FOLLOWED_BY VERIFY B`：后置验证；
- `ASSISTANT INSTRUCTS USER_TOOL`：双控制主体；
- `IF failure THEN fallback`：失败恢复。

只有满足最小支持度且不与政策冲突的 motif 才保留。训练频率只作为排序信号，不能覆盖正式政策。

### 4.5 步骤四：无图模块归并

A2SC 不聚类、不做图传播，按以下确定性键归并：

```text
primary intent
+ primary consequential tool
+ policy section scope
```

每个模块包含：

```json
{
  "module_id": "retail.modify_pending_address",
  "name": "Modify a pending order address",
  "description": "Use when a verified customer asks to change the shipping address of a pending order.",
  "triggers": ["change delivery address", "wrong shipping address"],
  "required_tools": ["get_order_details", "modify_pending_order_address"],
  "observe": ["identity", "order status", "current address"],
  "act": ["explain exact change", "obtain confirmation", "call tool"],
  "verify": ["tool returned updated address"],
  "branches": ["non-pending order", "confirmation denied", "tool failure"],
  "forbidden": ["write before confirmation"],
  "source_atom_ids": ["A-0017", "A-0018", "A-0019"]
}
```

模块目标长度建议为 400--1,200 tokens；一个任务最多激活两个模块。长度是 dev 预算参数，不根据 test 成绩调整。

### 4.6 步骤五：静态编译检查

只保留与 τ³ 成功直接相关的五项检查：

1. 工具名与参数存在；
2. requestor/actor 正确；
3. consequential tool 的显式前置条件未丢失；
4. confirmation/prohibition 不互相冲突；
5. 每个硬约束具有来源。

不在第一版加入通用程序验证器、任意代码扫描或复杂逻辑求解器。

## 5. G-A2SC：严格对齐的图增强版本

G-A2SC 完全复用 A2SC 的：

- 类型化 atoms；
- ToolCards；
- 局部轨迹 motifs；
- 静态检查；
- module schema；
- module 数量和 token 预算；
- Runtime。

唯一变化是步骤四的模块归并。

### 5.1 图节点与边

节点仍然是 A2SC 已产生的 atoms 和 ToolCards，不新增测试信息。边类型只保留：

```text
GROUNDS_TOOL
REQUIRES
PROHIBITS
PRECEDES
VERIFIES
EXCEPTION_TO
SAME_INTENT_VARIANT
OWNED_BY
```

禁止使用统一的“可能相关”边替代上述语义关系。

### 5.2 图的实际作用

图只用于三个明确目的：

1. 从 consequential tool 出发收集一跳前置、禁止和验证原子；
2. 通过 `EXCEPTION_TO` 补齐容易丢失的例外分支；
3. 通过 `SAME_INTENT_VARIANT` 选择不同来源的代表表达，避免模块只覆盖一种措辞。

不进行运行时多跳搜索。编译后的结果仍是与 A2SC 相同 schema 的 Action Module。

### 5.3 图方法获得支持的最低判据

若 G-A2SC 相对 A2SC 仅增加 token，且没有在以下任一指标产生稳定改善，则图贡献不成立：

- 多条件任务 Strict Success；
- Exception Branch Accuracy；
- Preconditions Satisfaction；
- 跨模板/复合 Telecom 子集成功率。

整体平均小幅领先但这些机制指标无变化，不能归因为图增强。

## 6. 精简的 Progressive Skill Runtime

### 6.1 为什么替换五通道 BM25

当前五通道会重复注入同一政策内容，且 action-name workflow 不易被自然语言 query 命中。新 Runtime 使用一个模块目录和一个激活接口：

```text
compact module catalog
-> activate_skill(module_id)
-> runtime hard-loads complete module
-> model calls original τ³ tools
```

### 6.2 常驻上下文

每个模块只常驻：

```text
module_id + name + description + required_tools
```

完整 atom、来源和 procedure 不常驻。

### 6.3 显式激活

提供统一元工具：

```json
{
  "name": "activate_skill",
  "parameters": {"module_id": "string"}
}
```

调用后 Runtime 强制返回完整模块。它不是业务动作，不修改 τ³ 环境，也不计入业务 Tool Selection Accuracy，但计入 token、延迟和 Trigger 指标。

与让模型自行 `read(SKILL.md)` 相比，硬加载使实验可以可靠地区分“看见目录”“选择模块”和“遵循模块”。Skill 使用效果依赖 agent harness，Trigger、Compliance 和 Boundary 是不同瓶颈，因此 Runtime 必须固定并完整披露[[1]](https://arxiv.org/abs/2608.04828)。

### 6.4 工具暴露与 Guard

主实验中：

- 所有方法看到相同的 τ³ 官方工具；
- Runtime 不根据模块删减或新增业务工具；
- Runtime 不阻止违规调用，只记录模块是否规定了该工具、前置条件和主体；
- Banking 事实仍只能通过官方 `KB_search` 获得。

这样避免 Guard 替模型完成任务。强制拦截只作为安全扩展实验，不进入主表。

### 6.5 Runtime 对所有方法的兼容

- 单文件方法可只有一个 domain module；
- 模块化方法拥有多个 action modules；
- 所有方法使用同一个 catalog renderer、`activate_skill`、最大激活数和字符预算；
- 主实验报告自然格式表现；另做 budget-matched 对照，避免长度单独解释结果。

## 7. 基线的简单而公平的定义

| 方法 | 简单设计 | 不允许额外获得的能力 |
|---|---|---|
| No Skill | 只有统一 Runtime adapter 与 τ³ tools | 无政策 Skill |
| Raw Policy RAG | 检索原始政策段；不重写、不归纳流程 | 无 ToolCard、无训练 motif |
| Native Prompt Skill | 同一生成模型直接把合法源资产写成单一 Skill | 无固定 schema、无附件检索 |
| Schema Prompt Skill | 按 observe/check/act/verify/exception 固定模板生成 | 无 atom 抽取、无训练 motif |
| Summary2Skill | 压缩政策和训练信息为简洁摘要 | 无结构化 ToolCard、无 provenance graph |
| Document Tool Maker | 以每个工具为中心生成名称、参数、actor 和简短用法 | 不做政策原子化和跨工具流程归纳 |
| Tool-Schema Compiler | 确定性地把官方 tool schema 渲染为 ToolCards | 不读取训练轨迹，不绑定政策条件 |
| A2SC | 类型化 atoms + direct tool binding + local motifs + Action Modules | 无图结构 |
| G-A2SC | 与 A2SC 相同输入和契约，以编译期图归并模块 | Runtime 不读图 |

`Tool-Schema Compiler` 是必须新增的强基线。没有它，就无法判断 A2SC 的收益是来自真正的政策—工具绑定，还是仅仅因为把工具描述重新排版了一次。

## 8. 预期指标：预测、成功判据与失败判据

### 8.1 不能把预测写成结果

当前目录没有 live `results.json`，正式 Skill packages 也是 `0/28`。因此不能提供声称已经观测到的准确率。以下是基于静态结构的预注册方向预测和最小有意义效应，不是论文结果。

### 8.2 相对表现预测

| 方法 | Task Success 预期 | Procedure Compliance 预期 | Tool Grounding 预期 | Token 成本 | 主要风险 |
|---|---|---|---|---|---|
| No Skill | 最低或接近最低 | 低 | 中：模型仍看到 schema | 最低 | 缺少领域 SOP |
| Raw Policy RAG | 中低 | 低到中 | 中 | 中 | 找到规则但不会组织动作 |
| Native Prompt | 中 | 中 | 中 | 高 | 长文档干扰，条件分散 |
| Schema Prompt | 中到中高 | 中高 | 中 | 高 | 模板正确但领域绑定弱 |
| Summary2Skill | 中 | 中 | 中低 | 低到中 | 压缩丢失例外与限制 |
| Document Tool Maker | 中高 | 中 | 高 | 中高 | 工具清楚但政策绑定弱 |
| Tool-Schema Compiler | 中 | 中 | 高 | 中 | 只知道工具，不知道 SOP |
| **A2SC** | **高** | **高** | **高** | **中** | 原子抽取或绑定错误 |
| **G-A2SC** | **高；复杂任务预期最高** | **高** | **高** | **中** | 图边噪声抵消收益 |

### 8.3 有限幅度的量化预测

相对“当前最强非提出方法”而非相对最弱基线，预期：

| 对照 | Domain Macro Strict Success | Preconditions Satisfaction | Verification Recall | 预测置信度 |
|---|---:|---:|---:|---|
| A2SC - strongest non-proposed baseline | `+2` 至 `+6` 个百分点 | `+4` 至 `+10` 个百分点 | `+3` 至 `+8` 个百分点 | 中等 |
| G-A2SC - A2SC，全部主任务 | `0` 至 `+3` 个百分点 | `0` 至 `+4` 个百分点 | `0` 至 `+3` 个百分点 | 低到中等 |
| G-A2SC - A2SC，多条件/例外子集 | `+2` 至 `+6` 个百分点 | `+3` 至 `+8` 个百分点 | `+1` 至 `+5` 个百分点 | 中等 |

这些区间是研究先验，不可用于事后修改算法。正式结果可能为零或负值。

### 8.4 分领域预测

- **Retail**：A2SC 最有希望明显提升，因为全部 16 个工具描述都带条件/限制，且确认后写操作很多。
- **Airline**：预计改善改签、取消和补偿的前置检查，但政策长条件可能导致原子抽取错误。
- **Telecom**：预期改善诊断—干预—测速验证链；Actor Ownership 很大程度受双控制 harness 保护，不应把其高分作为主要算法贡献。
- **Banking Knowledge**：A2SC/G-A2SC 的工具编译增益可能接近零；主瓶颈仍是 `KB_search` 的 required-document recall。若整体优势完全由前三域贡献，应如实报告。

### 8.5 预注册的最低成功判据

A2SC 只有同时满足以下条件才值得作为论文贡献：

1. 相对最强非提出方法，Domain Macro Strict Success 的配对差值为正，95% CI 不出现明显负效应；
2. 至少三个领域方向一致，或明确解释 Banking 的检索型例外；
3. Preconditions Satisfaction 或 Verification Recall 至少一项有不低于 5 个百分点的改善；
4. 运行 token 不高于 Native Prompt，最好降低至少 20%；
5. Tool Error Rate 和 Policy Violation 不恶化。

G-A2SC 只有在多条件/例外子集优于 A2SC，或以更低 token 达到相同性能时，图贡献才获得支持。若 G-A2SC 与 A2SC 持平，应保留 A2SC 为最终方法，而不是因图更复杂就坚持图版本。

## 9. 指标设计

### 9.1 一级指标

- Native Reward；
- Strict Task Success；
- Domain Macro Strict Success；
- DB / ENV_ASSERTION / COMMUNICATE / NL_ASSERTION / ACTION breakdown。

### 9.2 Skill 使用指标

- Trigger Recall：需要模块时是否调用 `activate_skill`；
- Route@1：首次激活模块是否正确；
- Activated-module Utility：激活后是否使用模块要求的工具或步骤；
- Unnecessary Activation Rate；
- Skill Tokens per Task。

### 9.3 Action-grounding 指标

- Tool Selection Accuracy；
- Argument Schema Validity；
- Actor Ownership Accuracy；
- Preconditions Satisfaction Rate；
- Confirmation-before-Action Rate；
- Verification Recall；
- Exception Branch Accuracy；
- Excess Tool Call Rate。

其中 Trigger、Compliance 与 Boundary 应分别报告，不能合并后掩盖失败来源[[1]](https://arxiv.org/abs/2608.04828)。已有跨领域研究也表明，自生成 Skill 并不天然有效，聚焦模块可能优于全面文档，因此必须同时报告负效应与 token 成本[[2]](https://arxiv.org/abs/2602.12670)。

## 10. 必要消融，而非全面堆叠

只做四个核心消融：

1. `A2SC - Typed Atoms`：退回 section-level chunks；
2. `A2SC - Tool Binding`：保留 atoms，但不生成绑定；
3. `A2SC - Local Motifs`：不使用训练动作片段；
4. `G-A2SC - Graph`：即 A2SC 主对照。

Runtime 只比较：

1. `Full Injection`；
2. `Progressive Hard Activation`。

第一版不做运行时 Graph-RAG、动态 tool allowlist、强制 policy guard、任意 scripts 生成或多 Agent 编排。

## 11. 建议实施顺序

1. 冻结本文 atom schema、module schema 和成功判据；
2. 先实现 `Tool-Schema Compiler`，确认 Runtime 能消费 ToolCard；
3. 实现 A2SC 的类型化原子和直接工具绑定；
4. 只用 Retail/Airline/Telecom train 与静态政策做 compile audit；
5. 实现单目录 `activate_skill` Runtime，替代五通道重复检索；
6. 对全部基线执行同一 smoke task，不调 test 参数；
7. 完成 A2SC 主实验后再实现 G-A2SC；
8. 只有 A2SC 确实改善工具落地指标时，才投入图增强实验。

这个顺序有意把图放在后面：如果 flat Atom-to-Action 编译本身无效，图只会组织无效结构，不会自动产生科研价值。

## 12. 最终论文叙事

若结果支持假设，最稳健的论文叙事是：

> 现有 Document-to-Skill 方法往往停留在政策摘要或工具说明，缺少从来源规则到可执行动作的显式落地。A2SC 将企业 SOP 分解为来源可追踪的类型化原子，并绑定到现有 Agent 工具的前置条件、行为主体和验证步骤；G-A2SC 进一步在相同原子和 Runtime 下利用编译期图组织条件、例外和语义变体。渐进式 Runtime 只暴露紧凑模块目录，并在显式激活后加载完整过程，从而同时评估 Skill 的可发现性、程序遵循和边界行为。

如果 G-A2SC 未超过 A2SC，则论文应把 A2SC 作为主方法，把图实验报告为负结果或条件性收益，而不是维持“图一定更先进”的预设。

## References

[1] Han, J., Yuanjian Xu, Ying Liao, et al. (2026). Skill-Use: Can LLMs Actually Use Skills in Agentic Harnesses? arXiv preprint arXiv:2608.04828. https://arxiv.org/abs/2608.04828

[2] Li, X., et al. (2026). SkillsBench: Benchmarking How Well Agent Skills Work Across Diverse Tasks. arXiv preprint arXiv:2602.12670. https://arxiv.org/abs/2602.12670
