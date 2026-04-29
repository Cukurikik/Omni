# Omni HALC Adaptive Focal-Contrast Decoder
# Ref: BillChan226/HALC — ICML'24
# Implements: Focal grounding, contrast scoring, matching-based beam search
import math
from typing import List, Dict, Tuple

def focal_contrast_score(original_logits: List[float], focal_logits: List[float],
                          alpha: float = 0.5) -> List[float]:
    return [round(o + alpha * (f - o), 8) for o, f in zip(original_logits, focal_logits)]

def visual_matching_score(token_emb: List[float], region_embs: List[List[float]]) -> float:
    if not region_embs: return 0.0
    best = -1.0
    for r in region_embs:
        dot = sum(a * b for a, b in zip(token_emb, r))
        na = math.sqrt(sum(a * a for a in token_emb)) or 1
        nb = math.sqrt(sum(b * b for b in r)) or 1
        best = max(best, dot / (na * nb))
    return round(best, 8)

def beam_search_step(beams: List[Tuple[List[int], float]], candidates: List[Tuple[int, float]],
                      visual_scores: List[float], beam_width: int = 5,
                      lam: float = 0.3) -> List[Tuple[List[int], float]]:
    new_beams = []
    for seq, score in beams:
        for tid, logit in candidates:
            vs = visual_scores[tid] if tid < len(visual_scores) else 0
            combined = score + logit + lam * vs
            new_beams.append((seq + [tid], combined))
    new_beams.sort(key=lambda x: x[1], reverse=True)
    return new_beams[:beam_width]

def halc_decode(logits: List[float], focal_logits: List[float],
                region_embs: List[List[float]], token_embs: List[List[float]]) -> Dict:
    adjusted = focal_contrast_score(logits, focal_logits)
    best_idx = max(range(len(adjusted)), key=lambda i: adjusted[i])
    vs = visual_matching_score(token_embs[best_idx] if best_idx < len(token_embs) else [],
                                region_embs)
    return {"token_id": best_idx, "adjusted_logit": adjusted[best_idx],
            "visual_match": vs, "hallucination_risk": round(max(0, 1 - vs), 6)}
