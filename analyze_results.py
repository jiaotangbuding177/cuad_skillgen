import json
from collections import Counter

def analyze_method(method_name):
    results_dir = rf'D:\cuad-skillgenbench\results\skillgen\generated\{method_name}\runtime_results'
    
    all_results = []
    case_stats = {}
    
    for case_file in ['contract_basic_info_results.jsonl', 'term_and_termination_results.jsonl',
                      'legal_governance_results.jsonl', 'ip_and_license_results.jsonl',
                      'competition_restrictions_results.jsonl', 'liability_and_indemnity_results.jsonl',
                      'assignment_and_control_results.jsonl', 'revenue_and_commercial_terms_results.jsonl',
                      'operational_rights_results.jsonl']:
        case_id = case_file.replace('_results.jsonl', '')
        results_path = rf'{results_dir}\{case_file}'
        
        try:
            results = []
            with open(results_path, 'r', encoding='utf-8') as f:
                for line in f:
                    if line.strip():
                        results.append(json.loads(line))
            
            status_dist = Counter(r.get('status', 'unknown') for r in results)
            gold_status_dist = Counter(r.get('_gold_status', 'unknown') for r in results)
            
            # Check if evidence_unit_ids match gold format
            has_ge_ids = 0
            has_contract_ids = 0
            for r in results:
                euids = r.get('evidence_unit_ids', [])
                if euids:
                    if any(str(e).startswith('GE-CUAD') for e in euids):
                        has_ge_ids += 1
                    else:
                        has_contract_ids += 1
            
            case_stats[case_id] = {
                'total': len(results),
                'status_dist': dict(status_dist),
                'gold_status_dist': dict(gold_status_dist),
                'has_ge_ids': has_ge_ids,
                'has_contract_ids': has_contract_ids,
            }
            
            all_results.extend(results)
        except FileNotFoundError:
            case_stats[case_id] = {'error': 'File not found'}
    
    return all_results, case_stats

# Analyze both methods
print("=" * 80)
print("native_prompt_skill Analysis")
print("=" * 80)
native_results, native_stats = analyze_method('native_prompt_skill')

print(f"Total tasks: {len(native_results)}")
print(f"\nPer-case breakdown:")
for case_id, stats in native_stats.items():
    if 'error' in stats:
        print(f"  {case_id}: {stats['error']}")
    else:
        print(f"  {case_id}: {stats['total']} tasks")
        print(f"    Predicted status: {stats['status_dist']}")
        print(f"    Gold status: {stats['gold_status_dist']}")
        print(f"    Evidence IDs format: GE-CUAD={stats['has_ge_ids']}, Contract={stats['has_contract_ids']}")

print("\n" + "=" * 80)
print("schema_prompt_skill Analysis")
print("=" * 80)
schema_results, schema_stats = analyze_method('schema_prompt_skill')

print(f"Total tasks: {len(schema_results)}")
print(f"\nPer-case breakdown:")
for case_id, stats in schema_stats.items():
    if 'error' in stats:
        print(f"  {case_id}: {stats['error']}")
    else:
        print(f"  {case_id}: {stats['total']} tasks")
        print(f"    Predicted status: {stats['status_dist']}")
        print(f"    Gold status: {stats['gold_status_dist']}")
        print(f"    Evidence IDs format: GE-CUAD={stats['has_ge_ids']}, Contract={stats['has_contract_ids']}")
