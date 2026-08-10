# CUAD-SkillGen 实验数据报告

## 1. 实验配置

| 配置项 | 取值 |
|---|---|
| 运行时协议 | package-aware-v1 |
| 运行时模型 | ecnu-plus |
| 评测分割 | test |
| 合同检索 | BM25 top-10 chunks |
| Skill知识检索 | BM25 top-6 items |
| 治理任务 | Included |
| 总任务数 | 4668 |

## 2. 方法说明

| 方法 | 说明 |
|---|---|
| native_prompt_skill | 直接 prompt 生成自由格式 SKILL.md，无结构化索引 |
| schema_prompt_skill | 结构化 prompt，固定章节，无实际数据索引 |
| summary2skill | 逐合同摘要，段落级原文索引 |
| document_tool_maker | 工具接口描述，函数级示例索引 |
| evoskill_compiler (v1) | Knowledge Atom + Evidence-Based Review Rules (规则驱动) |
| evoskill_compiler_v4 | Knowledge Atom + Common Clause Patterns & Example Phrasing (模式驱动) |

## 3. 主指标总表

### Task Success Rate

| 方法 | Value | 排名 |
|---|---|---|
| EvoSkill v4 [NEW] | 0.6952 | 1 |
| EvoSkill v1 | 0.6435 | 2 |
| Summary2Skill | 0.6407 | 3 |
| DocToolMaker | 0.6345 | 4 |
| Schema Prompt | 0.6298 | 5 |
| Native Prompt | 0.4994 | 6 |

### Status Macro-F1

| 方法 | Value | 排名 |
|---|---|---|
| EvoSkill v4 [NEW] | 0.8714 | 1 |
| EvoSkill v1 | 0.8477 | 2 |
| Schema Prompt | 0.8380 | 3 |
| Summary2Skill | 0.7696 | 4 |
| DocToolMaker | 0.7451 | 5 |
| Native Prompt | 0.5824 | 6 |

### Status Balanced Accuracy

| 方法 | Value | 排名 |
|---|---|---|
| EvoSkill v4 [NEW] | 0.8773 | 1 |
| EvoSkill v1 | 0.8626 | 2 |
| Schema Prompt | 0.8475 | 3 |
| Summary2Skill | 0.7937 | 4 |
| DocToolMaker | 0.7714 | 5 |
| Native Prompt | 0.6712 | 6 |

### Status Accuracy

| 方法 | Value | 排名 |
|---|---|---|
| EvoSkill v4 [NEW] | 0.8083 | 1 |
| Summary2Skill | 0.7569 | 2 |
| EvoSkill v1 | 0.7562 | 3 |
| DocToolMaker | 0.7412 | 4 |
| Schema Prompt | 0.7279 | 5 |
| Native Prompt | 0.6041 | 6 |

### Evidence Precision

| 方法 | Value | 排名 |
|---|---|---|
| Schema Prompt | 0.5101 | 1 |
| Native Prompt | 0.4852 | 2 |
| DocToolMaker | 0.4710 | 3 |
| EvoSkill v4 [NEW] | 0.4473 | 4 |
| EvoSkill v1 | 0.4467 | 5 |
| Summary2Skill | 0.4450 | 6 |

### Evidence Recall

| 方法 | Value | 排名 |
|---|---|---|
| Schema Prompt | 0.4900 | 1 |
| Native Prompt | 0.4818 | 2 |
| DocToolMaker | 0.4682 | 3 |
| Summary2Skill | 0.4643 | 4 |
| EvoSkill v1 | 0.4623 | 5 |
| EvoSkill v4 [NEW] | 0.4608 | 6 |

### Strict Evidence F1

| 方法 | Value | 排名 |
|---|---|---|
| Schema Prompt | 0.4772 | 1 |
| Native Prompt | 0.4611 | 2 |
| DocToolMaker | 0.4485 | 3 |
| Summary2Skill | 0.4329 | 4 |
| EvoSkill v1 | 0.4315 | 5 |
| EvoSkill v4 [NEW] | 0.4310 | 6 |

### Containment Evidence F1

| 方法 | Value | 排名 |
|---|---|---|
| Summary2Skill | 0.6638 | 1 |
| EvoSkill v4 [NEW] | 0.6536 | 2 |
| Schema Prompt | 0.6508 | 3 |
| Native Prompt | 0.6455 | 4 |
| DocToolMaker | 0.6447 | 5 |
| EvoSkill v1 | 0.6348 | 6 |

### Governance Boundary

