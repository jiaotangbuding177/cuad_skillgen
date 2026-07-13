# CUAD-SkillGen 基线方案（修订版 v2）

> 本文档定义 **5 个对比基线 + 1 个目标方法** 的具体落地方案，统一在 **Document-to-Skill** 维度上对比。目标：证明 **基于 Knowledge Atom 的 Skill 编译（evoskill_compiler）** 在证据精确性、治理安全性和可追溯性上优于其他 Document-to-Skill 生成方法。

---

## 1. 基线设计逻辑

### 1.1 要证明什么

| 论点 | 需要的对比 |
|---|---|
| 知识提取比不提取好 | evoskill vs native_prompt / schema_prompt |
| 原子级提取比摘要级好 | evoskill vs summary2skill |
| 原子级编译比工具接口生成好 | evoskill vs document_tool_maker |
| 自动化方法接近人工上界 | evoskill vs human_crafted |
| 结构化约束比自由生成好 | schema_prompt vs native_prompt |

### 1.2 统一维度：Document-to-Skill

所有方法共享同一范式：**输入合同文档 → 输出 SKILL.md + 附属文件**。区别在于中间表示和知识编译深度。

```
效果 ↑
     │                                    ★ human_crafted（上界）
0.80 ┤                              ● evoskill_compiler（目标方法）
     │                        ▲ summary2skill
     │                  ◆ document_tool_maker
0.30 ┤            ■ schema_prompt
     │      □ native_prompt
0.00 ┼──────┬──────┬──────┬──────┬──────→ 知识编译深度
          无     结构化   摘要级   工具接口  原子级
          提取   约束     提取     生成     编译
```

### 1.3 章节顺序

| 章节 | 方法 | 角色 |
|---|---|---|
| §3 | `native_prompt_skill` | Baseline 1：最简基线 |
| §4 | `schema_prompt_skill` | Baseline 2：结构化约束 |
| §5 | `summary2skill` | Baseline 3：摘要级知识提取 |
| §6 | `document_tool_maker` | Baseline 4：工具接口生成 |
| §7 | `human_crafted_skill` | Baseline 5：人工上界 |
| §8 | `evoskill_compiler` | **Target Method：目标方法** |

---

## 2. 公共参数

### 2.1 每个 case 共享的输入

| 输入 | 文件路径 | 格式 | 说明 |
|---|---|---|---|
| 能力包定义 | `cases/{case_id}/case.json` | JSON | `case_id`, `covered_categories`, `capability_requirements` |
| 类别描述 | `corpus/category_descriptions.jsonl` | JSONL（41行） | 每行: `{category, description, answer_format, group}` |
| 训练合同全文 | `corpus/contracts/*.txt` | TXT（306 份） | 每份一份合同 |
| 合同元数据 | `corpus/contract_metadata.jsonl` | JSONL（510行） | 每行: `{contract_id, title, text_length}` |
| 证据单元 | `cases/{case_id}/evidence_units.jsonl` | JSONL | 每行: `{evidence_unit_id, contract_id, category, answer_text, answer_start, answer_end}` |
| 运行时任务 | `cases/{case_id}/tasks.jsonl` | JSONL | 每行: `{task_id, contract_id, category, question, gold_status}` |
| 合同划分 | `splits/splits.json` | JSON | `{train: [...], dev: [...], test: [...]}` |

### 2.2 公共输出结构

```text
results/skillgen/generated/{method}/{case_id}/
  ├── SKILL.md               — Skill 文件（Agent 运行时读取）
  ├── skill_manifest.json    — 生成元数据
  ├── evidence_index.json    — 证据索引
  ├── security_policy.json   — 安全策略
  └── generation_log.json    — 生成日志
```

### 2.3 上下文过量问题

```
306 份训练合同 ≈ 4,200,000 tokens
Claude 200K 窗口 → 最多放 15 份
```

**每个方法必须明确回答**：4.2M tokens 的合同语料，选哪些、怎么选、怎么用？

---

## 3. Baseline 1：`native_prompt_skill`

### 3.1 定位

最简基线。**不提取知识、不结构化**。直接采样少量合同喂给 LLM，让它"凭感觉"写一个 Skill。

### 3.2 输入

| 输入 | 具体内容 | 数量/大小 |
|---|---|---|
| `case.json` | `covered_categories` + `capability_requirements` | ~500 tokens |
| 类别描述 | 该 case 覆盖类别的 `description` + `answer_format` | ~300 tokens |
| 合同全文 | train split 中随机采样 10 份（seed=42，优先有 evidence 的） | ~130,000 tokens |

**总输入 ~tokens：~130,800**

### 3.3 Prompt 构建

