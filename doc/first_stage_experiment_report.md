# CUAD-SkillGen 第一阶段实验报告

## 1. 报告范围与核心结论

本报告分析五种 Document-to-Skill 方法在统一 Package-Aware Agent 上的最终测试结果。运行时数据来自：

```text
results/skillgen/generated/package_runtime_evaluation_test_final-k10-k6.json
results/skillgen/generated/academic_judge_evaluation_test_final-k10-k6_summary.json
```

本阶段得到的核心结论是：

1. **EvoSkillCompiler 在任务成功率、类别均衡状态判断和治理能力上取得综合最优结果。**其 Task Success Rate 为 **0.6435**、Status Macro-F1 为 **0.8477**、Balanced Accuracy 为 **0.8626**，均在五种方法中排名第一；Overall Boundary Correct 为 **0.6905**、Governance Boundary Correct 为 **0.8916**、Human Review Routing 为 **0.7469**、External Violation Rate 为 **0.2531**，治理相关指标整体最优。
2. **EvoSkillCompiler 并未在证据定位质量上领先。**其 Evidence F1 为 **0.4315**，在五种方法中最低；Schema Prompt Skill 以 **0.4772** 排名第一。因此，当前结果不能支持“EvoSkill 在所有维度全面优于基线”的强结论。
3. **结构化输出约束本身已是一条很强的基线。**Schema Prompt Skill 在 Evidence Precision、Recall、F1 上均排名第一，Governance Boundary Correct 仅比 EvoSkill 低 0.0106，Boundary Policy Coverage 也达到 1.0000。这表明统一 schema 和显式边界规则贡献很大，EvoSkill 相对 schema 的增益需要通过消融实验进一步拆解。
4. **新增 Academic Judge 显示，语义答案质量与证据定位、治理指标形成明显分化。**Summary2Skill 的 Academic Judge Score 最高（**0.9660**），EvoSkillCompiler 排名第二（**0.9545**），Document Tool Maker 排名第三（**0.9492**）；Schema Prompt Skill 虽然 Evidence F1 最高，但 Academic Judge 最低（**0.8404**）。这说明“找到更贴近 gold span 的证据”不等价于“生成更完整、清晰的合同审查答案”。
5. **第一阶段结果支持一个更窄、更可靠的论文观点：结构化 Skill 编译有助于提升任务执行成功率和治理一致性，EvoSkill 也能保持较高的语义回答质量，但尚不能证明其在语义质量或证据对齐上全面优于强基线。**
6. 五种方法均已达到 **4668/4668** 的运行结果覆盖，`complete=true`、`missing_tasks=0`、最终 `error_rate=0`。Academic Judge 共形成 6494 条方法—任务判断记录；不同方法的被评任务数为 1286–1317，原因是该指标只评价 gold=`answered` 且预测也为 `answered` 的候选。

## 2. 研究问题

第一阶段围绕以下问题展开：

- **RQ1：**由合同训练集生成的 Skill，在统一 Agent 中能否提高测试合同任务的完成率？
- **RQ2：**结构化 Skill package 是否比仅包含自然语言提示的 Skill 更有利于证据定位？
- **RQ3：**显式安全策略和边界规则是否改善人工复核路由、越权输出控制和边界状态判断？
- **RQ4：**当前结果在多大程度上能支持 EvoSkillCompiler 的论文主张，哪些结论仍受混杂因素限制？

## 3. 实验设置

### 3.1 数据划分与任务构成

数据按合同划分，训练、开发和测试合同互不重叠：

| 数据划分 | 合同数 | 用途 |
|---|---:|---|
| Train | 306 | 生成五种方法的 Skill |
| Dev | 102 | 小规模 smoke test 和检索参数确认 |
| Test | 102 | 最终运行时评估 |

每种方法在 test 轨道上均执行 4668 条任务。任务状态构成为：

| Gold 状态 | 任务数 | 占比 |
|---|---:|---:|
| `answered` | 1447 | 31.00% |
| `evidence_missing` | 2843 | 60.90% |
| `missing_input` | 108 | 2.31% |
| `unsupported_scope` | 108 | 2.31% |
| `needs_human_review` | 162 | 3.47% |
| **合计** | **4668** | **100.00%** |

九个 case 的任务规模并不均衡，范围从 258 到 870 条。因此总体指标采用评估器定义的加权汇总，而不能简单理解为九个 case 的算术平均。

| Case | 总任务 | Answered | Boundary | Human Review |
|---|---:|---:|---:|---:|
| contract_basic_info | 564 | 473 | 42 | 18 |
| term_and_termination | 360 | 125 | 42 | 18 |
| legal_governance | 360 | 161 | 42 | 18 |
| ip_and_license | 870 | 155 | 42 | 18 |
| competition_restrictions | 768 | 115 | 42 | 18 |
| liability_and_indemnity | 462 | 121 | 42 | 18 |
| assignment_and_control | 258 | 111 | 42 | 18 |
| revenue_and_commercial_terms | 462 | 92 | 42 | 18 |
| operational_rights | 564 | 94 | 42 | 18 |
| **合计** | **4668** | **1447** | **378** | **162** |

### 3.2 对比方法

| 方法 | 方法特征 | 当前 package 的主要差异 |
|---|---|---|
| Native Prompt Skill | 直接提示生成 | 以 `SKILL.md` 为主，evidence index 和 security policy 为空对象 |
| Schema Prompt Skill | 固定章节和输出 schema | 以结构化 `SKILL.md` 为主，evidence index 和 security policy 为空对象 |
| Summary2Skill | 逐合同摘要、合并后生成 | 包含摘要来源构成的 evidence index，security policy 为空对象 |
| Document Tool Maker | 逐合同抽取工具、合并后生成 | 包含 tool manifest 和工具示例索引，security policy 为空对象 |
| EvoSkillCompiler | Knowledge Atoms + 安全策略 + 编译 | 包含大规模 evidence index 和显式 security policy |

上述 package 不对称是方法设计的一部分，也是实验希望评估的能力差异；但它同时意味着当前实验比较的是**整套方法**，不能单独归因于 Knowledge Atom、policy、检索或最终提示中的任意一个组件。

### 3.3 统一运行时

五种方法均使用同一运行配置：

| 配置项 | 取值 |
|---|---|
| Runtime protocol | `package-aware-v1` |
| Runtime model | `ecnu-plus` |
| Split | `test` |
| Run ID | `final-k10-k6` |
| Target contract chunks | BM25 top-10 |
| Skill knowledge | BM25 top-6 |
| Governance tasks | Included |

Agent 的 Skill 选择采用 **Oracle/task-specified Skill routing with dynamic intra-Skill retrieval**：任务的 `case_id` 固定指定加载哪个 Skill，Agent 再在该 Skill package 内动态检索规则、知识和工具。该轨道评估的是 Skill 内容与包内利用能力，不评估多 Skill 自主路由能力。

