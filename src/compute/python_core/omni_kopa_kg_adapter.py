# Omni KoPA Knowledge Prefix Adapter
# Ref: zjukg/KoPA — ACM MM 2024
# Implements: Structural embedding to virtual knowledge tokens for KG completion
import math
from typing import List, Dict, Tuple

def structural_embedding(entity_id: int, neighbors: List[int], embedding_dim: int = 64) -> List[float]:
    emb = [math.sin(entity_id * (i + 1) * 0.01) for i in range(embedding_dim)]
    for n in neighbors:
        for i in range(embedding_dim):
            emb[i] += math.cos(n * (i + 1) * 0.007) / max(len(neighbors), 1)
    norm = math.sqrt(sum(e * e for e in emb)) or 1
    return [round(e / norm, 8) for e in emb]

def knowledge_prefix_adapter(struct_emb: List[float], proj_matrix: List[List[float]]) -> List[float]:
    out_dim = len(proj_matrix[0]) if proj_matrix else 0
    return [round(sum(struct_emb[j] * proj_matrix[j][i] for j in range(min(len(struct_emb), len(proj_matrix)))), 8)
            for i in range(out_dim)]

def kgc_score(head_emb: List[float], rel_emb: List[float], tail_emb: List[float]) -> float:
    d = min(len(head_emb), len(rel_emb), len(tail_emb))
    score = sum((head_emb[i] + rel_emb[i] - tail_emb[i]) ** 2 for i in range(d))
    return round(-score, 6)

def rank_candidates(head: List[float], rel: List[float], candidates: List[Tuple[str, List[float]]],
                     top_k: int = 10) -> List[Tuple[str, float]]:
    scored = [(cid, kgc_score(head, rel, emb)) for cid, emb in candidates]
    scored.sort(key=lambda x: x[1], reverse=True)
    return scored[:top_k]
