"""Evaluator for package-aware CUAD-SkillGen runtime results."""

import json
import os
import re
from collections import Counter
from typing import Dict, Iterable, List, Sequence, Tuple

from common.loader import CUADSkillGenLoader


STATUS_LABELS = (
    "answered",
    "evidence_missing",
    "missing_input",
    "unsupported_scope",
    "needs_human_review",
)


def compute_status_metrics(confusion: Dict[str, Counter]) -> dict:
    """Compute imbalance-aware status metrics from a gold -> predicted matrix."""
    per_class = {}
    recalls = []
    f1_values = []
    for label in STATUS_LABELS:
        tp = confusion.get(label, Counter()).get(label, 0)
        support = sum(confusion.get(label, Counter()).values())
        predicted = sum(row.get(label, 0) for row in confusion.values())
        precision = tp / predicted if predicted else 0.0
        recall = tp / support if support else 0.0
        f1 = (
            2 * precision * recall / (precision + recall)
            if precision + recall
            else 0.0
        )
        per_class[label] = {
            "support": support,
            "predicted": predicted,
            "precision": round(precision, 4),
            "recall": round(recall, 4),
            "f1": round(f1, 4),
        }
        if support:
            recalls.append(recall)
            f1_values.append(f1)
    return {
        "status_macro_f1": round(sum(f1_values) / len(f1_values), 4)
        if f1_values else 0.0,
        "status_balanced_accuracy": round(sum(recalls) / len(recalls), 4)
        if recalls else 0.0,
        "status_per_class": per_class,
    }


def normalize_text(text: str) -> List[str]:
    return re.findall(r"[a-z0-9]+", (text or "").lower())


def text_f1(left: str, right: str) -> float:
    a, b = Counter(normalize_text(left)), Counter(normalize_text(right))
    if not a or not b:
        return 0.0
    overlap = sum((a & b).values())
    precision = overlap / sum(a.values())
    recall = overlap / sum(b.values())
    return 2 * precision * recall / (precision + recall) if precision + recall else 0.0


def span_iou(a_start: int, a_end: int, b_start: int, b_end: int) -> float:
    intersection = max(0, min(a_end, b_end) - max(a_start, b_start))
    union = max(a_end, b_end) - min(a_start, b_start)
    return intersection / union if union > 0 else 0.0


def compute_set_f1(predicted: set, gold: set) -> dict:
    if not predicted and not gold:
        return {"precision": 1.0, "recall": 1.0, "f1": 1.0}
    if not predicted:
        return {"precision": 1.0, "recall": 0.0, "f1": 0.0}
    if not gold:
        return {"precision": 0.0, "recall": 1.0, "f1": 0.0}
    tp = len(predicted & gold)
    precision = tp / len(predicted)
    recall = tp / len(gold)
    f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0
    return {"precision": precision, "recall": recall, "f1": f1}


def compute_evidence_f1(
    predicted_count: int, matched_gold: set, gold: set, matched_count: int
) -> dict:
    """Score extracted evidence while retaining unmatched predictions.

    ``matched_gold`` alone cannot be used as the predicted set because it has
    already discarded every unmatched prediction. Precision must therefore be
    based on the number of original predicted evidence items.
    """
    precision = matched_count / predicted_count if predicted_count else 0.0
    recall = len(matched_gold & gold) / len(gold) if gold else 0.0
    f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0
    return {"precision": precision, "recall": recall, "f1": f1}


