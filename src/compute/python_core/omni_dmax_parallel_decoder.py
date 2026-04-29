# Omni DMax Aggressive Parallel Decoder
# Ref: czg1225/DMax — Apache-2.0
# Implements: Multi-token parallel decoding for diffusion LLMs with confidence masking
import math
from typing import List, Dict, Tuple

def confidence_mask(logits: List[float], threshold: float = 0.6) -> List[bool]:
    probs = softmax(logits)
    return [p >= threshold for p in probs]

def softmax(x: List[float]) -> List[float]:
    mx = max(x) if x else 0
    exps = [math.exp(v - mx) for v in x]
    s = sum(exps) or 1
    return [e / s for e in exps]

def parallel_decode_step(token_logits: List[List[float]], mask_threshold: float = 0.5,
                          max_tokens: int = 8) -> Dict:
    decoded = []; confidences = []
    for i, logits in enumerate(token_logits[:max_tokens]):
        probs = softmax(logits)
        best_idx = max(range(len(probs)), key=lambda j: probs[j])
        conf = probs[best_idx]
        if conf >= mask_threshold:
            decoded.append(best_idx); confidences.append(round(conf, 6))
        else:
            break
    return {"tokens": decoded, "confidences": confidences,
            "n_parallel": len(decoded), "speedup": round(len(decoded) / max(1, 1), 2)}

def dmax_aggressive_schedule(step: int, total_steps: int, base_tokens: int = 4) -> int:
    progress = step / max(total_steps, 1)
    if progress < 0.3: return min(base_tokens * 2, 16)
    if progress < 0.7: return base_tokens
    return max(base_tokens // 2, 1)

def compute_acceptance_rate(proposed: List[int], verified: List[int]) -> float:
    if not proposed: return 0.0
    accepted = sum(1 for p, v in zip(proposed, verified) if p == v)
    return round(accepted / len(proposed), 6)
