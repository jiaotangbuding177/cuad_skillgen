# CUAD-SkillGen：实验设计与结果分析

## 1. 实验目标

本实验研究如何将企业合同语料编译为可供大语言模型智能体执行的 Skill package。与只生成自然语言提示不同，目标方法 EvoSkillCompiler 将训练合同归纳为 Knowledge Atoms（KAs），并进一步编译为可检索知识、审查规则和显式治理策略。实验重点不在于证明目标方法在所有指标上均为最优，而在于回答以下问题：

- **RQ1：任务执行。**结构化 Document-to-Skill 方法能否提高智能体在未见合同上的任务完成能力？
- **RQ2：状态与治理。**EvoSkillCompiler 能否在类别不均衡条件下更稳定地识别任务状态，并正确处理缺失输入、越界请求和人工复核？
- **RQ3：答案与证据。**结构化知识是否能够在保持答案语义质量的同时，为答案提供真实、有效且可追溯的目标合同证据？
- **RQ4：机制与代价。**EvoSkillCompiler 的收益是否与规则可追溯性和显式策略相关，其生成成本是否合理？

上述问题分别对应端到端任务指标、类别均衡指标、治理指标、语义与证据指标，以及静态审计和成本指标。为避免“指标堆积”，正文只报告能够区分某一具体能力的指标；重复、互补或已经出现天花板效应的指标放入附录或不作为方法优劣依据。

## 2. 数据集与任务

### 2.1 数据来源

实验基于 CUAD 合同审查数据构建 CUAD-SkillGen。原始 CUAD 类别被组织为9个能力域：

1. `contract_basic_info`
2. `term_and_termination`
3. `legal_governance`
4. `ip_and_license`
5. `competition_restrictions`
6. `liability_and_indemnity`
7. `assignment_and_control`
8. `revenue_and_commercial_terms`
9. `operational_rights`

数据按合同划分，训练、开发和测试合同互不重叠。

| 划分 | 合同数 | 用途 |
|---|---:|---|
| Train | 306 | 生成五种方法的 Skill package |
| Dev | 102 | 运行时检查与检索参数确认 |
| Test | 102 | 冻结配置后的最终评估 |

### 2.2 测试任务

每种方法均执行4668条测试任务。任务包含合同问答和额外构造的治理边界任务。

| Gold状态 | 数量 | 比例 |
|---|---:|---:|
| `answered` | 1447 | 31.00% |
| `evidence_missing` | 2843 | 60.90% |
| `missing_input` | 108 | 2.31% |
| `unsupported_scope` | 108 | 2.31% |
| `needs_human_review` | 162 | 3.47% |
| **合计** | **4668** | **100.00%** |

由于`evidence_missing`占60.90%，原始Status Accuracy容易被多数类主导。因此本文不将其作为核心状态指标，而采用对五种状态等权的Macro-F1，并报告分状态结果辅助解释。

## 3. 对比方法

实验比较五种自动Document-to-Skill方法。

| 方法 | 中间表示 | Package特征 |
|---|---|---|
| Native Prompt Skill | 无显式知识提取 | 自由生成`SKILL.md`，无独立索引和策略 |
| Schema Prompt Skill | 固定章节与输出Schema | 结构化`SKILL.md`，无实际证据索引 |
| Summary2Skill | 逐合同摘要 | 包含带来源的摘要段落索引 |
| Document Tool Maker | 工具接口与示例 | 包含工具描述、参数和示例索引 |
| EvoSkillCompiler | Knowledge Atoms与编译规则 | 包含细粒度知识索引、审查规则和显式安全策略 |

五种方法均以306份训练合同为输入，并输出统一目录结构下的`SKILL.md`、manifest、evidence index和security policy。不同方法输出内容的不对称是方法设计的一部分，但也意味着实验比较的是完整系统，而不能在没有消融的情况下将全部差异归因于单个组件。

## 4. 统一运行时

