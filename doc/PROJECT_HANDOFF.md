# CUAD-SkillGen 项目交接文档

> 更新时间：2026-08-11
>
> 当前分支：`main`
>
> 当前提交：`a7c7676 docs: add EvoSkill improvement experiment handoff document`
>
> 工作区状态：存在未提交的实验代码、文档与结果修改，接手时不得覆盖或回滚
>
> 自动测试：`tests/`目录20项全部通过（项目根目录全量收集受`test_ecnu_json.py`缺少API Key影响）
>
> 当前实验阶段：**Graph-enhanced Skill Compilation（GESC）新基线实现完成，正在进入Skill生成与运行时对照实验**

## 1. 项目目标

本项目研究如何将企业合同语料自动编译为可供大语言模型Agent执行的Skill package。核心目标方法是`evoskill_compiler`：它先从训练合同中抽取Knowledge Atoms（KAs），再编译为可检索知识、审查规则和显式治理策略。

项目不再追求“EvoSkill在所有指标上第一”，当前已经收敛的论文主张是：

> EvoSkillCompiler的主要价值在于提高任务执行成功率、类别均衡状态判断、治理一致性和规则可追溯性，同时保持较高的答案和证据语义质量；其当前局限是原子化知识如何更有效地转化为目标合同中的最小、完整和精确证据，以及相对强结构化基线的成本收益。

## 2. 当前整体进度

### 2.1 已完成

- 完成CUAD-SkillGen数据组织和合同级train/dev/test划分。
- 将CUAD类别组织为9个能力域。
- 完成5种原始Document-to-Skill方法：
  - `native_prompt_skill`
  - `schema_prompt_skill`
  - `summary2skill`
  - `document_tool_maker`
  - `evoskill_compiler`
- 在保留现有EvoSkill的前提下，新增第6种独立实验基线：
  - `graph_evoskill_compiler`
- 完成统一Package-aware Agent。
- 完成增量式、可恢复的运行时评测链路。
- 五种方法均完成4668/4668条test任务。
- 最终运行错误率均为0。
- 完成状态、任务、治理、证据、语义答案、静态规则和成本评测。
- 完成Evidence F1的小样本检索与错误类型诊断。
- 完成Mapper 5×5阈值敏感性分析。
- 增加Status Macro-F1与Balanced Accuracy。
- 增加Containment-aware Evidence F1。
- 增加Semantic Evidence Validity。
- 完成论文正文形式的实验章节。
- GESC图构建、Pattern归纳、来源多样性选择单元测试已补充。
- `tests/`目录20项单元测试全部通过。

### 2.2 当前论文成熟度

当前结果足以构成pilot study和论文实验章节初稿，但还不适合作为最终因果结论。主要缺口是：

- 尚无配对显著性检验和置信区间；
- 尚未统一各方法的Skill生成模型；
- 尚未完成人工证据校准；
- 尚未完成EvoSkill核心组件消融；
- 当前Agent采用Oracle Skill routing，而非自主多Skill路由。

## 3. 数据与实验设置

### 3.1 数据划分

| 划分 | 合同数 | 用途 |
|---|---:|---|
| Train | 306 | 生成五种方法的Skill |
| Dev | 102 | 检索配置确认与后续校准 |
| Test | 102 | 最终运行时评估 |

### 3.2 Test任务

每种方法共4668条任务：

| Gold状态 | 数量 | 比例 |
|---|---:|---:|
| `answered` | 1447 | 31.00% |
| `evidence_missing` | 2843 | 60.90% |
| `missing_input` | 108 | 2.31% |
| `unsupported_scope` | 108 | 2.31% |
| `needs_human_review` | 162 | 3.47% |

### 3.3 冻结运行配置

| 配置 | 取值 |
|---|---|
| Runtime model | `ecnu-plus` |
| Split | `test` |
| Run ID | `final-k10-k6` |
| Target contract retrieval | BM25 top-10 chunks |
| Skill knowledge retrieval | BM25 top-6 items |
| Governance tasks | Included |
| Skill routing | Oracle/task-specified |

