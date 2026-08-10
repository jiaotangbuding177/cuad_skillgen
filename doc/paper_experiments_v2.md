# EvoSkill 表示优化：从抽象规则到条款模式的实验研究

## 1. 研究背景

EvoSkillCompiler旨在将训练合同编译为可供大语言模型Agent使用的Skill package。原始版本（v1）先从合同中抽取Knowledge Atoms（KAs），再生成带来源引用的审查规则和显式治理策略。第一阶段实验表明，v1在任务成功率、类别均衡状态判断和治理边界上具有优势，但其证据对齐与答案组织仍未稳定超过摘要式基线。

进一步诊断发现，v1的主要瓶颈并非目标合同检索失败。对200条gold=`answered`任务的抽样分析显示，完整KA查询的Gold Chunk Recall@10达到0.955，检索失败和query drift合计仅占4.5%。更多错误发生在检索之后：Agent虽然获得了相关合同区域，但不总能判断目标合同是否真正包含待审查条款，或者没有选择最合适的引文。

基于这一观察，本阶段研究以下问题：

- **RQ1：**增加KA数量能否通过提高知识覆盖改善运行时表现？
- **RQ2：**扩大目标合同chunk上下文能否缓解引用碎片化？
- **RQ3：**将抽象审查规则改写为“条款模式+真实例句”，能否改善条款存在性判断与证据使用？
- **RQ4：**成功改造的增益来自精确证据抽取，还是来自状态校准与正确拒答？

## 2. 基线与问题诊断

### 2.1 原始EvoSkill

EvoSkill v1的`SKILL.md`以Evidence-Based Review Rules为核心。每条规则描述需要检查的法律或合同属性，并使用KA ID标记来源。例如：

```markdown
### Renewal Term
- Identify automatic renewal mechanisms [KA-0077, KA-0111].
- Determine whether the renewal term matches the initial term [KA-0001].
```

这种表示能够告诉Agent“应该检查什么”，但对“目标合同中的相关条款通常长什么样”提供的直接语言锚点有限。

### 2.2 v1核心表现

| 指标 | EvoSkill v1 | 最强对照 | 解释 |
|---|---:|---:|---|
| Task Success | 0.6435 | Summary2Skill 0.6407 | v1略高 |
| Status Macro-F1 | 0.8477 | Schema 0.8380 | v1最高 |
| Governance Boundary | 0.8916 | Schema 0.8810 | v1最高 |
| Strict Evidence F1 | 0.4315 | Schema 0.4772 | v1落后 |
| Containment Evidence F1 | 0.6348 | Summary2Skill 0.6638 | v1落后2.90 pp |

数据源：

- `results/skillgen/generated/package_runtime_evaluation_test_final-k10-k6.json`
- `results/skillgen/generated/evidence_diagnosis_evoskill_compiler_test_final-k10-k6.json`
- `results/skillgen/generated/evidence_review_and_mapper_sensitivity_evoskill_test_final-k10-k6.json`

## 3. 实验设置

### 3.1 统一运行条件

所有改造版本使用相同的运行时配置：

| 配置项 | 取值 |
|---|---|
| Runtime protocol | `package-aware-v1` |
| Runtime model | `ecnu-plus` |
| Split | `test` |
| 测试任务数 | 4668 |
| Target contract retrieval | BM25 top-10 chunks |
| Skill knowledge retrieval | BM25 top-6 items |
| Governance tasks | Included |
| Skill routing | Oracle/task-specified |

v1、v2、v3和v4的`run_config.json`在上述字段上完全一致。Gold status、reference answer和Gold evidence均不提供给运行时Agent。

### 3.2 评价指标筛选

本阶段只保留能够判断改造目标的指标：

1. **Task Success Rate：**衡量状态与严格证据链路的端到端成功。
2. **Status Macro-F1：**对五类状态等权，避免`evidence_missing`多数类主导。
3. **No-answer Correct：**衡量目标合同缺少证据时能否正确拒答。
4. **Strict Evidence F1：**衡量与CUAD Gold span的严格对齐。
5. **Containment Evidence F1：**预测引文完整包含Gold span时也视为匹配，用于控制长引文边界影响。
6. **Governance Boundary：**衡量`missing_input`、`unsupported_scope`和`needs_human_review`三类显式治理状态。

