# Omni GraphTranslator Aligner
# Compute: Align graph model embeddings to LLM token space.
# Ref: alibaba/GraphTranslator — BSD-3
import math
from typing import Dict, List

def project_graph_to_text(graph_emb: List[float], projection_matrix: List[List[float]]) -> List[float]:
    d_out = len(projection_matrix[0]) if projection_matrix else 0
    result = [0.0] * d_out
    for i, g in enumerate(graph_emb):
        if i < len(projection_matrix):
            for j in range(d_out): result[j] += g * projection_matrix[i][j]
    return result

def contrastive_graph_text_loss(graph_embs: List[List[float]], text_embs: List[List[float]], temp: float = 0.07) -> float:
    n = min(len(graph_embs), len(text_embs))
    if n == 0: return 0.0
    loss = 0.0
    for i in range(n):
        dot_pos = sum(a*b for a, b in zip(graph_embs[i], text_embs[i]))
        exp_pos = math.exp(dot_pos / temp)
        exp_sum = sum(math.exp(sum(a*b for a, b in zip(graph_embs[i], text_embs[j])) / temp) for j in range(n))
        loss += -math.log(exp_pos / max(exp_sum, 1e-10))
    return round(loss / n, 6)