运行时不向Agent暴露Gold status、reference answer或Gold evidence。训练知识只能用于搜索和推理，最终证据必须是从目标合同已检索区间中验证通过的原文。

## 4. 当前核心结果

### 4.1 论文主表

| 方法 | Task Success ↑ | Status Macro-F1 ↑ | Governance Boundary ↑ | Academic Judge ↑ | Semantic Evidence Validity（端到端）↑ |
|---|---:|---:|---:|---:|---:|
| Native Prompt Skill | 0.4994 | 0.5824 | 0.5714 | 0.9024 | 0.7996 |
| Schema Prompt Skill | 0.6298 | 0.8380 | 0.8810 | 0.8404 | 0.7630 |
| Summary2Skill | 0.6407 | 0.7696 | 0.7328 | **0.9660** | **0.8680** |
| Document Tool Maker | 0.6345 | 0.7451 | 0.6984 | 0.9492 | 0.8210 |
| **EvoSkillCompiler** | **0.6435** | **0.8477** | **0.8916** | 0.9545 | 0.8411 |

当前最可靠的解释：

- EvoSkill在任务执行、类别均衡状态判断和治理边界上排名第一。
- Summary2Skill在答案语义质量和语义证据有效性上排名第一。
- Schema是低成本强基线，其状态和治理结果接近EvoSkill。
- EvoSkill相对Summary和Schema的部分差距很小，未做显著性检验前不能宣称稳定领先。

### 4.2 证据结果

| 方法 | Strict Evidence F1 | Containment Evidence F1 | Semantic Validity（条件） | Semantic Validity（端到端） |
|---|---:|---:|---:|---:|
| Native | 0.4611 | 0.6455 | 0.8921 | 0.7996 |
| Schema | **0.4772** | 0.6508 | 0.8571 | 0.7630 |
| Summary2Skill | 0.4329 | **0.6638** | **0.9537** | **0.8680** |
| Document Tool | 0.4485 | 0.6447 | 0.9238 | 0.8210 |
| EvoSkill | 0.4315 | 0.6348 | 0.9319 | 0.8411 |

EvoSkill的Strict F1从0.4315经Containment修正后提高到0.6348，增加20.33个百分点，说明长引文完整包含Gold是严格F1偏低的重要原因。但Containment修正后仍比Summary低2.90个百分点，因此不能把全部差距归因于Mapper。

### 4.3 静态规则与成本

| 方法 | Source-grounded Rule Rate | Boundary Policy Coverage | 生成Token |
|---|---:|---:|---:|
| Native | 0.0337 | 0.2444 | 724,469 |
| Schema | 0.0237 | 1.0000 | 719,382 |
| Summary2Skill | 0.0000 | 0.5778 | 21,724,271 |
| Document Tool | 0.0000 | 0.4667 | 23,932,205 |
| EvoSkill | **0.8175** | **1.0000** | 22,130,872 |

EvoSkill的规则可追溯性明显领先，但其生成Token约为Native的30.55倍。相对Schema只有小幅性能增益，因此不能主张明显性价比优势。

## 5. 最近集中解决的问题

### 5.1 Status Accuracy受类别不平衡影响

#### 原问题

Summary的原始Status Accuracy为0.7569，略高于EvoSkill的0.7562。由于`evidence_missing`占60.90%，原始Accuracy主要受到多数类影响，无法代表五种状态的均衡能力。

#### 已完成修正

新增：

- Status Macro-F1；
- Balanced Accuracy；
- 五类状态Precision、Recall、F1；
- 状态混淆矩阵。

#### 修正后结果

| 方法 | Status Accuracy | Macro-F1 | Balanced Accuracy |
|---|---:|---:|---:|
| Native | 0.6041 | 0.5824 | 0.6712 |
| Schema | 0.7279 | 0.8380 | 0.8475 |
| Summary | **0.7569** | 0.7696 | 0.7937 |
| Document Tool | 0.7412 | 0.7451 | 0.7714 |
| EvoSkill | 0.7562 | **0.8477** | **0.8626** |

