# Omni ML CTF Challenge Engine
# Ref: alexdevassy/Machine_Learning_CTF_Challenges
from typing import List, Dict
import math

def fgsm_perturbation(input_features: List[float], gradient: List[float], epsilon: float = 0.01) -> List[float]:
    return [round(x + epsilon * (1 if g >= 0 else -1), 8) for x, g in zip(input_features, gradient)]

def detect_adversarial(original: List[float], perturbed: List[float], threshold: float = 0.1) -> bool:
    dist = math.sqrt(sum((a-b)**2 for a, b in zip(original, perturbed)))
    return dist > threshold

def model_extraction_query(query_budget: int, input_dim: int) -> List[List[float]]:
    queries = []
    for i in range(query_budget):
        q = [0.0] * input_dim
        q[i % input_dim] = 1.0
        queries.append(q)
    return queries

def evaluate_ctf(challenge_id: str, submitted_flag: str, correct_flag: str) -> Dict:
    return {"challenge": challenge_id, "correct": submitted_flag == correct_flag,
            "score": 100 if submitted_flag == correct_flag else 0}
