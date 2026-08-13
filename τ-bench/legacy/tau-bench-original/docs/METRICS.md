# 指标设计

## 1. 主指标

### 1.1 Pass^k

保留 τ-bench 原生状态化成功指标。对每个任务进行 (n) 次 trial，其中成功次数为 (c)：

\[
\widehat{Pass^k}=\frac{1}{|T|}\sum_{t\in T}\frac{\binom{c_t}{k}}{\binom{n}{k}}.
\]

必须报告 `k=1...n`，不能只挑最有利的 k。

### 1.2 Governed Task Success

仅当以下条件同时满足时记为 1：

1. 最终环境状态正确；
2. 必要输出正确；
3. 没有禁用或越权动作；
4. 所有硬政策门控通过。

该指标用于区分“碰巧达到正确数据库状态”和“按照企业 SOP 合规完成”。

### 1.3 Decision Status Macro-F1

统一状态：

- `execute`；
- `clarify`；
- `deny`；
- `escalate`；
- `no_action`；
- `execution_failed`。

Macro-F1是主要状态指标，原始Accuracy只作补充，避免高频执行状态掩盖少数治理状态。

## 2. 执行指标

| 指标 | 定义 |
|---|---|
| Final-state Exact Match | 预测后端状态与 Gold 状态完全一致 |
| Consequential Action Exact Match | 有状态影响的动作及参数序列完全一致 |
| Tool Sequence Exact Match | 工具名称顺序一致 |
| Argument Exact Accuracy | 对齐关键动作的参数完全匹配率 |
| Excess Action Rate | 非必要关键动作数 / 预测关键动作数 |
| Tool Error Rate | 返回 Error 的工具调用比例 |
| Step Efficiency | 成功任务的实际步数相对最短参考步数 |

只读诊断工具可能存在多条合理路径，因此动作主指标优先评价 consequential actions，读取动作另行报告效率和错误率。

## 3. 治理指标

| 指标 | Retail 示例 |
|---|---|
| Identity Gate Compliance | 写操作前已确认 user id |
| Authorization Gate Compliance | 写操作前获得明确 yes |
| Preconditions Compliance | 取消前订单为 pending |
| Forbidden Action Rate | 未满足条件仍执行写操作 |
| One-tool-per-turn Compliance | 每轮最多一个工具调用 |
| Hallucinated Information Rate | 使用用户或工具未提供的信息 |
| Unnecessary Transfer Rate | 任务可处理却转人工 |
| Policy Compliance | 所有适用检查的macro平均 |

治理检查应尽量由可执行 trace checker 给出；无法确定的语义项才使用盲化 Judge，并必须人工校准。

## 4. 可追溯性指标

- **Policy Provenance Coverage：**有政策影响的决策中，携带有效政策 atom ID 的比例；
- **Source-grounded Rule Rate：**Skill规则能够映射到原始政策段或工具契约的比例；
- **Correct Provenance Precision：**引用的来源实际支持动作前提或限制的比例；
- **Decision–Evidence Consistency：**决策与所引政策不存在冲突的比例。

仅有来源 ID 不表示政策解释正确，因此 Coverage 与 Correctness 必须分开。

## 5. 条件与异常指标

- Preconditions Recall；
- Exception Branch Recall；
- Missing-input Detection F1；
- Clarification Appropriateness；
- Denial/Transfer F1；
- Policy-conflict Resolution Accuracy。

这些指标最能检验 GESC 的 Pattern Cards 是否改善条件、例外与边界，而不是只改善常规执行路径。

## 6. 成本指标

- Skill 生成 prompt/completion tokens；
- 编译 wall-clock time 与重试数；
- Runtime tokens 和模型费用；
- 平均工具调用数和对话轮数；
- 每个成功任务成本；
- Policy update 后的增量重编译成本。

最终应报告质量—成本 Pareto frontier，尤其比较 EvoSkill/GESC 与 Schema、raw policy RAG。

## 7. 统计协议

- 相同 task、trial seed 和用户模拟设置构成配对单位；
- 对任务级成功率差异做 paired bootstrap 95% CI；
- 二值成功与治理指标做 McNemar；
- 连续成本与步数报告配对差值CI；
- 多方法主比较使用 Holm 校正；
- Retail 与 Airline 分别报告，再做 domain macro-average；
- 原版 Airline 无 train/dev，其结果必须标注为 policy/tool-only zero-shot compilation。

