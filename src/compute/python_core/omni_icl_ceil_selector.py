# Omni ICL-CEIL Compositional Exemplar Selector
# Ref: HKUNLP/icl-ceil — ICML 2023, Apache-2.0
import math
from typing import List, Dict, Tuple

def dpp_kernel(embeddings: List[List[float]]) -> List[List[float]]:
    n = len(embeddings); d = len(embeddings[0]) if embeddings else 0
    kernel = [[0.0] * n for _ in range(n)]
    for i in range(n):
        for j in range(n):
            kernel[i][j] = sum(embeddings[i][k] * embeddings[j][k] for k in range(d))
    return kernel

def greedy_dpp_select(kernel: List[List[float]], k: int) -> List[int]:
    n = len(kernel); selected = []; remaining = list(range(n))
    for _ in range(min(k, n)):
        best_idx, best_score = -1, -float('inf')
        for i in remaining:
            det_gain = kernel[i][i] - sum(kernel[i][s] ** 2 / max(kernel[s][s], 1e-9) for s in selected)
            if det_gain > best_score: best_score = det_gain; best_idx = i
        if best_idx >= 0: selected.append(best_idx); remaining.remove(best_idx)
    return selected

def compose_icl_prompt(exemplars: List[Dict], query: str) -> str:
    parts = [f"Input: {e['input']}\nOutput: {e['output']}" for e in exemplars]
    return "\n\n".join(parts) + f"\n\nInput: {query}\nOutput:"
