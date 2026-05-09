import torch

# OMNI MOTHER: Dynamic Routing Loss (Load Balancing)
# Prevents routing collapse where all tokens go to one expert

class OmniRoutingLoss:
    @staticmethod
    def compute_balance_loss(routing_probs: torch.Tensor, expert_mask: torch.Tensor, num_experts: int) -> torch.Tensor:
        # routing_probs: [batch*seq, num_experts]
        # expert_mask: [batch*seq, num_experts] (1 if routed, 0 else)
        
        density = expert_mask.mean(dim=0)
        prob_mean = routing_probs.mean(dim=0)
        
        loss = (density * prob_mean).sum() * num_experts
        return loss
