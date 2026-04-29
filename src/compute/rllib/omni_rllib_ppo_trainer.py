# OMNI MOTHER - DIVINE MEMORY INTEGRATION
# Ray RLlib PPO Trainer (OMNI Zero-Mock Implementation)
# Implements Proximal Policy Optimization clipping loss.

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

class PPOLossCalculator:
    def __init__(self, clip_param: float = 0.2):
        self.clip_param = clip_param

    def calculate_loss(self, advantages: List[float], old_probs: List[float], new_probs: List[float]) -> Result:
        if not advantages or len(advantages) != len(old_probs) or len(old_probs) != len(new_probs):
            return Result.err("Mismatched or empty input lists.")
            
        total_loss = 0.0
        for adv, op, np in zip(advantages, old_probs, new_probs):
            if op == 0.0:
                 return Result.err("Old probability cannot be zero.")
                 
            ratio = np / op
            surr1 = ratio * adv
            surr2 = max(min(ratio, 1.0 + self.clip_param), 1.0 - self.clip_param) * adv
            
            # PPO minimizes negative surrogate objective
            total_loss -= min(surr1, surr2)
            
        return Result.ok(total_loss / len(advantages))