### 3.4 证据处理链路

运行时不要求模型猜测数据集内部 evidence ID。Agent 从目标合同检索相关 chunk，要求模型输出原文引文；验证器确认引文真实存在于目标合同的已检索区间，再由离线 mapper 通过 span IoU 或 Text F1 对齐 gold evidence unit。

最终评估已使用修正后的一对一证据匹配：重复预测不能重复命中同一个 gold unit，未匹配预测会进入 Precision 分母。因此本报告中的 Evidence Precision 不再具有结构性恒等于 1 的错误。

## 4. 数据覆盖与结果有效性

| 方法 | 完成任务 | 预期任务 | 覆盖率 | 缺失任务 | 最终错误率 | 完整 |
|---|---:|---:|---:|---:|---:|---|
| Native Prompt Skill | 4668 | 4668 | 1.0000 | 0 | 0.0000 | 是 |
| Schema Prompt Skill | 4668 | 4668 | 1.0000 | 0 | 0.0000 | 是 |
| Summary2Skill | 4668 | 4668 | 1.0000 | 0 | 0.0000 | 是 |
| Document Tool Maker | 4668 | 4668 | 1.0000 | 0 | 0.0000 | 是 |
| EvoSkillCompiler | 4668 | 4668 | 1.0000 | 0 | 0.0000 | 是 |

运行结果采用 append-only JSONL 保存，重试会保留旧记录，因此部分结果文件的物理行数大于任务数。评估器按 `_task_id` 读取最后一条记录作为权威结果。覆盖率与错误率均基于去重后的最终记录，不受历史重试行影响。

## 5. 方法级总体结果

### 5.1 主结果

箭头表示指标方向：`↑` 越高越好，`↓` 越低越好。

| 方法 | Status Acc. ↑ | Task Success ↑ | Evidence F1 ↑ | No-answer ↑ | Governance Boundary ↑ | Overall Boundary ↑ | Human Review ↑ | External Violation ↓ | Isolation ↑ | Validation Failure ↓ |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Native Prompt Skill | 0.6041 | 0.4994 | 0.4611 | 0.4597 | 0.5714 | 0.4728 | 0.0000 | 1.0000 | 1.0000 | 0.2573 |
| Schema Prompt Skill | 0.7279 | 0.6298 | **0.4772** | 0.6250 | 0.8810 | 0.6551 | 0.7222 | 0.2778 | 1.0000 | 0.2269 |
| Summary2Skill | **0.7569** | 0.6407 | 0.4329 | **0.6820** | 0.7328 | 0.6880 | 0.3765 | 0.6235 | 1.0000 | **0.1221** |
| Document Tool Maker | 0.7412 | 0.6345 | 0.4485 | 0.6718 | 0.6984 | 0.6749 | 0.2963 | 0.7037 | 1.0000 | 0.1232 |
| **EvoSkillCompiler** | 0.7562 | **0.6435** | 0.4315 | 0.6637 | **0.8916** | **0.6905** | **0.7469** | **0.2531** | 1.0000 | 0.1300 |

由于原始 Status Accuracy 会受到 `evidence_missing` 占 60.90% 的类别不平衡影响，本报告进一步补充类别等权指标：

| 方法 | Status Accuracy ↑ | Status Macro-F1 ↑ | Balanced Accuracy ↑ |
|---|---:|---:|---:|
| Native Prompt Skill | 0.6041 | 0.5824 | 0.6712 |
| Schema Prompt Skill | 0.7279 | 0.8380 | 0.8475 |
| Summary2Skill | **0.7569** | 0.7696 | 0.7937 |
| Document Tool Maker | 0.7412 | 0.7451 | 0.7714 |
| **EvoSkillCompiler** | 0.7562 | **0.8477** | **0.8626** |

Macro-F1 对五种状态的 F1 等权平均，Balanced Accuracy 对五种状态的 Recall 等权平均。补正后 EvoSkill 两项均排名第一，说明其状态能力并非依赖多数类；Summary 的原始 Accuracy 高 0.0007，主要来自 `evidence_missing` 类的数量优势，而不是各类状态上的均衡领先。

### 5.2 Academic Judge：答案语义质量

Academic Judge 在 gold=`answered` 且方法预测状态也为 `answered` 的任务上进行盲化评价。Judge 可见任务问题、reference answer、候选答案和已经验证属于目标合同的证据，但不可见方法名称。总分按以下权重计算：

`Academic = 0.40 × Semantic Correctness + 0.25 × Completeness + 0.20 × Faithfulness + 0.15 × Clarity`

| 方法 | 被评任务 | Academic ↑ | Semantic Correctness ↑ | Completeness ↑ | Faithfulness ↑ | Clarity ↑ |
|---|---:|---:|---:|---:|---:|---:|
| Native Prompt Skill | 1297 | 0.9024 | 0.9137 | 0.8145 | 0.9543 | 0.9496 |
| Schema Prompt Skill | 1288 | 0.8404 | 0.8899 | 0.6905 | 0.9400 | 0.8253 |
| **Summary2Skill** | **1317** | **0.9660** | **0.9653** | **0.9363** | **0.9830** | **0.9946** |
| Document Tool Maker | 1286 | 0.9492 | 0.9488 | 0.9059 | 0.9724 | 0.9917 |
| EvoSkillCompiler | 1306 | 0.9545 | 0.9523 | 0.9197 | 0.9745 | 0.9916 |

结果形成三个梯队：Summary2Skill 排名第一；EvoSkill 与 Document Tool 构成高分第二梯队；Native 与 Schema 明显落后。EvoSkill 相对 Native 高 **5.21 pp**、相对 Schema 高 **11.41 pp**、相对 Document Tool 高 **0.53 pp**，但比 Summary2Skill 低 **1.15 pp**。在没有 paired bootstrap、Judge 重复采样和人工校准前，EvoSkill、Document Tool 与 Summary2Skill 之间的小幅差异不能直接解释为统计显著优势。

这一结果与 Evidence F1 的排名不同，但并不矛盾：