结论：类别补正后EvoSkill排名第一，原始Accuracy低估了其少数治理状态能力。

### 5.2 EvoSkill Evidence F1最低

#### 原问题

EvoSkill Strict Evidence F1为0.4315，在五种方法中最低。需要判断问题来自：

- 合同检索失败；
- KA query drift；
- Agent引文抽取失败；
- Gold span映射过严；
- Skill或证据选择质量真实较差。

#### 已完成诊断

随机抽取200条gold answered任务，比较三种查询：

| 查询 | Gold Chunk Recall@10 | All Gold Recall@10 | MRR |
|---|---:|---:|---:|
| Task only | 0.9450 | 0.8950 | 0.5876 |
| Package without KA | 0.9300 | 0.8950 | 0.6515 |
| Full query | **0.9550** | **0.9150** | **0.6518** |

完整KA查询没有整体降低Gold召回，因此当前结果不支持“KA普遍造成query drift”。

200条失败类型：

| 类型 | 数量 | 比例 |
|---|---:|---:|
| Strict匹配成功 | 106 | 53.0% |
| 替代或错误证据 | 48 | 24.0% |
| 接近Gold但未通过阈值 | 22 | 11.0% |
| Gold chunk已召回但引用抽取失败 | 15 | 7.5% |
| 检索失败或query drift | 9 | 4.5% |

48条未匹配证据复用已有盲化Academic Judge判断后：

- 43条为合理替代证据；
- 3条为部分支持；
- 2条为明确错误。

该结果是对同一个Academic Judge缓存的二次归类，不是独立第二Judge，需要人工校准。

#### Mapper敏感性

在同一200条样本中：

- 正式阈值`IoU=0.5 / Text F1=0.8`：F1=0.4235；
- 放宽到`IoU=0.3 / Text F1=0.5`：F1=0.5153。

结果对阈值高度敏感，但不能根据test结果事后更换主阈值。正式Strict口径已经保留，敏感性结果只作为稳健性分析。

#### 当前最终判断

Evidence F1偏低不是单一原因：

1. Strict Gold-span对长引文和合理替代证据存在低估；
2. EvoSkill仍有少量真实证据选择、覆盖和抽取差距；
3. 主要问题位于Gold chunk召回之后，而不是KA整体无法检索正确合同区域；
4. Summary保留更多来源段落和原文结构，更适合CUAD式抽取任务；
5. EvoSkill的抽象KA更有利于规则迁移、综合判断和治理控制。

### 5.3 证据指标体系重构

已经形成三层证据指标：

- **Strict Evidence F1：**严格复现CUAD Gold span；
- **Containment-aware Evidence F1：**预测引文完整包含Gold也算匹配；
- **Semantic Evidence Validity：**盲化LLM proxy判断引文是否支持reference finding。

当前Containment匹配没有引文长度膨胀上限，完整包含Gold的超长引文也可得到匹配。这是已知限制，后续应在dev人工集校准2×、3×、5×长度上限。

### 5.4 当前正在进行：Graph-enhanced Skill Compilation

#### 研究动机

EvoSkill v4通过在`SKILL.md`中增加Common Clause Patterns与Example Phrasing，已经证明“条款模式化组织”可能改善任务成功率、状态判断和no-answer能力。当前新实验进一步把这一做法从提示词中的隐式组织，升级为确定、可审计的图增强编译算法。

核心研究问题是：

> 在知识原子、security policy、Package-aware Agent、运行模型、数据划分和top-k参数保持相同的情况下，显式构建Knowledge Atom图并据此归纳Clause Pattern，能否比扁平KA编译更好地表达条款变体、条件、例外和判定边界？

#### 因果边界

`graph_evoskill_compiler`是独立基线，不替换`evoskill_compiler`。第一阶段只改变compile-time Skill组织方式：