```
System Prompt:
  "你是一个合同审查专家。请根据以下合同文档和审查类别，生成一个 SKILL.md 文件，
   描述如何审查该能力包覆盖的合同条款。"

User Prompt:
  === CASE DEFINITION ===
  Case ID: {case_id}
  Covered Categories:
    - {category_1}: {description_1} (Answer Format: {format_1})
    - {category_2}: {description_2} (Answer Format: {format_2})
    ...

  === CONTRACT DOCUMENTS ===
  --- Contract: {contract_id_1} ---
  {合同全文，截断到 13K tokens}
  --- Contract: {contract_id_2} ---
  {合同全文，截断到 13K tokens}
  ...（共 10 份）

  === INSTRUCTION ===
  Please generate a SKILL.md that describes how to review contracts
  for the above categories.
```

### 3.4 LLM 调用

| 调用 | 输入 tokens | 输出 tokens | 次数 |
|---|---|---|---|
| 生成 SKILL.md | ~130,800 | ~3,000 | **1 次 / case** |

**总计：9 次 LLM 调用**

### 3.5 输出

#### `SKILL.md`

```markdown
# {case_id} Review Skill

## Overview
（LLM 自由生成的概述）

## Review Steps
1. ...

## What to Look For
- ...

## Output Format
（LLM 自由决定）
```

> 无固定结构，内容完全由 LLM 生成。

#### `skill_manifest.json`

```json
{
  "method": "native_prompt_skill",
  "case_id": "ip_and_license",
  "model": "claude-sonnet-4-20250514",
  "input_summary": {"contracts_sampled": 10, "total_input_tokens": 130800},
  "usage": {"prompt_tokens": 130800, "completion_tokens": 2800, "total_tokens": 133600},
  "duration_seconds": 15.2
}
```

#### `evidence_index.json` → `{}`

#### `security_policy.json` → `{}`

### 3.6 预测结果

| 指标 | 预测值 | 原因 |
|---|---|---|
| Evidence F1 | 0.10-0.20 | 只能给出模糊指引 |
| Status Accuracy | 0.50-0.60 | 大致区分 answered vs evidence_missing |
| Source-Grounded Rate | 0.20-0.30 | 规则无具体合同依据 |
| Unsupported Rule Rate | 0.30-0.50 | 会编造不存在的模式 |
| External Violation Rate | 0.10-0.20 | 无安全策略约束 |

---

## 4. Baseline 2：`schema_prompt_skill`

### 4.1 定位

在 native_prompt 基础上增加**结构约束**。证明"给 LLM 固定 schema"能否减少幻觉。

### 4.2 输入

与 Baseline 1 相同，**新增 Schema 模板**：

| 输入 | 具体内容 | 数量/大小 |
|---|---|---|
| `case.json` + 类别描述 + 10 份合同 | 同 Baseline 1 | ~130,800 tokens |
| **新增** Schema 模板 | 固定的 SKILL.md section 结构定义 | ~500 tokens |

**总输入 ~tokens：~131,300**

### 4.3 Prompt 构建

System Prompt 中新增强制 section 定义：

```
System Prompt:
  "你是一个合同审查专家。请根据以下合同文档生成 SKILL.md。
   SKILL.md 必须严格包含以下 section（按顺序）：

   ## Covered Categories — 列出所有覆盖的类别及其描述
   ## Review Checklist — 每类别一个检查项
   ## Evidence Extraction Rules — 如何定位证据
   ## Output Format — 固定 JSON schema: {status, answer, evidence_unit_ids, ...}
   ## Boundary Rules — 必须包含以下规则：
     {从 case.json 的 required_behaviors 和 safety_requirements 逐条列出}"

User Prompt:（与 Baseline 1 相同）
```

### 4.4 LLM 调用

| 调用 | 输入 tokens | 输出 tokens | 次数 |
|---|---|---|---|
| 生成 SKILL.md | ~131,300 | ~3,500 | **1 次 / case** |

**总计：9 次 LLM 调用**

### 4.5 输出

#### `SKILL.md`

```markdown
# {case_id} Review Skill

## Covered Categories
- **License Grant**: {description} (Answer Format: {format})
...

## Review Checklist
- [ ] **License Grant**: Check for explicit grant language, scope, exclusivity
...

## Evidence Extraction Rules
1. Search for keywords related to the category
2. Extract the surrounding paragraph as evidence
3. Record exact text and location

## Output Format
{JSON schema}

## Boundary Rules
- Answer only using the target contract
- Do not cite non-target contracts
- Do not fabricate clauses
- Do not provide legal advice
- Return evidence_missing when no clause exists
- Route legal advice to human review
```

#### `evidence_index.json` → `{}`

#### `security_policy.json` → `{}`（约束写在 SKILL.md 的 Boundary Rules 中，不是独立文件）

### 4.6 预测结果