1. **指标对象不同。**Evidence F1 衡量候选引文与 CUAD gold span 的边界对齐；Academic Judge 衡量答案是否做出正确判断、是否覆盖条件与例外、是否忠实并清晰。引文边界更接近 gold，并不保证答案文本更完整。
2. **Schema 的主要短板是完整性和清晰度，而不是基本语义判断。**Schema 的 Semantic Correctness 仍为 0.8899，但 Completeness 只有 0.6905、Clarity 只有 0.8253，显著低于其他方法。这与固定 schema 容易生成短促、模板化答案的机制一致：它有利于稳定检索和引用，却可能压缩条件、例外、主体和期限等解释信息。
3. **Summary2Skill 的摘要表征更适合组织回答。**逐合同摘要再合并的流程保留了面向自然语言回答的上下文组织，因此在 Completeness（0.9363）、Faithfulness（0.9830）和 Clarity（0.9946）上均排名第一。它的 Evidence F1 较低，说明其优势更可能来自答案综合与表达，而非精确复现 gold span。
4. **EvoSkill 的结构化知识在语义层面有效，但检索对齐仍是瓶颈。**EvoSkill 的四个语义维度均超过 Native 与 Schema，且接近 Summary2Skill；这说明 Knowledge Atoms、规则和显式策略没有把答案退化成机械边界输出。不过，其较大的知识索引可能造成 query drift 或固定 top-k 下的竞争，因此 Academic Score 较高与 Evidence F1 最低可以同时出现。
5. **Document Tool 的工具化表示同样有利于答案组织。**其 Completeness、Faithfulness 和 Clarity 均接近 EvoSkill，说明结构化抽取结果和工具示例能够帮助模型形成可用答案，但其治理路由明显弱于 EvoSkill。

还必须注意一个比较限制：五种方法的被评任务集合并不完全一致。该评估器只纳入 gold=`answered` 且对应方法预测为 `answered` 的任务，因此被评数量从 1286 到 1317 不等。Academic Judge Score 是“在该方法选择回答的真阳性状态子集上，答案写得多好”的条件质量指标，不包含误拒答，也不能单独代替全量 Task Success。正式论文应补充所有方法共同回答任务的交集对比，或对未回答/错误状态施加统一惩罚，形成端到端语义效用指标。

### 5.3 相对 Native 基线的变化

| 方法 | Task Success 变化 | Evidence F1 变化 | No-answer 变化 | Governance Boundary 变化 | Overall Boundary 变化 |
|---|---:|---:|---:|---:|---:|
| Schema Prompt Skill | +13.04 pp | +1.61 pp | +16.53 pp | +30.96 pp | +18.23 pp |
| Summary2Skill | +14.13 pp | -2.82 pp | +22.23 pp | +16.14 pp | +21.52 pp |
| Document Tool Maker | +13.51 pp | -1.26 pp | +21.21 pp | +12.70 pp | +20.21 pp |
| EvoSkillCompiler | **+14.41 pp** | **-2.96 pp** | +20.40 pp | **+32.02 pp** | **+21.77 pp** |

EvoSkill 相对 Native 的主要增益集中在任务完成和治理，而不是证据 F1。与最强的结构化基线 Schema 相比，EvoSkill 的 Task Success 高 **1.37 pp**，Overall Boundary 高 **3.54 pp**，Governance Boundary 高 **1.06 pp**，Human Review 高 **2.47 pp**，External Violation 低 **2.47 pp**；但 Evidence F1 低 **4.57 pp**。这组结果说明 EvoSkill 的优势是有限且维度相关的，不是全面领先。

## 6. Case 级详细对比

### 6.1 Task Success Rate

| Case | Native | Schema | Summary | Document Tool | EvoSkill | 最优方法 |
|---|---:|---:|---:|---:|---:|---|
| contract_basic_info | 0.3723 | **0.3865** | 0.3209 | 0.3777 | 0.3599 | Schema |
| term_and_termination | 0.6222 | **0.6583** | 0.5639 | 0.6000 | 0.6139 | Schema |
| legal_governance | 0.7139 | **0.8806** | 0.8694 | 0.8694 | 0.8694 | Schema |
| ip_and_license | 0.2943 | 0.5793 | **0.7184** | 0.6264 | 0.5322 | Summary |
| competition_restrictions | 0.6250 | 0.7422 | 0.7591 | **0.7760** | 0.7747 | Document Tool |
| liability_and_indemnity | 0.6126 | **0.7468** | 0.5693 | 0.5996 | 0.6645 | Schema |
| assignment_and_control | 0.5620 | 0.6357 | 0.5969 | 0.6589 | **0.6860** | EvoSkill |
| revenue_and_commercial_terms | 0.4221 | 0.5022 | 0.6320 | 0.6082 | **0.7208** | EvoSkill |
| operational_rights | 0.4982 | 0.6259 | 0.6684 | 0.6223 | **0.6950** | EvoSkill |

EvoSkill 在 9 个 case 中赢得 3 个，集中于 assignment/control、commercial terms 和 operational rights；Schema 同样赢得 3 个，且在基础信息、期限和责任等 case 更稳。EvoSkill 的总体第一不是由所有领域一致领先产生，而是由部分 case 的较大优势，尤其 revenue_and_commercial_terms，对加权结果产生贡献。

### 6.2 Evidence F1

| Case | Native | Schema | Summary | Document Tool | EvoSkill | 最优方法 |
|---|---:|---:|---:|---:|---:|---|
| contract_basic_info | **0.3252** | 0.3085 | 0.2464 | 0.2942 | 0.2639 | Native |
| term_and_termination | 0.7547 | **0.7853** | 0.6429 | 0.7640 | 0.7147 | Schema |
| legal_governance | 0.7158 | **0.7613** | 0.7176 | 0.7245 | 0.7162 | Schema |
| ip_and_license | 0.4626 | 0.5016 | **0.5216** | 0.4425 | 0.4783 | Summary |
| competition_restrictions | 0.3874 | **0.4644** | 0.4412 | 0.4322 | 0.4021 | Schema |
| liability_and_indemnity | **0.5094** | 0.4851 | 0.5093 | 0.4776 | 0.4547 | Native |
| assignment_and_control | 0.4653 | **0.5227** | 0.4559 | 0.4939 | 0.4773 | Schema |
| revenue_and_commercial_terms | 0.3154 | 0.3168 | **0.3169** | 0.3159 | 0.2767 | Summary |
| operational_rights | 0.4821 | **0.4981** | 0.4354 | 0.4014 | 0.4371 | Schema |

Schema 在 5 个 case 的 Evidence F1 上领先，EvoSkill 没有任何 case 排名第一。该结果说明大规模 Knowledge Atom index 并未自动转化为更好的测试合同证据对齐。可能原因包括：

1. 训练知识被加入合同 chunk 的 BM25 查询，过多或过长的知识模式可能产生 query drift，使检索偏向训练中常见措辞，而不是目标合同的实际表述。
2. 当前仅保留 top-6 knowledge 和 top-10 chunks，Knowledge Atom 的数量优势可能在固定 top-k 下无法充分利用。
3. Evidence F1 对引文边界和 gold span 对齐敏感；复杂知识能帮助判断“回答什么”，但不一定帮助模型选择与 gold 标注边界最一致的引文。
4. Schema 基线的规则更短、更直接，可能为 BM25 提供更干净的关键词，从而在定位任务上优于更丰富的知识包。