原始Status Accuracy不作为核心指标，因为任务类别明显不均衡；External Violation与Human Review Routing在当前实现中互为补数，也不重复报告。

## 4. 改造方案

### 4.1 v2：扩大KA索引

v2将每个类别进入evidence index的KA数量从top-30增加到top-100。该改造希望提高知识覆盖率，但也引入了更多低置信度KA。

除KA截断数量外，运行时配置保持不变。

数据源：

- 汇总结果：`results/skillgen/generated/package_runtime_evaluation_test_final-k10-k6-v2.json`
- 任务明细：`results/skillgen/generated/evoskill_compiler/package_runtime_results/test/final-k10-k6-v2/`
- 生成脚本：`scripts/regen_evoskill_more_kas.py`

### 4.2 v3：扩大合同Chunk上下文

v3在检索到目标合同chunk后，将每个chunk向前后各扩展1200字符。该改造希望减少Gold条款被切断或引文过于碎片化的问题。

数据源：

- 汇总结果：`results/skillgen/generated/package_runtime_evaluation_test_final-k10-k6-v3-expand-chunks.json`
- 任务明细：`results/skillgen/generated/evoskill_compiler/package_runtime_results/test/final-k10-k6-v3-expand-chunks/`
- 运行时实现：`scripts/runtime/package_agent.py`

### 4.3 v4：Common Clause Patterns与Example Phrasing

v4不改变KA索引、security policy或运行时检索参数，只修改`SKILL.md`生成提示，将抽象规则列表改为条款模式和真实例句。

v4要求每个类别生成3—6种常见条款模式，每种模式包含：

- Pattern Name；
- Description；
- 1—2条来自KA原文的完整Example Phrasing；
- Variation Notes。

示例：

```markdown
#### Pattern: Automatic Annual Renewal

- Description: The agreement extends for successive one-year periods
  unless a party provides notice.
- Example Phrasing:
  > "will renew automatically from year to year unless cancelled in writing..."
    [KA-0016]
  > "shall be automatically renewed for successive one (1) year periods"
    [KA-0111]
- Variation Notes: Some contracts use month-to-month renewal [KA-0164].
```

该设计的核心假设是：抽象规则主要告诉Agent“检查什么”，真实例句则进一步告诉Agent“目标条款在文本中通常长什么样”。当目标合同中不存在类似语言模式时，Agent应更容易返回`evidence_missing`，而不是受通用训练知识诱导错误回答。

数据源：

- 汇总结果：`results/skillgen/generated/package_runtime_evaluation_test_final-k10-k6-v4-example-phrasing.json`
- 任务明细：`results/skillgen/generated/evoskill_compiler/package_runtime_results/test/final-k10-k6-v4-example-phrasing/`
- 生成提示：`scripts/baselines/evoskill_compiler.py`
- 再生成脚本：`scripts/regen_evoskill_more_kas.py`

## 5. 消融结果

### 5.1 三种改造的总体效果

| 版本 | 改造 | Task Success | 相对v1 | Status Macro-F1 | 相对v1 | Strict Evidence F1 | 相对v1 |
|---|---|---:|---:|---:|---:|---:|---:|
| v1 | 原始规则式Skill | 0.6435 | — | 0.8477 | — | 0.4315 | — |
| v2 | KA top-30→top-100 | 0.6300 | -1.35 pp | 0.8390 | -0.87 pp | 0.4385 | +0.70 pp |
| v3 | Chunk扩展±1200字符 | 0.6341 | -0.94 pp | — | — | 0.4295 | -0.20 pp |
| **v4** | **条款模式+真实例句** | **0.6952** | **+5.17 pp** | **0.8714** | **+2.37 pp** | 0.4310 | -0.05 pp |

v2虽然使Strict Evidence F1提高0.70个百分点，但Task Success和Macro-F1同时下降，说明额外低置信度KA带来的噪声超过其覆盖收益。v3使Containment F1从0.6348提高到0.6466，但Task Success和Strict F1下降，表明扩大上下文增加了Gold覆盖，也引入了更多无关条款。

只有v4同时提高Task Success和类别均衡状态能力，因此是本阶段唯一具有明确正向信号的改造。

