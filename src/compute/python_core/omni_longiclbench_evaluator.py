# Omni LongICLBench Evaluator
# Ref: TIGER-AI-Lab/LongICLBench — MIT
from typing import List, Dict

def evaluate_icl(predictions: List[str], labels: List[str]) -> Dict:
    correct = sum(1 for p, l in zip(predictions, labels) if p.strip() == l.strip())
    return {"accuracy": round(correct / max(len(labels), 1), 6), "n": len(labels)}

def context_length_bucket(n_examples: int) -> str:
    if n_examples <= 10: return "short"
    if n_examples <= 50: return "medium"
    return "long"

def aggregate_by_bucket(results: List[Dict]) -> Dict:
    buckets: Dict[str, List] = {}
    for r in results:
        b = r.get("bucket", "unknown")
        buckets.setdefault(b, []).append(r.get("accuracy", 0))
    return {b: round(sum(v)/max(len(v),1), 6) for b, v in buckets.items()}
