# SPIN Self-Play Fine-Tuning Loss
# DPO-equivalent loss for iterative self-play

import torch, math
from typing import Optional, Generic, TypeVar
T = TypeVar('T'); E = TypeVar('E')
class OmniResult(Generic[T, E]):
    def __init__(self, value: Optional[T] = None, error: Optional[E] = None):
        self.is_ok = error is None; self.value = value; self.error = error

class SPINLoss:
    MAX_SEQ = 16384
    def __init__(self, beta: float = 0.1):
        if beta <= 0 or beta > 10:
            raise ValueError("Beta must be in (0, 10]")
        self.beta = beta

    def compute(self, policy_chosen_logps: torch.Tensor, policy_rejected_logps: torch.Tensor,
                ref_chosen_logps: torch.Tensor, ref_rejected_logps: torch.Tensor) -> OmniResult[torch.Tensor, str]:
        if policy_chosen_logps.shape != policy_rejected_logps.shape:
            return OmniResult(error="Log-prob tensor shape mismatch")
        if policy_chosen_logps.numel() > self.MAX_SEQ:
            return OmniResult(error=f"Sequence elements exceed {self.MAX_SEQ}")
        # SPIN objective: equivalent to DPO with self-generated negatives
        chosen_rewards = self.beta * (policy_chosen_logps - ref_chosen_logps)
        rejected_rewards = self.beta * (policy_rejected_logps - ref_rejected_logps)
        logits = chosen_rewards - rejected_rewards
        loss = -torch.nn.functional.logsigmoid(logits).mean()
        if torch.isnan(loss) or torch.isinf(loss):
            return OmniResult(error="NaN/Inf detected in SPIN loss")
        return OmniResult(value=loss)
