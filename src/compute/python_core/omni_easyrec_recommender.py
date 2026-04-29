# Omni EasyRec LLM Recommender
# Compute Layer: Language model collaborative filtering for recommendation.
# Ref: HKUDS/EasyRec — EMNLP 2025
# Uses text-based item representations with contrastive alignment.
import math, hashlib
from typing import List, Dict, Tuple

def cosine_similarity(a: List[float], b: List[float]) -> float:
    if len(a) != len(b) or not a:
        return 0.0
    dot = sum(x * y for x, y in zip(a, b))
    norm_a = math.sqrt(sum(x * x for x in a))
    norm_b = math.sqrt(sum(x * x for x in b))
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return dot / (norm_a * norm_b)

def contrastive_loss(anchor: List[float], positive: List[float], negatives: List[List[float]], temperature: float = 0.07) -> float:
    pos_sim = cosine_similarity(anchor, positive) / temperature
    neg_sims = [cosine_similarity(anchor, n) / temperature for n in negatives]
    max_val = max([pos_sim] + neg_sims)
    exp_pos = math.exp(pos_sim - max_val)
    exp_neg_sum = sum(math.exp(ns - max_val) for ns in neg_sims)
    denom = exp_pos + exp_neg_sum
    if denom == 0:
        return 0.0
    return -math.log(exp_pos / denom)

def recommend_items(user_embedding: List[float], item_embeddings: List[Dict], top_k: int = 10) -> List[Dict]:
    scored = []
    for item in item_embeddings:
        emb = item.get("embedding", [])
        sim = cosine_similarity(user_embedding, emb)
        scored.append({"item_id": item.get("id", ""), "score": round(sim, 8)})
    scored.sort(key=lambda x: x["score"], reverse=True)
    return scored[:top_k]

def build_text_profile(interactions: List[str]) -> str:
    return " | ".join(interactions[-20:]) if interactions else ""
