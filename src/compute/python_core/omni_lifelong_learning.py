# Omni Lifelong Learning LLM Engine
# Ref: zzz47zzz/awesome-lifelong-learning-methods-for-llm
from typing import List, Dict
import math

def calculate_catastrophic_forgetting(baseline_accuracy: float, new_task_accuracy: float, old_task_retest_accuracy: float) -> dict:
    """Calculate the extent of catastrophic forgetting after learning a new task."""
    forgetting = baseline_accuracy - old_task_retest_accuracy
    plasticity = new_task_accuracy
    stability = 1.0 - max(0.0, forgetting)
    
    # Harmonic mean of plasticity and stability
    if plasticity + stability == 0:
        overall_score = 0.0
    else:
        overall_score = 2 * (plasticity * stability) / (plasticity + stability)
        
    return {
        "forgetting_delta": round(forgetting, 4),
        "plasticity": round(plasticity, 4),
        "stability": round(stability, 4),
        "lifelong_score": round(overall_score, 4)
    }

def elastic_weight_consolidation_penalty(weights: List[float], fisher_diag: List[float], old_weights: List[float]) -> float:
    """Calculate EWC regularization penalty to prevent forgetting."""
    if not weights or len(weights) != len(fisher_diag) or len(weights) != len(old_weights):
        return 0.0
        
    penalty = 0.0
    for w, f, w_old in zip(weights, fisher_diag, old_weights):
        penalty += f * ((w - w_old) ** 2)
        
    return round(penalty * 0.5, 6)