### 5.2 v4核心结果

| 指标 | v1 | v4 | 变化 | 结论 |
|---|---:|---:|---:|---|
| Task Success | 0.6435 | **0.6952** | **+5.17 pp** | 明显改善 |
| Status Macro-F1 | 0.8477 | **0.8714** | **+2.37 pp** | 改善 |
| Balanced Accuracy | 0.8626 | **0.8773** | **+1.47 pp** | 改善 |
| No-answer Correct | 0.6637 | **0.7503** | **+8.66 pp** | 核心改善 |
| Containment Evidence F1 | 0.6348 | **0.6536** | **+1.88 pp** | 改善 |
| Strict Evidence F1 | 0.4315 | 0.4310 | -0.05 pp | 未改善 |
| Governance Boundary | **0.8916** | 0.8863 | -0.53 pp | 基本持平、略降 |

数据源：

- v1：`results/skillgen/generated/package_runtime_evaluation_test_final-k10-k6.json`
- v4：`results/skillgen/generated/package_runtime_evaluation_test_final-k10-k6-v4-example-phrasing.json`
- 完整跨方法报告：`results/skillgen/generated/experiment_data_report.md`

### 5.3 配对任务分析

基于v1与v4完全相同的4668条任务，按照当前Task Success定义进行配对比较：

| 配对结果 | 任务数 |
|---|---:|
| v1与v4均成功 | 2862 |
| 仅v1成功 | 142 |
| 仅v4成功 | 383 |
| v1与v4均失败 | 1281 |

v4净增加241条成功任务，对应约5.16个百分点。探索性统计结果为：

- Paired bootstrap 95%区间：`[+4.18, +6.08] pp`；
- McNemar exact test：`p≈1.4×10^-26`。

该结果说明在当前固定任务上，v4提升明显大于普通任务级随机波动。但v4是在分析test结果并尝试多个方案后选出的，因此这些统计量只能作为探索性证据，不能替代独立holdout上的确认性检验。

配对统计的数据源为：

- `results/skillgen/generated/evoskill_compiler/package_runtime_results/test/final-k10-k6/`
- `results/skillgen/generated/evoskill_compiler/package_runtime_results/test/final-k10-k6-v4-example-phrasing/`

## 6. 作用机制分析

### 6.1 v4主要改善正确拒答

| 状态指标 | v1 | v4 | 变化 |
|---|---:|---:|---:|
| `answered` Precision | 0.5751 | **0.6451** | +7.00 pp |
| `answered` Recall | 0.9026 | 0.9019 | -0.07 pp |
| `evidence_missing` Recall | 0.6637 | **0.7503** | +8.66 pp |
| `evidence_missing → answered`误判 | 956 | **710** | -246（-26%） |

v4在保持answered Recall基本不变的情况下，提高了answered Precision和evidence-missing Recall。因此，Task Success提升不是通过简单增加拒答获得，而是通过更准确地区分“目标合同确实包含该条款”和“训练知识中存在这种模式，但目标合同没有证据”。

Example Phrasing为Agent提供了具体文本原型。当目标合同出现相似语言时，Agent能够建立更明确的模式匹配；当目标合同缺少相似表述时，Agent更有依据返回`evidence_missing`。这与v4减少246条`evidence_missing → answered`误判的结果一致。

### 6.2 改善并非精确Gold-span抽取提升

v4的Strict Evidence F1为0.4310，与v1的0.4315基本一致；Evidence Recall还从0.4623略降至0.4608。因此，v4并没有使Agent更精确地复现CUAD Gold span。

Containment Evidence F1从0.6348提高到0.6536，说明v4更容易输出完整覆盖Gold的上下文证据，但其主要贡献仍然是条款存在性判断和状态校准，而不是严格抽取边界优化。

### 6.3 提升的领域分布

