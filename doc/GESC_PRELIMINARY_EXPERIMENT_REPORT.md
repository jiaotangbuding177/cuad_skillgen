# Graph-enhanced Skill Compilation 初步实验结果报告

> 实验日期：2026-08-11  
> 方法：`graph_evoskill_compiler`（GESC）  
> 结果状态：确定性运行指标完成；Academic Judge与Semantic Evidence Validity尚未完成  
> 数据源：`results/skillgen/generated/package_runtime_evaluation_test_graph-k10-k6.json`

## 1. 实验设置

GESC复用EvoSkill已有的Knowledge Atoms、`evidence_index.json`和`security_policy.json`，只改变compile-time Skill组织方式：先构建知识原子图、归纳Clause Pattern和选择代表例句，再生成`SKILL.md`。运行时继续使用同一Package-aware Agent。

| 配置 | 取值 |
|---|---|
| Runtime model | `ecnu-plus` |
| Split | `test` |
| Test tasks | 4,668 |
| Target contract retrieval | BM25 top-10 chunks |
| Skill knowledge retrieval | BM25 top-6 items |
| Governance tasks | Included |
| Error rate | 0.0000 |
| Result coverage | 1.0000 |

主对照为EvoSkill v4，因为v4已经采用Common Clause Patterns与Example Phrasing，是当前最强EvoSkill版本；同时保留EvoSkill v1作为“扁平规则编译”的参照。

## 2. 总体结果

| 指标 | EvoSkill v1 | EvoSkill v4 | GESC | GESC−v4 | GESC−v1 |
|---|---:|---:|---:|---:|---:|
| Task Success | 0.6435 | **0.6952** | 0.6590 | -0.0362 | +0.0155 |
| Status Accuracy | 0.7562 | **0.8083** | 0.7706 | -0.0377 | +0.0144 |
| Status Macro-F1 | 0.8477 | **0.8714** | 0.8504 | -0.0210 | +0.0027 |
| Balanced Accuracy | 0.8626 | **0.8773** | 0.8628 | -0.0145 | +0.0002 |
| No-answer Recall | 0.6637 | **0.7503** | 0.6936 | -0.0567 | +0.0299 |
| Strict Evidence Precision | 0.4467 | 0.4473 | **0.4564** | +0.0091 | +0.0097 |
| Strict Evidence Recall | **0.4623** | 0.4608 | 0.4583 | -0.0025 | -0.0040 |
| Strict Evidence F1 | 0.4315 | 0.4310 | **0.4360** | +0.0050 | +0.0045 |
| Containment Evidence F1 | 0.6348 | **0.6536** | 0.6427 | -0.0109 | +0.0079 |
| Governance Boundary | **0.8916** | 0.8863 | 0.8836 | -0.0027 | -0.0080 |
| Overall Boundary | 0.6905 | **0.7662** | 0.7159 | -0.0503 | +0.0254 |
| Validation Failure Rate ↓ | 0.1300 | 0.1290 | **0.1270** | -0.0020 | -0.0030 |

## 3. 初步结论

### 3.1 GESC相对EvoSkill v1有效，但未超过EvoSkill v4

GESC相对v1在Task Success（+1.55个百分点）、No-answer Recall（+2.99个百分点）、Overall Boundary（+2.54个百分点）、Strict Evidence F1（+0.45个百分点）和Containment F1（+0.79个百分点）上都有提升。说明把扁平KA组织为Clause Pattern总体上比早期规则式编译更有效。

但是，相对已经引入Pattern/Example Phrasing的v4，GESC的Task Success下降3.62个百分点、Macro-F1下降2.10个百分点、No-answer Recall下降5.67个百分点。当前数据不支持“显式知识原子图优于EvoSkill v4”的主张。

更准确的阶段性表述是：

> 图增强编译保留了EvoSkill v1的大部分治理和类别均衡能力，并改善了严格证据精度，但当前确定性图聚类与Pattern选择没有复现EvoSkill v4由LLM直接组织模式时的整体判定优势。

### 3.2 主要退化来自answered/evidence_missing边界，而不是证据抽取崩溃

| 状态 | EvoSkill v4 | GESC | 变化 |
|---|---:|---:|---:|
| Gold answered recall | 0.9019 | 0.8922 | -0.0097 |
| Gold evidence_missing recall | 0.7503 | 0.6936 | -0.0567 |
| Predicted answered | 2,023 | 2,171 | +148 |
| Predicted evidence_missing | 2,293 | 2,140 | -153 |

GESC没有明显失去识别真实answered条款的能力，其answered recall只下降0.97个百分点；主要问题是把更多本应`evidence_missing`的目标合同判断为`answered`。这同时解释了Task Success、No-answer Recall和Overall Boundary的下降。

Strict Evidence Precision反而提高0.91个百分点、Validation Failure下降0.20个百分点，说明“已经输出的引文完全失控”不是主要原因。当前瓶颈更接近**Pattern诱导出的过度判定/假阳性**。

