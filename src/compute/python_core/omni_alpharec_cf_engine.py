# Omni AlphaRec CF Engine
# Ref: LehengTHU/AlphaRec — ICLR 2025 Oral
# Implements: Language-representation CF with MLP + Graph Conv + Contrastive Loss
import math
from typing import List, Dict, Tuple

def mlp_transform(x: List[float], w1: List[List[float]], w2: List[List[float]]) -> List[float]:
    hidden = [max(0, sum(x[j] * w1[j][i] for j in range(len(x)))) for i in range(len(w1[0]))]
    return [sum(hidden[j] * w2[j][i] for j in range(len(hidden))) for i in range(len(w2[0]))]

def graph_conv(node_emb: List[float], neighbor_embs: List[List[float]], self_weight: float = 0.5) -> List[float]:
    if not neighbor_embs: return node_emb
    d = len(node_emb)
    agg = [sum(n[i] for n in neighbor_embs) / len(neighbor_embs) for i in range(d)]
    return [round(self_weight * node_emb[i] + (1 - self_weight) * agg[i], 8) for i in range(d)]

def contrastive_loss(anchor: List[float], positive: List[float],
                      negatives: List[List[float]], temp: float = 0.07) -> float:
    def sim(a, b): return sum(x * y for x, y in zip(a, b))
    pos_score = math.exp(sim(anchor, positive) / temp)
    neg_sum = sum(math.exp(sim(anchor, neg) / temp) for neg in negatives)
    return round(-math.log(pos_score / max(pos_score + neg_sum, 1e-9)), 6)

def zero_shot_recommend(query_emb: List[float], item_embs: List[Tuple[str, List[float]]],
                         top_k: int = 10) -> List[Tuple[str, float]]:
    scored = []
    for iid, emb in item_embs:
        dot = sum(a * b for a, b in zip(query_emb, emb))
        na = math.sqrt(sum(a * a for a in query_emb)) or 1
        nb = math.sqrt(sum(b * b for b in emb)) or 1
        scored.append((iid, round(dot / (na * nb), 8)))
    scored.sort(key=lambda x: x[1], reverse=True)
    return scored[:top_k]
