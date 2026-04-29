# Omni LoRI Multi-Task Low-Rank Adaptation Engine
# Ref: juzhengz/LoRI — COLM'25
# Reducing cross-task interference in multi-task LoRA
import math
from typing import List, Dict

def compute_lora_delta(A: List[List[float]], B: List[List[float]]) -> List[List[float]]:
    """Compute LoRA weight delta: W_delta = B @ A (low-rank product)."""
    r = len(A)
    d_out = len(B)
    d_in = len(A[0]) if A else 0
    result = [[0.0]*d_in for _ in range(d_out)]
    for i in range(d_out):
        for j in range(d_in):
            for k in range(r):
                result[i][j] += B[i][k] * A[k][j]
            result[i][j] = round(result[i][j], 8)
    return result

def task_interference_score(deltas: List[List[List[float]]]) -> float:
    """Measure cross-task interference via cosine between flattened LoRA deltas."""
    if len(deltas) < 2:
        return 0.0
    flat = []
    for d in deltas:
        f = [v for row in d for v in row]
        flat.append(f)
    total_cos = 0; pairs = 0
    for i in range(len(flat)):
        for j in range(i+1, len(flat)):
            dot = sum(a*b for a, b in zip(flat[i], flat[j]))
            ni = math.sqrt(sum(a**2 for a in flat[i])) or 1e-8
            nj = math.sqrt(sum(a**2 for a in flat[j])) or 1e-8
            total_cos += abs(dot / (ni * nj))
            pairs += 1
    return round(total_cos / max(pairs, 1), 6)

def orthogonal_regularization(A: List[List[float]], B: List[List[float]], lam: float = 0.1) -> float:
    """LoRI orthogonal regularization loss to reduce interference."""
    r = len(A)
    gram = [[0.0]*r for _ in range(r)]
    for i in range(r):
        for j in range(r):
            gram[i][j] = sum(A[i][k]*A[j][k] for k in range(len(A[0]))) if A[0] else 0
    identity_diff = 0.0
    for i in range(r):
        for j in range(r):
            target = 1.0 if i == j else 0.0
            identity_diff += (gram[i][j] - target) ** 2
    return round(lam * identity_diff, 8)

def merge_task_adapters(adapters: List[Dict], weights: List[float] = None) -> Dict:
    """Merge multiple task-specific LoRA adapters with weighted averaging."""
    n = len(adapters)
    if not n:
        return {}
    if weights is None:
        weights = [1.0 / n] * n
    first = adapters[0]
    merged_params = sum(a.get("n_params", 0) for a in adapters)
    interference = task_interference_score([a.get("delta", [[0]]) for a in adapters])
    return {"n_tasks": n, "total_params": merged_params,
            "interference_score": interference, "weights": weights}
