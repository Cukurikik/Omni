# Omni ICSFSurvey Self-Correction Engine
# Ref: IAAR-Shanghai/ICSFSurvey — Self-correction/refinement
from typing import List, Dict

def self_consistency_vote(answers: List[str]) -> Dict:
    freq = {}
    for a in answers: freq[a] = freq.get(a, 0) + 1
    winner = max(freq, key=freq.get) if freq else ""
    return {"consensus": winner, "confidence": round(freq.get(winner,0)/max(len(answers),1), 4), "n_candidates": len(set(answers))}

def self_refine_iteration(response: str, feedback: str) -> Dict:
    improved = len(feedback.split()) > 5
    return {"original_len": len(response.split()), "feedback_len": len(feedback.split()), "refined": improved}

def internal_consistency_score(responses: List[str]) -> float:
    if len(responses) < 2: return 1.0
    tokens_sets = [set(r.lower().split()) for r in responses]
    overlap = 0; pairs = 0
    for i in range(len(tokens_sets)):
        for j in range(i+1, len(tokens_sets)):
            pairs += 1; overlap += len(tokens_sets[i]&tokens_sets[j])/max(len(tokens_sets[i]|tokens_sets[j]),1)
    return round(overlap / max(pairs, 1), 4)