| 组成 | EvoSkill v4 | GESC | 是否保持一致 |
|---|---|---|---|
| 原始KA | EvoSkill evidence index | 复用同一evidence index | 是 |
| Security policy | EvoSkill policy | 原样复用 | 是 |
| Runtime Agent | Package-aware Agent | Package-aware Agent | 是 |
| Runtime retrieval | chunks=10, knowledge=6 | chunks=10, knowledge=6 | 是 |
| 编译输入组织 | 每类Top-30扁平KA | 每类Top-200构图后选择Pattern | 否 |
| Skill提示结构 | Pattern/Example提示 | 图选择的Pattern Cards | 否 |

因此主对照`evoskill_compiler`与`graph_evoskill_compiler`的差异，原则上可以归因于图增强编译，而不是重新抽取KA或更换Agent。当前阶段不引入runtime Graph-RAG，避免把编译收益和运行时检索收益混在一起。

#### 已完成实现

- 新增`scripts/baselines/graph_evoskill_compiler.py`。
- 节点类型：`KnowledgeAtom`、`ClausePattern`、`Category`、`Contract`。
- 边类型：`BELONGS_TO`、`DERIVED_FROM`、`VARIANT_OF`、`INSTANCE_OF`。
- 使用倒排候选和token Jaccard构造稀疏同类别变体边。
- 使用中心原子约束的星型聚类归纳Pattern，避免普通连通分量的chaining。
- 使用置信度、图中心性、来源合同覆盖、条件/例外信息为Pattern排序。
- 使用来源多样性与MMR式冗余惩罚选择代表例句。
- 输出`knowledge_graph.json`和`pattern_cards.json`供审计与消融。
- 保留源EvoSkill的`evidence_index.json`和`security_policy.json`，保证现有Agent兼容。
- 已接入`run_all_baselines.py`、`run_package_runtime.py`、Academic Judge、Semantic Evidence Validity及静态Skill评测入口。

#### 当前默认参数

| 参数 | 默认值 | 含义 |
|---|---:|---|
| `graph_ka_limit` | 200/category | 每类参与构图的高置信KA上限 |
| `similarity_threshold` | 0.24 | KA并入Pattern中心的Jaccard阈值 |
| `max_neighbors` | 6 | 每个KA保留的变体近邻上限 |
| `patterns_per_category` | 6 | 每类进入编译提示的Pattern上限 |
| `examples_per_pattern` | 3 | 每个Pattern的代表例句上限 |

#### 离线构图验证

已对全部9个case的真实EvoSkill evidence index执行不调用LLM的dry-run：

| Case | 节点 | 边 | 进入编译的Pattern |
|---|---:|---:|---:|
| contract_basic_info | 1,318 | 5,660 | 30 |
| term_and_termination | 721 | 3,014 | 18 |
| legal_governance | 846 | 3,183 | 18 |
| ip_and_license | 1,881 | 7,151 | 48 |
| competition_restrictions | 925 | 2,108 | 42 |
| liability_and_indemnity | 1,002 | 3,639 | 24 |
| assignment_and_control | 630 | 2,244 | 12 |
| revenue_and_commercial_terms | 1,020 | 2,244 | 24 |
| operational_rights | 970 | 3,401 | 30 |

早期连通分量实现曾把Anti-Assignment的161/200个KA吞并为一个大Pattern，表明法律模板中存在明显的近邻链式传播。改用星型聚类后，`assignment_and_control`中两个类别选中的Pattern规模为：

```text
Change of Control: 31, 18, 5, 7, 4, 4
Anti-Assignment:   38, 29, 16, 11, 10, 7
```

这一修正已经进入当前默认实现和设计文档。

#### 当前尚未完成

- 尚未调用LLM为全部case生成GESC `SKILL.md`。
- 尚未运行`graph_evoskill_compiler`的test 4668任务。
- 尚未生成GESC的Academic Judge与Semantic Evidence Validity结果。
- 尚未执行GESC消融和配对显著性检验。
- 尚不能声称GESC有效；目前只能确认实现、可复现协议和离线图结构通过验证。

