# Omni UHGEval Hallucination Evaluation Engine
# Ref: IAAR-Shanghai/UHGEval — ACL'24 | Apache-2.0
# Unified hallucination evaluation framework
from typing import List, Dict
import math

def detect_hallucination_discriminative(response: str, reference: str) -> Dict:
    """Discriminative hallucination detection via token overlap."""
    resp_tokens = set(response.lower().split())
    ref_tokens = set(reference.lower().split())
    if not ref_tokens:
        return {"hallucination_ratio": 1.0, "grounded_ratio": 0.0}
    grounded = len(resp_tokens & ref_tokens)
    ungrounded = len(resp_tokens - ref_tokens)
    total = max(len(resp_tokens), 1)
    return {
        "hallucination_ratio": round(ungrounded / total, 4),
        "grounded_ratio": round(grounded / total, 4),
        "n_grounded_tokens": grounded, "n_ungrounded_tokens": ungrounded
    }

def selective_generation_score(responses: List[Dict]) -> Dict:
    """Compute selective generation metrics: abstention rate and quality."""
    abstained = sum(1 for r in responses if r.get("abstained", False))
    answered = len(responses) - abstained
    correct_when_answered = sum(1 for r in responses if not r.get("abstained", False) and r.get("correct", False))
    return {
        "abstention_rate": round(abstained / max(len(responses), 1), 4),
        "accuracy_when_answered": round(correct_when_answered / max(answered, 1), 4),
        "n_total": len(responses)
    }

def hallucination_category_analysis(samples: List[Dict]) -> Dict:
    """Categorize hallucinations: factual, faithfulness, or intrinsic."""
    cats = {"factual": 0, "faithfulness": 0, "intrinsic": 0}
    for s in samples:
        cat = s.get("category", "factual")
        if cat in cats:
            cats[cat] += 1
    total = max(sum(cats.values()), 1)
    return {k: round(v / total, 4) for k, v in cats.items()}

def uhg_benchmark_score(results: List[Dict]) -> Dict:
    """Compute overall UHGEval benchmark score."""
    if not results:
        return {"uhg_score": 0, "n_tasks": 0}
    task_scores = [r.get("score", 0) for r in results]
    return {
        "uhg_score": round(sum(task_scores) / len(task_scores), 4),
        "n_tasks": len(results),
        "min_score": round(min(task_scores), 4),
        "max_score": round(max(task_scores), 4)
    }
