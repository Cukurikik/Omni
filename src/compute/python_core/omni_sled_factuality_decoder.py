# Omni SLED Factuality Decoder
# Compute: Self Logits Evolution Decoding for improving LLM factuality.
# Ref: JayZhang42/SLED — Self Logits Evolution
import math
from typing import List, Dict

def compute_logit_evolution(early_logits: List[float], late_logits: List[float], alpha: float = 1.5) -> List[float]:
    if len(early_logits) != len(late_logits): return late_logits
    return [late + alpha * (late - early) for early, late in zip(early_logits, late_logits)]

def sled_decode_step(base_logits: List[float], evolved_logits: List[float]) -> Dict:
    probs = softmax_vec(evolved_logits)
    top_idx = max(range(len(probs)), key=lambda i: probs[i])
    entropy = -sum(p * math.log(max(p, 1e-12)) for p in probs)
    return {"token_idx": top_idx, "confidence": round(probs[top_idx], 8), "entropy": round(entropy, 6)}

def softmax_vec(logits: List[float]) -> List[float]:
    mx = max(logits) if logits else 0
    exps = [math.exp(l - mx) for l in logits]
    s = sum(exps)
    return [e / max(s, 1e-12) for e in exps]

def factuality_improvement(base_acc: float, sled_acc: float) -> float:
    return round(sled_acc - base_acc, 6)
