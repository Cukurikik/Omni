# Omni SelfAware Calibration Engine
# Ref: yinzhangyue/SelfAware — Apache-2.0
import math
from typing import List, Dict

def classify_answerability(question: str, known_topics: List[str]) -> Dict:
    q_words = set(question.lower().split())
    overlap = sum(1 for t in known_topics if any(w in q_words for w in t.lower().split()))
    confidence = min(overlap / max(len(known_topics), 1) * 5, 1.0)
    return {"answerable": confidence > 0.3, "confidence": round(confidence, 4)}

def expected_calibration_error(predictions: List[Dict], n_bins: int = 10) -> float:
    bins = [[] for _ in range(n_bins)]
    for p in predictions:
        idx = min(int(p["confidence"] * n_bins), n_bins - 1)
        bins[idx].append(p)
    ece = 0; total = len(predictions)
    for b in bins:
        if not b: continue
        avg_conf = sum(p["confidence"] for p in b) / len(b)
        accuracy = sum(1 for p in b if p.get("correct", False)) / len(b)
        ece += len(b) / total * abs(avg_conf - accuracy)
    return round(ece, 6)

def idk_rate(predictions: List[Dict]) -> float:
    idk = sum(1 for p in predictions if not p.get("answerable", True))
    return round(idk / max(len(predictions), 1), 4)