| 指标 | 预测值 | vs native_prompt |
|---|---|---|
| Evidence F1 | 0.15-0.25 | +0.05 |
| Status Accuracy | 0.55-0.65 | +0.05 |
| Source-Grounded Rate | 0.25-0.35 | +0.05 |
| Unsupported Rule Rate | 0.20-0.35 | -0.10 |
| External Violation Rate | 0.05-0.15 | -0.05 |

---

## 5. Baseline 3：`summary2skill`

### 5.1 定位

**摘要级知识提取**。对每份合同生成结构化摘要，合并后生成 Skill。证明"原子级提取"比"摘要级提取"更精确。

### 5.2 输入

#### Step 1：逐份摘要（306 次调用）

| 输入 | 具体内容 | 数量/大小 |
|---|---|---|
| 合同全文（1 份） | `corpus/contracts/{contract_id}.txt` | ~13,000 tokens |
| `case.json` | `covered_categories` 列表 | ~200 tokens |
| 类别描述 | 该 case 覆盖类别的 `description` | ~300 tokens |
| 摘要 Schema | 固定 JSON 输出格式 | ~500 tokens |

**每次输入 ~tokens：~14,000**

#### Step 2：合并摘要（2 次调用）

| 输入 | 具体内容 | 数量/大小 |
|---|---|---|
| 306 个摘要 | 分 2 批送入 | ~150,000 tokens/批 |

#### Step 3：生成 SKILL.md（1 次调用）

| 输入 | 具体内容 | 数量/大小 |
|---|---|---|
| 聚合知识 | Step 2 输出 | ~20,000 tokens |
| `case.json` + Schema | 能力包定义 + SKILL 结构 | ~1,000 tokens |

### 5.3 Step 1 Prompt 构建

```
System Prompt:
  "你是合同审查专家。请从以下合同中提取与 {case_id} 相关的结构化信息。"

User Prompt:
  === CONTRACT ===
  Contract ID: {contract_id}
  {合同全文}

  === CATEGORIES TO EXTRACT ===
  {category_1}: {description_1}
  {category_2}: {description_2}
  ...

  === OUTPUT SCHEMA ===
  {
    "contract_id": "...",
    "extractions": [
      {
        "category": "...",
        "found": true/false,
        "summary": "一句话摘要",
        "key_terms": ["term1", "term2"],
        "source_paragraph": "原文段落（直接引用）"
      }
    ]
  }
```

### 5.4 LLM 调用

| 调用 | 输入 tokens | 输出 tokens | 次数 |
|---|---|---|---|
| Step 1: 逐份摘要 | ~14,000 | ~1,000 | **306 次 / case** |
| Step 2: 合并 | ~150,000 × 2 | ~10,000 | **2 次 / case** |
| Step 3: 生成 SKILL | ~21,000 | ~4,000 | **1 次 / case** |

**总计：(306 + 2 + 1) × 9 = 2,781 次 LLM 调用**

### 5.5 输出

#### `SKILL.md`

```markdown
# {case_id} Review Skill

## Covered Categories
- **License Grant**: Found in 80% of contracts. Typical pattern: ...
...

## Common Patterns
### License Grant
- Pattern A: "Licensor hereby grants Licensee a {type} license to..." (60%)
- Pattern B: "Subject to the terms, the right to use..." (25%)
...

## Review Checklist / Output Format / Boundary Rules
...
```

#### `evidence_index.json`

```json
{
  "License Grant": {
    "found_in_contracts": 245,
    "total_contracts": 306,
    "source_paragraphs": [
      {"contract_id": "...", "paragraph_snippet": "..."}
    ]
  }
}
```

> 溯源精度为**合同级**（知道来自哪份合同），**不是 span 级**。

#### `security_policy.json` → `{}`

### 5.6 预测结果

| 指标 | 预测值 |
|---|---|
| Evidence F1 | 0.30-0.45 |
| Status Accuracy | 0.65-0.75 |
| Source-Grounded Rate | 0.55-0.70 |
| Unsupported Rule Rate | 0.08-0.15 |
| External Violation Rate | 0.05-0.10 |

---

## 6. Baseline 4：`document_tool_maker`

### 6.1 定位

**Document-to-Tool 生成基线**。不显式构建 Knowledge Atoms，而是让 LLM 从合同语料中归纳出一组 **callable tools/functions**，并生成对应的 SKILL.md 和 tool 定义。该方法代表"把文档转为工具接口"的前沿思路（类似 Toolformer / ART / Gorilla 等工作的文档适配版），用于检验**仅生成工具接口是否足以获得企业级证据追溯和治理能力**。

### 6.2 与 evoskill_compiler 的关键差异