这些原因目前属于基于系统机制和结果模式的解释性假设，尚需检索召回率、chunk oracle recall 和消融实验验证，不能作为已证明的因果机制。

### 6.3 Governance Boundary Correct

| Case | Native | Schema | Summary | Document Tool | EvoSkill | 最优方法 |
|---|---:|---:|---:|---:|---:|---|
| contract_basic_info | 0.5714 | 0.8810 | 0.7619 | 0.7619 | **0.9048** | EvoSkill |
| term_and_termination | 0.5714 | **0.8810** | 0.7619 | 0.5714 | 0.8810 | Schema / EvoSkill |
| legal_governance | 0.5714 | **0.8810** | 0.8810 | 0.7619 | 0.8810 | Schema / Summary / EvoSkill |
| ip_and_license | 0.5714 | **0.8810** | 0.7619 | 0.5714 | 0.8810 | Schema / EvoSkill |
| competition_restrictions | 0.5714 | 0.8810 | 0.5714 | 0.7619 | **0.9048** | EvoSkill |
| liability_and_indemnity | 0.5714 | **0.8810** | 0.7619 | 0.7619 | 0.8810 | Schema / EvoSkill |
| assignment_and_control | 0.5714 | 0.8810 | 0.7619 | 0.7619 | **0.9048** | EvoSkill |
| revenue_and_commercial_terms | 0.5714 | **0.8810** | 0.5714 | 0.7619 | 0.8810 | Schema / EvoSkill |
| operational_rights | 0.5714 | 0.8810 | 0.7619 | 0.5714 | **0.9048** | EvoSkill |

本表为 `governance_boundary_correct`，只覆盖 `missing_input`、`unsupported_scope` 和 `needs_human_review`。EvoSkill 在所有 case 上都达到 0.8810 或 0.9048，表现最稳定。其显式 `security_policy.json` 会被 Agent 的 deterministic boundary router 读取；当任务触发 legal advice 或 external output 条件时，只有 package 表达了相应策略，Agent 才会提前路由至 `needs_human_review`。这一机制与 EvoSkill 的 Human Review 和 External Violation 优势方向一致。

但这里存在重要的解释边界：结果证明的是“**包含可被当前 Agent 解析的显式策略的 package**”在该运行时中更有效，而不是孤立证明 Knowledge Atom 编译本身导致治理提升。Schema 虽然没有独立 security policy 文件，但其 `SKILL.md` 已包含足够明确的边界语言，因此也取得接近 EvoSkill 的结果。

## 7. 指标专项分析

### 7.1 Task Success 与 Status Accuracy

EvoSkill 的 Task Success 为 0.6435，较 Native 提升 14.41 个百分点，但仅较 Summary 高 0.28 个百分点、较 Document Tool 高 0.90 个百分点、较 Schema 高 1.37 个百分点。没有置信区间和配对显著性检验前，不能声称这些小差距具有统计显著性。

Summary 的 Status Accuracy 以 0.7569 略高于 EvoSkill 的 0.7562，但差距仅 0.0007，且该指标被占比 60.90% 的 `evidence_missing` 主导。补充类别等权计算后，EvoSkill 的 Status Macro-F1（0.8477）和 Balanced Accuracy（0.8626）均排名第一，说明其在少数治理状态上的优势被原始 Accuracy 稀释。Task Success 与 Status Accuracy 的差异还源于 answered 任务成功条件额外要求至少一条引文映射到 gold evidence。

EvoSkill 的分状态结果进一步显示：`answered` F1=0.7025、`evidence_missing` F1=0.7732、`missing_input` F1=1.0000、`unsupported_scope` F1=0.9076、`needs_human_review` F1=0.8551。其主要剩余状态错误不是少数类治理失效，而是 `answered` 与 `evidence_missing` 之间的取舍：answered Recall 高达 0.9026，但 Precision 只有 0.5751，说明模型仍存在偏向回答的倾向。

更重要的是，当前 Task Success **没有检查答案文本的语义正确性和完整性**。对 gold=`answered` 的任务，只要预测状态为 `answered` 且至少一条证据映射成功，即计为成功。因此该指标准确的名称应理解为“状态与证据链路成功率”，而不能等价表述为完整的回答质量。

### 7.2 Evidence Precision、Recall 与 F1

Schema 同时取得最高 Evidence Precision（0.5101）、Recall（0.4900）和 F1（0.4772），说明其证据优势不是由单独偏向多引用或少引用造成。EvoSkill 的 Precision 为 0.4467、Recall 为 0.4623，两项均未领先。

Evidence 指标只在 1447 条 gold=`answered` 任务上计算，按任务先计算 P/R/F1 再做宏平均，最后按各 case 的 answered 数量加权。它衡量引文与 CUAD gold spans 的对齐，不直接衡量答案解释是否完整，也不衡量 `evidence_missing` 任务是否正确避免编造证据。

#### 7.2.1 小规模证据链路诊断

为定位 EvoSkill 的 Evidence F1 瓶颈，固定现有 package、BM25、chunk 划分和 test 运行结果，使用随机种子 42 从 gold=`answered` 任务中抽取 200 条进行不调用 LLM 的离线诊断。比较三种合同检索查询：

- `task_only`：仅 category 与 question；
- `package_without_knowledge`：task + SKILL guidance + tool description，不加入 KA；
- `full`：当前正式运行时的完整 task + guidance + KA + tool query。

| 查询变体 | Any Gold Chunk Recall@10 ↑ | All Gold Chunk Recall@10 ↑ | Gold Chunk MRR ↑ |
|---|---:|---:|---:|
| Task only | 0.9450 | 0.8950 | 0.5876 |
| Package without knowledge | 0.9300 | 0.8950 | 0.6515 |
| **Full query** | **0.9550** | **0.9150** | **0.6518** |

在该200条样本上，完整查询并未整体降低召回：相对 task-only，Any Gold Recall@10 提高 1.0 pp、All Gold Recall@10 提高 2.0 pp、MRR 提高 0.0642。因此，当前证据不支持“KA 普遍导致 query drift”这一解释；KA 更可能在总体上改善首屏排序，同时只在少数任务上造成漂移。

| 诊断类别 | 任务数 | 占比 |
|---|---:|---:|
| 已按正式阈值匹配 gold | 106 | 53.0% |
| 替代或错误证据，需人工/语义 Judge 区分 | 48 | 24.0% |
| 接近 gold，但受映射阈值或引用边界影响 | 22 | 11.0% |
| Gold chunk 已召回，但未形成可匹配引文 | 15 | 7.5% |
| 合同检索失败 | 4 | 2.0% |
| Package query drift | 3 | 1.5% |
| Knowledge query drift | 2 | 1.0% |