#### 下一轮主假设

GESC应首先影响Skill对语义变体及条件/例外的表达，因此优先观察：Task Success、Status Macro-F1、Balanced Accuracy、No-answer Recall、Academic Judge、Semantic Evidence Validity和Containment-aware Evidence F1。Strict Evidence F1只保留为Gold-span对齐诊断，不作为图增强质量的唯一结论。

## 6. 当前待解决问题

### P0：最终论文前必须完成

#### 6.0 完成GESC主对照实验

当前最高优先级是完成`graph_evoskill_compiler`闭环，而不是继续修改图算法：

1. 生成全部9个case的GESC Skill package；
2. 先做静态审计，检查类别覆盖、Pattern可读性、条件/例外保真和提示长度；
3. 使用与EvoSkill v4完全相同的`ecnu-plus + top-k10/k6 + test`配置运行4668任务；
4. 完成确定性指标、Academic Judge和Semantic Evidence Validity；
5. 对相同task做paired bootstrap和McNemar检验；
6. 根据主结果再决定是否执行`no-centrality`、`no-source-diversity`和`random-patterns`消融。

在主实验完成前不要根据test结果反复调整`similarity_threshold`或Pattern数量。若需要调参，应先在dev或离线图统计上预注册候选配置。

#### 6.1 配对统计检验

需要基于相同task执行：

- paired bootstrap 95% CI；
- Task Success、状态正确等二值指标的McNemar检验；
- Academic Judge和Semantic Validity在共同回答任务交集上的配对比较。

目标：判断EvoSkill相对Summary的0.28个百分点Task Success、相对Schema的0.97个百分点Macro-F1是否只是采样波动。

#### 6.2 人工证据校准

建议从dev集建立约200条证据校准集，覆盖：

- Strict匹配成功；
- Containment新增匹配；
- 合理替代证据；
- 部分支持；
- 明确错误；
- 引用抽取失败。

需要人工标注：

- `valid`
- `partial`
- `invalid`
- `ambiguous`

然后报告：

- LLM—human agreement；
- Strict/Containment与人工标签的一致性；
- Semantic Evidence Validity的人类校准结果；
- 合理的Containment长度上限。

#### 6.3 核心消融

至少完成以下变体：

1. `No Policy`：验证治理优势是否来自显式policy；
2. `No KA Retrieval`：验证KA对任务和证据的贡献；
3. `KA only for reasoning`：合同检索只使用category+question，KA只进入推理上下文；
4. `Minimal Sufficient Quote`：要求输出最短充分连续引文；
5. `Same SKILL.md + Empty Package`：隔离package附件相对最终文本的贡献。

### P1：强烈建议完成

#### 6.4 统一生成模型与预算

当前生成模型不一致：

- Native、Schema：`deepseek-chat`
- Document Tool、EvoSkill：`ecnu-plus`
- Summary：混合两种模型

正式因果比较应统一：

- model；
- temperature；
- max tokens；
- retry策略；
- 生成预算。

同时报告质量—成本Pareto frontier。

#### 6.5 证据抽取改进

不建议首先重写KA编译。优先测试：

- KA不进入合同BM25 query，只用于推理；
- 先选择证据，再生成答案；
- 要求最小充分引文；
- 每个结论只保留一条核心证据；
- 增加证据reranking；
- 对长条款做句子级引用选择。

重点观察：

- Containment Precision/Recall/F1；
- Semantic Evidence Validity；
- Academic Judge Completeness；
- No-answer；
- Validation Failure。

#### 6.6 Evidence Index Quality

尚未单独评价evidence index的：

- 来源真实性；
- 覆盖率；
- span/category一致性；
- 重复和冲突KA；
- 不同case之间的错误归类。

### P2：扩展实验

- 自主多Skill路由；
- 跨case模糊问题；
- 多Skill组合任务；
- 干扰合同下的Contract Isolation；
- prompt injection；
- 训练证据诱导引用；
- 跨运行模型复现。

