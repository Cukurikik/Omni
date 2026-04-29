# OMNI MOTHER - DIVINE MEMORY INTEGRATION
# TRL DPO Optimizer (OMNI Zero-Mock Implementation)
# Implements Direct Preference Optimization loss calculation.

from dataclasses import dataclass
from typing import List, Optional
import math

@dataclass
class Result:
    value: Optional[float] # DPO Loss value
    error: Optional[str]
    is_ok: bool

    @staticmethod
    def ok(val: float) -> 'Result':
        return Result(value=val, error=None, is_ok=True)

    @staticmethod
    def err(err: str) -> 'Result':
        return Result(value=None, error=err, is_ok=False)

class DPOOptimizer:
    def __init__(self, beta: float = 0.1):
        self.beta = beta

    def sigmoid(self, x: float) -> float:
        if x >= 0:
            z = math.exp(-x)
            return 1 / (1 + z)
        else:
            z = math.exp(x)
            return z / (1 + z)

    def calculate_loss(self, 
                       pi_logps_chosen: List[float], 
                       pi_logps_rejected: List[float], 
                       ref_logps_chosen: List[float], 
                       ref_logps_rejected: List[float]) -> Result:
        
        if not (len(pi_logps_chosen) == len(pi_logps_rejected) == len(ref_logps_chosen) == len(ref_logps_rejected)):
            return Result.err("Log-probability array limits must exactly match.")

        total_loss = 0.0
        
        for pi_c, pi_r, ref_c, ref_r in zip(pi_logps_chosen, pi_logps_rejected, ref_logps_chosen, ref_logps_rejected):
            # Calculate implied rewards
            reward_chosen = self.beta * (pi_c - ref_c)
            reward_rejected = self.beta * (pi_r - ref_r)
            
            # log(sigmoid(r_chosen - r_rejected))
            diff = reward_chosen - reward_rejected
            
            # Loss is negative log sigmoid of the difference
            sig = max(self.sigmoid(diff), 1e-10) # Avoid log(0)
            total_loss -= math.log(sig)
            
        return Result.ok(total_loss / max(1, len(pi_logps_chosen)))
