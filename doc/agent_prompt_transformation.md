# Agent 结果处理改造：从 Prompt 塞入到 Package-Aware

## 一、问题发现

### 1.1 原始设计的假设缺陷

最初 Agent 的设计假设是：**只要把整份 SKILL.md 和整份合同原文一起塞进 LLM 的 prompt，LLM 就能自行理解规则、定位证据、输出正确的证据 ID。** 这个假设在真实合同审查场景中存在三个致命问题。

**问题 1：抽象 ID 无法由 LLM 直接生成。**

SKILL.md 中提到的证据规则是对合同知识的结构化描述，而 gold evidence unit IDs（如 `GE-CUAD-002374`）是数据集标注阶段由人工确定的编号。LLM 在推理时无法接触到这个编号系统，也就不可能输出正确的 ID。评估时将这组 ID 与金标准做 set 比较，结果永远是 F1 = 0——不是因为模型能力不足，而是因为评估指标对接了一条 LLM 不可能通过的路径。

**问题 2：合同全文作为上下文压力过大。**

一份企业合同平均 1 万到 5 万词，全量放入 prompt 后，上下文中的无关条款成为噪声。每一轮 6-8 万 tokens 的输入中，与当前问题真正相关的段落通常只占 5-15%。LLM 在如此低的信噪比下定位细粒度证据引文的成功率有限，且 token 消耗巨大。

**问题 3：无验证环节，幻觉无法被阻断。**

LLM 输出的 `evidence_unit_ids` 没有任何人对它做验证。模型可能输出不存在的 ID、输出属于其他合同的 ID、或者输出一个与金标准编号格式相似但无意义的字符串。这些错误全部被写入结果文件，且直接参与指标计算。

### 1.2 实证验证

agent.py 的第一个版本（原始 prompt 塞入方式）在实际运行中暴露出的数据如下：

| 观察项 | 数值 | 说明 |
|---|---|---|
| Evidence F1 | 始终为 0 | LLM 输出的 evidence_unit_ids 无法匹配任何金标准单位 |
| 验证失败率 | 无法计算 | 因为根本没有验证环节 |
| Contract Isolation | 无法验证 | 无法区分引文来自目标合同还是其他合同 |
| Token 消耗 | 极高 | 每任务平均将整份 50K token 合同送入 LLM |

即使模型正确回答了问题内容，只要 `evidence_unit_ids` 不匹配，指标就判为失败。这意味着**原始设计中的指标计算层和模型推理层之间存在结构性的数据鸿沟。**

---

## 二、模块简述

改造后的系统由四个功能模块构成，它们共同组成一条从「合同原始文本」到「可验证的引文证据」的完整链路。

**模块 1：合同分块器。** 将一份完整合同按 4800 字符为单位切分为固定尺寸的文本块，块间保留 600 字符重叠以确保跨段落的条款不被截断。每个块独立记录其在原文中的起始和结束字符偏移量，保证后续验证可以精确回查。

**模块 2：多源检索器。** 对每个输入的任务，从三个来源中分别检索与其最相关的内容：从 SKILL.md 中检索规则章节（top-4），从 evidence_index.json 中检索知识原子（top-6），从合同分块中检索相关文本块（top-10）。检索算法使用 BM25，不依赖外部向量数据库或嵌入模型。

**模块 3：引文验证器。** LLM 输出的每段证据引文都在合同原文中做精确的位置查证。如果引文的文本内容在指定偏移范围内存在，则通过验证；如果不存在，则标记为 `unverified_evidence_quote`。对于 `answered` 状态但没有通过任何验证的任务，状态自动降级为 `evidence_missing`。

**模块 4：证据映射器。** 评估阶段将验证通过的引文段落与金标准 evidence units 做映射。映射依据两项指标：字符跨度的 IoU 和归一化文本 F1。只要有一项超过阈值（IoU >= 0.5 或 Text F1 >= 0.8），即认为该引文与金标准证据单位对齐。这样即使模型引用的文本与标注人员的选区不完全一致，也能通过全文相似度匹配到正确的金标准 ID。

