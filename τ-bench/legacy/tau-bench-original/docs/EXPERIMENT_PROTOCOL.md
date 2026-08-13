# τ-bench Document-to-Skill 实验协议

## 1. 论文目标

该扩展实验不用于证明 EvoSkill 更擅长文本抽取，而用于检验以下核心命题：

> 将企业 SOP 编译为可检索知识、可执行工作流和显式治理策略，能否在相同 Agent、工具、环境和模型下，提高多轮任务完成、条件与例外判断、政策合规和规则可追溯性。

τ-bench提供动态用户交互、领域政策、工具调用与可验证数据库状态，原始评价以最终环境状态为核心[[1]](https://arxiv.org/abs/2406.12045)。这使它能够补足CUAD主要评价抽取和证据定位的限制。

## 2. 研究问题

- **RQ1 执行：** EvoSkill/GESC 是否提高 `Pass^k` 和最终状态正确率？
- **RQ2 决策：** 是否提高 `execute/clarify/deny/escalate/no_action` 的 Macro-F1，尤其是少数治理状态？
- **RQ3 治理：** 是否减少未核验身份、未确认即写入、错误工具和越权操作？
- **RQ4 可追溯性：** 每个关键决策和后端写操作是否能定位到政策知识单元？
- **RQ5 成本收益：** 相对 Schema 和 raw policy RAG 的增益是否足以抵偿编译与运行成本？
- **RQ6 图增强：** 在原始政策、工具、Agent和运行配置一致时，图组织的 Pattern Cards 是否改善条件/例外工作流？

## 3. 对照方法

| 方法 | 作用 |
|---|---|
| `raw_policy_rag` | 不进行知识编译，提供原始政策检索对照 |
| `native_prompt_skill` | 自由形式 Skill |
| `schema_prompt_skill` | 固定章节和决策步骤的低成本强基线 |
| `summary2skill` | 政策摘要与训练工作流频次 |
| `document_tool_maker` | 以工具契约为中心组织 SOP |
| `evoskill_compiler` | 政策、规则和工具契约原子化，显式治理与来源 |
| `graph_evoskill_compiler` | 在相同原子上构图并编译 Pattern Cards |

当前目录中的 `deterministic_bootstrap` 产物只验证工程协议。正式主实验必须给所有生成型方法使用同一生成模型、temperature、最大输出、重试策略和预算，并将配置写入 manifest。

## 4. 公平性冻结

下列条件在方法间保持一致：

- 原始上游提交和任务 split；
- Runtime Agent：上游 ToolCallingAgent；
- Agent model 与 user simulator model；
- 工具模式与后端初始数据；
- temperature、最大步数、trial 数和 task 顺序；
- 每次 trial 从同一初始数据库重置；
- dev/test 均不参与 Skill 编译；
- GESC 只改变 compile-time Skill 组织，不改变 runtime graph retrieval。

推荐主配置：`temperature=0, max_steps=30, num_trials=4`。模型名称不在代码中预设，待与CUAD统一后再冻结。

## 5. 实验阶段

### 阶段 A：生成与静态审计

1. 固定上游提交并校验文件哈希；
2. 生成所有方法的两个领域 Skill；
3. 检查政策覆盖、工具覆盖、来源覆盖、禁止 test 泄漏；
4. 对 EvoSkill/GESC 抽查身份、确认、退款、修改和异常条款；
5. 记录生成 token、耗时、失败与重试。

### 阶段 B：Dev 预注册

仅使用 retail dev：

- 冻结状态标签映射；
- 冻结治理检查器；
- 冻结最大步骤、检索预算和输出解析；
- 冻结 trace 到政策证据的匹配规则；
- 禁止根据 test 结果调整图阈值或 Pattern 数量。

Airline 没有 dev，不得用其 test 调参。

### 阶段 C：Test 主实验

对每个方法、领域和 task 运行相同 trial。每个 `task_id × trial` 独立落盘。主报告同时给出原始 reward、Pass^k、治理成功和错误类型。

### 阶段 D：配对统计

- 对同一 task 的 mean trial success 执行 paired bootstrap 95% CI；
- 对逐 trial 的二值任务成功和治理成功执行 McNemar 检验；
- 对共同完成任务比较动作数、成本和政策来源覆盖；
- 多重比较采用 Holm 校正；
- 主比较预注册为 EvoSkill vs Schema、EvoSkill vs Summary、GESC vs EvoSkill。

## 6. 必要消融

1. `No Policy`：移除显式治理层；
2. `No Provenance`：保留知识文本但删除来源 ID；
3. `No Workflow Patterns`：不使用 train 动作模式；
4. `No Confirmation Atoms`：删除授权门控知识；
5. `Flat KA vs Graph Pattern`：EvoSkill 与 GESC 主对照；
6. `Skill only` vs `Skill + raw source retrieval`：区分编译充分性和源文档兜底；
7. `Oracle structured SOP`：人工结构化小样本上界。

## 7. 可以与不可以宣称的结论

若主结果显著，可主张 Skill 编译在状态化、政策约束工具任务中改善执行或治理。仍不可以声称：

- 原版 τ-bench 代表全部企业 SOP；
- deterministic mock 的满分是算法证据；
- airline 与 retail 具有相同训练条件；
- GESC 收益来自 runtime Graph-RAG；
- LLM Judge 等同人工治理审计；
- 原版过时任务代表当前 τ³-bench 性能。

## References

[1] Yao, S., Shinn, N., Razavi, P., & Narasimhan, K. (2024). *τ-bench: A Benchmark for Tool-Agent-User Interaction in Real-World Domains*. arXiv. https://arxiv.org/abs/2406.12045

