"""
Generate a comprehensive markdown data report for all baselines + v4.
"""
import json
import os

with open('results/skillgen/generated/package_runtime_evaluation_test_final-k10-k6.json', encoding='utf-8') as f:
    v1_data = json.load(f)
with open('results/skillgen/generated/package_runtime_evaluation_test_final-k10-k6-v4-example-phrasing.json', encoding='utf-8') as f:
    v4_data = json.load(f)

v4_evo = v4_data[0]

methods = {}
for m in v1_data:
    methods[m['method']] = m
methods['evoskill_compiler_v4'] = v4_evo

main_metrics = [
    ('task_success_rate', 'Task Success Rate', True),
    ('status_macro_f1', 'Status Macro-F1', True),
    ('status_balanced_accuracy', 'Status Balanced Accuracy', True),
    ('status_accuracy', 'Status Accuracy', True),
    ('evidence_precision', 'Evidence Precision', True),
    ('evidence_recall', 'Evidence Recall', True),
    ('evidence_f1', 'Strict Evidence F1', True),
    ('containment_evidence_f1', 'Containment Evidence F1', True),
    ('governance_boundary_correct', 'Governance Boundary', True),
    ('boundary_correct', 'Boundary Correct', True),
    ('human_review_routing', 'Human Review Routing', True),
    ('external_violation_rate', 'External Violation Rate', False),
    ('validation_failure_rate', 'Validation Failure Rate', False),
]

method_order = [
    'native_prompt_skill', 'schema_prompt_skill', 'summary2skill',
    'document_tool_maker', 'evoskill_compiler', 'evoskill_compiler_v4'
]
method_labels = {
    'native_prompt_skill': 'Native Prompt',
    'schema_prompt_skill': 'Schema Prompt',
    'summary2skill': 'Summary2Skill',
    'document_tool_maker': 'DocToolMaker',
    'evoskill_compiler': 'EvoSkill v1',
    'evoskill_compiler_v4': 'EvoSkill v4',
}

case_ids = list(methods['evoskill_compiler']['cases'].keys())

out = []
def w(s=''):
    out.append(s)

w('# CUAD-SkillGen 实验数据报告')
w()
w('## 1. 实验配置')
w()
w('| 配置项 | 取值 |')
w('|---|---|')
w('| 运行时协议 | package-aware-v1 |')
w('| 运行时模型 | ecnu-plus |')
w('| 评测分割 | test |')
w('| 合同检索 | BM25 top-10 chunks |')
w('| Skill知识检索 | BM25 top-6 items |')
w('| 治理任务 | Included |')
w('| 总任务数 | 4668 |')
w()

w('## 2. 方法说明')
w()
w('| 方法 | 说明 |')
w('|---|---|')
w('| native_prompt_skill | 直接 prompt 生成自由格式 SKILL.md，无结构化索引 |')
w('| schema_prompt_skill | 结构化 prompt，固定章节，无实际数据索引 |')
w('| summary2skill | 逐合同摘要，段落级原文索引 |')
w('| document_tool_maker | 工具接口描述，函数级示例索引 |')
w('| evoskill_compiler (v1) | Knowledge Atom + Evidence-Based Review Rules (规则驱动) |')
w('| evoskill_compiler_v4 | Knowledge Atom + Common Clause Patterns & Example Phrasing (模式驱动) |')
w()

# ===== Section 3: Main results table =====
w('## 3. 主指标总表')
w()

for metric_key, metric_label, higher_better in main_metrics:
    w(f'### {metric_label}')
    w()
    w('| 方法 | Value | 排名 |')
    w('|---|---|---|')

    vals = [(mid, methods[mid].get(metric_key, 0)) for mid in method_order]
    vals.sort(key=lambda x: -x[1])

    for rank, (mid, val) in enumerate(vals, 1):
        label = method_labels[mid]
        if mid == 'evoskill_compiler_v4':
            label += ' [NEW]'
        w(f'| {label} | {val:.4f} | {rank} |')
    w()

# ===== Section 4: Per-case tables =====
w('## 4. 分 Case 指标')
w()

# Header
case_header = '| Case | ' + ' | '.join(method_labels[m] for m in method_order) + ' |'
case_sep = '|---|' + '|'.join('---' for _ in method_order) + '|'

for metric_key, metric_label in [
    ('task_success_rate', 'Task Success Rate'),
    ('status_macro_f1', 'Status Macro-F1'),
    ('evidence_f1', 'Strict Evidence F1'),
    ('containment_evidence_f1', 'Containment Evidence F1'),
]:
    w(f'### {metric_label}')
    w()
    w(case_header)
    w(case_sep)
    for case_id in case_ids:
        row = f'| {case_id} '
        best = -1
        best_mid = None
        for mid in method_order:
            if mid in methods and case_id in methods[mid].get('cases', {}):
                val = methods[mid]['cases'][case_id].get(metric_key, 0)
                row += f'| {val:.4f} '
                if val > best:
                    best = val
                    best_mid = mid
            else:
                row += '| - '
        row += '|'
        w(row)
    w()