| 方法 | Value | 排名 |
|---|---|---|
| EvoSkill v1 | 0.8916 | 1 |
| EvoSkill v4 [NEW] | 0.8863 | 2 |
| Schema Prompt | 0.8810 | 3 |
| Summary2Skill | 0.7328 | 4 |
| DocToolMaker | 0.6984 | 5 |
| Native Prompt | 0.5714 | 6 |

### Boundary Correct

| 方法 | Value | 排名 |
|---|---|---|
| EvoSkill v4 [NEW] | 0.7662 | 1 |
| EvoSkill v1 | 0.6905 | 2 |
| Summary2Skill | 0.6880 | 3 |
| DocToolMaker | 0.6749 | 4 |
| Schema Prompt | 0.6551 | 5 |
| Native Prompt | 0.4728 | 6 |

### Human Review Routing

| 方法 | Value | 排名 |
|---|---|---|
| EvoSkill v1 | 0.7469 | 1 |
| EvoSkill v4 [NEW] | 0.7346 | 2 |
| Schema Prompt | 0.7222 | 3 |
| Summary2Skill | 0.3765 | 4 |
| DocToolMaker | 0.2963 | 5 |
| Native Prompt | 0.0000 | 6 |

### External Violation Rate

| 方法 | Value | 排名 |
|---|---|---|
| Native Prompt | 1.0000 | 1 |
| DocToolMaker | 0.7037 | 2 |
| Summary2Skill | 0.6235 | 3 |
| Schema Prompt | 0.2778 | 4 |
| EvoSkill v4 [NEW] | 0.2654 | 5 |
| EvoSkill v1 | 0.2531 | 6 |

### Validation Failure Rate

| 方法 | Value | 排名 |
|---|---|---|
| Native Prompt | 0.2573 | 1 |
| Schema Prompt | 0.2269 | 2 |
| EvoSkill v1 | 0.1300 | 3 |
| EvoSkill v4 [NEW] | 0.1290 | 4 |
| DocToolMaker | 0.1232 | 5 |
| Summary2Skill | 0.1221 | 6 |

## 4. 分 Case 指标

### Task Success Rate

| Case | Native Prompt | Schema Prompt | Summary2Skill | DocToolMaker | EvoSkill v1 | EvoSkill v4 |
|---|---|---|---|---|---|---|
| contract_basic_info | 0.3723 | 0.3865 | 0.3209 | 0.3777 | 0.3599 | 0.3652 |
| term_and_termination | 0.6222 | 0.6583 | 0.5639 | 0.6000 | 0.6139 | 0.6639 |
| legal_governance | 0.7139 | 0.8806 | 0.8694 | 0.8694 | 0.8694 | 0.8694 |
| ip_and_license | 0.2943 | 0.5793 | 0.7184 | 0.6264 | 0.5322 | 0.7552 |
| competition_restrictions | 0.6250 | 0.7422 | 0.7591 | 0.7760 | 0.7747 | 0.7839 |
| liability_and_indemnity | 0.6126 | 0.7468 | 0.5693 | 0.5996 | 0.6645 | 0.6991 |
| assignment_and_control | 0.5620 | 0.6357 | 0.5969 | 0.6589 | 0.6860 | 0.6589 |
| revenue_and_commercial_terms | 0.4221 | 0.5022 | 0.6320 | 0.6082 | 0.7208 | 0.7359 |
| operational_rights | 0.4982 | 0.6259 | 0.6684 | 0.6223 | 0.6950 | 0.7004 |

### Status Macro-F1

| Case | Native Prompt | Schema Prompt | Summary2Skill | DocToolMaker | EvoSkill v1 | EvoSkill v4 |
|---|---|---|---|---|---|---|
| contract_basic_info | 0.5974 | 0.8233 | 0.7562 | 0.7595 | 0.8406 | 0.8311 |
| term_and_termination | 0.6211 | 0.8283 | 0.7439 | 0.6116 | 0.7929 | 0.8422 |
| legal_governance | 0.6559 | 0.9247 | 0.9335 | 0.8671 | 0.9335 | 0.9345 |
| ip_and_license | 0.4632 | 0.7981 | 0.7617 | 0.6032 | 0.7678 | 0.8525 |
| competition_restrictions | 0.5870 | 0.8334 | 0.6377 | 0.7865 | 0.8562 | 0.8556 |
| liability_and_indemnity | 0.6192 | 0.8466 | 0.7110 | 0.7514 | 0.8198 | 0.8293 |
| assignment_and_control | 0.6232 | 0.8356 | 0.7743 | 0.7889 | 0.8780 | 0.8537 |
| revenue_and_commercial_terms | 0.5254 | 0.7508 | 0.6082 | 0.7358 | 0.8183 | 0.8461 |
| operational_rights | 0.5369 | 0.7950 | 0.7480 | 0.5915 | 0.8251 | 0.8311 |

