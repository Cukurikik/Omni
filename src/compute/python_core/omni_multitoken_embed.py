# Omni MultiToken Embedding Engine
# Ref: sshh12/multi_token — Apache-2.0
import math
from typing import List, Dict
def project_modality(features: List[float], proj: List[List[float]]) -> List[float]:
    d = len(proj[0]) if proj else 0
    return [round(sum(features[j]*proj[j][i] for j in range(min(len(features),len(proj)))),8) for i in range(d)]
def cosine_similarity(a: List[float], b: List[float]) -> float:
    dot = sum(x*y for x,y in zip(a,b))
    na = math.sqrt(sum(x**2 for x in a)) or 1; nb = math.sqrt(sum(x**2 for x in b)) or 1
    return round(dot/(na*nb), 4)
def multi_token_expand(embedding: List[float], n_tokens: int) -> List[List[float]]:
    d = len(embedding); chunk = max(1, d // n_tokens)
    return [embedding[i*chunk:(i+1)*chunk] for i in range(n_tokens)]
