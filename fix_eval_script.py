with open(r'D:\cuad-skillgenbench\scripts\evaluate_skill_quality.py', 'r', encoding='utf-8') as f:
    content = f.read()

# 修复 print_summary 函数中的错误处理
old_code = '''    for ev in evaluations:
        if "error" in ev:
            print(f"{ev['method']:<25} {ev['case_id']:<25} ERROR: {ev['error']}")
            continue'''

new_code = '''    for ev in evaluations:
        if "error" in ev:
            method = ev.get('method', 'unknown')
            case_id = ev.get('case_id', 'unknown')
            print(f"{method:<25} {case_id:<25} ERROR: {ev['error']}")
            continue'''

content = content.replace(old_code, new_code)

with open(r'D:\cuad-skillgenbench\scripts\evaluate_skill_quality.py', 'w', encoding='utf-8') as f:
    f.write(content)

print('Fixed')