| 维度 | `document_tool_maker` | `evoskill_compiler` |
|---|---|---|
| 中间表示 | tool/function specs | Knowledge Atoms |
| 知识粒度 | capability/tool 级 | atom/span 级 |
| 证据索引 | 可选、弱结构（tool 示例级） | 必选、span-level |
| 安全策略 | 写在 tool description 中 | 独立 `security_policy.json` |
| 可审计性 | tool 调用可审计 | tool + evidence + rule 全链路可审计 |
| 运行时行为 | Agent 选择 tool → 传入参数 → 获取结果 | Agent 按 Skill 规则 → 查 evidence_index → 输出 |

### 6.3 输入

#### Step 1：逐份归纳 tool specs（306 次调用）

| 输入 | 具体内容 | 数量/大小 |
|---|---|---|
| 合同全文（1 份） | `corpus/contracts/{contract_id}.txt` | ~13,000 tokens |
| `case.json` | `covered_categories` 列表 | ~200 tokens |
| 类别描述 | 该 case 覆盖类别的 `description` | ~300 tokens |
| Tool Schema | function/tool 的输出格式定义 | ~600 tokens |

**每次输入 ~tokens：~14,100**

#### Step 2：合并去重 tool specs（1 次调用）

| 输入 | 具体内容 | 数量/大小 |
|---|---|---|
| 306 份 tool specs | 所有合同的 tool 定义集合 | ~100,000 tokens |

#### Step 3：生成 SKILL.md + tool_manifest.json（1 次调用）

| 输入 | 具体内容 | 数量/大小 |
|---|---|---|
| 合并后的 tool 集合 | Step 2 输出 | ~30,000 tokens |
| `case.json` + Schema | 能力包定义 + SKILL 结构 | ~1,000 tokens |

### 6.4 Step 1 Prompt 构建

```
System Prompt:
  "你是一个合同审查工具设计师。请从以下合同中提取可复用的审查工具（tools）。
   每个 tool 是一个 callable function，有明确的输入参数、输出格式和功能描述。"

User Prompt:
  === CONTRACT ===
  Contract ID: {contract_id}
  {合同全文}

  === CATEGORIES ===
  {category_1}: {description_1}
  {category_2}: {description_2}
  ...

  === TOOL SCHEMA ===
  [
    {
      "tool_id": "tool_{seq:03d}",
      "name": "check_{category_snake_case}",
      "description": "一句话描述该工具做什么",
      "category": "覆盖的审查类别",
      "parameters": {
        "contract_text": "string — 合同全文或相关段落",
        "target_clause": "string (optional) — 待审查的具体条款"
      },
      "returns": {
        "found": "boolean",
        "extracted_text": "string — 找到的原文片段",
        "confidence": "float 0-1",
        "explanation": "string — 审查结论"
      },
      "example": {
        "input": "示例输入",
        "output": {"found": true, "extracted_text": "...", "confidence": 0.9, "explanation": "..."}
      }
    }
  ]

  === RULES ===
  1. 每个 tool 对应一个审查类别或子能力
  2. example 必须来自当前合同的真实内容
  3. description 必须清晰说明工具的功能和限制
```

### 6.5 LLM 调用

| 调用 | 输入 tokens | 输出 tokens | 次数 |
|---|---|---|---|
| Step 1: 逐份归纳 tool | ~14,100 | ~2,000 | **306 次 / case** |
| Step 2: 合并去重 | ~100,000 | ~15,000 | **1 次 / case** |
| Step 3: 生成 SKILL + manifest | ~31,000 | ~5,000 | **1 次 / case** |

**总计：(306 + 1 + 1) × 9 = 2,772 次 LLM 调用**

### 6.6 输出

#### `SKILL.md`

```markdown
# {case_id} Review Skill (Tool-Based)

## Overview
This skill provides a set of callable review tools for {case_id}.
Use the tools below to analyze contract clauses.

## Available Tools

### tool_001: check_license_grant
- **Category**: License Grant
- **Description**: Checks whether the contract contains a license grant clause
- **Parameters**: contract_text (string), target_clause (string, optional)
- **Returns**: {found, extracted_text, confidence, explanation}
- **Usage**: Call with the full contract text. Returns the license grant clause if found.

### tool_002: check_non_transferable
- **Category**: Non-Transferable License
- **Description**: Checks whether the license is non-transferable
...

## Review Workflow
1. Identify the task category from the question
2. Select the corresponding tool
3. Call the tool with the target contract text
4. Format the tool output into the required response format

## Output Format
{JSON schema}

## Boundary Rules
{从 case.json 提取，写在 tool description 中}
```

#### `tool_manifest.json`（`document_tool_maker` 特有）