### 3.3 当前最可能的直接机制：缺失型KA被编译成可回答的Negative Pattern

对`ip_and_license/SKILL.md`的初步审计发现，GESC生成了如下规则：

```text
Negative Finding: If the contract explicitly denies the pattern or falls into
a "No" pattern category, return answered with a negative finding and evidence.
```

同一Skill还出现由`"No"`以及“合同不包含license grant”等训练原子归纳出的Negative Pattern。这里存在语义层级混淆：

- “目标合同存在明确否定条款”可以是有文本证据的answered；
- “训练合同没有发现某类条款”应当表示absence/evidence_missing，不能作为可迁移的条款模式；
- “KA interpretation认为某合同不包含条款”不是目标合同中的可引用证据。

GESC将每类候选从v4的Top-30扩大到Top-200，并奖励来源多样性和边界信息。这会增加低信息、否定式、缺失式或类别映射噪声KA进入Pattern Card的概率；编译LLM随后把这些原子写成可执行的Negative Pattern，导致Agent更积极地返回`answered`。

这一机制目前是**由结果分布和Skill文本共同支持的强假设**，但仍需对错误task与触发Pattern进行逐项映射后才能确认为完整因果解释。

## 4. 分Case变化（GESC相对EvoSkill v4）

| Case | Task Success | Macro-F1 | No-answer | Containment F1 | Validation Failure ↓ |
|---|---:|---:|---:|---:|---:|
| contract_basic_info | +0.0160 | +0.0009 | +0.1224 | -0.0102 | -0.0213 |
| term_and_termination | -0.0333 | -0.0277 | -0.0880 | -0.0027 | -0.0111 |
| legal_governance | -0.0083 | +0.0052 | +0.0063 | -0.0181 | -0.0083 |
| **ip_and_license** | **-0.2023** | **-0.0722** | **-0.2541** | -0.0361 | +0.0425 |
| competition_restrictions | +0.0351 | +0.0040 | +0.0458 | +0.0183 | +0.0013 |
| liability_and_indemnity | -0.0259 | -0.0132 | -0.0468 | -0.0023 | **-0.0541** |
| assignment_and_control | -0.0387 | +0.0018 | -0.0476 | -0.0107 | -0.0310 |
| revenue_and_commercial_terms | +0.0217 | -0.0010 | +0.0518 | -0.0335 | -0.0065 |
| operational_rights | -0.0036 | -0.0251 | -0.0140 | +0.0043 | +0.0142 |

结果具有明显case异质性：GESC在`contract_basic_info`、`competition_restrictions`和`revenue_and_commercial_terms`提高Task Success，但`ip_and_license`单个case下降20.23个百分点，是总体退化的主要来源。不能只用全局均值判断“图组织整体无效”；更可能是某些类别的Pattern质量或否定语义处理存在局部灾难性问题。

## 5. 当前不能下的结论

1. 尚未完成Academic Judge，不能判断GESC答案语义质量是否提高。
2. 尚未完成Semantic Evidence Validity，不能把Strict F1的小幅提升解释为真实证据质量提升。
3. 尚未进行paired bootstrap和McNemar检验，小于1个百分点的变化暂不能视为稳定增益。
4. 当前GESC同时改变了候选规模（Top-30→Top-200）和组织算法，不能把差异全部归因于“图结构”本身。
5. 尚未验证Pattern Card与具体假阳性task之间的直接触发关系。

## 6. 建议的下一步

优先做诊断，而不是立即重跑一个新大实验：

1. 对`ip_and_license`中“v4正确判为evidence_missing、GESC错误判为answered”的任务做差异集。
2. 检查这些task检索到的KA、GESC Skill Pattern和最终引文，统计是否由`No`、`does not contain`、`absence`等缺失型原子触发。
3. 对全部Pattern Card增加KA类型审计：`positive_clause`、`explicit_negative_clause`、`absence_annotation`、`uncertain`。
4. 在dev或小规模test诊断集上验证两项最小修正：
   - 构图前排除`absence_annotation`；
   - 编译时禁止仅凭训练KA中的“No/absence”将目标合同判为answered。
5. 设置公平消融：`GESC Top-30`与`GESC Top-200`，区分图组织收益和候选扩容噪声。
6. 完成Academic Judge和Semantic Evidence Validity后，再决定是否值得全量重跑修正版。

## 7. 阶段性论文表述

当前结果更适合写成一个带失败分析的算法探索：

> GESC相对规则式EvoSkill v1改善了任务成功、边界判断和证据匹配，但没有超过采用LLM隐式模式归纳的EvoSkill v4。错误分析表明，图编译的主要风险并非证据定位退化，而是大规模候选KA中的absence/negative annotations被结构化后放大为可执行模式，造成evidence_missing到answered的系统性偏移。这说明知识图增强的关键不只是建立相似关系，还需要对知识原子的语义极性与证据可迁移性进行类型约束。

该发现支持下一版算法方向：从“无类型KA相似图”升级为“带极性和可迁移性约束的Typed Evidence Graph”。
