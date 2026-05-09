"""
moe_canary_router.py — Compute / Operations
Layer: Compute / Routing — Canary Expert Rollout

When a specific expert is fine-tuned (e.g., Coding Expert v2), we don't
want to replace the old expert immediately. This module sits inside the 
gating network and diverts a configurable percentage of traffic (e.g., 1%)
to the new expert to test for regressions.
"""

import torch
import random

class CanaryRouter:
    """
    Intercepts routing logic to facilitate A/B testing of individual MoE experts.
    """
    def __init__(self, original_expert_id: int, canary_expert_id: int, traffic_percentage: float = 0.05):
        self.original_expert_id = original_expert_id
        self.canary_expert_id = canary_expert_id
        self.traffic_percentage = traffic_percentage
        
        print(f"[Canary Router] Diverting {traffic_percentage*100}% of traffic from Expert {original_expert_id} to {canary_expert_id}")

    def apply_canary_routing(self, top_k_indices: torch.Tensor) -> torch.Tensor:
        """
        top_k_indices: (Batch, SeqLen, TopK)
        Modifies the indices in-place based on the canary policy.
        """
        # Flatten for iteration
        flat_indices = top_k_indices.view(-1)
        
        for i in range(flat_indices.shape[0]):
            if flat_indices[i].item() == self.original_expert_id:
                # Stochastic diversion
                if random.random() < self.traffic_percentage:
                    flat_indices[i] = self.canary_expert_id
                    
        return flat_indices.view_as(top_k_indices)

# Example Usage in the Router:
# gate_logits = ...
# _, top_k_indices = torch.topk(gate_logits, k=2, dim=-1)
# if canary_deployment_active:
#     top_k_indices = canary_router.apply_canary_routing(top_k_indices)
