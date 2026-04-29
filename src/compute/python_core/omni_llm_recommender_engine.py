# Omni LLM-Enhanced Recommender Engine
# Ref: liuqidong07/Awesome-LLM-Enhanced-Recommender-Systems — KDD'25
# Implements: Knowledge/Interaction/Model enhancement taxonomy
import math
from typing import List, Dict, Tuple

def cosine_similarity(a: List[float], b: List[float]) -> float:
    dot = sum(x * y for x, y in zip(a, b))
    na = math.sqrt(sum(x * x for x in a)) or 1e-9
    nb = math.sqrt(sum(y * y for y in b)) or 1e-9
    return round(dot / (na * nb), 8)

def knowledge_enhance_score(user_profile_emb: List[float], item_text_emb: List[float],
                            kg_emb: List[float], alpha: float = 0.6) -> float:
    text_sim = cosine_similarity(user_profile_emb, item_text_emb)
    kg_sim = cosine_similarity(user_profile_emb, kg_emb)
    return round(alpha * text_sim + (1 - alpha) * kg_sim, 8)

def interaction_enhance(user_items: List[int], augmented_items: List[int],
                        confidence: float = 0.8) -> List[Tuple[int, float]]:
    original = set(user_items)
    return [(item, confidence) for item in augmented_items if item not in original]

def model_distill_loss(teacher_logits: List[float], student_logits: List[float],
                       temperature: float = 2.0) -> float:
    t_soft = [math.exp(l / temperature) for l in teacher_logits]
    s_soft = [math.exp(l / temperature) for l in student_logits]
    t_sum = sum(t_soft) or 1e-9; s_sum = sum(s_soft) or 1e-9
    kl = sum((t / t_sum) * math.log((t / t_sum) / max(s / s_sum, 1e-12))
             for t, s in zip(t_soft, s_soft) if t > 0)
    return round(kl * temperature * temperature, 8)

def rank_items(user_emb: List[float], item_embs: List[Tuple[int, List[float]]],
               top_k: int = 10) -> List[Tuple[int, float]]:
    scored = [(iid, cosine_similarity(user_emb, emb)) for iid, emb in item_embs]
    scored.sort(key=lambda x: x[1], reverse=True)
    return scored[:top_k]