```json
{
  "method": "document_tool_maker",
  "case_id": "ip_and_license",
  "total_tools": 24,
  "tools": [
    {
      "tool_id": "tool_001",
      "name": "check_license_grant",
      "category": "License Grant",
      "description": "Checks whether the contract contains a license grant clause",
      "source_contracts": ["contract_id_1", "contract_id_2", "..."],
      "example": {
        "input": {"contract_text": "Licensor grants to Licensee..."},
        "output": {"found": true, "extracted_text": "...", "confidence": 0.95}
      }
    },
    ...
  ]
}
```

#### `evidence_index.json`

```json
{
  "tool_001": {
    "example_sources": [
      {"contract_id": "...", "snippet": "..."}
    ]
  }
}
```

> 溯源精度为 **tool 示例级**（知道工具的 example 来自哪些合同），**不是 span 级**。

#### `security_policy.json`

```json
{}
```

> 安全约束写在 SKILL.md 的 Boundary Rules 和每个 tool 的 description 中，不是独立结构化文件。

### 6.7 预测结果

| 指标 | 预测值 | 原因 |
|---|---|---|
| Evidence F1 | 0.25-0.40 | tool 的 example 有溯源，但运行时不精确匹配 span |
| Status Accuracy | 0.60-0.70 | tool 输出有 confidence 字段，但无结构化规则约束 |
| Source-Grounded Rate | 0.40-0.55 | tool example 来自真实合同，但运行时回答可能漂移 |
| Unsupported Rule Rate | 0.15-0.25 | 无独立安全策略，依赖 tool description 中的约束 |
| External Violation Rate | 0.08-0.15 | tool 接口不天然阻止外发行为 |

### 6.8 与 evoskill_compiler 的关键差距预测

| 维度 | document_tool_maker | evoskill_compiler | 差距来源 |
|---|---|---|---|
| Evidence F1 | 0.25-0.40 | 0.50-0.70 | KA 有精确 span，tool example 只有示例 |
| Source-Grounded | 0.40-0.55 | 0.70-0.85 | KA 每条可追溯，tool 溯源弱 |
| External Violation | 0.08-0.15 | 0.02-0.05 | security_policy 可机器验证，tool description 不能 |

---

## 7. Baseline 5：`human_crafted_skill`（上界参考）

### 7.1 定位

人工编写的 Skill，代表**理论上能达到的最高质量**。

### 7.2 输入

| 输入 | 具体内容 | 数量/大小 |
|---|---|---|
| 训练合同 | 人工阅读 ~50 份（有 evidence 的优先） | ~650,000 tokens/人/case |
| `case.json` + `evidence_units.jsonl` + 类别描述 | 参考 | — |
| 人工时间 | ~12.5 小时/case × 9 cases | **~112.5 小时** |

### 7.3 人工编写流程

```
Step 1: 人工阅读 ~50 份合同，标记关键条款
Step 2: 人工编写 SKILL.md（审查流程 + 边界规则 + 输出格式）
Step 3: 人工编写 evidence_index.json（精确标注 span）
Step 4: 人工编写 security_policy.json（安全策略）
Step 5: 人工标注 10 个 dev 任务作为示例
```

### 7.4 LLM 调用

**0 次**（纯人工）

### 7.5 输出

与 evoskill_compiler 输出**格式完全相同**：

| 文件 | 内容 |
|---|---|
| `SKILL.md` | 人工精心编写，引用精确 evidence |
| `skill_manifest.json` | 人工填写 |
| `evidence_index.json` | 人工精选的 span 级证据 |
| `security_policy.json` | 人工编写的安全策略 |

### 7.6 预测结果

| 指标 | 预测值 | vs evoskill |
|---|---|---|
| Evidence F1 | 0.60-0.80 | +0.10 |
| Status Accuracy | 0.80-0.90 | +0.05 |
| Source-Grounded Rate | 0.80-0.95 | +0.10 |
| Unsupported Rule Rate | 0.02-0.05 | -0.03 |
| External Violation Rate | 0.01-0.03 | -0.01 |

---

## 8. Target Method：`evoskill_compiler`

### 8.1 定位

**原子级知识提取 + 安全策略编译**。核心目标方法。

### 8.2 输入

#### Step 1：逐份提取 Knowledge Atoms（306 次调用）

| 输入 | 具体内容 | 数量/大小 |
|---|---|---|
| 合同全文（1 份） | `corpus/contracts/{contract_id}.txt` | ~13,000 tokens |
| `case.json` | `covered_categories` + `capability_requirements` | ~500 tokens |
| 类别描述 | `description` + `answer_format` | ~300 tokens |
| KA Schema | Knowledge Atom 输出格式 | ~400 tokens |

**每次输入 ~tokens：~14,200**

#### Step 2：构建 evidence_index.json（确定性，无 LLM）

| 输入 | 具体内容 | 数量 |
|---|---|---|
| Step 1 所有 KA | 306 份合同的 KA 集合 | ~1,500 条 KA/case |

#### Step 3：构建 security_policy.json（确定性，无 LLM）

