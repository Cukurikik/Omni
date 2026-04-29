# Omni GUNDAM Data Management Engine
# Ref: GUNDAM-Labet/GUNDAM — Apache-2.0
from typing import List, Dict
def quality_score(sample: Dict, criteria: List[str]) -> float:
    score = 0
    for c in criteria:
        if c == "length" and len(sample.get("text","")) > 50: score += 1
        elif c == "diversity" and len(set(sample.get("text","").split())) > 10: score += 1
        elif c == "coherence": score += 0.5
    return round(score / max(len(criteria),1), 4)
def prioritize_data(samples: List[Dict], criteria: List[str], top_k: int = 100) -> List[Dict]:
    scored = [(s, quality_score(s, criteria)) for s in samples]
    scored.sort(key=lambda x: x[1], reverse=True)
    return [{"sample": s, "score": sc} for s, sc in scored[:top_k]]
def filter_low_quality(samples: List[Dict], threshold: float = 0.3) -> List[Dict]:
    return [s for s in samples if quality_score(s, ["length","diversity"]) >= threshold]
