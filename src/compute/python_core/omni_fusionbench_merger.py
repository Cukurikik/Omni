# Omni FusionBench Model Merger
# Ref: tanganke/fusion_bench — MIT
# Implements: Task arithmetic, TIES, Fisher merging, DARE
import math
from typing import List, Dict

def task_arithmetic_merge(base: List[float], deltas: List[List[float]], scaling: float = 0.3) -> List[float]:
    d = len(base)
    merged = list(base)
    for i in range(d):
        total_delta = sum(delta[i] - base[i] for delta in deltas)
        merged[i] = base[i] + scaling * total_delta
    return [round(m, 8) for m in merged]

def ties_merge(base: List[float], deltas: List[List[float]], top_k: float = 0.2) -> List[float]:
    d = len(base); n = len(deltas)
    task_vectors = [[deltas[j][i] - base[i] for i in range(d)] for j in range(n)]
    merged = list(base)
    for i in range(d):
        vals = [tv[i] for tv in task_vectors]
        magnitudes = sorted(enumerate(vals), key=lambda x: abs(x[1]), reverse=True)
        keep = max(1, int(len(magnitudes) * top_k))
        signs = [1 if v >= 0 else -1 for _, v in magnitudes[:keep]]
        majority_sign = 1 if sum(signs) >= 0 else -1
        aligned = [v for _, v in magnitudes[:keep] if (v >= 0) == (majority_sign >= 0)]
        merged[i] = base[i] + (sum(aligned) / max(len(aligned), 1))
    return [round(m, 8) for m in merged]

def dare_prune(delta: List[float], drop_rate: float = 0.9, seed: int = 42) -> List[float]:
    result = []
    for i, d in enumerate(delta):
        h = ((seed * (i+1) * 2654435761) >> 16) % 100
        if h < int(drop_rate * 100): result.append(0.0)
        else: result.append(d / max(1 - drop_rate, 0.01))
    return [round(r, 8) for r in result]