| 输入 | 具体内容 |
|---|---|
| `case.json` | `required_behaviors` + `safety_requirements` |

#### Step 4：生成 SKILL.md（1 次调用）

| 输入 | 具体内容 | 数量/大小 |
|---|---|---|
| evidence_index（top-200 KA） | 按 category 组织的 KA 集合 | ~50,000 tokens |
| security_policy.json | 安全策略 | ~500 tokens |
| `case.json` + Schema | 能力包定义 + SKILL 结构 | ~1,000 tokens |

**输入 ~tokens：~51,500**

#### Step 5：编译优化（1 次调用，可选）

| 输入 | 具体内容 | 数量/大小 |
|---|---|---|
| 草稿 SKILL.md | Step 4 输出 | ~4,000 tokens |
| evidence_index 摘要 | KA 统计 | ~2,000 tokens |
| 审计 checklist | 去冗 + 一致性 + 安全检查 | ~500 tokens |

### 8.3 Step 1 Prompt 构建

```
System Prompt:
  "你是一个合同审查专家。请从以下合同中提取 Knowledge Atoms（知识原子）。
   每个 Knowledge Atom 是一个独立的事实单元，必须包含精确的原文引用。"

User Prompt:
  === CONTRACT ===
  Contract ID: {contract_id}
  {合同全文}

  === CATEGORIES TO EXTRACT ===
  {category_1}: {description_1} (Answer Format: {format_1})
  {category_2}: {description_2} (Answer Format: {format_2})
  ...

  === KNOWLEDGE ATOM SCHEMA ===
  [
    {
      "ka_id": "KA-{seq:04d}",
      "category": "必须匹配上述类别之一",
      "text": "从合同中直接引用的原文片段（不可改写）",
      "span_start": 原文起始字符偏移（整数）,
      "span_end": 原文结束字符偏移（整数）,
      "interpretation": "对这段原文的审查解读（一句话）",
      "confidence": 0.0-1.0
    }
  ]

  === RULES ===
  1. text 必须是合同原文的直接引用，不可改写或总结
  2. span_start 和 span_end 必须精确对应 text 在合同中的位置
  3. 每个 category 提取所有相关原子（可能 0 个或多个）
  4. 如果合同中完全没有某类别的内容，不要编造
```

### 8.4 Step 4 Prompt 构建

```
System Prompt:
  "请根据以下 Knowledge Atom 证据索引，生成 SKILL.md。
   Skill 中的每条规则必须引用具体的 KA ID 作为依据。"

User Prompt:
  === EVIDENCE INDEX (top-200 KAs by category) ===
  ## License Grant (45 KAs)
  KA-0001: "Licensor grants to Licensee a non-exclusive license..."
    → Source: {contract_id}, span [18234-18412]
    → Interpretation: Standard non-exclusive license grant
  ...

  === SECURITY POLICY ===
  Required Behaviors:
    - answer only using the target contract
    - cite source-grounded evidence
    - return evidence_missing when no clause exists
    ...
  Safety Requirements:
    - do not cite non-target contracts
    - do not fabricate clauses
    ...

  === SKILL.md STRUCTURE ===
  ## Covered Categories
  ## Evidence-Based Review Rules（每条规则引用 KA ID）
  ## Review Checklist
  ## Output Format
  ## Boundary Rules（引用 security policy）
```

### 8.5 LLM 调用

| 调用 | 输入 tokens | 输出 tokens | 次数 |
|---|---|---|---|
| Step 1: 逐份提取 KA | ~14,200 | ~2,000 | **306 次 / case** |
| Step 2-3: 构建索引+策略 | — | — | **0（确定性）** |
| Step 4: 生成 SKILL | ~51,500 | ~4,000 | **1 次 / case** |
| Step 5: 编译优化 | ~6,500 | ~3,500 | **1 次 / case** |

**总计：(306 + 1 + 1) × 9 = 2,772 次 LLM 调用**

### 8.6 输出

#### `SKILL.md`

```markdown
# {case_id} Review Skill

## Covered Categories
- **License Grant**: 45 evidence atoms from training corpus
- **Non-Transferable License**: 23 evidence atoms
...

## Evidence-Based Review Rules

### Rule 1: Identify License Grant Clauses
Look for explicit grant language. Common patterns:
- "Licensor hereby grants Licensee a {type} license to..." [KA-0001, KA-0003, KA-0007]
- "Subject to the terms, the right to use..." [KA-0012, KA-0015]

### Rule 2: Check Transfer Restrictions
- "Licensee shall not transfer, assign, or sublicense..." [KA-0101, KA-0105]
...

## Review Checklist
- [ ] Scan for category keywords (see rules above)
- [ ] Extract matching paragraphs with exact span positions
- [ ] Map extracted text to the most matching category
- [ ] If no match, return evidence_missing

## Output Format
{JSON schema with evidence_unit_ids referencing KA IDs}

## Boundary Rules
- Only use evidence from target contract [SR-001]
- Never fabricate clause text [SR-002]
- Route legal judgment to human review [RB-006]
- Return unsupported_scope for non-covered categories [RB-005]
```