该分布表明，至少在本次小样本中，纯检索及 query drift 只解释 9/200（4.5%）任务；更大的问题位于召回之后：70/200（35.0%）任务输出了未按正式阈值匹配的证据，其中22条已达到放宽匹配条件（span IoU≥0.3 或 Text F1≥0.5），另48条需要人工或 Evidence Relevance Judge 判断究竟是合理替代证据还是确实选错证据；另有15条属于引用抽取失败。

因此暂不建议直接重写 KA 检索算法。本报告随后对上述48条“替代或错误证据”完成已有盲化 LLM 判断的二次归类，并对 mapper 执行 sensitivity analysis。该诊断仍基于200条单次抽样，正式论文应在 dev 集重复种子或扩大样本后确认。

#### 7.2.2 LLM 证据复核

上述48条“替代或错误证据”全部已经包含在此前完成的盲化 Academic LLM Judge 缓存中。为避免重复调用和方法名泄露，本次复用该 Judge 的 Faithfulness、Semantic Correctness 与 rationale，按以下公开规则进行二次证据归类：

- `valid_alternative`：Faithfulness≥0.9 且 Semantic Correctness≥0.8；
- `wrong_evidence`：Faithfulness<0.5 或 Semantic Correctness<0.3；
- `partial_support`：Faithfulness≥0.8、Semantic Correctness≥0.3，但未达到 valid；
- 其余为 `ambiguous`。

这不是独立第二个 Judge，而是对已经完成的盲化 LLM 判断进行证据错误类型归纳。

| LLM 复核标签 | 数量 | 占48条比例 |
|---|---:|---:|
| Valid alternative | 43 | 89.58% |
| Partial support | 3 | 6.25% |
| Wrong evidence | 2 | 4.17% |
| Ambiguous | 0 | 0.00% |

其中46/48（95.83%）被判断为有效替代证据或部分支持，仅2条属于明确错误。该结果显著改变了对 Evidence F1 的解释：多数未匹配引文并不是模型引用了无关合同内容，而是引用了能够支持结论、但未与 CUAD 单一 gold span 达到形式匹配阈值的替代段落。换言之，当前 Evidence F1 同时混合了“证据选择能力”和“复现数据集 gold span 的能力”。

该结论仍需要人工专家抽样校准，因为复核复用了同一个 Academic Judge，不能视为独立模型间一致性证据。正式论文建议将这46条中至少20–30条交由合同领域人工复核，并报告 LLM—human agreement。

#### 7.2.3 Mapper sensitivity analysis

在同一200条样本上，对 span IoU 阈值 `{0.3,0.4,0.5,0.6,0.7}` 与 Text F1 阈值 `{0.5,0.6,0.7,0.8,0.9}` 做5×5网格分析。正式口径为 IoU=0.5、Text F1=0.8。

| IoU 阈值 | Text F1 阈值 | 匹配任务率 | Evidence Precision | Evidence Recall | Evidence F1 |
|---:|---:|---:|---:|---:|---:|
| 0.7 | 0.8 | 0.4750 | 0.3818 | 0.4059 | 0.3739 |
| 0.6 | 0.8 | 0.4950 | 0.4018 | 0.4234 | 0.3923 |
| **0.5** | **0.8** | **0.5300** | **0.4377** | **0.4540** | **0.4235** |
| 0.4 | 0.8 | 0.5750 | 0.4827 | 0.4848 | 0.4572 |
| 0.3 | 0.8 | 0.6200 | 0.5218 | 0.5236 | 0.4933 |
| 0.5 | 0.7 | 0.5350 | 0.4427 | 0.4590 | 0.4285 |
| 0.5 | 0.6 | 0.5700 | 0.4743 | 0.4844 | 0.4535 |
| 0.5 | 0.5 | 0.6350 | 0.5331 | 0.5386 | 0.5053 |
| 0.3 | 0.5 | **0.6450** | **0.5431** | **0.5486** | **0.5153** |

Evidence F1 对 mapper 阈值高度敏感：从正式 `(0.5,0.8)` 的0.4235降低到 `(0.3,0.5)` 后升至0.5153，增加9.18 pp，匹配任务数从106增至129。但不能据此事后把正式主指标改成最宽松阈值，因为更宽阈值也可能引入错误匹配，并导致针对当前结果调参。

较稳妥的论文处理是：

1. 保留预先确定的 `(IoU=0.5, Text F1=0.8)` 作为严格 Evidence F1 主口径；
2. 报告 mapper sensitivity 作为稳健性分析，明确结论受标注边界影响；
3. 增加经过人工校准的 `Semantically Valid Evidence Rate`，覆盖合理替代证据；
4. 不依据本次 test sensitivity 修改阈值；如需选新阈值，只能在 dev 集和人工标注样本上校准后冻结；
5. 算法改进优先集中在15条 citation extraction failure，而不是重写整体 KA 检索。

结合检索诊断、LLM复核和阈值敏感性，当前最合理的判断是：**EvoSkill 的 Evidence F1 偏低主要由 gold span 覆盖不足、引用边界和严格 mapper 共同造成，真实错误证据在抽样中的占比很低；现阶段没有证据支持大规模修改 KA 检索算法。**

#### 7.2.4 Containment-aware Evidence F1 与 Semantic Evidence Validity

根据诊断结果，本报告进一步增加两项正式补充指标，同时保留原 Strict Evidence F1：

1. **Containment-aware Evidence F1：**沿用相同 case、合同、category、严格 IoU/Text F1 阈值和一对一匹配；如果预测引文的字符区间完整包含 Gold span，也视为匹配成功。
2. **Semantic Evidence Validity：**复用全量盲化 Academic LLM Judge。只有 Faithfulness≥0.9 且 Semantic Correctness≥0.8 才标记为 `valid`；Faithfulness≥0.8、Semantic Correctness≥0.3 的其余结果标记为 `partial`；Faithfulness<0.5 或 Semantic Correctness<0.3 标记为 `invalid`。该指标是 LLM proxy，需要后续人工校准。

##### Containment-aware结果

| 方法 | Strict P | Strict R | Strict F1 | Containment P | Containment R | Containment F1 |
|---|---:|---:|---:|---:|---:|---:|
| Native Prompt Skill | 0.4852 | 0.4818 | 0.4611 | 0.7188 | 0.6628 | 0.6455 |
| Schema Prompt Skill | **0.5101** | **0.4900** | **0.4772** | **0.7312** | 0.6616 | 0.6508 |
| **Summary2Skill** | 0.4450 | 0.4643 | 0.4329 | 0.7280 | **0.6947** | **0.6638** |
| Document Tool Maker | 0.4710 | 0.4682 | 0.4485 | 0.7115 | 0.6599 | 0.6447 |
| EvoSkillCompiler | 0.4467 | 0.4623 | 0.4315 | 0.6999 | 0.6667 | 0.6348 |

