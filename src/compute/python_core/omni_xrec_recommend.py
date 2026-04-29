# Omni XRec Explainable Recommendation Engine
# Ref: HKUDS/XRec — EMNLP'24
from typing import List, Dict
import math

def user_item_score(user_emb: List[float], item_emb: List[float]) -> float:
    dot = sum(u*i for u, i in zip(user_emb, item_emb))
    return round(1.0 / (1.0 + math.exp(-dot)), 4)

def top_k_recommend(user_emb: List[float], items: List[Dict], k: int = 10) -> List[Dict]:
    scored = [(it, user_item_score(user_emb, it.get("emb", []))) for it in items]
    scored.sort(key=lambda x: x[1], reverse=True)
    return [{"item": it["id"], "score": sc} for it, sc in scored[:k]]

def explain_recommendation(user_profile: Dict, item: Dict) -> str:
    common = set(user_profile.get("interests",[])) & set(item.get("tags",[]))
    if common: return f"Recommended because you like {', '.join(list(common)[:3])}"
    return "Recommended based on similar user preferences"

def ndcg_at_k(ranked: List[bool], k: int = 10) -> float:
    dcg = sum((1 if r else 0) / math.log2(i+2) for i, r in enumerate(ranked[:k]))
    ideal = sorted(ranked[:k], reverse=True)
    idcg = sum((1 if r else 0) / math.log2(i+2) for i, r in enumerate(ideal))
    return round(dcg / max(idcg, 1e-8), 4)
