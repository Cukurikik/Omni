"""
OMNI MOTHER: MoE Load Balancing Loss Functions (Production Grade)
Implements three research-grade auxiliary losses for MoE training:
1. Switch Transformer auxiliary loss (Fedus et al.)
2. Expert Choice load-balancing loss (Zhou et al.)
3. Z-loss for router logit stability (Zoph et al.)
"""
import torch
import torch.nn.functional as F
from typing import Optional

class AuxiliaryLoadBalancingLoss:
    """Switch Transformer aux loss: N * Σ(f_i * P_i)."""
    @staticmethod
    def compute(routing_probs: torch.Tensor, num_experts: int,
                top_k: int = 1) -> torch.Tensor:
        num_tokens = routing_probs.size(0)
        me_probs = routing_probs.mean(dim=0)  # [E]
        if top_k == 1:
            indices = routing_probs.argmax(dim=-1)
        else:
            indices = routing_probs.topk(top_k, dim=-1).indices[:, 0]
        mask = F.one_hot(indices, num_classes=num_experts).float()
        me_tokens = mask.mean(dim=0)  # [E]
        return num_experts * (me_probs * me_tokens).sum()

class ExpertChoiceLoss:
    """Expert-choice style loss encouraging uniform token distribution."""
    @staticmethod
    def compute(routing_probs: torch.Tensor, num_experts: int) -> torch.Tensor:
        # Variance of the token-count distribution across experts
        indices = routing_probs.argmax(dim=-1)
        counts = torch.zeros(num_experts, device=routing_probs.device)
        for i in range(num_experts):
            counts[i] = (indices == i).float().sum()
        ideal = float(routing_probs.size(0)) / num_experts
        return ((counts - ideal) ** 2).mean() / (ideal ** 2 + 1e-8)

class ZLoss:
    """Z-loss penalizing large router logits to prevent overflow.
    loss = (1/N) * Σ log²(Σ exp(logits_i))  over tokens."""
    @staticmethod
    def compute(router_logits: torch.Tensor) -> torch.Tensor:
        log_z = torch.logsumexp(router_logits, dim=-1)
        return (log_z ** 2).mean()

class OmniMoELoss:
    """Composite MoE loss combining all three strategies."""
    def __init__(self, num_experts: int, aux_weight: float = 0.01,
                 z_weight: float = 0.001, use_expert_choice: bool = False):
        self.num_experts = num_experts
        self.aux_weight = aux_weight
        self.z_weight = z_weight
        self.use_expert_choice = use_expert_choice

    def __call__(self, routing_probs: torch.Tensor,
                 router_logits: Optional[torch.Tensor] = None) -> torch.Tensor:
        if self.use_expert_choice:
            loss = ExpertChoiceLoss.compute(routing_probs, self.num_experts)
        else:
            loss = AuxiliaryLoadBalancingLoss.compute(routing_probs, self.num_experts)
        loss = loss * self.aux_weight
        if router_logits is not None and self.z_weight > 0:
            loss = loss + ZLoss.compute(router_logits) * self.z_weight
        return loss
