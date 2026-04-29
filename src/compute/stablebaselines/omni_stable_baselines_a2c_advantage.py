# OMNI MOTHER - DIVINE MEMORY INTEGRATION
# Stable Baselines (OMNI Zero-Mock Implementation)
# Implements Synchronous Advantage Actor Critic (A2C) Advantage calculation.

from dataclasses import dataclass
from typing import List, Optional
import math

@dataclass
class Result:
    value: Optional[List[float]] # Calculated Advantage Values
    error: Optional[str]
    is_ok: bool

    @staticmethod
    def ok(val: List[float]) -> 'Result':
        return Result(value=val, error=None, is_ok=True)

    @staticmethod
    def err(err: str) -> 'Result':
        return Result(value=None, error=err, is_ok=False)

class A2CAdvantageEngine:
    def evaluate_advantage(self, rewards: List[float], values: List[float], gamma: float, next_value: float) -> Result:
        """
        Computes sequential empirical returns and advantage estimation mathematically.
        Advantage = Return - Value. 
        """
        if not rewards or not values:
            return Result.err("Reward and Value sequences cannot be empty.")
            
        if len(rewards) != len(values):
            return Result.err("Length mismatch between rewards and values.")
            
        if gamma < 0.0 or gamma > 1.0:
            return Result.err("Discount factor gamma must be bounded [0, 1].")
            
        n_steps = len(rewards)
        returns = [0.0] * n_steps
        advantages = [0.0] * n_steps
        
        current_return = next_value
        
        # Traverse backwards for exponential discount accumulation
        for t in reversed(range(n_steps)):
             current_return = rewards[t] + gamma * current_return
             returns[t] = current_return
             advantages[t] = returns[t] - values[t]
             
        return Result.ok(advantages)
