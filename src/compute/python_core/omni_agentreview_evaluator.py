# Omni AgentReview Peer Review Simulator
# Ref: Ahren09/AgentReview — EMNLP'24
from typing import List, Dict

def compute_review_score(clarity: float, novelty: float, soundness: float,
                          significance: float) -> float:
    return round(0.25 * clarity + 0.3 * novelty + 0.3 * soundness + 0.15 * significance, 4)

def aggregate_reviews(reviews: List[Dict]) -> Dict:
    if not reviews: return {"decision": "reject", "mean_score": 0}
    scores = [r.get("overall", 0) for r in reviews]
    mean = sum(scores) / len(scores)
    decision = "accept" if mean >= 6.0 else "borderline" if mean >= 4.5 else "reject"
    return {"decision": decision, "mean_score": round(mean, 2), "n_reviews": len(reviews)}

def detect_bias(reviews: List[Dict]) -> Dict:
    scores = [r.get("overall", 5) for r in reviews]
    if len(scores) < 2: return {"variance": 0, "biased": False}
    mean = sum(scores) / len(scores)
    var = sum((s - mean)**2 for s in scores) / len(scores)
    return {"variance": round(var, 4), "biased": var > 4.0}
