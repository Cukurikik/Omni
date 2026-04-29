# Omni ChatGPT IE Evaluator
# Compute Layer: Information Extraction evaluation (NER, RE, ED, ET).
# Ref: pkuserc/ChatGPT_for_IE — Performance, Explainability, Calibration, Faithfulness.
from typing import List, Dict, Set, Tuple

def precision_recall_f1(predictions: Set[str], ground_truth: Set[str]) -> Dict:
    if not predictions and not ground_truth:
        return {"precision": 1.0, "recall": 1.0, "f1": 1.0}
    tp = len(predictions & ground_truth)
    precision = tp / len(predictions) if predictions else 0.0
    recall = tp / len(ground_truth) if ground_truth else 0.0
    f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0.0
    return {"precision": round(precision, 6), "recall": round(recall, 6), "f1": round(f1, 6)}

def evaluate_ner(predictions: List[Dict], ground_truth: List[Dict]) -> Dict:
    pred_set = {(e["text"], e["label"]) for e in predictions}
    gt_set = {(e["text"], e["label"]) for e in ground_truth}
    return precision_recall_f1(pred_set, gt_set)

def evaluate_relation_extraction(pred_triples: List[Tuple], gt_triples: List[Tuple]) -> Dict:
    return precision_recall_f1(set(pred_triples), set(gt_triples))

def calibration_error(confidences: List[float], correctness: List[bool], n_bins: int = 10) -> float:
    if not confidences or len(confidences) != len(correctness):
        return 0.0
    bins = [[] for _ in range(n_bins)]
    for c, correct in zip(confidences, correctness):
        idx = min(int(c * n_bins), n_bins - 1)
        bins[idx].append((c, 1.0 if correct else 0.0))
    ece = 0.0
    total = len(confidences)
    for b in bins:
        if not b:
            continue
        avg_conf = sum(x[0] for x in b) / len(b)
        avg_acc = sum(x[1] for x in b) / len(b)
        ece += (len(b) / total) * abs(avg_conf - avg_acc)
    return round(ece, 8)
