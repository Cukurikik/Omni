from typing import Dict, Any
from dataclasses import dataclass
import numpy as np

# OMNI Uni-DPO Engine — Compute Layer
# Absorbing pspdada/Uni-DPO: Unified Dynamic Preference Optimization for LLMs (ICLR 2026).
# Implements the mathematical DPO loss computation.

@dataclass
class DpoResult:
    ok: bool
    loss: float = 0.0
    error: str = None

class OmniUniDpoEngine:
    def __init__(self, beta: float = 0.1):
        self.beta = beta
        self.loss_computations = 0

    def compute_dpo_loss(self, policy_chosen_logps: np.ndarray, policy_rejected_logps: np.ndarray,
                         ref_chosen_logps: np.ndarray, ref_rejected_logps: np.ndarray) -> DpoResult:
        """
        Bradley-Terry DPO loss: L = -log(sigmoid(beta * (log_ratio_chosen - log_ratio_rejected)))
        All inputs are 1D arrays of shape (batch_size,) representing log probabilities.
        """
        if any(not isinstance(x, np.ndarray) for x in [policy_chosen_logps, policy_rejected_logps, ref_chosen_logps, ref_rejected_logps]):
            return DpoResult(False, error="DPOError: All inputs must be numpy arrays")
        if not all(x.shape == policy_chosen_logps.shape for x in [policy_rejected_logps, ref_chosen_logps, ref_rejected_logps]):
            return DpoResult(False, error="DPOError: Shape mismatch across inputs")
        try:
            self.loss_computations += 1
            log_ratio_chosen = policy_chosen_logps - ref_chosen_logps
            log_ratio_rejected = policy_rejected_logps - ref_rejected_logps
            logits = self.beta * (log_ratio_chosen - log_ratio_rejected)
            # Numerically stable log-sigmoid: log(sigmoid(x)) = -softplus(-x)
            losses = np.logaddexp(0, -logits)
            mean_loss = float(np.mean(losses))
            return DpoResult(True, loss=mean_loss)
        except Exception as e:
            return DpoResult(False, error=f"DPOError: {str(e)}")

    def diagnostics(self) -> Dict[str, Any]:
        return {"engine": "OmniUniDpoEngine", "beta": self.beta,
                "computations": self.loss_computations, "status": "Operational"}
