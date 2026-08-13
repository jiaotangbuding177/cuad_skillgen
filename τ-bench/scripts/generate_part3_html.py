"""Generate Part 3 of the review HTML: 74 rule-only unmatched atoms."""
import json

data = json.loads(open('results/evaluation/atom_extraction_llm_comparison.json', encoding='utf-8').read())
atoms = data['comparison']['rule_unmatched_atoms']

# Sort by value priority
high_value_keywords = ['warning', 'does not check', 'must be valid', 'max 6 months',
                       'raises', 'valueerror', 'check the bill', 'already paid',
                       'not active', 'not found', 'not suspended']

def value_score(atom):
    text = atom['text'].lower()
    origin = atom['origin']

    score = 0
    # High value: error handling, warnings, validation
    if any(kw in text for kw in ['warning', 'does not check', 'raises: valueerror',
                                   'must be valid', 'max 6 months', 'always check']):
        score += 100
    # Medium value: required_input (but redundant with tool schema)
    if atom['type'] == 'required_input' and origin == 'tool_schema':
        score += 30
    # Low value: actor ownership (all are "owned by assistant")
    if 'owned by the assistant actor' in text:
        score -= 50
    # Medium value: policy text
    if origin == 'policy':
        # Check if it's a complete sentence vs fragment
        if len(atom['text']) > 30 and atom['text'].endswith('.'):
            score += 20
        else:
            score += 5
    # Tool descriptions vary
    if origin == 'tool_description':
        if any(kw in text for kw in ['args:', 'returns:']):
            score -= 10  # boilerplate
        else:
            score += 10  # functional description

    return score

# Sort atoms by value score descending
scored = [(value_score(a), a) for a in atoms]
scored.sort(key=lambda x: -x[0])

# Categorize
high = [(s, a) for s, a in scored if s >= 50]
medium = [(s, a) for s, a in scored if 10 <= s < 50]
low = [(s, a) for s, a in scored if s < 10]

print(f"Total: {len(atoms)}")
print(f"High value (score>=50): {len(high)}")
print(f"Medium value (10<=score<50): {len(medium)}")
print(f"Low value (score<10): {len(low)}")

# Generate HTML rows
type_colors = {
    'precondition': '#3498db',
    'prohibition': '#e74c3c',
    'fact': '#95a5a6',
    'actor_constraint': '#9b59b6',
    'required_input': '#f39c12',
    'escalation': '#e67e22',
    'permission': '#1abc9c',
    'postcondition': '#16a085',
    'confirmation': '#2980b9',
    'exception': '#c0392b',
    'communication_requirement': '#8e44ad',
}

def value_badge(score):
    if score >= 50:
        return '<span class="similarity high">高价值</span>'
    elif score >= 10:
        return '<span class="similarity medium">中价值</span>'
    else:
        return '<span class="similarity low">低价值</span>'

def origin_badge(origin):
    badges = {
        'tool_description': '<span style="background:#ecf0f1;padding:2px 6px;border-radius:3px;font-size:11px;">tool_desc</span>',
        'tool_schema': '<span style="background:#ecf0f1;padding:2px 6px;border-radius:3px;font-size:11px;">tool_schema</span>',
        'policy': '<span style="background:#d5f5e3;padding:2px 6px;border-radius:3px;font-size:11px;">policy</span>',
    }
    return badges.get(origin, origin)

rows = []
for idx, (score, atom) in enumerate(scored, 1):
    color = type_colors.get(atom['type'], '#95a5a6')
    text = atom['text'].replace('<', '&lt;').replace('>', '&gt;')
    # Truncate very long text
    if len(text) > 200:
        text = text[:197] + '...'

    row = f'''      <tr>
        <td class="row-number">{idx}</td>
        <td><code>{atom['atom_id'].replace('ATOM-', '')}</code></td>
        <td><span class="type-tag" style="background:{color};color:white;">{atom['type']}</span></td>
        <td>{atom['subject']}</td>
        <td class="text-cell">{text}</td>
        <td>{origin_badge(atom['origin'])}</td>
        <td>{value_badge(score)}</td>
        <td>
          <select class="judge-select">
            <option value="">-- 选择 --</option>
            <option value="keep">✓ 应保留</option>
            <option value="maybe">⚠ 待定</option>
            <option value="drop">✗ 可丢弃</option>
          </select>
        </td>
        <td><textarea class="judge-notes" placeholder="审查备注..."></textarea></td>
      </tr>'''
    rows.append(row)