### 4.1 Package-aware Agent

所有方法使用同一个Package-aware Agent和同一个运行模型`ecnu-plus`。任务的`case_id`直接指定应加载的Skill，Agent再在该Skill内部检索指导、知识和工具。因此本实验评估的是**已知正确Skill条件下的包内利用能力**，不评估自主多Skill路由。

冻结后的运行配置如下。

| 配置 | 取值 |
|---|---|
| Runtime protocol | `package-aware-v1` |
| Runtime model | `ecnu-plus` |
| Split | `test` |
| Run ID | `final-k10-k6` |
| 合同检索 | BM25 top-10 chunks |
| Skill知识检索 | BM25 top-6 items |
| 治理任务 | Included |

五种方法均完成4668/4668条任务，最终错误率为0，因此方法比较不受缺失任务或API失败直接污染。

### 4.2 证据处理

训练知识只用于指导搜索和推理，不允许作为目标合同证据。Agent首先检索目标合同片段，然后要求运行模型输出原文引文。验证器只保留真实存在于目标合同已检索区间中的引文，并记录字符位置。Gold状态、reference answer和gold evidence在运行时均不可见。

离线评估阶段使用三种互补证据口径：

- **Strict Evidence F1：**预测引文与CUAD Gold满足Span IoU≥0.5或Text F1≥0.8，并进行一对一匹配。该指标衡量严格Gold-span复现能力。
- **Containment-aware Evidence F1：**在Strict规则上增加“预测引文完整包含Gold span即匹配”。该指标减少长引文受到的IoU惩罚。
- **Semantic Evidence Validity：**使用盲化LLM Judge判断已验证证据是否支持reference finding。Faithfulness≥0.9且Semantic Correctness≥0.8时记为valid。

Strict F1用于保持与统一Gold标注的可复现比较；Containment F1用于控制引用边界差异；Semantic Validity用于识别没有命中唯一Gold span但语义上有效的替代证据。三者不能相互替代。

## 5. 评价指标

### 5.1 正文主指标

本文主表保留五个互补指标。

1. **Task Success Rate。**非answered任务要求状态完全正确；answered任务额外要求至少一条预测证据映射到Gold。它衡量状态与证据链路的端到端成功，但不直接评价答案文本完整性。
2. **Status Macro-F1。**分别计算五种状态的F1后等权平均，用于消除多数类主导。
3. **Governance Boundary Correct。**在`missing_input`、`unsupported_scope`和`needs_human_review`共378条任务上计算状态正确率，直接评价企业治理边界。
4. **Academic Judge Score。**对gold和预测均为answered的任务，从Semantic Correctness、Completeness、Faithfulness和Clarity四个维度进行盲化评分，权重分别为0.40、0.25、0.20和0.15。
5. **Semantic Evidence Validity（端到端）。**以全部1447条gold answered任务为分母，评价方法最终产生语义有效证据的比例，同时惩罚错误拒答。

### 5.2 辅助指标

- Strict和Containment-aware Evidence F1用于分析证据边界与Gold对齐。
- Source-grounded Rule Rate用于审计生成规则的来源可追溯性。
- Boundary Policy Coverage用于检查package是否显式表达五类边界要求。
- 生成Token用于呈现质量收益的计算代价。

原始Status Accuracy仅作为兼容性结果；External Violation Rate与Human Review Routing在当前实现中互为补数，不重复计为两项证据；Contract Isolation在五种方法上均为1.0，出现天花板效应，因此不进入主表。

## 6. 总体结果

### 6.1 主结果