class GoldEvidenceMapper:
    def __init__(self, loader: CUADSkillGenLoader):
        self.by_case_contract_category: Dict[Tuple[str, str, str], List[dict]] = {}
        for case_id in loader.get_all_case_ids():
            for unit in loader.load_evidence_units(case_id):
                key = (case_id, unit["contract_id"], unit["category"])
                self.by_case_contract_category.setdefault(key, []).append(unit)

    def map_evidence(
        self,
        case_id: str,
        contract_id: str,
        category: str,
        evidence: Sequence[dict],
        iou_threshold: float = 0.5,
        text_threshold: float = 0.8,
        containment_aware: bool = False,
    ) -> Tuple[set, List[dict]]:
        candidates = self.by_case_contract_category.get(
            (case_id, contract_id, category), []
        )
        # Build all valid edges first, then greedily keep a one-to-one matching.
        # This prevents duplicate predictions from receiving credit for the same
        # gold evidence unit.
        edges = []
        for predicted_index, predicted in enumerate(evidence):
            for gold in candidates:
                iou = span_iou(
                    int(predicted.get("span_start", -1)),
                    int(predicted.get("span_end", -1)),
                    int(gold.get("answer_start", -2)),
                    int(gold.get("answer_end", -2)),
                )
                similarity = text_f1(predicted.get("text", ""), gold.get("source_span", ""))
                predicted_start = int(predicted.get("span_start", -1))
                predicted_end = int(predicted.get("span_end", -1))
                gold_start = int(gold.get("answer_start", -2))
                gold_end = int(gold.get("answer_end", -2))
                gold_contained = (
                    predicted_start >= 0
                    and predicted_start <= gold_start
                    and predicted_end >= gold_end
                )
                score = max(iou, similarity)
                if (
                    iou >= iou_threshold
                    or similarity >= text_threshold
                    or (containment_aware and gold_contained)
                ):
                    edges.append((
                        score, predicted_index, gold, iou, similarity,
                        gold_contained,
                    ))

        matched = set()
        matched_predictions = set()
        details = []
        for score, predicted_index, gold, iou, similarity, gold_contained in sorted(
            edges, key=lambda item: item[0], reverse=True
        ):
            gold_id = gold["evidence_unit_id"]
            if predicted_index in matched_predictions or gold_id in matched:
                continue
            matched_predictions.add(predicted_index)
            matched.add(gold_id)
            predicted = evidence[predicted_index]
            details.append({
                    "predicted_index": predicted_index,
                    "predicted_span_start": predicted.get("span_start"),
                    "predicted_span_end": predicted.get("span_end"),
                    "gold_evidence_unit_id": gold_id,
                    "match_score": round(score, 4),
                    "span_iou": round(iou, 4),
                    "text_f1": round(similarity, 4),
                    "gold_fully_contained": gold_contained,
                })
        return matched, details


def load_latest_results(path: str) -> Dict[str, dict]:
    latest = {}
    if not os.path.exists(path):
        return latest
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                result = json.loads(line)
                if result.get("_task_id"):
                    latest[result["_task_id"]] = result
    return latest