## 7. 已知限制与注意事项

1. 当前结果比较的是完整方法系统，不能把所有提升因果归因于KA。
2. Agent使用Oracle Skill routing，不能声称具备自主Skill选择能力。
3. Academic Judge只评价gold和预测均为answered的条件子集。
4. Semantic Evidence Validity复用Academic Judge的Faithfulness和Semantic Correctness，是LLM proxy，不是独立人工结论。
5. 当前只有单一runtime模型、单个run ID，没有重复采样。
6. Static Source-grounded Rule Rate识别来源标记，不等同于规则实质法律正确。
7. Contract Isolation五种方法均为1.0，主要由统一验证器保证，不能用于证明EvoSkill优势。
8. Containment-aware匹配没有长度膨胀限制。
9. `Human Review Routing`与`1 - External Violation Rate`当前互补，不能作为两份独立证据。
10. `results/skillgen/generated/evidence_llm_review_evoskill_test_final-k10-k6.jsonl`当前为0字节。独立Evidence Judge调用因终端未配置`ECNU_API_KEY`而未执行；现有复核使用Academic Judge缓存。

## 8. 关键文件

### 8.1 论文与设计

- `doc/GRAPH_ENHANCED_SKILL_COMPILATION.md`：当前GESC完整算法、因果边界、参数、产物与消融协议。
- `doc/EVOSKILL_IMPROVEMENT_HANDOFF.md`：EvoSkill v4改造阶段的专项交接记录。
- `doc/paper_experiments_v2.md`：当前论文实验叙事与EvoSkill改造记录。
- `doc/paper_experiments.md`：当前可直接进入论文正文的实验章节。
- `doc/first_stage_experiment_report.md`：完整指标、诊断过程和第一阶段记录。
- `doc/package_aware_runtime_experiment.md`：运行时实验协议。
- `doc/skillgen_dataset_organization_and_cuad_conversion.md`：数据集构建方案。
- `cuad_skillgen_baselines_plan.md`：基线设计。
- `cuad_skillgen_evaluation_metrics_plan.md`：原始指标计划。

### 8.2 核心代码

- `scripts/baselines/graph_evoskill_compiler.py`：GESC构图、Pattern归纳、代表例句选择与Skill编译。
- `scripts/runtime/package_agent.py`：Package-aware Agent、检索、引文验证。
- `scripts/runtime/package_evaluator.py`：任务、状态、治理、Strict和Containment证据指标。
- `scripts/run_package_runtime.py`：运行与离线重算入口。
- `scripts/evaluate_academic_judge.py`：答案语义Judge。
- `scripts/evaluate_semantic_evidence.py`：Semantic Evidence Validity。
- `scripts/diagnose_evidence_pipeline.py`：小样本检索与失败归因。
- `scripts/review_evidence_diagnosis.py`：证据复核与Mapper sensitivity。
- `scripts/evaluate_skill_quality.py`：静态Skill审计。
- `tests/test_package_runtime.py`：Package-aware runtime测试。
- `tests/test_graph_evoskill_compiler.py`：GESC图模式、Pattern Card、KA上限与来源多样性测试。

### 8.3 关键结果

- `results/skillgen/generated/package_runtime_evaluation_test_final-k10-k6.json`
- `results/skillgen/generated/academic_judge_evaluation_test_final-k10-k6.jsonl`
- `results/skillgen/generated/academic_judge_evaluation_test_final-k10-k6_summary.json`
- `results/skillgen/generated/semantic_evidence_validity_test_final-k10-k6.json`
- `results/skillgen/generated/evidence_diagnosis_evoskill_compiler_test_final-k10-k6.json`
- `results/skillgen/generated/evidence_review_and_mapper_sensitivity_evoskill_test_final-k10-k6.json`
- `results/skillgen/generated/skill_quality_evaluation.json`

## 9. 常用命令