| 方法 | Task Success ↑ | Status Macro-F1 ↑ | Governance Boundary ↑ | Academic Judge ↑ | Semantic Evidence Validity ↑ |
|---|---:|---:|---:|---:|---:|
| Native Prompt Skill | 0.4994 | 0.5824 | 0.5714 | 0.9024 | 0.7996 |
| Schema Prompt Skill | 0.6298 | 0.8380 | 0.8810 | 0.8404 | 0.7630 |
| **Summary2Skill** | 0.6407 | 0.7696 | 0.7328 | **0.9660** | **0.8680** |
| Document Tool Maker | 0.6345 | 0.7451 | 0.6984 | 0.9492 | 0.8210 |
| **EvoSkillCompiler** | **0.6435** | **0.8477** | **0.8916** | 0.9545 | 0.8411 |

EvoSkillCompiler在Task Success、Status Macro-F1和Governance Boundary三项指标上排名第一，说明其主要优势集中在任务执行和治理一致性。相较Native，EvoSkill的Task Success提高14.41个百分点，Macro-F1提高26.53个百分点，Governance Boundary提高32.02个百分点。类别均衡指标的提升表明，该结果不是依靠大量预测`evidence_missing`获得。

与强基线相比，EvoSkill的优势较小：Task Success仅比Summary2Skill高0.28个百分点，Macro-F1比Schema高0.97个百分点，Governance Boundary比Schema高1.06个百分点。在缺少配对显著性检验的情况下，这些小差距不能解释为稳定的统计优势。

另一方面，Summary2Skill在Academic Judge和Semantic Evidence Validity上均排名第一。EvoSkill的Academic Judge为0.9545、端到端Semantic Evidence Validity为0.8411，均排名第二。这表明EvoSkill在强化治理时保持了较高的答案和证据质量，但摘要式表示在自然语言答案综合和语义证据选择上仍具有优势。

### 6.2 状态能力分析

EvoSkill的分状态结果如下。

| 状态 | Precision | Recall | F1 |
|---|---:|---:|---:|
| `answered` | 0.5751 | 0.9026 | 0.7025 |
| `evidence_missing` | 0.9259 | 0.6637 | 0.7732 |
| `missing_input` | 1.0000 | 1.0000 | 1.0000 |
| `unsupported_scope` | 0.8308 | 1.0000 | 0.9076 |
| `needs_human_review` | 1.0000 | 0.7469 | 0.8551 |

EvoSkill对少数治理状态表现稳定，尤其能够完全召回`missing_input`和`unsupported_scope`。其主要状态错误发生在`answered`与`evidence_missing`之间：answered Recall达到0.9026，但Precision只有0.5751，说明训练知识提高了回答覆盖率，也可能使Agent在目标合同证据不足时倾向回答。该结果解释了为什么EvoSkill的类别均衡能力和治理能力最优，而No-answer能力并非最高。

### 6.3 治理能力

Governance Boundary只评价三种显式治理状态，不受大量普通无证据任务支配。EvoSkill达到0.8916，Schema达到0.8810，二者明显高于Native的0.5714。EvoSkill package包含独立security policy，Agent的确定性边界路由会读取其中关于缺失输入、支持范围、人工复核和外部输出的规则；Schema虽然没有独立策略文件，但其结构化`SKILL.md`也包含较明确的边界语言。因此，结果支持“显式、可解析的策略表达改善治理行为”，但尚不能单独证明增益全部来自Knowledge Atom。

## 7. 答案与证据质量

### 7.1 语义答案质量

Academic Judge结果如下。

| 方法 | 被评任务 | Correctness | Completeness | Faithfulness | Clarity | 总分 |
|---|---:|---:|---:|---:|---:|---:|
| Native Prompt Skill | 1297 | 0.9137 | 0.8145 | 0.9543 | 0.9496 | 0.9024 |
| Schema Prompt Skill | 1288 | 0.8899 | 0.6905 | 0.9400 | 0.8253 | 0.8404 |
| **Summary2Skill** | **1317** | **0.9653** | **0.9363** | **0.9830** | **0.9946** | **0.9660** |
| Document Tool Maker | 1286 | 0.9488 | 0.9059 | 0.9724 | 0.9917 | 0.9492 |
| EvoSkillCompiler | 1306 | 0.9523 | 0.9197 | 0.9745 | 0.9916 | 0.9545 |

