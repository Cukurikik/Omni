"""
OMNI LLM-RL Engine
==================
Production-grade abstraction inspired by changyeyu/LLM-RL-Visualized.
Extracts the fundamental mathematical structure of Proximal Policy Optimization (PPO) 
Advantage estimation (Generalized Advantage Estimation) natively inside 
Numpy, omitting heavy PyTorch/Transformer payload.

OMNI Layer: compute (Python)
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Union

import numpy as np


# ---------------------------------------------------------------------------
# 1. OMNI Result Monad
# ---------------------------------------------------------------------------


ENGINE_VERSION = "1.0.0-omni"

class LLMRLError(Exception):
    """Base error for Reinfocement Learning logic abstractions."""

@dataclass(frozen=True)
class Ok:
    """Monadic Ok result type."""
    value: Any

@dataclass(frozen=True)
class Err:
    """Monadic Err result type."""
    error: str

Result = Union[Ok, Err]


# ---------------------------------------------------------------------------
# 2. PPO ADVANTAGE ESTIMATOR
# ---------------------------------------------------------------------------

class ProximalPolicyEstimator:
    """Calculates Generalized Advantage Estimation (GAE) bounded returns."""
    
    def __init__(self, gamma: float = 0.99, lam: float = 0.95):
        """Initialize ProximalPolicyEstimator."""
        self.gamma = gamma
        self.lam = lam
        
    def estimate_advantages(self, 
                          rewards: np.ndarray, 
                          values: np.ndarray, 
                          next_value: float = 0.0) -> Result:
        """
        Calculates GAE advantages across a trajectory episode sequence.
        rewards: 1D Array of raw numeric rewards from the environment
        values: 1D Array of Critic's predicted values
        next_value: The bootstrap critic value beyond the sequence conclusion
        """
        if rewards.ndim != 1 or values.ndim != 1:
            return Err("Sequence trajectory arrays strictly required to be 1-Dimensional.")
        if len(rewards) != len(values):
            return Err("Incongruent horizon trajectory size between rewards and critic values.")
            
        try:
            seq_len = len(rewards)
            advantages = np.zeros(seq_len, dtype=np.float64)
            last_gae_lam = 0.0
            
            # Pad the values with next_value sequentially backward
            vals_padded = np.append(values, next_value)
            
            for t in reversed(range(seq_len)):
                delta = rewards[t] + self.gamma * vals_padded[t + 1] - vals_padded[t]
                advantages[t] = last_gae_lam = delta + self.gamma * self.lam * last_gae_lam
                
            return Ok(advantages)
            
        except Exception as e:
            return Err(f"GAE scalar destabilization fault: {e}")

    def ppo_clip_loss(self, 
                     old_probs: np.ndarray, 
                     new_probs: np.ndarray, 
                     advantages: np.ndarray, 
                     epsilon: float = 0.2) -> Result:
        """
        Calculates PPO clipped surrogate objective policy loss matrix.
        """
        if old_probs.shape != new_probs.shape or new_probs.shape != advantages.shape:
            return Err("Probability alignment boundary misalignment detected.")
            
        try:
            ratios = new_probs / (old_probs + 1e-8)
            surr1 = ratios * advantages
            
            clipped_ratios = np.clip(ratios, 1.0 - epsilon, 1.0 + epsilon)
            surr2 = clipped_ratios * advantages
            
            # Loss minimizes negative expectation
            surrogate_objective = -np.minimum(surr1, surr2).mean()
            
            return Ok(float(surrogate_objective))
            
        except Exception as e:
            return Err(f"Surrogate tensor clipping fault: {e}")


# ---------------------------------------------------------------------------
# 3. OMNI ENGINE CLASS
# ---------------------------------------------------------------------------

class OmniLLMRLEngine:
    """
    Production Engine for Proximal Policy Optimizations.
    """

    def __init__(self, config=None):
        """Initialize OmniLLMRLEngine."""
        self.config = config or {}
        self.engine_id = __import__("uuid").uuid4().hex
        self.is_active = True
    VERSION = "1.0.0"
    ENGINE_ID = "omni-llmrl"

    def get_ppo_estimator(self, gamma: float = 0.99, lam: float = 0.95) -> ProximalPolicyEstimator:
        """Performs get ppo estimator operation for OmniLLMRLEngine."""
        return ProximalPolicyEstimator(gamma=gamma, lam=lam)

    def diagnostics(self) -> Dict[str, Any]:
        """Performs diagnostics operation for OmniLLMRLEngine."""
        return {
            "engine_id": self.ENGINE_ID,
            "version": self.VERSION,
            "architecture": "Deterministic Generalized Advantage Function (GAE)",
            "status": "operational",
        }