### 9.0 GESC当前实验命令

不调用LLM，检查全部case图规模：

```powershell
python scripts/baselines/graph_evoskill_compiler.py --dry-run
```

先生成单个case用于静态审计：

```powershell
python scripts/baselines/graph_evoskill_compiler.py `
  --case-id assignment_and_control `
  --model ecnu-plus
```

确认单case产物后生成全部GESC Skill：

```powershell
python scripts/baselines/graph_evoskill_compiler.py --model ecnu-plus
```

运行正式test主对照：

```powershell
python scripts/run_package_runtime.py `
  --method graph_evoskill_compiler `
  --split test `
  --run-id graph-k10-k6 `
  --top-k-chunks 10 `
  --top-k-knowledge 6
```

若目标是与现有`final-k10-k6`逐task配对，统计脚本必须显式读取两个方法各自的结果目录，不能因run ID不同而把另一方法误判为结果缺失。

### 9.1 运行测试

```powershell
python -m pytest tests -q
```

当前预期：

```text
20 passed
```

不要直接把根目录`python -m pytest -q`失败解释为算法测试失败；当前根目录的`test_ecnu_json.py`在测试收集阶段直接初始化OpenAI客户端，没有API Key时会报错。

### 9.2 不调用LLM重算运行指标

```powershell
python scripts/run_package_runtime.py `
  --evaluate-only `
  --split test `
  --run-id final-k10-k6
```

### 9.3 重算Semantic Evidence Validity

```powershell
python scripts/evaluate_semantic_evidence.py `
  --split test `
  --run-id final-k10-k6
```

### 9.4 重跑200条Evidence诊断

```powershell
python scripts/diagnose_evidence_pipeline.py `
  --method evoskill_compiler `
  --split test `
  --run-id final-k10-k6 `
  --max-tasks 200 `
  --seed 42
```

### 9.5 重算Mapper敏感性

不调用新LLM：

```powershell
python scripts/review_evidence_diagnosis.py --evaluate-only
```

### 9.6 需要LLM的评测

调用`ecnu-plus`前需设置：

```powershell
$env:ECNU_API_KEY="..."
```

Academic Judge：

```powershell
python scripts/evaluate_academic_judge.py `
  --split test `
  --run-id final-k10-k6
```

## 10. 推荐接手顺序

1. 阅读`doc/GRAPH_ENHANCED_SKILL_COMPILATION.md`，确认当前算法、默认参数、因果边界和实验假设。
2. 运行GESC dry-run并检查9个case图统计能够复现；不要在test结果出现前继续修改默认参数。
3. 生成`assignment_and_control`单case Skill，人工检查Pattern Card与`SKILL.md`是否忠于KA、条件和例外。
4. 审计通过后生成全部9个GESC Skill package，并记录生成token、耗时和失败重试。
5. 使用相同`ecnu-plus + test + k10/k6`配置运行4668任务，完成确定性指标、Academic Judge和Semantic Evidence Validity。
6. 对GESC与EvoSkill v4执行paired bootstrap与McNemar检验；只有确认方向后再运行图组件消融。
7. GESC主实验闭环后，再恢复dev人工证据校准、`Minimal Sufficient Quote`、`No Policy`和`No KA Retrieval`等原P0/P1任务。

## 11. 一句话交接结论

项目已经完成从数据集、五种原始Skill生成方法、统一Agent到多层评测和论文实验初稿的完整闭环，并新增了第六种独立基线`graph_evoskill_compiler`。最近的工作先解决了状态类别不平衡和Evidence F1解释偏差，随后把EvoSkill v4中有效的Pattern/Example Phrasing思路升级为可审计的知识原子图编译。GESC实现、全case离线构图和测试已经完成，但尚无运行时结果，因此目前不能宣称图增强有效。下一阶段最重要的任务是保持KA、Agent与k10/k6配置不变，完成GESC Skill生成、4668任务主对照、语义评测和配对统计检验，再决定是否推进图检索或进一步修改KA算法。