Schema在Strict Evidence F1上表现较好，但Academic Judge最低，主要由Completeness和Clarity拖累。这说明固定输出结构有助于稳定定位，却可能生成过于短促或模板化的答案。Summary2Skill保留了面向自然语言回答的上下文组织，因此在四个语义维度上均排名第一。EvoSkill在四个维度上接近Summary，说明Knowledge Atoms和治理策略没有使答案退化为机械规则输出。

Academic Judge只评价gold和预测均为answered的条件子集，各方法被评任务不完全相同，因此不能单独代表端到端能力。本文通过Semantic Evidence Validity端到端口径和Task Success对其进行补充。

### 7.2 Gold对齐与语义有效性

| 方法 | Strict Evidence F1 ↑ | Containment Evidence F1 ↑ | Semantic Validity（条件）↑ | Semantic Validity（端到端）↑ |
|---|---:|---:|---:|---:|
| Native Prompt Skill | 0.4611 | 0.6455 | 0.8921 | 0.7996 |
| Schema Prompt Skill | **0.4772** | 0.6508 | 0.8571 | 0.7630 |
| **Summary2Skill** | 0.4329 | **0.6638** | **0.9537** | **0.8680** |
| Document Tool Maker | 0.4485 | 0.6447 | 0.9238 | 0.8210 |
| EvoSkillCompiler | 0.4315 | 0.6348 | 0.9319 | 0.8411 |

EvoSkill的Strict Evidence F1最低，但Containment修正后从0.4315提高到0.6348，增加20.33个百分点。这说明较长引文完整包含Gold是严格指标低估结果的重要原因。然而，EvoSkill的Containment F1仍比Summary低2.90个百分点，Precision和Recall也同时略低，因此不能将全部差距归因于span边界。

Semantic Evidence Validity给出了不同视角。在EvoSkill决定回答且提供已验证证据的1306条任务中，1217条同时满足高Faithfulness和高Semantic Correctness，条件有效率为0.9319；以全部1447条gold answered任务为分母后，端到端有效率为0.8411。该结果说明EvoSkill的大多数引文能够支持答案，但Summary在证据选择和回答覆盖上仍更强。

### 7.3 Evidence F1诊断实验

为定位EvoSkill的证据瓶颈，从test answered任务中以随机种子42抽取200条，不调用LLM重新生成答案，仅复现检索并分析既有输出。

#### 查询消融

| 查询 | Gold Chunk Recall@10 | All Gold Recall@10 | MRR |
|---|---:|---:|---:|
| Task only | 0.9450 | 0.8950 | 0.5876 |
| Package without KA | 0.9300 | 0.8950 | 0.6515 |
| **Full query** | **0.9550** | **0.9150** | **0.6518** |

完整查询没有整体降低Gold chunk召回，因此当前结果不支持“KA普遍造成query drift”。在200条样本中，纯合同检索失败、package drift和knowledge drift合计仅9条；更主要的损失位于检索之后。

#### 失败类型

| 类型 | 数量 | 比例 |
|---|---:|---:|
| Strict匹配成功 | 106 | 53.0% |
| 替代或错误证据，需语义复核 | 48 | 24.0% |
| 接近Gold但未通过严格阈值 | 22 | 11.0% |
| Gold chunk已召回但引用抽取失败 | 15 | 7.5% |
| 检索失败或query drift | 9 | 4.5% |

48条“替代或错误证据”均存在于盲化Academic Judge缓存中。按照预先公开的Faithfulness和Semantic Correctness规则二次归类后，43条为valid alternative，3条为partial support，仅2条为wrong evidence。该结果说明Strict F1混合衡量了真实证据能力与复现唯一Gold span的能力。不过，这一复核复用了同一个Judge，仍需人工专家抽样校准。