def evaluate_case(
    path: str, mapper: GoldEvidenceMapper, expected_tasks: int = 0
) -> dict:
    results = list(load_latest_results(path).values())
    if not results:
        return {"error": "No results"}

    status_correct = 0
    errors = 0
    evidence_metrics = []
    containment_evidence_metrics = []
    no_answer_total = no_answer_correct = 0
    governance_boundary_total = governance_boundary_correct = 0
    isolation_total = isolation_correct = 0
    external_total = external_violations = 0
    human_total = human_correct = 0
    answered_total = answered_success = 0
    validation_failures = 0
    status_confusion: Dict[str, Counter] = {
        label: Counter() for label in STATUS_LABELS
    }

    for result in results:
        pred = result.get("status", "error")
        gold = result.get("_gold_status", "")
        status_confusion.setdefault(gold, Counter())[pred] += 1
        errors += pred == "error"
        status_correct += pred == gold
        validation_failures += bool(result.get("validation_errors"))

        if gold == "answered":
            answered_total += 1
            mapped, details = mapper.map_evidence(
                result.get("_case_id", ""),
                result.get("_target_contract_id", ""),
                result.get("_category", ""),
                result.get("evidence", []),
            )
            containment_mapped, containment_details = mapper.map_evidence(
                result.get("_case_id", ""),
                result.get("_target_contract_id", ""),
                result.get("_category", ""),
                result.get("evidence", []),
                containment_aware=True,
            )
            result["_mapped_gold_evidence_unit_ids"] = sorted(mapped)
            result["_evidence_matches"] = details
            if pred == "answered" and mapped:
                answered_success += 1
            evidence_metrics.append(compute_evidence_f1(
                predicted_count=len(result.get("evidence", [])),
                matched_gold=mapped,
                gold=set(result.get("_gold_evidence_unit_ids", [])),
                matched_count=len(details),
            ))
            containment_evidence_metrics.append(compute_evidence_f1(
                predicted_count=len(result.get("evidence", [])),
                matched_gold=containment_mapped,
                gold=set(result.get("_gold_evidence_unit_ids", [])),
                matched_count=len(containment_details),
            ))

        if gold == "evidence_missing":
            no_answer_total += 1
            no_answer_correct += pred == gold
        if gold in {"missing_input", "unsupported_scope", "needs_human_review"}:
            governance_boundary_total += 1
            governance_boundary_correct += pred == gold
        if gold == "needs_human_review":
            human_total += 1
            human_correct += pred == "needs_human_review"
            external_total += 1
            if pred != "needs_human_review":
                external_violations += 1

        if result.get("_target_contract_id"):
            isolation_total += 1
            target = result["_target_contract_id"]
            sources = result.get("source_contract_ids", [])
            evidence_sources = [item.get("contract_id") for item in result.get("evidence", [])]
            if all(source == target for source in sources + evidence_sources):
                isolation_correct += 1

    def average(key: str) -> float:
        return sum(item[key] for item in evidence_metrics) / len(evidence_metrics) if evidence_metrics else 0.0

    def containment_average(key: str) -> float:
        return (
            sum(item[key] for item in containment_evidence_metrics)
            / len(containment_evidence_metrics)
            if containment_evidence_metrics else 0.0
        )

    total = len(results)
    boundary_total = no_answer_total + governance_boundary_total
    boundary_correct = no_answer_correct + governance_boundary_correct
    task_success = (
        answered_success
        + sum(
            1 for result in results
            if result.get("_gold_status") != "answered"
            and result.get("status") == result.get("_gold_status")
        )
    ) / total
    status_metrics = compute_status_metrics(status_confusion)
    return {
        "total_tasks": total,
        "expected_tasks": expected_tasks or total,
        "missing_tasks": max((expected_tasks or total) - total, 0),
        "result_coverage": round(total / expected_tasks, 4) if expected_tasks else 1.0,
        "complete": not expected_tasks or total == expected_tasks,
        "answered_tasks": answered_total,
        "no_answer_tasks": no_answer_total,
        "governance_boundary_tasks": governance_boundary_total,
        "boundary_tasks": boundary_total,
        "legacy_boundary_tasks": governance_boundary_total,
        "isolation_tasks": isolation_total,
        "human_review_tasks": human_total,
        "external_restricted_tasks": external_total,
        "error_rate": round(errors / total, 4),
        "status_accuracy": round(status_correct / total, 4),
        "status_macro_f1": status_metrics["status_macro_f1"],
        "status_balanced_accuracy": status_metrics["status_balanced_accuracy"],
        "status_per_class": status_metrics["status_per_class"],
        "status_confusion": {
            gold: dict(predictions)
            for gold, predictions in status_confusion.items()
        },
        "task_success_rate": round(task_success, 4),
        "evidence_precision": round(average("precision"), 4),
        "evidence_recall": round(average("recall"), 4),
        "evidence_f1": round(average("f1"), 4),
        "containment_evidence_precision": round(containment_average("precision"), 4),
        "containment_evidence_recall": round(containment_average("recall"), 4),
        "containment_evidence_f1": round(containment_average("f1"), 4),
        "no_answer_correct": round(no_answer_correct / no_answer_total, 4) if no_answer_total else 0.0,
        "governance_boundary_correct": round(governance_boundary_correct / governance_boundary_total, 4) if governance_boundary_total else 0.0,
        "overall_boundary_correct": round(boundary_correct / boundary_total, 4) if boundary_total else 0.0,
        "boundary_correct": round(boundary_correct / boundary_total, 4) if boundary_total else 0.0,
        "legacy_boundary_correct": round(governance_boundary_correct / governance_boundary_total, 4) if governance_boundary_total else 0.0,
        "contract_isolation": round(isolation_correct / isolation_total, 4) if isolation_total else 0.0,
        "human_review_routing": round(human_correct / human_total, 4) if human_total else 0.0,
        "external_violation_rate": round(external_violations / external_total, 4) if external_total else 0.0,
        "validation_failure_rate": round(validation_failures / total, 4),
    }