#### `skill_manifest.json`

```json
{
  "method": "evoskill_compiler",
  "case_id": "ip_and_license",
  "model": "claude-sonnet-4-20250514",
  "pipeline": {
    "step1_extract": {
      "contracts_processed": 306,
      "total_kas_extracted": 1523,
      "avg_kas_per_contract": 5.0,
      "kas_by_category": {"License Grant": 450, "...": "..."}
    },
    "step2_index": {"total_kas_in_index": 1523},
    "step3_security": {"required_behaviors_count": 6, "safety_requirements_count": 4},
    "step4_generate": {"kas_used_in_skill": 200, "skill_md_tokens": 4000},
    "step5_compile": {"redundancy_removed": 12, "consistency_fixes": 3, "security_audit_passed": true}
  },
  "usage": {"total_tokens": 5220000},
  "duration_seconds": 2100.0
}
```

#### `evidence_index.json`

```json
{
  "License Grant": [
    {
      "ka_id": "KA-0001",
      "category": "License Grant",
      "text": "Licensor grants to Licensee a non-exclusive, non-transferable license...",
      "source_contract_id": "LIMEENERGYCO_09_09_1999-EX-10-DISTRIBUTOR_AGREEMENT",
      "span_start": 18234,
      "span_end": 18412,
      "interpretation": "Standard non-exclusive license grant",
      "confidence": 0.95
    }
  ]
}
```

> **关键**：溯源精度为 **span 级**（精确到 contract_id + span_start + span_end）。

#### `security_policy.json`

```json
{
  "allowed_status": ["answered", "evidence_missing", "missing_input", "unsupported_scope", "needs_human_review"],
  "required_behaviors": [
    {"rule_id": "RB-001", "text": "answer only using the target contract", "enforcement": "hard"},
    {"rule_id": "RB-002", "text": "cite source-grounded evidence", "enforcement": "hard"},
    {"rule_id": "RB-003", "text": "return evidence_missing when no clause exists", "enforcement": "hard"},
    {"rule_id": "RB-004", "text": "return missing_input when contract_id or category is absent", "enforcement": "hard"},
    {"rule_id": "RB-005", "text": "return unsupported_scope when outside covered_categories", "enforcement": "hard"},
    {"rule_id": "RB-006", "text": "route legal advice to human review", "enforcement": "hard"}
  ],
  "safety_requirements": [
    {"rule_id": "SR-001", "text": "do not cite non-target contracts", "enforcement": "hard", "check": "verify source_contract_ids == [target_contract_id]"},
    {"rule_id": "SR-002", "text": "do not fabricate clauses", "enforcement": "hard", "check": "verify evidence spans exist in target contract"},
    {"rule_id": "SR-003", "text": "do not provide legal advice", "enforcement": "hard", "check": "detect legal judgment language"},
    {"rule_id": "SR-004", "text": "do not generate externally sendable legal opinions", "enforcement": "hard", "check": "detect formal document patterns"}
  ]
}
```

> **关键创新**：每条规则有 `enforcement` 级别和 `check` 方法，可运行时机器验证。

### 8.7 预测结果

| 指标 | 预测值 | vs document_tool_maker |
|---|---|---|
| Evidence F1 | 0.50-0.70 | +0.25 |
| Status Accuracy | 0.75-0.85 | +0.15 |
| Source-Grounded Rate | 0.70-0.85 | +0.30 |
| Unsupported Rule Rate | 0.05-0.10 | -0.10 |
| External Violation Rate | 0.02-0.05 | -0.08 |

---

## 9. 汇总对比

### 9.1 输入输出对比

| 方法 | 输入数据量 | LLM 调用/case | evidence_index | security_policy |
|---|---|---:|---|---|
| `native_prompt_skill` | 10 份合同 ~131K tokens | **1** | `{}` 空 | `{}` 空 |
| `schema_prompt_skill` | 10 份合同 ~131K tokens | **1** | `{}` 空 | 文本约束（写在 SKILL.md 中） |
| `summary2skill` | 306 份合同逐份摘要 | **308** | 合同/摘要级 | `{}` 空 |
| `document_tool_maker` | 306 份合同逐份归纳 tool | **308** | tool/example 级 | 工具描述级（非结构化） |
| `human_crafted_skill` | ~50 份合同（人工阅读） | **0** | span 级 | 人工结构化 |
| **`evoskill_compiler`** | 306 份合同逐份抽取 KA | **308** | **span/KA 级** | **结构化 + 机器可验证** |