所有方法的Containment F1均大幅高于Strict F1，说明“完整包含Gold但引用范围更长”是全体方法共同存在的评估现象。EvoSkill从0.4315升至0.6348，增加20.33 pp，证明严格IoU确实低估了其长引文；但它在Containment F1中仍排名第五，比Summary低2.90 pp。因此，不能把EvoSkill的全部Evidence差距都归因于span边界，预测证据数量、部分Gold遗漏和引用选择仍然造成剩余差距。

当前Containment规则严格遵循“完整包含即匹配”，没有设置最大长度膨胀比。这满足本阶段验证目标，但可能让过长引文获得匹配。正式论文建议在dev人工集上补充`predicted_length / gold_length`分布，并测试2×、3×、5×长度上限。

##### Semantic Evidence Validity结果

条件口径只评价“gold=`answered`、方法也输出`answered`且至少存在一条已验证证据”的任务；端到端口径以全部1447条gold answered任务为分母，因此会同时惩罚拒答和无有效证据。

| 方法 | Judge覆盖 | Valid / Judged | 条件Semantic Validity | 端到端Semantic Validity | 部分证据计0.5的端到端分数 |
|---|---:|---:|---:|---:|---:|
| Native Prompt Skill | 1.0000 | 1157 / 1297 | 0.8921 | 0.7996 | 0.8127 |
| Schema Prompt Skill | 1.0000 | 1104 / 1288 | 0.8571 | 0.7630 | 0.7830 |
| **Summary2Skill** | 1.0000 | **1256 / 1317** | **0.9537** | **0.8680** | **0.8728** |
| Document Tool Maker | 1.0000 | 1188 / 1286 | 0.9238 | 0.8210 | 0.8310 |
| EvoSkillCompiler | 1.0000 | 1217 / 1306 | 0.9319 | 0.8411 | 0.8500 |

EvoSkill的条件Semantic Validity为0.9319、端到端为0.8411，均排名第二。这说明在EvoSkill决定回答并给出已验证引文时，93.19%的任务同时满足高Faithfulness和高Semantic Correctness；把拒答损失计入后，仍有84.11%的全部gold answered任务获得语义有效证据。

新指标给出的最终判断是：

- Strict F1低估了长引文和替代证据，Containment-aware修正后EvoSkill提高20.33 pp；
- EvoSkill的语义证据有效性较高且排名第二，真实引文质量不是主要短板；
- Summary2Skill在Containment F1和Semantic Validity上均排名第一，因此EvoSkill仍存在真实的证据选择或覆盖差距；
- 论文应并列报告Strict F1、Containment-aware F1和Semantic Validity，不能用新指标替换或隐藏Strict F1；
- Semantic Validity复用单一Academic Judge，正式结论仍需人工抽样校准。

### 7.3 Boundary、Human Review 与 External Violation

修正后的 Boundary 拆为两层：`No-answer Correct` 覆盖 2843 条 `evidence_missing` 任务；`Governance Boundary Correct` 覆盖 378 条 `missing_input`、`unsupported_scope`、`needs_human_review` 任务；`Overall Boundary Correct` 是两者合并后的总体边界指标。EvoSkill：

- No-answer Correct = 0.6637，约对应 1887/2843 个无证据任务正确；
- Governance Boundary Correct = 0.8916，约对应 337/378 个治理边界状态正确；
- Overall Boundary Correct = 0.6905，约对应 2224/3221 个总体边界状态正确；
- Human Review Routing = 0.7469，约对应 121/162 个正确路由；
- External Violation Rate = 0.2531，约对应 41/162 个未正确限制。

Human Review Routing 与 `1 - External Violation Rate` 在当前实现中是同一批 needs-human-review 任务的互补结果，因此不能把它们当作两个独立证据重复计入综合结论。

这次指标修正后，`boundary_correct` 已经对齐原计划，表示 `Overall Boundary Correct`；旧口径保留为 `governance_boundary_correct` 和 `legacy_boundary_correct`，用于继续观察三类治理边界任务。

### 7.4 Contract Isolation

五种方法均为 1.0000。当前结果表明验证后的证据和 source IDs 没有跨目标合同引用，但不能证明 EvoSkill 比其他方法更好，因为统一运行时验证器对所有方法都施加了相同的目标合同限制，指标已出现天花板效应。

### 7.5 Validation Failure

Summary（0.1221）、Document Tool（0.1232）和 EvoSkill（0.1300）显著低于 Native（0.2573）与 Schema（0.2269）。Validation Failure 表示结果中出现至少一个验证错误的任务比例，常见原因包括模型输出无法在检索区间中找到的引文，以及 answered 输出没有任何可验证证据。

该指标支持“训练知识或工具结构有助于模型输出更可验证的合同引文”的解释，但它不等同于 Evidence F1。一个引文可以真实存在于合同中而没有对齐 gold span，因此出现 EvoSkill 验证失败较低、Evidence F1 仍不高的组合并不矛盾。

## 8. 生成成本与收益

### 8.1 静态 Skill 指标

根据最终 5 方法 × 9 case 的 package 重新计算静态质量指标后，得到以下结果：

| 方法 | Source-grounded Rule Rate ↑ | Unsupported Rule Rate ↓ | Boundary Policy Coverage ↑ |
|---|---:|---:|---:|
| Native Prompt Skill | 0.0337 | 0.9663 | 0.2444 |
| Schema Prompt Skill | 0.0237 | 0.9763 | 1.0000 |
| Summary2Skill | 0.0000 | 1.0000 | 0.5778 |
| Document Tool Maker | 0.0000 | 1.0000 | 0.4667 |
| **EvoSkillCompiler** | **0.8175** | **0.1825** | **1.0000** |

这组三项指标更直接对应 EvoSkill 的方案优势：规则是否有来源标记、无依据审查规则是否更少、边界策略是否显式覆盖。需要注意的是，这里采用 deterministic package audit，通过规则行中的 KA/证据/示例来源标记判断 source-grounding；它适合作为最终 package 的结构化审计，但仍可在正式论文中用 LLM judge 或人工抽样进一步校准。

### 8.2 生成成本

根据当前九个 `skill_manifest.json` 汇总：

| 方法 | 生成模型 | 生成 Token | 记录耗时（小时） | 相对 Native Token 倍数 |
|---|---|---:|---:|---:|
| Native Prompt Skill | deepseek-chat × 9 | 724,469 | 0.06 | 1.00× |
| Schema Prompt Skill | deepseek-chat × 9 | 719,382 | 0.05 | 0.99× |
| Summary2Skill | deepseek-chat × 4；ecnu-plus × 5 | 21,724,271 | 6.48 | 29.99× |
| Document Tool Maker | ecnu-plus × 9 | 23,932,205 | 27.79 | 33.03× |
| EvoSkillCompiler | ecnu-plus × 9 | 22,130,872 | 10.56 | 30.55× |

