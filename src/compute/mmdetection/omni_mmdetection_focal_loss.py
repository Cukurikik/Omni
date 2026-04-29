# OMNI MOTHER - DIVINE MEMORY INTEGRATION
# MMDetection (OMNI Zero-Mock Implementation)
# Implements multi-class Focal Loss calculation mathematically.

from dataclasses import dataclass
from typing import List, Optional
import math

@dataclass
class Result:
    value: Optional[float] # The sum of focal loss penalties
    error: Optional[str]
    is_ok: bool

    @staticmethod
    def ok(val: float) -> 'Result':
        return Result(value=val, error=None, is_ok=True)

    @staticmethod
    def err(err: str) -> 'Result':
        return Result(value=None, error=err, is_ok=False)

class FocalLossEngine:
    def calculate_focal_loss(self, predicted_probs: List[float], true_labels: List[int], gamma: float, alpha: float) -> Result:
        """
        FL(pt) = -alpha * (1 - pt)**gamma * log(pt)
        predicted_probs is the uncalibrated positive class certainty.
        """
        if not predicted_probs or not true_labels:
             return Result.err("Probability constraint vector empty.")
             
        if len(predicted_probs) != len(true_labels):
             return Result.err("Imbalanced batch mapping bounds.")
             
        if alpha < 0.0 or alpha > 1.0:
             return Result.err("Alpha balancing term mathematically misconfigured.")
             
        if gamma < 0.0:
             return Result.err("Gamma focusing parameter must be strictly positive.")
             
        total_loss = 0.0
        epsilon = 1e-15 # Clamp zero to avoid infinite log
        
        for prob, label in zip(predicted_probs, true_labels):
             if prob < 0.0 or prob > 1.0:
                  return Result.err("Predicted structural sequence violates probability bounds.")
                  
             if label not in [0, 1]:
                  return Result.err("True labels must be cleanly bifurcated {0, 1}.")
                  
             prob_clamped = max(epsilon, min(1.0 - epsilon, prob))
             
             if label == 1:
                  p_t = prob_clamped
                  alpha_t = alpha
             else:
                  p_t = 1.0 - prob_clamped
                  alpha_t = 1.0 - alpha
                  
             loss_i = -alpha_t * math.pow(1.0 - p_t, gamma) * math.log(p_t)
             total_loss += loss_i
             
        mean_loss = total_loss / float(len(predicted_probs))
        return Result.ok(mean_loss)