#### Mapper敏感性

在同一200条样本上，将Span IoU从0.5降至0.3、Text F1从0.8降至0.5时，Evidence F1从0.4235升至0.5153，增加9.18个百分点。这表明结果对映射阈值敏感。本文不依据test结果修改正式阈值，而保留Strict口径，并将敏感性分析作为稳健性证据。若后续需要选择宽松阈值，应在dev人工标注集上校准后冻结。

综合诊断表明，EvoSkill的主要证据问题不是完全无法召回Gold区域，而是知识抽象、证据选择和引用边界与CUAD抽取式标注之间存在不完全匹配。Summary保留更多来源段落和原文结构，更适合当前证据抽取任务；EvoSkill的KAs更适合规则迁移、综合判断和治理控制。

## 8. 机制证据与生成成本

### 8.1 静态规则审计

| 方法 | Source-grounded Rule Rate ↑ | Boundary Policy Coverage ↑ |
|---|---:|---:|
| Native Prompt Skill | 0.0337 | 0.2444 |
| Schema Prompt Skill | 0.0237 | **1.0000** |
| Summary2Skill | 0.0000 | 0.5778 |
| Document Tool Maker | 0.0000 | 0.4667 |
| **EvoSkillCompiler** | **0.8175** | **1.0000** |

EvoSkill的Source-grounded Rule Rate达到0.8175，明显高于其他方法，且Boundary Policy Coverage完整。这与其治理表现形成机制上的一致证据：EvoSkill不仅生成边界语言，还显式记录规则来源和独立策略。

需要注意，当前Source-grounded Rule Rate由确定性package audit计算，主要识别KA、证据和示例来源标记。它证明的是结构化来源标记，而不是人工确认后的实质法律正确性。正式论文应对抽取规则进行人工或独立LLM抽样校准。

### 8.2 生成成本

| 方法 | 生成Token | 相对Native |
|---|---:|---:|
| Native Prompt Skill | 724,469 | 1.00× |
| Schema Prompt Skill | 719,382 | 0.99× |
| Summary2Skill | 21,724,271 | 29.99× |
| Document Tool Maker | 23,932,205 | 33.03× |
| EvoSkillCompiler | 22,130,872 | 30.55× |

EvoSkill相对Native消耗约30.55倍生成Token，换取14.41个百分点Task Success和32.02个百分点Governance Boundary提升。但相对低成本Schema，EvoSkill的Task Success和Governance Boundary只分别提高1.37和1.06个百分点。因此，现有结果支持EvoSkill相对直接提示基线的系统性能力提升，却不能支持其相对Schema具有明显性价比优势。

此外，各方法生成模型并不完全一致：Native和Schema使用`deepseek-chat`；Document Tool和EvoSkill使用`ecnu-plus`；Summary混合使用两种模型。因此成本和小幅性能差异均不能完全归因于算法。

## 9. 对研究问题的回答

### RQ1：结构化Document-to-Skill是否提高任务执行？

是。四种结构化或知识抽取方法的Task Success均超过0.629，而Native只有0.4994。EvoSkill以0.6435排名第一，但相对Summary的优势仅0.28个百分点，尚不能证明其显著优于所有结构化基线。

### RQ2：EvoSkill是否改善类别均衡状态判断和治理？

是，这是当前证据最充分的结论。EvoSkill的Status Macro-F1为0.8477、Governance Boundary为0.8916，均排名第一。静态审计也显示其具备完整策略覆盖和明显更高的规则来源标记率。不过，Schema结果接近EvoSkill，说明结构化Schema和显式边界语言本身已经是强基线。

### RQ3：EvoSkill是否提高答案和证据质量？

部分支持。EvoSkill的Academic Judge为0.9545、Semantic Evidence Validity端到端为0.8411，均排名第二，说明其答案和证据总体可靠；但Summary在两项指标上更好。EvoSkill的Strict F1受Gold-span边界明显影响，Containment修正后提升20.33个百分点，但仍未领先。因此不能声称EvoSkill提供最强的证据定位能力。

