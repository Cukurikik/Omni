# Omni RecLM Instruction Tuner
# Ref: HKUDS/RecLM — ACL2025
# Implements: Two-turn collaborative instruction tuning with RL reward
import math
from typing import List, Dict, Tuple

def build_two_turn_prompt(user_history: List[str], item_meta: str) -> str:
    history_str = ", ".join(user_history[-10:])
    return (f"Turn 1: User has interacted with [{history_str}]. "
            f"Turn 2: Based on collaborative patterns, describe the profile for: {item_meta}")

def collaborative_profile_score(user_emb: List[float], item_emb: List[float],
                                 neighbor_embs: List[List[float]], alpha: float = 0.3) -> float:
    direct = sum(a * b for a, b in zip(user_emb, item_emb))
    if neighbor_embs:
        neighbor_avg = [sum(n[d] for n in neighbor_embs) / len(neighbor_embs) for d in range(len(user_emb))]
        neighbor_sim = sum(a * b for a, b in zip(user_emb, neighbor_avg))
    else:
        neighbor_sim = 0
    return round(direct + alpha * neighbor_sim, 6)

def ppo_reward(predicted_rank: int, ground_truth_rank: int, max_rank: int = 100) -> float:
    if predicted_rank <= ground_truth_rank: return 1.0 - predicted_rank / max_rank
    return -0.5 * (predicted_rank - ground_truth_rank) / max_rank

def anti_oversmooth_loss(embeddings: List[List[float]], temperature: float = 0.07) -> float:
    if len(embeddings) < 2: return 0.0
    n = len(embeddings); d = len(embeddings[0])
    total = 0.0
    for i in range(n):
        for j in range(i + 1, n):
            sim = sum(embeddings[i][k] * embeddings[j][k] for k in range(d))
            total += math.exp(sim / temperature)
    return round(-math.log(total / max(n * (n - 1) / 2, 1) + 1e-9), 6)