# ===== Section 5: em->ans confusion =====
w('## 5. 状态混淆分析 (evidence_missing -> answered 误判)')
w()
w('| Case | EvoSkill v1 | EvoSkill v4 | Delta |')
w('|---|---|---|:-:|')
total_v1, total_v4 = 0, 0
for case_id in case_ids:
    e1 = methods['evoskill_compiler']['cases'][case_id]['status_confusion'].get('evidence_missing', {}).get('answered', 0)
    e4 = methods['evoskill_compiler_v4']['cases'][case_id]['status_confusion'].get('evidence_missing', {}).get('answered', 0)
    total_v1 += e1
    total_v4 += e4
    pct = f'{(e4-e1)/e1*100:+.0f}%' if e1 > 0 else 'N/A'
    w(f'| {case_id} | {e1} | {e4} | {e4-e1:+d} ({pct}) |')
pct_total = (total_v4-total_v1)/total_v1*100
w(f'| **TOTAL** | **{total_v1}** | **{total_v4}** | **{total_v4-total_v1:+d} ({pct_total:+.0f}%)** |')
w()

# ===== Section 6: Cross-method ranking summary =====
w('## 6. 跨方法排名汇总')
w()
ranking_metrics = [
    ('task_success_rate', 'Task Success'),
    ('status_macro_f1', 'Status Macro-F1'),
    ('containment_evidence_f1', 'Containment Ev F1'),
    ('governance_boundary_correct', 'Governance Boundary'),
    ('evidence_f1', 'Strict Evidence F1'),
]
for metric_key, metric_label in ranking_metrics:
    w(f'### {metric_label}')
    w()
    w('| 排名 | 方法 | Value |')
    w('|---|---|---|')
    vals = [(mid, methods[mid].get(metric_key, 0)) for mid in method_order]
    vals.sort(key=lambda x: -x[1])
    for rank, (mid, val) in enumerate(vals, 1):
        label = method_labels[mid]
        if mid == 'evoskill_compiler_v4':
            label += ' [NEW]'
        w(f'| {rank} | {label} | {val:.4f} |')
    w()

# ===== Section 7: v1 vs v4 detailed =====
w('## 7. EvoSkill v1 vs v4 详细对比')
w()
w('| Metric | v1 | v4 | Delta | v1 Rank | v4 Rank |')
w('|---|---|:-:|:-:|:-:|')
for metric_key, metric_label, higher_better in main_metrics:
    v1v = methods['evoskill_compiler'].get(metric_key, 0)
    v4v = methods['evoskill_compiler_v4'].get(metric_key, 0)
    d = v4v - v1v
    all_vals = [(mid, methods[mid].get(metric_key, 0)) for mid in method_order]
    all_vals.sort(key=lambda x: -x[1])
    v1_rank = [i for i,(mid,_) in enumerate(all_vals,1) if mid == 'evoskill_compiler'][0]
    v4_rank = [i for i,(mid,_) in enumerate(all_vals,1) if mid == 'evoskill_compiler_v4'][0]
    arrow = 'UP' if d > 0 else ('DOWN' if d < 0 else 'FLAT')
    w(f'| {metric_label} | {v1v:.4f} | {v4v:.4f} | {d:+.4f} {arrow} | {v1_rank} | {v4_rank} |')
w()

# ===== Section 8: Improvement summary =====
w('## 8. v4 改进说明')
w()
w('v4 对 evoskill_compiler 的唯一修改是 SKILL.md 的生成 prompt 中的章节结构。')
w()
w('**改之前 (v1):**')
w()
w('GENERATE_SYSTEM prompt 要求生成:')
w('```')
w('## Evidence-Based Review Rules')
w('For each category, describe review rules with [KA-XXXX] references.')
w('Example: "Look for explicit grant language such as ... [KA-0001, KA-0003]"')
w('```')
w()
w('生成出的 SKILL.md 是规则列表形式:')
w('```markdown')
w('### 1. Renewal Term')
w('* Identify Automatic Renewal Mechanisms: Look for language indicating')
w('  automatic renewal upon expiration [KA-0077, KA-0111].')
w('* Determine Renewal Duration: Check if the renewal term matches the')
w('  initial term. Variations include one-year [KA-0001], two-year [KA-0327].')
w('```')
w()
w('**改之后 (v4):**')
w()
w('GENERATE_SYSTEM prompt 要求生成:')
w('```')
w('## Common Clause Patterns & Example Phrasing')
w('For each category, derive 3-6 common clause PATTERNS from the evidence KAs.')
w('For each pattern include:')
w('- Pattern Name / Description / Example Phrasing / Variation Notes')
w('```')
w()
w('生成出的 SKILL.md 是模式+例句形式:')
w('```markdown')
w('#### Pattern 1: Automatic Annual Renewal')
w('- Description: The agreement automatically extends for successive')
w('  one-year periods unless terminated by notice.')
w('- Example Phrasing:')
w('  > "will renew automatically from year to year unless cancelled')
w('     in writing by either Party..." [KA-0016]')
w('  > "shall be automatically renewed for successive one (1) year')
w('     periods" [KA-0111]')
w('- Variation Notes: Some specify month-to-month [KA-0164]')
w('```')
w()
w('**关键差异**: v1 是抽象的规则列表（"去检查有没有X"），v4 是具体的语言模板（"你要找的条款长这样：[真实原文]"）。evidence_index.json、security_policy.json 等全部不变。')

# Write file
repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
output_path = os.path.join(repo_root, 'results', 'skillgen', 'generated', 'experiment_data_report.md')
os.makedirs(os.path.dirname(output_path), exist_ok=True)
with open(output_path, 'w', encoding='utf-8') as f:
    f.write('\n'.join(out))

print(f'Wrote {len(out)} lines to {output_path}')
