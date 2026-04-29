# OMNI MOTHER - DIVINE MEMORY INTEGRATION
# Stable Baselines 3 PPO Objective (OMNI Zero-Mock Implementation)
# Implements the clipped surrogate PPO loss math.

from dataclasses import dataclass
from typing import List, Optional

@dataclass
class Result:
    value: Optional[float]
    error: Optional[str]
    is_ok: bool

    @staticmethod
    def ok(val: float) -> 'Result':
        return Result(value=val, error=None, is_ok=True)

    @staticmethod
    def err(err: str) -> 'Result':
        return Result(value=None, error=err, is_ok=False)

class PPOObjectiveEngine:
    def clipped_surrogate_loss(self, log_probs_new: List[float], log_probs_old: List[float], advantages: List[float], epsilon: float = 0.2) -> Result:
        if not log_probs_new or len(log_probs_new) != len(log_probs_old) or len(log_probs_new) != len(advantages):
             return Result.err("Dimensional mismatch in trajectory batch arrays.")
             
        # PPO Loss is a minimization objective (thus multiplying target by -1)
        total_loss = 0.0
        n = len(log_probs_new)
        
        import math
        for i in range(n):
            # log probability difference corresponds to probability ratio: exp(new - old)
            ratio = math.exp(log_probs_new[i] - log_probs_old[i])
            surrogate_1 = ratio * advantages[i]
            
            # Clipping parameter bounds
            clip_val = max(1.0 - epsilon, min(ratio, 1.0 + epsilon))
            surrogate_2 = clip_val * advantages[i]
            
            # Negative because optimizers typically minimize
            total_loss += -min(surrogate_1, surrogate_2)
            
        return Result.ok(total_loss / n)
