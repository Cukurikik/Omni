# Omni Mechanistic Interpretability Engine
# Ref: itsqyh/Awesome-LMMs-Mechanistic-Interpretability
import math
from typing import List, Dict
def attention_entropy(attn_weights: List[float]) -> float:
    return round(-sum(w * math.log(max(w,1e-10)) for w in attn_weights if w > 0), 6)
def probe_linear(activations: List[float], probe_weights: List[float], bias: float = 0) -> float:
    return round(sum(a*w for a,w in zip(activations, probe_weights)) + bias, 6)
def feature_attribution(input_tokens: List[str], attribution_scores: List[float]) -> List[Dict]:
    return [{"token": t, "score": round(s,4)} for t,s in zip(input_tokens, attribution_scores)]
def circuit_discovery(layer_activations: List[List[float]], threshold: float = 0.8) -> Dict:
    active = []
    for i, acts in enumerate(layer_activations):
        max_act = max(abs(a) for a in acts) if acts else 0
        if max_act > threshold: active.append(i)
    return {"active_layers": active, "n_active": len(active), "total_layers": len(layer_activations)}