### 9.2 核心维度对比

| 方法 | 中间表示 | 知识粒度 | 溯源精度 | 安全策略 | 数据覆盖 |
|---|---|---|---|---|---|
| `native_prompt` | 无 | 无 | 无 | 无 | 3% |
| `schema_prompt` | 无 | 无 | 无 | 文本约束 | 3% |
| `summary2skill` | 结构化摘要 | 字段级 | 合同级 | 无 | 100% |
| `document_tool_maker` | tool/function specs | tool 级 | tool 示例级 | 工具描述级 | 100% |
| **`evoskill`** | **Knowledge Atoms** | **atom 级** | **span 级** | **机器可验证** | **100%** |
| `human_crafted` | Knowledge Atoms | atom 级 | span 级 | 结构化 | ~16% |

### 9.3 预测效果排名

| 排名 | 方法 | Evidence F1 | Status Acc | Source-Grounded | External Violation |
|---:|---|---|---|---|---|
| 1 | `human_crafted` | 0.60-0.80 | 0.80-0.90 | 0.80-0.95 | 0.01-0.03 |
| 2 | **`evoskill_compiler`** | **0.50-0.70** | **0.75-0.85** | **0.70-0.85** | **0.02-0.05** |
| 3 | `summary2skill` | 0.30-0.45 | 0.65-0.75 | 0.55-0.70 | 0.05-0.10 |
| 4 | `document_tool_maker` | 0.25-0.40 | 0.60-0.70 | 0.40-0.55 | 0.08-0.15 |
| 5 | `schema_prompt` | 0.15-0.25 | 0.55-0.65 | 0.25-0.35 | 0.05-0.15 |
| 6 | `native_prompt` | 0.10-0.20 | 0.50-0.60 | 0.20-0.30 | 0.10-0.20 |

### 9.4 论文中重点展示的对比

| 对比 | 证明什么 | 关键差距 |
|---|---|---|
| `evoskill` vs `native_prompt` | 直接提示生成 Skill 不足以形成稳定企业能力 | Evidence F1 +0.40~0.50 |
| `evoskill` vs `schema_prompt` | 固定 schema 不能替代知识编译 | Evidence F1 +0.35 |
| `evoskill` vs `summary2skill` | atom-level 证据组织优于 summary-level 归纳 | Evidence F1 +0.20~0.25 |
| **`evoskill` vs `document_tool_maker`** | **仅生成 callable tools 不足以获得强证据追溯和治理能力** | **Evidence F1 +0.25, External Violation -0.08** |
| `evoskill` vs `human_crafted` | 自动编译 Skill 接近人工上界 | 差距 < 0.10 |
| `evoskill` 治理任务 | security_policy 在边界测试中的效果 | External Violation Rate 最低 |

---

## 10. 实施路线图

### Phase 1：基础设施（Week 1）

- [ ] 编写统一的 Skill 生成框架
- [ ] 实现运行时 Agent 容器
- [ ] 实现统一评估器

### Phase 2：基线实现（Week 2-3）

| 顺序 | 方法 | 角色 | 预计工时 | LLM 调用总计 |
|---|---|---|---|---|
| 1 | `native_prompt_skill` | Baseline 1 | 2h | 9 |
| 2 | `schema_prompt_skill` | Baseline 2 | 3h | 9 |
| 3 | `summary2skill` | Baseline 3 | 12h | 2,781 |
| 4 | `document_tool_maker` | Baseline 4 | 14h | 2,772 |
| 5 | `evoskill_compiler` | **Target** | 16h | 2,772 |
| 6 | `human_crafted_skill` | Baseline 5（上界） | 并行，112.5h 人工 | 0 |

### Phase 3：运行评估（Week 4）

- [ ] 每个方法 × 9 个 case 生成 Skill
- [ ] 21,396 个 task 在 Agent 容器中运行
- [ ] 计算所有指标

### Phase 4：论文撰写（Week 5-6）

- [ ] 结果表 + 消融图
- [ ] 治理任务专项分析
- [ ] Case study

---

## 11. 风险与缓解

| 风险 | 影响 | 缓解措施 |
|---|---|---|
| evoskill 效果不如预期 | 核心论点不成立 | dev split 提前验证 |
| summary2skill 效果接近 evoskill | 无法证明原子级优势 | 增加 span 级评估 |
| document_tool_maker 效果接近 evoskill | 无法证明 KA vs tool 的差异 | 重点比较 evidence 溯源精度和 security 审计能力 |
| human_crafted 质量不稳定 | 上界不可靠 | 2 人独立编写 |
| 治理任务区分度不够 | 所有方法得分相近 | 增加困难样本 |
| LLM 调用成本过高 | 预算超支 | 便宜模型做提取，贵模型只用于最终生成 |
