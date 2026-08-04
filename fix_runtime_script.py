with open(r'D:\cuad-skillgenbench\scripts\run_runtime_evaluation.py', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. 添加 --incremental 参数到 main()
old_args = '''    parser.add_argument("--overwrite", action="store_true",
                        help="Overwrite existing runtime results")'''

new_args = '''    parser.add_argument("--overwrite", action="store_true",
                        help="Overwrite existing runtime results")
    parser.add_argument("--incremental", action="store_true",
                        help="Only re-run tasks with status='error'")'''

if old_args in content:
    content = content.replace(old_args, new_args)
    print('OK - Added --incremental argument')
else:
    print('ERROR: Could not find argument section')

# 2. 修改 run_method 调用，传递 incremental 参数
old_call = '''        run_method(method, case_ids, loader, llm, args.results_root, args.overwrite)'''

new_call = '''        run_method(method, case_ids, loader, llm, args.results_root, args.overwrite, args.incremental)'''

if old_call in content:
    content = content.replace(old_call, new_call)
    print('OK - Updated run_method call')
else:
    print('ERROR: Could not find run_method call')

# 3. 修改 run_method 函数签名
old_sig = '''def run_method(method: str, case_ids: list, loader: CUADSkillGenLoader, 
               llm: LLMClient, results_root: str, overwrite: bool = False):'''

new_sig = '''def run_method(method: str, case_ids: list, loader: CUADSkillGenLoader, 
               llm: LLMClient, results_root: str, overwrite: bool = False, incremental: bool = False):'''

if old_sig in content:
    content = content.replace(old_sig, new_sig)
    print('OK - Updated run_method signature')
else:
    print('ERROR: Could not find run_method signature')

# 4. 修改 agent.run_all_tasks 调用
old_agent_call = '''        result = agent.run_all_tasks(case_id, runtime_dir, overwrite)'''

new_agent_call = '''        result = agent.run_all_tasks(case_id, runtime_dir, overwrite, incremental)'''

if old_agent_call in content:
    content = content.replace(old_agent_call, new_agent_call)
    print('OK - Updated agent.run_all_tasks call')
else:
    print('ERROR: Could not find agent.run_all_tasks call')

with open(r'D:\cuad-skillgenbench\scripts\run_runtime_evaluation.py', 'w', encoding='utf-8') as f:
    f.write(content)

print('Done - run_runtime_evaluation.py updated')