### Strict Evidence F1

| Case | Native Prompt | Schema Prompt | Summary2Skill | DocToolMaker | EvoSkill v1 | EvoSkill v4 |
|---|---|---|---|---|---|---|
| contract_basic_info | 0.3252 | 0.3085 | 0.2464 | 0.2942 | 0.2639 | 0.2704 |
| term_and_termination | 0.7547 | 0.7853 | 0.6429 | 0.7640 | 0.7147 | 0.7173 |
| legal_governance | 0.7158 | 0.7613 | 0.7176 | 0.7245 | 0.7162 | 0.6935 |
| ip_and_license | 0.4626 | 0.5016 | 0.5216 | 0.4425 | 0.4783 | 0.4900 |
| competition_restrictions | 0.3874 | 0.4644 | 0.4412 | 0.4322 | 0.4021 | 0.4139 |
| liability_and_indemnity | 0.5094 | 0.4851 | 0.5093 | 0.4776 | 0.4547 | 0.4519 |
| assignment_and_control | 0.4653 | 0.5227 | 0.4559 | 0.4939 | 0.4773 | 0.4561 |
| revenue_and_commercial_terms | 0.3154 | 0.3168 | 0.3169 | 0.3159 | 0.2767 | 0.3044 |
| operational_rights | 0.4821 | 0.4981 | 0.4354 | 0.4014 | 0.4371 | 0.4005 |

### Containment Evidence F1

| Case | Native Prompt | Schema Prompt | Summary2Skill | DocToolMaker | EvoSkill v1 | EvoSkill v4 |
|---|---|---|---|---|---|---|
| contract_basic_info | 0.7125 | 0.6980 | 0.7115 | 0.6794 | 0.6610 | 0.6825 |
| term_and_termination | 0.8040 | 0.8240 | 0.8147 | 0.8320 | 0.8360 | 0.8440 |
| legal_governance | 0.8040 | 0.8039 | 0.8202 | 0.8043 | 0.8144 | 0.8098 |
| ip_and_license | 0.4923 | 0.5561 | 0.5733 | 0.5535 | 0.5430 | 0.5717 |
| competition_restrictions | 0.5196 | 0.5490 | 0.5631 | 0.5472 | 0.5394 | 0.5618 |
| liability_and_indemnity | 0.5889 | 0.5889 | 0.6394 | 0.5983 | 0.5733 | 0.5918 |
| assignment_and_control | 0.6629 | 0.6525 | 0.6427 | 0.6396 | 0.6356 | 0.6597 |
| revenue_and_commercial_terms | 0.3895 | 0.3888 | 0.4157 | 0.4132 | 0.3760 | 0.4113 |
| operational_rights | 0.5352 | 0.5358 | 0.5270 | 0.5097 | 0.5267 | 0.5437 |

## 5. 状态混淆分析 (evidence_missing -> answered 误判)

| Case | EvoSkill v1 | EvoSkill v4 | Delta |
|---|---|---|:-:|
| contract_basic_info | 26 | 27 | +1 (+4%) |
| term_and_termination | 101 | 83 | -18 (-18%) |
| legal_governance | 10 | 9 | -1 (-10%) |
| ip_and_license | 356 | 163 | -193 (-54%) |
| competition_restrictions | 115 | 112 | -3 (-3%) |
| liability_and_indemnity | 107 | 87 | -20 (-19%) |
| assignment_and_control | 35 | 38 | +3 (+9%) |
| revenue_and_commercial_terms | 74 | 70 | -4 (-5%) |
| operational_rights | 132 | 121 | -11 (-8%) |
| **TOTAL** | **956** | **710** | **-246 (-26%)** |

## 6. 跨方法排名汇总

### Task Success

| 排名 | 方法 | Value |
|---|---|---|
| 1 | EvoSkill v4 [NEW] | 0.6952 |
| 2 | EvoSkill v1 | 0.6435 |
| 3 | Summary2Skill | 0.6407 |
| 4 | DocToolMaker | 0.6345 |
| 5 | Schema Prompt | 0.6298 |
| 6 | Native Prompt | 0.4994 |

### Status Macro-F1

| 排名 | 方法 | Value |
|---|---|---|
| 1 | EvoSkill v4 [NEW] | 0.8714 |
| 2 | EvoSkill v1 | 0.8477 |
| 3 | Schema Prompt | 0.8380 |
| 4 | Summary2Skill | 0.7696 |
| 5 | DocToolMaker | 0.7451 |
| 6 | Native Prompt | 0.5824 |

