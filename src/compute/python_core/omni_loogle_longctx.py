# Omni LooGLE Long Context Evaluator
# Ref: bigai-nlco/LooGLE — ACL 2024, MIT
from typing import List, Dict

TASK_TYPES = ["short_dependency_qa", "long_dependency_qa", "timeline_reorder",
              "computation", "comprehension", "summarization"]

def evaluate_long_context(prediction: str, reference: str, metric: str = "f1") -> Dict:
    pred_tokens = set(prediction.lower().split())
    ref_tokens = set(reference.lower().split())
    if metric == "exact_match":
        return {"score": 1.0 if prediction.strip().lower() == reference.strip().lower() else 0.0}
    tp = len(pred_tokens & ref_tokens)
    precision = tp / max(len(pred_tokens), 1)
    recall = tp / max(len(ref_tokens), 1)
    f1 = 2 * precision * recall / max(precision + recall, 1e-9)
    return {"precision": round(precision, 4), "recall": round(recall, 4), "f1": round(f1, 4)}

def context_length_bucket(n_tokens: int) -> str:
    if n_tokens < 4096: return "short"
    if n_tokens < 16384: return "medium"
    if n_tokens < 65536: return "long"
    return "ultra_long"

def aggregate_by_task(results: List[Dict]) -> Dict:
    by_task = {}
    for r in results:
        task = r.get("task_type", "unknown")
        by_task.setdefault(task, []).append(r.get("f1", 0))
    return {t: round(sum(v)/max(len(v),1), 4) for t, v in by_task.items()}
