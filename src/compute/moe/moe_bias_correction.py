"""
moe_bias_correction.py — Auxiliary-Loss-Free Load Balancing
Layer: Compute / AI — MoE Routing Optimization

Implements the DeepSeek V3 style auxiliary-loss-free load balancing.
Instead of adding an auxiliary loss term which degrades training stability,
this applies a dynamic bias term to the routing logits to naturally
force load balancing without corrupting the gradient signal.
"""
import torch
import torch.nn as nn
from typing import Tuple


class BiasCorrectionRouter(nn.Module):
    """
    Router that uses dynamic bias updates to balance load
    instead of an auxiliary loss function.
    """
    def __init__(self, dim: int, num_experts: int, top_k: int = 1, bias_update_rate: float = 0.01):
        super().__init__()
        self.dim = dim
        self.num_experts = num_experts
        self.top_k = top_k
        self.bias_update_rate = bias_update_rate

        self.gate = nn.Linear(dim, num_experts, bias=False)
        
        # The dynamic bias term (not updated by SGD, updated manually)
        self.register_buffer("routing_bias", torch.zeros(num_experts))

    def forward(self, hidden_states: torch.Tensor) -> Tuple[torch.Tensor, torch.Tensor]:
        """
        Returns:
            routing_weights: (B*S, top_k)
            selected_experts: (B*S, top_k)
        """
        B, S, D = hidden_states.shape
        hidden_states = hidden_states.view(-1, D)
        N = hidden_states.shape[0]

        # Raw logits from the gate
        raw_logits = self.gate(hidden_states)

        # Add the dynamic balancing bias
        biased_logits = raw_logits + self.routing_bias
        
        # Softmax over biased logits
        probs = torch.softmax(biased_logits, dim=-1)

        # Select Top-K
        top_k_probs, selected_experts = torch.topk(probs, self.top_k, dim=-1)
        
        # Normalize weights
        routing_weights = top_k_probs / top_k_probs.sum(dim=-1, keepdim=True)

        if self.training:
            # Update the bias term based on the current batch's routing decisions
            self._update_bias(selected_experts, N)

        return routing_weights, selected_experts

    @torch.no_grad()
    def _update_bias(self, selected_experts: torch.Tensor, total_tokens: int):
        """
        Updates the routing bias.
        Experts that receive more tokens than average get their bias reduced.
        Experts that receive fewer tokens get their bias increased.
        """
        # Count token allocation per expert (using the first choice for simplicity)
        first_choice = selected_experts[:, 0]
        expert_counts = torch.bincount(first_choice, minlength=self.num_experts).float()
        
        # Calculate routing fraction per expert
        routing_fraction = expert_counts / total_tokens
        
        # Ideal fraction (uniform distribution)
        ideal_fraction = 1.0 / self.num_experts
        
        # Error term: Positive if expert is under-utilized, Negative if over-utilized
        error = ideal_fraction - routing_fraction
        
        # Update bias
        self.routing_bias += self.bias_update_rate * error
        
        # Optional: Clip bias to prevent extreme values
        self.routing_bias.clamp_(-2.0, 2.0)