| Case | v1 Task Success | v4 Task Success | 变化 |
|---|---:|---:|---:|
| `ip_and_license` | 0.5322 | **0.7552** | **+22.30 pp** |
| `term_and_termination` | 0.6139 | **0.6639** | +5.00 pp |
| `liability_and_indemnity` | 0.6645 | **0.6991** | +3.46 pp |
| `revenue_and_commercial_terms` | 0.7208 | **0.7359** | +1.51 pp |
| `competition_restrictions` | 0.7747 | **0.7839** | +0.92 pp |
| `operational_rights` | 0.6950 | **0.7004** | +0.54 pp |
| `contract_basic_info` | 0.3599 | **0.3652** | +0.53 pp |
| `legal_governance` | 0.8694 | 0.8694 | 0.00 pp |
| `assignment_and_control` | **0.6860** | 0.6589 | -2.71 pp |

v4在6个case上提升、1个持平、2个下降，说明效果并非只存在于单一领域；但总体净增约241条成功任务中，按四舍五入估算约194条来自`ip_and_license`，约占80%。因此，当前总体提升高度受License类条款驱动。后续需要判断Example Phrasing是否特别适用于措辞多样的授权条款，或者只是修复了该case中质量较低的v1 Skill。

## 7. 与现有方法的比较

| 方法 | Task Success | Status Macro-F1 | Containment Evidence F1 | Governance Boundary |
|---|---:|---:|---:|---:|
| Native Prompt | 0.4994 | 0.5824 | 0.6455 | 0.5714 |
| Schema Prompt | 0.6298 | 0.8380 | 0.6508 | 0.8810 |
| Summary2Skill | 0.6407 | 0.7696 | **0.6638** | 0.7328 |
| Document Tool Maker | 0.6345 | 0.7451 | 0.6447 | 0.6984 |
| EvoSkill v1 | 0.6435 | 0.8477 | 0.6348 | **0.8916** |
| **EvoSkill v4** | **0.6952** | **0.8714** | 0.6536 | 0.8863 |

v4在Task Success和Status Macro-F1上形成了比v1更清晰的领先；Containment Evidence F1由原来的末位提升至第二，但仍低于Summary2Skill；Governance Boundary略低于v1，但仍接近最高水平。

因此，v4的合理定位是：

> 在保留EvoSkill治理优势的同时，通过真实条款模式改善目标条款存在性判断和正确拒答，从而提高端到端任务成功率。

当前证据不支持“v4全面提高答案和证据质量”，因为Strict Evidence F1没有改善，且尚未完成v4专属Academic Judge和Semantic Evidence Validity评测。

## 8. 无效方向及其研究价值

### 8.1 增加KA数量为何失败

top-30不仅是容量限制，也是隐式quality gate。增加到top-100后，更多低置信度和相似KA进入Skill package，增加了噪声和错误回答倾向。该结果说明EvoSkill后续优化应优先提高KA选择质量，而不是单纯扩大索引规模。

### 8.2 扩大Chunk为何失败

原始chunk约4800字符，已经能够覆盖绝大多数Gold区域。继续扩展上下文虽然提高Containment覆盖，却引入相邻无关条款，稀释模型注意力。该结果说明证据问题主要不是上下文长度不足，而是召回后如何识别最相关条款和生成最小充分引文。

这些负结果排除了两个直观但低效的方向，使后续工作可以集中在Skill表示和证据选择策略上。

## 9. 有效性边界

### 9.1 Test-set选择偏差

v2、v3和v4均在已经分析过的test轨道上比较，v4又是多个候选方案中表现最好的一个。因此，v4结果应被视为强正向的探索性发现，而非最终确认性结论。正式论文需要在dev上冻结方案，并在未参与设计的新holdout上确认。

### 9.2 单次Skill生成与运行

v4 Skill生成使用`temperature=0.2`，当前只有一套生成产物和一次完整运行。需要多次独立生成或固定种子重复实验，以区分提示结构贡献与生成随机性。

### 9.3 语义质量尚未补齐

当前没有v4专属Academic Judge和Semantic Evidence Validity结果。Task Success提升主要由状态校准驱动，不能自动解释为答案Correctness、Completeness或Faithfulness同步提高。

### 9.4 改造效果的领域集中性

约80%的净提升来自`ip_and_license`。正式结论需要报告分case结果，并避免将单域大幅改善表述为所有领域一致提升。

### 9.5 完整系统而非单一算法组件

虽然v4只修改`SKILL.md`生成提示，实际对比仍包含一次新的LLM生成过程。除非通过多次生成或固定产物复现，否则不能完全排除生成样本差异。