---

## 三、流程变更

### 3.1 变更前：单向盲猜

```text
任务输入
    |
    v
加载整份 SKILL.md -------------------------+
                                            |
加载整份合同文本（truncate to 50K tokens） ---+
                                            |
                                            v
                              LLM 一次推理：
                              - 阅读全部 SKILL 规则
                              - 阅读全部合同原文
                              - 输出证据 ID
                                            |
                                            v
                              直接写入结果文件
                              （无验证、无映射）
```

### 3.2 变更后：多阶段保障

```text
任务输入
    |
    v
    +-- 硬路由检查 ---- 匹配边界规则 -> 直接返回（不调 LLM）
    |
    v
加载 Skill Package（5 个文件）
    |
    +-- 规则检索：BM25 从 SKILL.md 提取相关章节
    +-- 知识检索：BM25 从 evidence_index 提取相关知识
    +-- 合同分块：按 4800 字符切割，保留偏移
    +-- 块检索：BM25 提取最相关 top-10 合同块
    |
    v
LLM 推理：基于检索到的上下文输出引文 + 偏移
    |
    v
引文验证器：逐条验证引文是否在合同原文中真实存在
    |
    +-- 验证通过 -> 写入结果
    +-- 验证失败 -> 标记 validation_error / 降级 status
    |
    v（评估阶段）
证据映射器：通过 IoU/Text F1 映射到金标准 evidence unit ID
```

---

## 四、方法对比

### 4.1 设计范式对比

| 维度 | 直接 Prompt 塞入 | Package-Aware 改造 |
|---|---|---|
| 设计哲学 | LLM 全权负责阅读、理解、推理、输出 | 确定性模块分担检索、验证、映射，LLM 只负责在限定范围内提取引文 |
| Skill 利用方式 | 全文塞入，一视同仁 | 分章节检索，按需取用 |
| 合同利用方式 | 全文截断，不分先后 | 分块检索，只保留与问题最相关的段落 |
| 证据链路 | LLM -> 抽象 ID -> 无验证 -> 直接评估 | LLM -> 引文文本 + 偏移 -> 原文验证 -> 映射到金标准 ID |
| 错误阻断 | 无 | 引文验证器在 LLM 输出后即阻断幻觉 |
| 扩展性 | 增加 SKILL.md 长度或合同长度直接增加 prompt | 增加知识量不影响 prompt 大小（仍只检索 top-6 / top-10） |

### 4.2 核心切换点

改造中最关键的一个切换是：**证据的表现形式从「不可验证的抽象编号」变为「可验证的合同原文引文」。** 这看起来是一个输出格式的变化，实际上改变了整个评估范式——旧范式要求 LLM 输出它不可能知道的编号，新范式要求 LLM 输出它正在阅读的合同中的原话，这是一个从「猜测」到「摘录」的切换。

### 4.3 实际效果

以 native_prompt_skill 在 test 集上的完整结果验证：

| 指标 | 旧方式 | 改造后 |
|---|---|---|
| Evidence Precision | 无意义（匹配不上任何 ID） | 1.000 |
| Evidence Recall | 0.000 | 0.453 |
| Evidence F1 | 0.000 | 0.505 |
| Validation Failure Rate | 无法计算 | 0.162（有据可查） |
| Contract Isolation | 无法验证 | 1.000 |
| 任务处理量 | 依赖于旧评估脚本 | 4668 条 test 任务完成 |

Precision = 1.0 的含义不是模型完美无瑕，而是验证器确保只有真实存在于合同中的引文才能进入评估环节。这意味着 16.2% 的验证失败率中，那些被模型编造出来的引文全部被标记并排除，不会污染指标。

---

## 五、流程展示

以下用示意图展示一个任务经过改造后的完整链路。

