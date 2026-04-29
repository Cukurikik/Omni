# Omni UoT Uncertainty-Aware Planner
# Ref: zhiyuanhubj/UoT — NeurIPS 2024
# Implements: Uncertainty simulation, information-gain rewards, reward propagation
import math
from typing import List, Dict, Tuple

def entropy(probs: List[float]) -> float:
    return round(-sum(p * math.log2(max(p, 1e-12)) for p in probs if p > 0), 6)

def information_gain(prior: List[float], posterior: List[float]) -> float:
    return round(max(entropy(prior) - entropy(posterior), 0), 6)

def simulate_outcomes(hypothesis_probs: List[float], question_relevance: List[float]) -> List[float]:
    updated = []
    for h, r in zip(hypothesis_probs, question_relevance):
        updated.append(h * r)
    total = sum(updated) or 1
    return [round(u / total, 6) for u in updated]

def select_best_question(questions: List[Dict], hypotheses: List[float]) -> Dict:
    best_q, best_ig = None, -1
    for q in questions:
        posterior = simulate_outcomes(hypotheses, q.get("relevance", [1.0] * len(hypotheses)))
        ig = information_gain(hypotheses, posterior)
        if ig > best_ig: best_ig = ig; best_q = q
    return {"question": best_q, "expected_info_gain": best_ig}

def propagate_reward(tree: List[Dict], gamma: float = 0.9) -> List[float]:
    n = len(tree); rewards = [t.get("reward", 0) for t in tree]
    for i in range(n - 2, -1, -1):
        rewards[i] += gamma * rewards[i + 1] if i + 1 < n else 0
    return [round(r, 6) for r in rewards]
