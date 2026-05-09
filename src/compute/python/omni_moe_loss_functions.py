import torch
import torch.nn.functional as F

# OMNI MOTHER: Specialized Loss Functions for MoE
# Includes Router Z-Loss, Load Balancing Loss, and Contrastive Loss

class OmniMoELoss:
    @staticmethod
    def router_z_loss(logits: torch.Tensor, coef: float = 1e-3) -> torch.Tensor:
        """Penalizes large logits to stabilize routing."""
        log_z = torch.logsumexp(logits, dim=-1)
        return coef * torch.mean(log_z ** 2)

    @staticmethod
    def load_balancing_loss(routing_probs: torch.Tensor, expert_mask: torch.Tensor, coef: float = 1e-2) -> torch.Tensor:
        """
        routing_probs: [N, E]
        expert_mask: [N, E] indicating token assignment
        """
        num_experts = routing_probs.size(-1)
        importance = routing_probs.mean(dim=0)
        load = expert_mask.float().mean(dim=0)
        
        return coef * num_experts * torch.sum(importance * load)
