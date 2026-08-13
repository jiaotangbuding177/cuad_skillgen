# Package-aware Runtime v1：统一七基线升级方案

## 1. 目标与实验定位

v1 将当前“完整 `SKILL.md` 作为系统提示”的 Runtime 升级为：

```text
方法特有SKILL.md静态骨架
+ 每轮从package附件检索的任务相关上下文
+ τ³实际工具与对话状态
→ 统一LLMAgent
```

升级适配全部七种方法，而不是只增强 EvoSkill/GESC。主研究变量仍然是编译方法；Package-aware 加载、BM25、查询构造、通道顺序、top-k、字符预算和 Agent 完全共享。

## 2. 公平的 Package 契约

所有方法走同一加载与检索接口，但只开放该方法按定义能够产生的资产：

| 文件 | v1 用法 |
|---|---|
| `SKILL.md` | 所有方法：完整保留为静态骨架，并切分为 `skill` 检索通道 |
| `evidence_index.json` | Raw：原始 atoms；Document Tool：仅工具 atoms；Evo/GESC：全部合法 atoms |
| `security_policy.json` | 仅 Evo/GESC 开放为 `rule` 通道 |
| `workflow_patterns.json` | 仅 Evo/GESC 开放为 `workflow` 通道 |
| `pattern_cards.json` | 仅 GESC 存在，作为普通 `pattern` 候选检索 |
| `knowledge_graph.json` | v1 不读取、不遍历，留待独立 Graph-RAG 实验 |

虽然当前 bootstrap 生成器为审计一致性在每个目录都落盘了附件，Runtime 不会据“文件存在”就全部启用，而是根据冻结的方法能力配置过滤。否则 Raw/Native/Summary 会被额外赋予 EvoSkill 的规则与工作流，破坏基线定义。GESC 的 Pattern Cards 是其原生编译产物，允许作为普通文本候选进入 Runtime；这属于图编译产物的使用，不等于运行时沿图扩展。

| 方法 | v1 可检索资产 |
|---|---|
| Raw Policy RAG | Skill sections + source atoms |
| Native Prompt | Skill sections |
| Schema Prompt | Skill sections |
| Summary2Skill | Skill sections |
| Document Tool Maker | Skill sections + tool-contract atoms |
| EvoSkill | Skill sections + atoms + rules + workflows |
| GESC | Skill sections + atoms + rules + workflows + Pattern Cards |

## 3. 每轮检索协议

查询由“最近 6 条历史消息 + 当前进入消息”确定性拼接，包括自然语言、tool name、arguments 和 tool result。禁止加入 task 定义、reference actions、assertions、reward 或 required documents。

五个检索通道独立使用同一个本地 BM25：

| 通道 | 默认 top-k | 内容 |
|---|---:|---|
| rule | 3 | 适用政策、禁止、前提和升级规则 |
| atom | 6 | 政策段与工具契约 |
| workflow | 3 | train-derived actor-aware 流程 |
| pattern | 3 | GESC compile-time Pattern Cards；其他方法为空 |
| skill | 4 | 当前方法自身的 Skill 段落 |

候选按 `skill → rule → atom → workflow → pattern` 轮询装入，而不是先把某个通道填满，以避免 Evo/GESC 的 atoms 抢占全部预算、使 Skill 或 Pattern 通道饥饿。每项最多 1,800 字符，每轮动态上下文最多 12,000 字符；超出预算的项跳过，不为 GESC 或某个长 package 扩容。所有参数在 `config/experiment.json` 冻结。

## 4. Banking 隔离

Banking 的 698 篇产品知识虽然存在于 package evidence index，但 v1 在加载时排除 `knowledge_document` atoms。理由是任务知识已经由 τ³ 官方 `KB_search` 的固定 BM25 top-10 提供；如果 package retriever 再次检索全文，就会绕开官方检索通道、重复上下文并使 Required-document Recall 的解释失真。

Banking package retrieval 仅提供 task-independent policy/tool/process atoms，产品事实仍遵循：

```text
Agent → KB_search → 官方698篇知识库 → Top-10文档
```

## 5. Agent 实现

`PackageAwareAgent` 继承官方 `LLMAgent`。在每次 `generate_next_message` 前：

1. 从对话状态构造查询；
2. 从五个通道检索；
3. 将动态上下文追加到静态 `Runtime Adapter + SKILL.md`；
4. 更新当轮 system message；
5. 调用官方模型生成函数；
6. 将检索追踪写入 assistant message `raw_data.skillgen_package_retrieval`。

模型仍只能产生自然语言或调用 τ³ 暴露的 assistant tools；User tools、环境、Orchestrator 和 evaluator 不变。

## 6. 可审计输出

每轮追踪包含：

```json
{
  "query": "最近对话构造的查询",
  "items": [
    {
      "item_id": "POL-0014",
      "lane": "rule",
      "source": "KA-00014",
      "score": 3.27,
      "chars": 612
    }
  ],
  "context_chars": 5340,
  "budget_chars": 12000,
  "package_hash": "..."
}
```

离线脚本据此生成 `package_retrievals`、累计上下文字符、唯一命中 item 数及逐轮检索事件。该追踪不依赖模型自报，因此可复算。

## 7. 因果边界

v1 主对照保持：

```text
相同任务、模型、seed、工具、查询、BM25、top-k和预算
不同方法生成的SKILL.md及方法特有编译产物
```

需要分别报告两个实验：

- `prompt_only`：验证最终 `SKILL.md` 文本贡献；
- `package_v1`：验证完整 package 在共享 Runtime 下的系统贡献。

不能用 `package_v1` 结果反推“所有收益都来自 Knowledge Atoms”，因为它同时使用静态 Skill、规则、atoms 和 workflows。组件归因需要 `No atoms/No rules/No workflows` 消融。

## 8. 已知限制与 v2 边界

- BM25 主要适用于当前英文 benchmark；跨语言需统一 multilingual retriever；
- 完整 `SKILL.md` 仍常驻上下文，方法间长度是生成方法属性但会影响成本；
- workflow 由 train reference actions 归纳，只能作为软提示；
- v1 没有强制 Policy Guard、结构化状态机或 Postcondition middleware；
- v1 不做图遍历、多跳扩展或 runtime reranking；
- provenance 追踪证明“检索了什么”，不自动证明模型决定确实因该证据产生。

v2 可增加固定 token tokenizer、共享 reranker、精简 Skill scaffold 和显式治理拦截器；Graph-RAG 必须作为独立变量，而不是偷偷加入 GESC 主对照。

## 9. 运行方式

单次 Package-aware dry-run：

```powershell
vendor\tau3-bench\.venv\Scripts\python.exe scripts\run_agent_runtime.py `
  --method evoskill_compiler --domain telecom `
  --agent-model <agent-model> --user-model <user-model> `
  --num-tasks 1 --runtime-mode package_v1 --dry-run
```

Prompt-only 对照只需改为：

```text
--runtime-mode prompt_only
```

正式矩阵默认读取 `config/experiment.json` 中的 `package_v1` 配置，完成单元按 manifest 跳过并可恢复。

不调用模型即可审计七种方法的实际命中项：

```powershell
python scripts/audit_package_retrieval.py --domain telecom
```

输出明确标记为离线检索审计，不是 Agent benchmark 分数。
