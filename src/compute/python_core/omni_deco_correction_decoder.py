# Omni DeCo Dynamic Correction Decoder
# Compute Layer: Hallucination mitigation via dynamic correction decoding.
# Ref: zjunlp/Deco — ICLR 2025
# Key: Adjusts logit distribution during decoding based on visual grounding signals.
import math
from typing import List, Dict, Tuple

def compute_correction_weight(visual_confidence: float, text_confidence: float, alpha: float = 0.5) -> float:
    if visual_confidence < 0 or text_confidence < 0:
        return 0.0
    return alpha * visual_confidence + (1.0 - alpha) * text_confidence

def apply_dynamic_correction(logits: List[float], correction_mask: List[bool], penalty: float = 2.0) -> List[float]:
    if len(logits) != len(correction_mask):
        return logits
    corrected = []
    for i, logit in enumerate(logits):
        if correction_mask[i]:
            corrected.append(logit - penalty)
        else:
            corrected.append(logit)
    return corrected

def softmax(logits: List[float]) -> List[float]:
    max_l = max(logits) if logits else 0.0
    exps = [math.exp(l - max_l) for l in logits]
    total = sum(exps)
    if total == 0:
        return [1.0 / len(logits)] * len(logits)
    return [e / total for e in exps]

def deco_decode_step(logits: List[float], visual_scores: List[float], threshold: float = 0.3, penalty: float = 2.0) -> Dict:
    correction_mask = [vs < threshold for vs in visual_scores]
    corrected_logits = apply_dynamic_correction(logits, correction_mask, penalty)
    probs = softmax(corrected_logits)
    top_idx = max(range(len(probs)), key=lambda i: probs[i])
    return {
        "selected_token_idx": top_idx,
        "confidence": round(probs[top_idx], 8),
        "corrections_applied": sum(correction_mask),
        "total_tokens": len(logits),
    }

def detect_hallucination_risk(attention_weights: List[float], ctx_boundary: int) -> Dict:
    if not attention_weights or ctx_boundary <= 0:
        return {"risk": 0.0, "grounded": False}
    ctx_sum = sum(attention_weights[:ctx_boundary])
    total = sum(attention_weights)
    ratio = ctx_sum / total if total > 0 else 0.0
    return {"risk": round(1.0 - ratio, 8), "grounded": ratio > 0.5}