# Write HTML fragment
html = f'''
  <div class="section-divider" style="margin: 60px 0 40px; border-top: 3px solid #e74c3c; padding-top: 30px;">
    <h2 style="color: #2c3e50; font-size: 22px; margin-bottom: 10px;">第三部分：规则独有原子（74 个）</h2>
    <p style="color: #7f8c8d; font-size: 14px; margin-bottom: 10px;">规则抽取到，但 LLM 没有匹配上的原子。按预估价值从高到低排序。</p>
    <div style="display: flex; gap: 20px; margin-bottom: 20px;">
      <div style="background: #d5f5e3; padding: 10px 20px; border-radius: 6px;">
        <strong style="color: #27ae60;">高价值: {len(high)}</strong>
        <span style="font-size: 12px; color: #666;">（错误处理/警告/验证）</span>
      </div>
      <div style="background: #fef5e7; padding: 10px 20px; border-radius: 6px;">
        <strong style="color: #f39c12;">中价值: {len(medium)}</strong>
        <span style="font-size: 12px; color: #666;">（参数要求/policy片段）</span>
      </div>
      <div style="background: #fadbd8; padding: 10px 20px; border-radius: 6px;">
        <strong style="color: #e74c3c;">低价值: {len(low)}</strong>
        <span style="font-size: 12px; color: #666;">（模板文本/冗余信息）</span>
      </div>
    </div>
  </div>

  <table>
    <thead>
      <tr>
        <th style="width: 40px;">#</th>
        <th style="width: 80px;">原子 ID</th>
        <th style="width: 110px;">类型</th>
        <th style="width: 120px;">主体</th>
        <th style="width: 400px;">文本内容</th>
        <th style="width: 100px;">来源</th>
        <th style="width: 80px;">预估价值</th>
        <th class="judge-column">人工判断</th>
        <th style="width: 180px;">备注</th>
      </tr>
    </thead>
    <tbody>
{chr(10).join(rows)}
    </tbody>
  </table>

  <div class="legend" style="margin-top: 30px;">
    <h3>价值评估说明</h3>
    <p><strong>高价值（8 个）</strong>：错误处理前提（Raises: ValueError）、关键警告（Warning: does not check PAID）、业务约束（max 6 months）。这些告诉 agent 何时工具调用会失败。</p>
    <p><strong>中价值（约 20-30 个）</strong>：工具参数要求（与 tool schema JSON 重复）、完整 policy 规则片段、工具功能描述。</p>
    <p><strong>低价值（约 30-40 个）</strong>："owned by assistant actor"（冗余）、不完整的 policy 片段（如 "line IDs associated with their account."）、Args:/Returns: 模板。</p>
    <p><strong>排序规则</strong>：表格按预估价值从高到低排序，高价值原子在最前面。</p>
    <p><strong>对算法影响</strong>：缺失 8 个高价值原子可能影响 agent 在边界情况下的表现（如尝试在已暂停线路上再次暂停）。但 τ³-bench 测试任务是否涉及这些边界情况需要看具体 test tasks。</p>
  </div>
'''

# Insert into the main HTML
main_html = open('results/evaluation/atom_extraction_review.html', encoding='utf-8').read()

# Find the insertion point: before the final legend div
# The legend div we want to insert before is the one at the very end
# Let's insert before the </div> that closes the container

# Find the last occurrence of the legend section and insert before the closing </div>
import re
# Find the position right before the closing </div> of the container
# We'll insert before the last </div>\n\n<script>
insert_point = main_html.rfind('\n<script>')

if insert_point == -1:
    print("ERROR: Could not find insertion point")
    exit(1)

# Insert the Part 3 HTML
new_html = main_html[:insert_point] + '\n' + html + main_html[insert_point:]

with open('results/evaluation/atom_extraction_review.html', 'w', encoding='utf-8') as f:
    f.write(new_html)

print(f"\nGenerated {len(rows)} rows for Part 3")
print(f"Inserted at position {insert_point}")
print("Done!")