EvoSkill 相对 Native 消耗约 30.55 倍生成 tokens，换取 14.41 pp Task Success、21.77 pp Overall Boundary 和 32.02 pp Governance Boundary 提升；但相对 Schema 的增益仅为 1.37 pp Task Success、3.54 pp Overall Boundary 和 1.06 pp Governance Boundary，同时 Evidence F1 下降 4.57 pp。由此可见：

- 若论文目标是证明**相对直接提示基线的系统性改进**，现有结果有较强支持；
- 若目标是证明**相对低成本结构化 schema 基线具有明显性价比优势**，现有结果不支持，甚至提示成本收益存在明显问题；
- 后续必须报告生成成本，并把性能增益和成本放在同一张表中，不能只报告质量排名。

这里的耗时来自 manifest 中各生成调用耗时累计，会受 API 排队、重试和模型服务状态影响，只能作为观察值，不是稳定的算法复杂度指标。

## 9. 对论文观点的支持程度

### 9.1 当前结果较强支持的观点

**观点 A：直接将非结构化 Skill 内容交给 Agent，不足以形成稳定的企业治理行为。**

证据是 Native 的 Overall Boundary Correct 仅 0.4728，Governance Boundary Correct 为 0.5714，Human Review Routing 为 0，External Violation Rate 为 1.0；所有具备更明确结构或策略表达的方法都明显改善了这些指标。

**观点 B：将文档转化为可检索、可执行的 package，而不仅是自然语言提示，有助于运行时任务成功。**

Summary、Document Tool 和 EvoSkill 的 Task Success 均在 0.63 以上，相比 Native 的 0.4994 提升超过 13 个百分点。EvoSkill 取得最高值 0.6435。

**观点 C：显式安全和边界策略有助于提高治理一致性。**

EvoSkill 在 Overall Boundary、Governance Boundary、Human Review 和 External Violation 上均最优，且九个 case 的治理边界表现稳定。机制上，Agent 确实会读取 package policy 并用于 deterministic boundary routing，因此结果与系统设计形成闭环。

### 9.2 当前仅有限支持的观点

**观点 D：Knowledge Atom 编译优于摘要或工具抽取。**

EvoSkill 的总体 Task Success 只比 Summary 高 0.28 pp、比 Document Tool 高 0.90 pp；没有显著性检验，不能确认差异不是模型采样波动。EvoSkill 在九个 case 中只赢得三个 Task Success 第一名。

**观点 E：EvoSkill 提供更强的可追溯证据。**

当前 EvoSkill 的 Evidence F1 最低，不能用这组结果声称其证据定位更好。较低的 Validation Failure 只能说明输出引文更常通过原文验证，不能替代 gold evidence 对齐结果。

### 9.3 当前不能支持的观点

1. **不能声称 EvoSkill 在所有指标上全面最优。**Evidence P/R/F1 均不是最优。
2. **不能声称 EvoSkill 的答案语义质量显著优于所有强基线。**Academic Judge 已显示 EvoSkill 明显高于 Native 和 Schema，但低于 Summary2Skill，且尚无配对显著性检验、Judge 重复采样或人工评分校准。
3. **不能声称 Agent 能自主发现并选择正确 Skill。**当前 Skill 由任务 `case_id` 固定加载。
4. **不能把所有提升因果归因于 Knowledge Atom。**EvoSkill 同时改变了 evidence index、security policy、Skill 文本和生成模型。
5. **不能声称优于人工专家 Skill。**本次最终运行时结果中没有 `human_crafted_skill` 对照。

### 9.4 推荐的论文结论表述

当前最稳妥的核心表述是：

> 在 CUAD-SkillGen 的统一 package-aware 运行时中，结构化 Document-to-Skill 方法整体优于直接提示基线。EvoSkillCompiler 在任务成功率与治理边界指标上取得最佳总体结果，并在 Academic Judge 中保持第二名，表明显式知识组织与安全策略能够改善 Skill 的执行一致性，同时维持较高的语义答案质量；但 Summary2Skill 的语义评分更高，Schema Prompt Skill 的证据对齐更好，因此现有证据尚不足以证明 EvoSkill 在所有质量维度上的普遍优势。

## 10. 客观性与内部效度限制

### 10.1 生成模型不一致

Native 和 Schema 的九个 Skill 均由 `deepseek-chat` 生成；Document Tool 与 EvoSkill 均由 `ecnu-plus` 生成；Summary 有 4 个 case 使用 deepseek-chat、5 个使用 ecnu-plus。虽然运行时统一使用 ecnu-plus，但生成模型差异仍是明确混杂变量。

因此，当前结果比较的是“生成方法 + 生成模型”的联合产物。生成模型一致性是已知 TODO；在修复前，论文必须如实披露，不能将小幅差异完全归因于算法。

### 10.2 Package 能力不对称与组件耦合

Native/Schema 没有实际 evidence index 和独立 policy，Summary 有摘要索引，Document Tool 有工具索引，EvoSkill 同时有 Knowledge Atom index 和 policy。这种差异是方法能力本身，但一次比较同时改变多个变量，无法回答“究竟是 index、policy、生成 prompt 还是知识粒度带来提升”。

### 10.3 Agent 与 EvoSkill 表示存在适配优势

统一 Agent 能识别 EvoSkill 的 category-list KA、Summary 的 source paragraphs 和 Document Tool 的 tool metadata，并有专门的 normalization 分支。虽然所有方法共享同一个运行器，但不同表示经过不同适配代码。需要通过单元测试、等预算检索和 representation-neutral adapter 审计，排除适配质量差异。

### 10.4 Skill 路由是 Oracle，而非自主选择

任务的 case_id 固定加载对应 Skill。这能隔离 Skill 内容质量和跨 Skill 路由错误，是合理的第一阶段设计；但它不能支撑“Agent 会自主选择正确 Skill”的主张。自主多 Skill 路由应作为独立实验轨道，报告 routing accuracy、end-to-end success 和误路由代价。

### 10.5 Academic Judge 是条件子集评价，不能替代端到端成功率

当前 Task Success 中的 answered 成功只需要状态正确且存在一个 gold evidence match，因而仍不能直接代表答案文本质量。新增 Academic Judge 补充了 Semantic Correctness、Completeness、Faithfulness 和 Clarity，但只评价 gold=`answered` 且预测也为 `answered` 的任务。各方法被评集合和样本量不同，分数不惩罚误拒答，也没有覆盖边界类任务；因此必须与 Task Success、Status Accuracy 和 Boundary 指标联合解释。

此外，本次只使用单一 `ecnu-plus` Judge、temperature=0 和一次判断，没有报告 Judge 自一致性、跨 Judge 一致性或与人工专家评分的相关性。高分段集中在 0.95 左右，可能存在量表饱和；Summary、EvoSkill 和 Document Tool 之间的细小差异尤其需要 paired common-set 评估与人工抽样校准。

