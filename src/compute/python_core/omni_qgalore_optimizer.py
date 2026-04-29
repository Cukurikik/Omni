# Omni Q-GaLore Quantized Low-Rank Optimizer
# Ref: VITA-Group/Q-GaLore — Apache-2.0
# Implements: INT4 quantized projection, layer-adaptive rank, GaLore update
import math
from typing import List, Dict

def int4_quantize(values: List[float]) -> Dict:
    vmin = min(values) if values else 0; vmax = max(values) if values else 0
    scale = (vmax - vmin) / 15 if vmax != vmin else 1
    quantized = [max(0, min(15, round((v - vmin) / scale))) for v in values]
    return {"quantized": quantized, "scale": round(scale, 8), "zero_point": round(vmin, 8)}

def int4_dequantize(qdata: Dict) -> List[float]:
    return [round(q * qdata["scale"] + qdata["zero_point"], 8) for q in qdata["quantized"]]

def layer_adaptive_rank(grad_norms: List[float], base_rank: int = 64, budget: int = 512) -> List[int]:
    total = sum(grad_norms) or 1
    ranks = [max(1, int(base_rank * (gn / total) * len(grad_norms))) for gn in grad_norms]
    while sum(ranks) > budget:
        max_idx = max(range(len(ranks)), key=lambda i: ranks[i])
        ranks[max_idx] = max(1, ranks[max_idx] - 1)
    return ranks

def qgalore_update(params: List[float], gradient: List[float], rank: int,
                    lr: float = 0.001, seed: int = 42) -> List[float]:
    d = len(params)
    proj = [0.0] * rank
    scale = 1.0 / math.sqrt(rank)
    for i in range(d):
        h = ((seed * (i+1) * 2654435761) >> 16) % rank
        sign = 1.0 if ((seed * (i+1) * 2246822519) >> 17) % 2 == 0 else -1.0
        proj[h] += gradient[i] * sign * scale
    qproj = int4_quantize(proj)
    deq = int4_dequantize(qproj)
    updated = list(params)
    for i in range(d):
        h = ((seed * (i+1) * 2654435761) >> 16) % rank
        sign = 1.0 if ((seed * (i+1) * 2246822519) >> 17) % 2 == 0 else -1.0
        updated[i] -= lr * deq[h] * sign * math.sqrt(rank)
    return [round(u, 8) for u in updated]