### RQ4：性能收益是否与机制一致，代价是否合理？

机制证据基本一致：EvoSkill具有最高的规则来源标记率和完整策略覆盖，并在治理指标上领先。但其生成成本约为Native的30.55倍，相对Schema的性能增益有限。因此，EvoSkill的价值主要体现在治理、可追溯性和综合能力，而不是低成本。

## 10. 有效性威胁

### 10.1 内部效度

- **生成模型不一致。**不同方法使用了不同生成模型，当前比较是“方法+生成模型”的联合结果。
- **组件耦合。**EvoSkill同时改变KA索引、Skill文本和security policy，无法从主实验确定单个组件贡献。
- **运行时适配差异。**统一Agent对KA、摘要段落和工具元数据使用不同标准化分支，可能引入表示适配差异。
- **单次运行。**最终结果来自一个运行模型和一个run ID，尚未报告重复采样、置信区间或配对显著性。

### 10.2 构念效度

- Task Success不直接检查完整答案语义，需要与Academic Judge联合解释。
- Academic Judge和Semantic Validity复用单一Judge，可能存在量表饱和和模型偏差。
- Strict Evidence F1依赖有限Gold span，可能把合理替代证据计为错误。
- Containment匹配没有长度膨胀上限，过长引文可能获得额外信用。
- 静态规则审计识别来源标记，不等同于人工验证后的法律正确性。

### 10.3 外部效度

- 当前实验仅覆盖企业合同审查。
- Skill由`case_id`进行Oracle路由，未验证自主多Skill选择。
- Contract Isolation由统一验证器保证且已出现天花板效应，尚未覆盖干扰合同和提示注入场景。

## 11. 后续消融实验

为确定EvoSkill证据差距的来源，后续应优先执行以下最小消融：

1. **No Policy：**删除独立策略，验证治理优势是否来自显式policy。
2. **No KA Retrieval：**保留Skill文本但不检索KA，验证KA对任务与证据的贡献。
3. **KA仅用于推理：**合同检索只使用category和question，KA只进入推理上下文，检验KA是否干扰目标合同检索或证据选择。
4. **Minimal Sufficient Quote：**要求Agent输出支持结论的最短连续原文，检验长引文和冗余证据是否造成Containment Precision下降。
5. **等生成模型与等预算：**统一模型、temperature、token预算和重试策略，消除当前生成条件混杂。

此外，应在dev集建立人工证据校准集，用于选择Containment长度上限、校准Semantic Evidence Judge，并在冻结后只对test执行一次最终评估。

## 12. 实验结论

实验结果表明，结构化Document-to-Skill方法相较直接提示能够明显提高合同审查Agent的任务执行能力。EvoSkillCompiler在Task Success、类别均衡状态判断和治理边界上取得最佳结果，同时具有最高的规则来源标记率和完整策略覆盖，说明Knowledge Atom编译与显式策略能够形成更稳定、可治理、可追溯的Skill package。

该优势并非全面领先。Summary2Skill在答案语义质量、Semantic Evidence Validity和Containment-aware Evidence F1上表现更好；Schema Prompt Skill则以极低生成成本取得接近EvoSkill的状态与治理结果。证据诊断进一步显示，EvoSkill的Strict Evidence F1受到长引文、替代证据和有限Gold span影响，但在修正边界后仍存在约2–3个百分点的真实证据差距。

因此，当前实验最稳妥地支持以下结论：

> EvoSkillCompiler的主要贡献是将训练合同编译为具有显式来源和治理策略的可执行Skill，从而提升任务成功率与治理一致性，并保持较高的答案和证据语义质量；其当前局限在于原子化知识如何更有效地转化为目标合同中的最小、完整和精确证据，同时其相对强结构化基线的成本收益仍需进一步验证。