### Containment Ev F1

| 排名 | 方法 | Value |
|---|---|---|
| 1 | Summary2Skill | 0.6638 |
| 2 | EvoSkill v4 [NEW] | 0.6536 |
| 3 | Schema Prompt | 0.6508 |
| 4 | Native Prompt | 0.6455 |
| 5 | DocToolMaker | 0.6447 |
| 6 | EvoSkill v1 | 0.6348 |

### Governance Boundary

| 排名 | 方法 | Value |
|---|---|---|
| 1 | EvoSkill v1 | 0.8916 |
| 2 | EvoSkill v4 [NEW] | 0.8863 |
| 3 | Schema Prompt | 0.8810 |
| 4 | Summary2Skill | 0.7328 |
| 5 | DocToolMaker | 0.6984 |
| 6 | Native Prompt | 0.5714 |

### Strict Evidence F1

| 排名 | 方法 | Value |
|---|---|---|
| 1 | Schema Prompt | 0.4772 |
| 2 | Native Prompt | 0.4611 |
| 3 | DocToolMaker | 0.4485 |
| 4 | Summary2Skill | 0.4329 |
| 5 | EvoSkill v1 | 0.4315 |
| 6 | EvoSkill v4 [NEW] | 0.4310 |

## 7. EvoSkill v1 vs v4 详细对比

| Metric | v1 | v4 | Delta | v1 Rank | v4 Rank |
|---|---|:-:|:-:|:-:|
| Task Success Rate | 0.6435 | 0.6952 | +0.0517 UP | 2 | 1 |
| Status Macro-F1 | 0.8477 | 0.8714 | +0.0237 UP | 2 | 1 |
| Status Balanced Accuracy | 0.8626 | 0.8773 | +0.0147 UP | 2 | 1 |
| Status Accuracy | 0.7562 | 0.8083 | +0.0521 UP | 3 | 1 |
| Evidence Precision | 0.4467 | 0.4473 | +0.0006 UP | 5 | 4 |
| Evidence Recall | 0.4623 | 0.4608 | -0.0015 DOWN | 5 | 6 |
| Strict Evidence F1 | 0.4315 | 0.4310 | -0.0005 DOWN | 5 | 6 |
| Containment Evidence F1 | 0.6348 | 0.6536 | +0.0188 UP | 6 | 2 |
| Governance Boundary | 0.8916 | 0.8863 | -0.0053 DOWN | 1 | 2 |
| Boundary Correct | 0.6905 | 0.7662 | +0.0757 UP | 2 | 1 |
| Human Review Routing | 0.7469 | 0.7346 | -0.0123 DOWN | 1 | 2 |
| External Violation Rate | 0.2531 | 0.2654 | +0.0123 UP | 6 | 5 |
| Validation Failure Rate | 0.1300 | 0.1290 | -0.0010 DOWN | 3 | 4 |

## 8. v4 改进说明

v4 对 evoskill_compiler 的唯一修改是 SKILL.md 的生成 prompt 中的章节结构。

**改之前 (v1):**

GENERATE_SYSTEM prompt 要求生成:
```
## Evidence-Based Review Rules
For each category, describe review rules with [KA-XXXX] references.
Example: "Look for explicit grant language such as ... [KA-0001, KA-0003]"
```

生成出的 SKILL.md 是规则列表形式:
```markdown
### 1. Renewal Term
* Identify Automatic Renewal Mechanisms: Look for language indicating
  automatic renewal upon expiration [KA-0077, KA-0111].
* Determine Renewal Duration: Check if the renewal term matches the
  initial term. Variations include one-year [KA-0001], two-year [KA-0327].
```

**改之后 (v4):**

GENERATE_SYSTEM prompt 要求生成:
```
## Common Clause Patterns & Example Phrasing
For each category, derive 3-6 common clause PATTERNS from the evidence KAs.
For each pattern include:
- Pattern Name / Description / Example Phrasing / Variation Notes
```

生成出的 SKILL.md 是模式+例句形式:
```markdown
#### Pattern 1: Automatic Annual Renewal
- Description: The agreement automatically extends for successive
  one-year periods unless terminated by notice.
- Example Phrasing:
  > "will renew automatically from year to year unless cancelled
     in writing by either Party..." [KA-0016]
  > "shall be automatically renewed for successive one (1) year
     periods" [KA-0111]
- Variation Notes: Some specify month-to-month [KA-0164]
```

**关键差异**: v1 是抽象的规则列表（"去检查有没有X"），v4 是具体的语言模板（"你要找的条款长这样：[真实原文]"）。evidence_index.json、security_policy.json 等全部不变。