## 10. 下一步实验

### 10.1 必须完成

1. 对v4运行Academic Judge和Semantic Evidence Validity；
2. 在dev集重复v1/v4比较并冻结v4方案；
3. 使用未参与方案选择的新holdout进行最终确认；
4. 对v1/v4进行多次独立Skill生成和运行；
5. 保存不可变package快照，并在manifest中记录`SKILL.md`、evidence index和policy哈希。

### 10.2 机制验证

1. **Remove Example Phrasing：**保留Pattern结构但删除真实例句，验证收益是否来自例句本身；
2. **Examples without Pattern Grouping：**保留例句但取消模式分组，区分组织结构和原文锚点贡献；
3. **Minimal Sufficient Quote：**要求Agent输出最短充分引文，观察Strict与Containment F1；
4. **KA only for reasoning：**KA不进入合同BM25 query，只进入推理上下文；
5. **No Policy：**验证v4是否仍依赖原有security policy维持治理表现。

## 11. 阶段结论

本阶段通过三组针对性实验验证了EvoSkill性能瓶颈不应通过简单增加知识数量或扩大合同上下文解决。增加KA数量会引入低质量噪声，扩大chunk会稀释检索精度；二者均未改善端到端任务能力。

将抽象审查规则改写为Common Clause Patterns与真实Example Phrasing是唯一获得明确正向信号的改造。v4在保持answered Recall基本不变的同时，将`evidence_missing → answered`误判减少26%，使Task Success提高5.17个百分点、Status Macro-F1提高2.37个百分点，并使Containment Evidence F1提高1.88个百分点。配对任务分析表明该提升在当前固定test任务上具有稳定信号。

v4没有改善Strict Evidence F1，治理指标也有轻微下降；同时，其总体收益高度集中于`ip_and_license`，且尚缺少独立holdout、重复生成和语义Judge。因此，当前最稳妥的科研结论是：

> 真实条款例句能够为EvoSkill Agent提供比抽象审查规则更有效的语言匹配锚点，主要通过改善条款存在性判断和无证据拒答提高端到端任务成功率。该结果支持“模式驱动Skill表示”作为EvoSkill的下一版本方向，但仍需独立数据和重复实验确认其跨领域稳定性与语义质量。

## 12. 数据与代码索引

### 12.1 汇总数据

- v1：`results/skillgen/generated/package_runtime_evaluation_test_final-k10-k6.json`
- v2：`results/skillgen/generated/package_runtime_evaluation_test_final-k10-k6-v2.json`
- v3：`results/skillgen/generated/package_runtime_evaluation_test_final-k10-k6-v3-expand-chunks.json`
- v4：`results/skillgen/generated/package_runtime_evaluation_test_final-k10-k6-v4-example-phrasing.json`
- 跨方法报告：`results/skillgen/generated/experiment_data_report.md`

### 12.2 Task级数据

- v1：`results/skillgen/generated/evoskill_compiler/package_runtime_results/test/final-k10-k6/`
- v2：`results/skillgen/generated/evoskill_compiler/package_runtime_results/test/final-k10-k6-v2/`
- v3：`results/skillgen/generated/evoskill_compiler/package_runtime_results/test/final-k10-k6-v3-expand-chunks/`
- v4：`results/skillgen/generated/evoskill_compiler/package_runtime_results/test/final-k10-k6-v4-example-phrasing/`

### 12.3 诊断数据

- Evidence链路诊断：`results/skillgen/generated/evidence_diagnosis_evoskill_compiler_test_final-k10-k6.json`
- LLM复核与Mapper sensitivity：`results/skillgen/generated/evidence_review_and_mapper_sensitivity_evoskill_test_final-k10-k6.json`
- 原始Academic Judge缓存：`results/skillgen/generated/academic_judge_evaluation_test_final-k10-k6.jsonl`

### 12.4 实现代码

- EvoSkill编译：`scripts/baselines/evoskill_compiler.py`
- Package-aware Agent：`scripts/runtime/package_agent.py`
- 运行时评估器：`scripts/runtime/package_evaluator.py`
- EvoSkill再生成：`scripts/regen_evoskill_more_kas.py`
- 数据报告生成：`scripts/gen_report.py`
