with open(r'D:\cuad-skillgenbench\scripts\runtime\agent.py', 'r', encoding='utf-8') as f:
    content = f.read()

# 找到 run_all_tasks 方法并修改
old_method = '''    def run_all_tasks(self, case_id: str, output_dir: str, overwrite: bool = False) -> dict:
        """Run all tasks for a case and save results."""
        tasks = self.loader.load_tasks(case_id)
        os.makedirs(output_dir, exist_ok=True)
        output_path = os.path.join(output_dir, f"{case_id}_results.jsonl")

        if os.path.exists(output_path) and not overwrite:
            print(f"  [{case_id}] Results already exist, skipping")
            return {"skipped": True}

        print(f"  [{case_id}] Processing {len(tasks)} tasks...")
        results = []
        total_usage = {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0}
        start_time = time.time()

        for i, task in enumerate(tasks):
            result = self.process_task(task)
            result["_task_id"] = task["task_id"]
            result["_gold_status"] = task["gold_status"]
            result["_gold_evidence_unit_ids"] = task.get("gold_evidence_unit_ids", [])

            # Track usage
            usage = result.pop("_usage", {})
            for k in total_usage:
                total_usage[k] += usage.get(k, 0)

            results.append(result)

            if (i + 1) % 100 == 0:
                print(f"    Progress: {i+1}/{len(tasks)}")

        # Write results
        with open(output_path, "w", encoding="utf-8") as f:
            for r in results:
                f.write(json.dumps(r, ensure_ascii=False) + "\\n")

        duration = time.time() - start_time
        print(f"  [{case_id}] Done: {len(results)} tasks in {duration:.1f}s, {total_usage['total_tokens']} tokens")

        return {
            "skipped": False,
            "task_count": len(results),
            "usage": total_usage,
            "duration": duration,
        }'''

new_method = '''    def run_all_tasks(self, case_id: str, output_dir: str, overwrite: bool = False, incremental: bool = False) -> dict:
        """Run all tasks for a case and save results.
        
        Args:
            case_id: Case identifier
            output_dir: Output directory path
            overwrite: If True, overwrite existing results
            incremental: If True, only re-run tasks with status="error"
        """
        tasks = self.loader.load_tasks(case_id)
        os.makedirs(output_dir, exist_ok=True)
        output_path = os.path.join(output_dir, f"{case_id}_results.jsonl")

        # Load existing results if incremental mode
        existing_results = {}
        if incremental and os.path.exists(output_path):
            print(f"  [{case_id}] Loading existing results for incremental run...")
            with open(output_path, "r", encoding="utf-8") as f:
                for line in f:
                    if line.strip():
                        r = json.loads(line)
                        task_id = r.get("_task_id")
                        if task_id:
                            existing_results[task_id] = r
            
            # Count how many are errors
            error_count = sum(1 for r in existing_results.values() if r.get("status") == "error")
            print(f"  [{case_id}] Found {len(existing_results)} existing results, {error_count} errors to retry")

        if os.path.exists(output_path) and not overwrite and not incremental:
            print(f"  [{case_id}] Results already exist, skipping")
            return {"skipped": True}

        # Determine which tasks to process
        if incremental and existing_results:
            tasks_to_process = [t for t in tasks if t["task_id"] not in existing_results or 
                               existing_results[t["task_id"]].get("status") == "error"]
            print(f"  [{case_id}] Processing {len(tasks_to_process)} tasks (incremental)...")
        else:
            tasks_to_process = tasks
            print(f"  [{case_id}] Processing {len(tasks_to_process)} tasks...")

        results = []
        total_usage = {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0}
        start_time = time.time()

        for i, task in enumerate(tasks_to_process):
            result = self.process_task(task)
            result["_task_id"] = task["task_id"]
            result["_gold_status"] = task["gold_status"]
            result["_gold_evidence_unit_ids"] = task.get("gold_evidence_unit_ids", [])

            # Track usage
            usage = result.pop("_usage", {})
            for k in total_usage:
                total_usage[k] += usage.get(k, 0)

            # Update existing results or add new
            existing_results[task["task_id"]] = result

            if (i + 1) % 100 == 0:
                print(f"    Progress: {i+1}/{len(tasks_to_process)}")

        # Write all results (including existing ones)
        all_results = list(existing_results.values())
        with open(output_path, "w", encoding="utf-8") as f:
            for r in all_results:
                f.write(json.dumps(r, ensure_ascii=False) + "\\n")

        duration = time.time() - start_time
        print(f"  [{case_id}] Done: {len(tasks_to_process)} tasks in {duration:.1f}s, {total_usage['total_tokens']} tokens")
        print(f"  [{case_id}] Total results: {len(all_results)}")

        return {
            "skipped": False,
            "task_count": len(tasks_to_process),
            "total_results": len(all_results),
            "usage": total_usage,
            "duration": duration,
        }'''

if old_method in content:
    content = content.replace(old_method, new_method)
    with open(r'D:\cuad-skillgenbench\scripts\runtime\agent.py', 'w', encoding='utf-8') as f:
        f.write(content)
    print('OK - agent.py updated with incremental support')
else:
    print('ERROR: Could not find target method')
