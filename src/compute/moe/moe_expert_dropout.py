"""
moe_expert_dropout.py — Expert Dropout for MoE Training
Layer: Compute / AI — Regularization

Implements Expert Dropout: randomly masking out experts during training
to prevent "expert collapse" (where only a few experts get all the updates)
and to force the router to learn robust, distributed representations.
"""
import torch
import torch.nn as nn
from typing import Tuple, Optional


class MoEExpertDropout(nn.Module):
    """
    Applies expert dropout during the routing phase.
    """
    def __init__(self, num_experts: int, dropout_prob: float = 0.1):
        super().__init__()
        self.num_experts = num_experts
        self.dropout_prob = dropout_prob

    def forward(
        self, 
        routing_logits: torch.Tensor
    ) -> Tuple[torch.Tensor, torch.Tensor]:
        """
        Args:
            routing_logits: (..., num_experts) raw logits before softmax.
        Returns:
            masked_logits: Logits with dropped experts set to -inf.
            dropout_mask: Boolean mask of dropped experts (True = dropped).
        """
        if not self.training or self.dropout_prob <= 0.0:
            return routing_logits, torch.zeros(self.num_experts, dtype=torch.bool, device=routing_logits.device)

        # Generate a dropout mask for the experts.
        # We drop the same experts across the entire batch to simulate node failure
        # and force batch-level re-routing.
        dropout_mask = torch.rand(self.num_experts, device=routing_logits.device) < self.dropout_prob
        
        # Ensure we don't drop ALL experts (safety check)
        if dropout_mask.all():
            dropout_mask[torch.randint(0, self.num_experts, (1,)).item()] = False

        # Apply mask
        masked_logits = routing_logits.clone()
        
        # We need to broadcast the mask if logits are batched (B, S, E)
        expanded_mask = dropout_mask.view(*([1] * (routing_logits.dim() - 1)), self.num_experts)
        masked_logits = masked_logits.masked_fill(expanded_mask, float('-inf'))

        return masked_logits, dropout_mask


class TokenChoiceExpertDropout(nn.Module):
    """
    Randomly drops the token's top-1 choice to force it to use its top-2/top-3.
    This acts as a data augmentation technique for the experts.
    """
    def __init__(self, drop_top1_prob: float = 0.05):
        super().__init__()
        self.drop_top1_prob = drop_top1_prob

    def forward(self, routing_probs: torch.Tensor) -> torch.Tensor:
        """
        Args:
            routing_probs: (B, S, num_experts)
        """
        if not self.training or self.drop_top1_prob <= 0.0:
            return routing_probs

        B, S, E = routing_probs.shape
        flat_probs = routing_probs.view(-1, E)
        
        # Determine which tokens will have their top-1 dropped
        drop_mask = torch.rand(flat_probs.shape[0], device=flat_probs.device) < self.drop_top1_prob
        
        if not drop_mask.any():
            return routing_probs

        # Find the top-1 index
        _, top1_idx = torch.max(flat_probs, dim=-1, keepdim=True)
        
        # Create a modification mask
        modified_probs = flat_probs.clone()
        
        # Zero out the top-1 probability for selected tokens
        row_indices = torch.arange(flat_probs.shape[0], device=flat_probs.device)
        modified_probs[row_indices[drop_mask], top1_idx[drop_mask].squeeze(-1)] = 0.0
        
        # Renormalize the probabilities for those tokens
        sum_probs = modified_probs[drop_mask].sum(dim=-1, keepdim=True)
        
        # Avoid division by zero if all probabilities were somehow 0
        safe_sum = torch.where(sum_probs == 0, torch.ones_like(sum_probs), sum_probs)
        modified_probs[drop_mask] = modified_probs[drop_mask] / safe_sum

        return modified_probs.view(B, S, E)
