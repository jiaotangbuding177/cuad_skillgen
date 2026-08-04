import json
from collections import Counter

def compute_f1(pred_set, gold_set):
    if not gold_set and not pred_set:
        return 1.0, 1.0, 1.0
    if not gold_set:
        return 0.0, 1.0, 0.0
    if not pred_set:
        return 1.0, 0.0, 0.0
    
    tp = len(pred_set & gold_set)
    precision = tp / len(pred_set) if pred_set else 0.0
    recall = tp / len(gold_set) if gold_set else 0.0
    f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0.0
    return precision, recall, f1

def normalize_status(status):
    """Map agent output status to expected status."""
    status_map = {
        'success': 'answered',
        'ok': 'answered',
        'answered': 'answered',
        'evidence_missing': 'evidence_missing',
        'missing_input': 'missing_input',
        'unsupported_scope': 'unsupported_scope',
        'needs_human_review': 'needs_human_review',
    }
    return status_map.get(status, status)

def analyze_case(results_path):
    results = []
    with open(results_path, 'r', encoding='utf-8') as f:
        for line in f:
            if line.strip():
                results.append(json.loads(line))
    
    # Filter out error tasks
    valid_results = [r for r in results if r.get('status') != 'error']
    error_count = len(results) - len(valid_results)
    
    # Status accuracy (with normalization)
    status_correct = 0
    for r in valid_results:
        pred = normalize_status(r.get('status', 'unknown'))
        gold = r.get('_gold_status', 'unknown')
        if pred == gold:
            status_correct += 1
    
    status_accuracy = status_correct / len(valid_results) if valid_results else 0.0
    
    # Evidence F1
    f1_scores = []
    for r in valid_results:
        pred_ids = set(r.get('evidence_unit_ids', []))
        gold_ids = set(r.get('_gold_evidence_unit_ids', []))
        if gold_ids:
            _, _, f1 = compute_f1(pred_ids, gold_ids)
            f1_scores.append(f1)
    
    evidence_f1 = sum(f1_scores) / len(f1_scores) if f1_scores else 0.0
    
    # Boundary correctness
    boundary_correct = 0
    boundary_opportunities = 0
    for r in valid_results:
        gold = r.get('_gold_status', '')
        pred = normalize_status(r.get('status', ''))
        if gold in ('needs_human_review', 'unsupported_scope', 'missing_input'):
            boundary_opportunities += 1
            if pred == gold:
                boundary_correct += 1
    
    boundary_accuracy = boundary_correct / boundary_opportunities if boundary_opportunities > 0 else 0.0
    
    return {
        'total_tasks': len(results),
        'valid_tasks': len(valid_results),
        'error_tasks': error_count,
        'status_accuracy': status_accuracy,
        'evidence_f1': evidence_f1,
        'boundary_accuracy': boundary_accuracy,
        'boundary_opportunities': boundary_opportunities,
    }

# Analyze native_prompt_skill valid cases
print("=" * 80)
print("native_prompt_skill - Valid Cases Metrics")
print("=" * 80)

valid_cases = ['contract_basic_info', 'term_and_termination']
all_metrics = []

for case_id in valid_cases:
    results_path = rf'D:\cuad-skillgenbench\results\skillgen\generated\native_prompt_skill\runtime_results\{case_id}_results.jsonl'
    metrics = analyze_case(results_path)
    metrics['case_id'] = case_id
    all_metrics.append(metrics)
    
    print(f"\n{case_id}:")
    print(f"  Total tasks: {metrics['total_tasks']}")
    print(f"  Valid tasks: {metrics['valid_tasks']} ({metrics['valid_tasks']/metrics['total_tasks']*100:.1f}%)")
    print(f"  Error tasks: {metrics['error_tasks']} ({metrics['error_tasks']/metrics['total_tasks']*100:.1f}%)")
    print(f"  Status Accuracy: {metrics['status_accuracy']:.4f}")
    print(f"  Evidence F1: {metrics['evidence_f1']:.4f}")
    print(f"  Boundary Accuracy: {metrics['boundary_accuracy']:.4f} ({metrics['boundary_opportunities']} opportunities)")

# Aggregate
print("\n" + "=" * 80)
print("Aggregated Metrics (native_prompt_skill)")
print("=" * 80)
total_valid = sum(m['valid_tasks'] for m in all_metrics)
total_tasks = sum(m['total_tasks'] for m in all_metrics)
avg_status_acc = sum(m['status_accuracy'] * m['valid_tasks'] for m in all_metrics) / total_valid if total_valid > 0 else 0
avg_evidence_f1 = sum(m['evidence_f1'] * m['valid_tasks'] for m in all_metrics) / total_valid if total_valid > 0 else 0
total_boundary_opp = sum(m['boundary_opportunities'] for m in all_metrics)

print(f"Total tasks: {total_tasks}")
print(f"Valid tasks: {total_valid} ({total_valid/total_tasks*100:.1f}%)")
print(f"Error tasks: {total_tasks - total_valid} ({(total_tasks-total_valid)/total_tasks*100:.1f}%)")
print(f"Weighted Status Accuracy: {avg_status_acc:.4f}")
print(f"Weighted Evidence F1: {avg_evidence_f1:.4f}")
print(f"Total Boundary Opportunities: {total_boundary_opp}")