def evaluate_methods(
    loader: CUADSkillGenLoader,
    results_root: str,
    methods: Iterable[str],
    case_ids: Iterable[str],
    split: str = "test",
    run_id: str = "package-v1",
) -> List[dict]:
    mapper = GoldEvidenceMapper(loader)
    evaluations = []
    for method in methods:
        run_dir = os.path.join(
            results_root, method, "package_runtime_results", split, run_id
        )
        run_config_path = os.path.join(run_dir, "run_config.json")
        include_governance = True
        if os.path.exists(run_config_path):
            with open(run_config_path, "r", encoding="utf-8") as f:
                include_governance = bool(json.load(f).get("include_governance", True))

        cases = {}
        for case_id in case_ids:
            if split == "all":
                expected_tasks = len(loader.load_tasks(case_id))
            else:
                contract_ids = set(loader.get_split_contract_ids(split))
                expected_tasks = sum(
                    1 for task in loader.load_tasks(case_id)
                    if task.get("contract_id") in contract_ids
                    or (
                        include_governance
                        and task.get("construction_source") == "newly_added_governance_task"
                    )
                )
            path = os.path.join(
                results_root, method, "package_runtime_results", split, run_id,
                f"{case_id}_results.jsonl"
            )
            cases[case_id] = (
                evaluate_case(path, mapper, expected_tasks)
                if os.path.exists(path)
                else {
                    "error": "Results not found",
                    "total_tasks": 0,
                    "expected_tasks": expected_tasks,
                    "missing_tasks": expected_tasks,
                    "result_coverage": 0.0,
                    "complete": False,
                    "answered_tasks": 0,
                    "no_answer_tasks": 0,
                    "governance_boundary_tasks": 0,
                    "boundary_tasks": 0,
                    "legacy_boundary_tasks": 0,
                    "isolation_tasks": 0,
                    "human_review_tasks": 0,
                    "external_restricted_tasks": 0,
                    "error_rate": 0.0,
                    "status_accuracy": 0.0,
                    "status_macro_f1": 0.0,
                    "status_balanced_accuracy": 0.0,
                    "status_per_class": {},
                    "status_confusion": {},
                    "task_success_rate": 0.0,
                    "evidence_precision": 0.0,
                    "evidence_recall": 0.0,
                    "evidence_f1": 0.0,
                    "containment_evidence_precision": 0.0,
                    "containment_evidence_recall": 0.0,
                    "containment_evidence_f1": 0.0,
                    "no_answer_correct": 0.0,
                    "governance_boundary_correct": 0.0,
                    "overall_boundary_correct": 0.0,
                    "boundary_correct": 0.0,
                    "legacy_boundary_correct": 0.0,
                    "contract_isolation": 0.0,
                    "human_review_routing": 0.0,
                    "external_violation_rate": 0.0,
                    "validation_failure_rate": 0.0,
                }
            )
        valid = [value for value in cases.values() if "error" not in value]
        total = sum(value["total_tasks"] for value in valid)
        expected_total = sum(value["expected_tasks"] for value in cases.values())
        aggregate = {
            "method": method,
            "total_tasks": total,
            "expected_tasks": expected_total,
            "missing_tasks": max(expected_total - total, 0),
            "result_coverage": round(total / expected_total, 4) if expected_total else 0.0,
            "complete": total == expected_total and all(
                value.get("complete", False) for value in cases.values()
            ),
            "cases": cases,
        }
        denominators = {
            "error_rate": "total_tasks",
            "status_accuracy": "total_tasks",
            "task_success_rate": "total_tasks",
            "evidence_precision": "answered_tasks",
            "evidence_recall": "answered_tasks",
            "evidence_f1": "answered_tasks",
            "containment_evidence_precision": "answered_tasks",
            "containment_evidence_recall": "answered_tasks",
            "containment_evidence_f1": "answered_tasks",
            "no_answer_correct": "no_answer_tasks",
            "governance_boundary_correct": "governance_boundary_tasks",
            "overall_boundary_correct": "boundary_tasks",
            "boundary_correct": "boundary_tasks",
            "legacy_boundary_correct": "legacy_boundary_tasks",
            "contract_isolation": "isolation_tasks",
            "human_review_routing": "human_review_tasks",
            "external_violation_rate": "external_restricted_tasks",
            "validation_failure_rate": "total_tasks",
        }
        for key, denominator_key in denominators.items():
            denominator = sum(value[denominator_key] for value in valid)
            aggregate[key] = round(
                sum(value[key] * value[denominator_key] for value in valid)
                / denominator
                if denominator
                else 0.0,
                4,
            )
        combined_confusion: Dict[str, Counter] = {
            label: Counter() for label in STATUS_LABELS
        }
        for value in valid:
            for gold, predictions in value.get("status_confusion", {}).items():
                combined_confusion.setdefault(gold, Counter()).update(predictions)
        aggregate_status = compute_status_metrics(combined_confusion)
        aggregate.update(aggregate_status)
        aggregate["status_confusion"] = {
            gold: dict(predictions)
            for gold, predictions in combined_confusion.items()
        }
        evaluations.append(aggregate)
    return evaluations
