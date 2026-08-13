# 规则抽取与 LLM 抽取最小对比实验

## 实验目的

该实验只回答一个问题：在相同的 Telecom policy section 与前 8 个 tool contract 上，当前确定性规则抽取器与 LLM 抽取器产生的 Knowledge Atom 结构差异有多大。它不编译 Skill、不运行 Agent、不读取 train/test task、reference action、reward 或 required-document label，因此不能作为 τ³ 性能结果。

执行脚本为 `scripts/compare_atom_extractors.py`，结果为 `results/evaluation/atom_extraction_llm_comparison.json`。

```powershell
python scripts/compare_atom_extractors.py --domain telecom --max-sections 3
```

当前 `.env` 解析到的模型名为 `ecnu-plus`。报告只记录 base URL host、输入哈希和 usage，不记录 API key。

## 固定输入

- 领域：Telecom；
- policy：前 3 个非空规范化 policy sections；
- tool contract：前 8 个官方工具 schema；
- 温度：0；
- LLM 输出：要求每个原子包含 `type/subject/text/object/source_title`；
- 允许类型：与 A2SC 冻结类型集合相同；
- held-out：不使用 train/test task、gold trajectory 或 reward。

## 观测结果

| 指标 | 结果 |
|---|---:|
| 规则原子数 | 86 |
| LLM 原子数 | 19 |
| 词面匹配数 | 12 |
| 规则原子文本覆盖率 | 13.95% |
| LLM 原子匹配精度 | 63.16% |
| 匹配对上的类型一致率 | 33.33% |
| LLM 无效 JSON/非法原子数 | 0 |

LLM 主要做了三件规则抽取器没有做好的事情：合并列表和硬换行、拆分复合治理规则、把同一条规则的条件与动作分离。例如：

- 规则将 “No other bills ... Logic: Sets bill status ...” 保留为一个复合原子，LLM 拆成前置条件与后置动作；
- 规则把 “should deny requests” 归为 `fact`，LLM 归为 `prohibition`；
- 规则把 “can help users ...” 归为 `permission`，LLM 归为 `actor_constraint`，说明类型判断仍存在边界歧义；
- LLM 额外生成了 “transfer 前先调用 transfer_to_human_agents” 和固定转人工话术这类可执行原子。

## 研究解释

这个结果不支持“规则抽取已经足够可靠”的强结论。规则抽取的优势是确定性、低成本、可复现和来源定位；但当前实现容易受到三个问题影响：

1. 文档硬换行和 Markdown 列表导致复合句切分粒度不稳定；
2. `must/can/after/verify` 等词面规则不能稳定区分 `fact`、`permission`、`precondition`、`prohibition` 与 `postcondition`；
3. 工具 docstring 常把 Preconditions、Logic、Returns 放在同一段，单纯句法规则不能恢复完整的条件—动作—结果结构。

同时，这个结果也不支持“LLM 原子天然正确”。LLM 的 19 个原子可能遗漏规则中的事实和工具参数，且匹配对中的类型一致率只有 33.33%。此外，当前文本匹配是词面诊断，不是人工语义标注；规则原子数更多并不等于规则召回更高，LLM 原子数更少也不等于更精确。

## 对 A2SC 的建议

不建议把系统升级为“全部由 LLM 抽取”。更稳妥的最小升级是两阶段：

1. 规则/解析器负责完整覆盖、来源行号、工具参数、actor ownership 和禁止读取 test/gold；
2. LLM 只在 dev policy sections 上做结构化重写或候选拆分，输出 `candidate_atoms`，并经过 schema 校验、来源字符串校验、工具名白名单和人工/规则冲突检查；
3. 未通过校验的 LLM 原子不能进入正式 Action Module；
4. 正式论文中将规则版作为主 A2SC，将 `LLM-assisted atomization` 作为独立扩展或消融，而不是混入主结果。

下一步若要证明 LLM 抽取是否真正有价值，应在四个领域各抽取 dev policy 子集，建立双人语义 gold，报告 atom-level precision/recall/F1、类型 macro-F1、source span validity、tool-binding precision，以及下游 τ³ reward 与 precondition/verification recall。当前这一次实验只能证明两种抽取器输出差异显著，不能证明哪一种最终性能更高。