### 10.6 Boundary 指标已修正，但需明确口径

当前评估已将 `evidence_missing` 纳入总体边界指标，并拆分为 `no_answer_correct`、`governance_boundary_correct` 和 `boundary_correct`。论文中必须明确：`boundary_correct` 是总体边界，`governance_boundary_correct` 才是旧口径下的三类治理边界。

### 10.7 Contract Isolation 天花板效应

所有方法均为 1.0，主要说明统一验证链路能够限制跨合同引用。该指标没有区分方法，不能用于支持 EvoSkill 的相对优势。需要设计对抗性任务，例如同时提供相似的干扰合同、诱导引用训练样例或冲突条款。

### 10.8 单模型、单次运行、无显著性检验

最终结果来自单一 runtime 模型 ecnu-plus 和一个 run ID，没有重复采样、置信区间或跨模型复现。生成随机性和运行模型随机性都可能影响 0.28 至 1.37 pp 的小差异。

### 10.9 Dev 调参规模有限

`top_k_chunks=10`、`top_k_knowledge=6` 仅经过较小规模 smoke run 后冻结，而不是完整 dev 网格搜索。这减少了过度调参风险，但不能证明该参数对所有方法同样最优。尤其 EvoSkill 的大索引可能需要不同检索预算。

### 10.10 静态质量指标仍需人工或 LLM 校准

`skill_quality_evaluation.json` 已基于最终 package 统一重算，并补入 Source-grounded Rule Rate、Unsupported Rule Rate 和 Boundary Policy Coverage。当前实现是 deterministic package audit，主要依赖来源标记和边界关键词；正式论文中建议对规则抽取与 grounding 判断做人工抽样或 LLM judge 校准。

## 11. 后续加强方向

### 11.1 第一优先级：补齐当前结论缺口

1. **校准并强化答案语义评价。**当前已完成盲化 Academic Judge；下一步应在五种方法共同回答正确的任务交集上做 paired comparison，报告 bootstrap 95% CI，并由合同领域人工专家抽样复核 correctness、completeness、faithfulness 和 clarity。还应构造包含误拒答惩罚的端到端语义效用指标。
2. **校准 Boundary 与静态规则指标。**当前已分别报告 `No-answer Correct`、`Governance Boundary Correct` 和 `Overall Boundary Correct`；后续需要对 source-grounded / unsupported 规则抽取做人工或 LLM 校准。
3. **增加配对统计检验。**基于同一 task 的方法结果执行 paired bootstrap，报告 95% CI；二值成功率可补充 McNemar 检验。只有这样才能判断 EvoSkill 对 Summary 的 0.28 pp 增益是否真实。
4. **补齐 Evidence Index Quality。**当前已补 Source-grounded Rule Rate、Unsupported Rule Rate 和 Boundary Policy Coverage；下一步应单独评估 evidence index 的真实性、覆盖率和 span/category 一致性。

### 11.2 第二优先级：做最小但关键的消融实验

在不进行大规模调参的前提下，建议只做以下四个 EvoSkill 变体：

| 变体 | 用途 |
|---|---|
| Full EvoSkill | 当前完整方法 |
| No Policy | 测试治理提升是否来自显式 policy |
| No KA Retrieval | 测试任务成功与证据定位是否依赖 KA |
| Same SKILL.md + Empty Package | 测试 package 附件相对最终文本本身的增益 |

这组消融比继续搜索大量 top-k 参数更有论文价值，因为它直接回答核心方法的组件贡献。

### 11.3 第三优先级：控制生成模型与预算

后续正式实验应使用同一生成模型、temperature、max tokens 和重试策略生成全部方法；同时报告：

- 实际生成 tokens 和 API calls；
- Skill package 大小；
- runtime tokens、延迟和调用次数；
- 等预算结果，例如固定 1M 生成 tokens 时的质量；
- 质量-成本 Pareto frontier。

在统一生成模型前，可保留当前结果作为 pilot study，但不应作为最终因果对比表。

### 11.4 第四优先级：验证检索机制

当前 Evidence F1 是 EvoSkill 的主要短板。建议增加不调用 LLM 的检索诊断：

1. `Gold Chunk Recall@10`：top-10 chunks 是否包含 gold span；
2. `Gold Chunk MRR`：正确 chunk 的排名；
3. query ablation：task-only、task+SKILL、task+KA 三种查询对比；
4. top-k sensitivity：只测试 k=5/10/20 三点，不做大规模网格；
5. 按 case 分析 query drift，重点检查 revenue/commercial、contract basic info 和 operational rights。

如果 EvoSkill 的 Gold Chunk Recall 低于 Schema，就能直接解释其 Evidence F1 落后；如果 chunk recall 相当，则问题更可能在引文抽取或 gold mapping。

### 11.5 第五优先级：建立独立路由与对抗轨道

在当前 Oracle routing 轨道之外，增加：

- 多 Skill 自主选择任务；
- 跨 case 模糊问题；
- 同时需要两个 Skill 的组合任务；
- 相似干扰合同下的 contract isolation；
- prompt injection、训练证据诱导引用、外部法律文书生成等安全任务。

该轨道应单独报告 Skill Routing Accuracy、End-to-End Success 和 Safety Violation，不能与当前 package-quality 轨道混为一谈。

## 12. 第一阶段结论

第一阶段已经建立了一条完整、可增量恢复、结果覆盖一致的 Package-Aware 运行时评估链路。五种方法均完成 4668 条 test 任务，错误率为 0，证据指标也已经从不可实现的 ID 猜测修正为“原文引文验证 + gold evidence 映射”，并新增了 correctness、completeness、faithfulness 和 clarity 四维 Academic Judge。因此，当前结果足以作为论文的 pilot 实验和方法有效性初证。

结果表明 EvoSkillCompiler 的主要价值体现在**任务成功、治理边界和静态规则可追溯性**：它取得最高 Task Success、Overall Boundary、Governance Boundary、Human Review Routing、Source-grounded Rule Rate 和最低 External Violation Rate、Unsupported Rule Rate。Academic Judge 为 0.9545，排名第二，说明它在强化治理的同时保持了较高答案质量；但 Summary2Skill 以 0.9660 取得语义质量第一，EvoSkill 的 Evidence F1 又落后于 Schema、Native 和 Document Tool，且相对强基线的成功率优势很小、生成成本约为直接基线的 30 倍。

因此，本阶段能够支撑的不是“EvoSkill 全面优于所有方法”，而是一个更精确的结论：**结构化 Skill 编译和显式策略可以改善执行成功率与治理一致性，并能维持较高的语义答案质量；但摘要式表征在答案完整性与表达上仍更强，知识索引如何转化为更准确的测试合同证据定位，仍是下一阶段必须解决和验证的问题。**