```text
任务示例：
  Category: Anti-Assignment
  Question: "Does the contract contain an anti-assignment clause?"
  目标合同: PelicanDeliversInc_Development_Agreement（约 35,000 字符）
```

**Step 1 — 合同分块**

```text
合同全文 35,000 字符
    |
    +-- chunk-0001 (0-4800)     "EXHIBIT 10.3 DEVELOPMENT AGREEMENT..."
    +-- chunk-0002 (4200-9000)  "1. DEFINITIONS. Unless otherwise specified..."
    +-- chunk-0003 (8400-13200) "2. SCOPE OF WORK..."
    |   ...
    +-- chunk-0008 (29400-34200) "12.5 ASSIGNMENT This Agreement will be..."
    |   ...
    +-- chunk-0016（去到最后）
```

**Step 2 — 多源检索**

```text
查询: "Anti-Assignment Does the contract contain an anti-assignment clause?"

SKILL.md 检索 (top-4):       知识检索 (top-6):            合同块检索 (top-10):

Anti-Assignment               KA-0180: "Neither           chunk-0008: "12.5
审查规则说明                    Party may assign            ASSIGNMENT..."
证据提取要求                    this Agreement              chunk-0001: "EXHIBIT
边界条件                       without consent"             10.3..."
                              KA-0351: "Developer          chunk-0007: "11.
                               may assign to               TERM..."
                               successor"                  ...
```

**Step 3 — LLM 推理（基于检索到的上下文）**

```text
输入给 LLM 的内容：
  [检索到的 4 段 SKILL.md 规则]
  [检索到的 6 条知识原子]
  [检索到的 10 个合同块，原文顺序排列，共约 48,000 字符]

LLM 输出：
  {
    "status": "answered",
    "answer": "The contract contains an anti-assignment clause...",
    "evidence": [
      {
        "text": "12.5 ASSIGNMENT This Agreement...neither Party may assign...",
        "span_start": 28873,
        "span_end": 29538,
        "chunk_id": "chunk-0008",
        "contract_id": "PelicanDeliversInc_..."
      }
    ]
  }
```

**Step 4 — 引文验证**

```text
待验证引文:
  "12.5 ASSIGNMENT This Agreement...neither Party may assign..."

合同 chunk-0008 原文片段 (29400-34200):
  "12.5 ASSIGNMENT This Agreement will be binding on and inure to
   the benefit of the Parties...neither Party may assign, delegate..."

查找结果：文本在 chunk-0008 的 28873-29538 范围内连续存在 -> 验证通过
```

**Step 5 — 证据映射（评估阶段）**

```text
验证通过的引文段落:
  "12.5 ASSIGNMENT This Agreement...neither Party may assign without consent"

候选金标准证据单位（同合同 + 同类别）:
  GE-CUAD-002374 -> span (28873-29538) -> IoU = 1.0 -> 匹配
  GE-CUAD-002375 -> span (26000-27500) -> IoU = 0.0, Text F1 = 0.12 -> 不匹配

映射结果: {GE-CUAD-002374}
```

**Step 6 — 指标计算**

```text
pred_ids = {GE-CUAD-002374}
gold_ids = {GE-CUAD-002374}

Precision = 1/1 = 1.0
Recall    = 1/1 = 1.0
F1        = (2 * 1.0 * 1.0) / (1.0 + 1.0) = 1.0
```

而在旧方式下，LLM 不做文本引文提取，而是尝试输出它根本不知道的 `evidence_unit_ids: ["anti-assignment-clause-1"]`。这个字符串不是任何合法的 `GE-CUAD-*` 格式，评估器在 set 比较时命中数为 0，F1 = 0。

---

## 总结

整套改造的核心叙事是：**从让 LLM 猜测不可及的信息，转变为给 LLM 一套阶梯——合同分块降低噪声、多源检索提供精度、引文验证阻断幻觉、证据映射弥合格式鸿沟——每一步承担一个确定性的职责，LLM 只做它最擅长的事：在已经缩小到 1-2 个段落范围内，找出相关的原文引文。**
