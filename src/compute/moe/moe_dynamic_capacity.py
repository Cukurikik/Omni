"""
moe_dynamic_capacity.py — Dynamic Expert Capacity Scaling
Layer: Compute / AI — MoE Routing Optimization

Implements dynamic expert capacity limits based on token complexity
or entropy. Instead of a fixed capacity factor, the routing engine
allocates more capacity to experts handling harder tokens.
"""
import torch
import torch.nn as nn
from typing import Dict, Tuple, Optional


class DynamicCapacityRouter(nn.Module):
    """Router that adjusts capacity limits dynamically per batch."""
    def __init__(self, dim: int, num_experts: int, top_k: int = 2,
                 base_capacity_factor: float = 1.25):
        super().__init__()
        self.dim = dim
        self.num_experts = num_experts
        self.top_k = top_k
        self.base_capacity_factor = base_capacity_factor

        self.gate = nn.Linear(dim, num_experts, bias=False)
        
        # Complexity predictor (predicts how "hard" a token is)
        self.complexity_predictor = nn.Sequential(
            nn.Linear(dim, 64),
            nn.ReLU(),
            nn.Linear(64, 1),
            nn.Sigmoid()
        )

    def forward(
        self, 
        hidden_states: torch.Tensor,
        expert_states: Optional[torch.Tensor] = None
    ) -> Tuple[torch.Tensor, torch.Tensor, torch.Tensor, torch.Tensor]:
        """
        Returns:
            routing_weights: (B*S, top_k)
            selected_experts: (B*S, top_k)
            dropped_mask: (B*S)
            aux_loss: scalar
        """
        B, S, D = hidden_states.shape
        hidden_states = hidden_states.view(-1, D)
        N = hidden_states.shape[0]

        # 1. Routing Logits
        logits = self.gate(hidden_states)
        probs = torch.softmax(logits, dim=-1)

        # 2. Token Complexity
        # Predict complexity score in [0, 1]
        complexity = self.complexity_predictor(hidden_states).squeeze(-1)
        
        # 3. Dynamic Capacity Calculation
        # Base capacity tokens per expert = (N * top_k / num_experts) * factor
        base_capacity = int((N * self.top_k / self.num_experts) * self.base_capacity_factor)
        
        # We allow experts to expand their capacity up to 50% more if they
        # receive high complexity tokens.
        expert_capacities = torch.full((self.num_experts,), base_capacity, device=hidden_states.device)
        
        # Determine base routing without capacity limits
        top_k_probs, top_k_indices = torch.topk(probs, self.top_k, dim=-1)
        
        # Distribute extra capacity based on average complexity of tokens routed to each expert
        # (Using first choice only for capacity adjustment approximation)
        first_choice = top_k_indices[:, 0]
        for e in range(self.num_experts):
            mask = first_choice == e
            if mask.sum() > 0:
                avg_comp = complexity[mask].mean().item()
                # If average complexity > 0.5, increase capacity proportionally
                if avg_comp > 0.5:
                    expansion = 1.0 + (avg_comp - 0.5)  # Max 1.5x
                    expert_capacities[e] = int(base_capacity * expansion)

        # 4. Enforce Capacities (Token Dropping)
        # Sort tokens by routing probability to prioritize high-confidence tokens
        sorted_probs, sorted_tokens = torch.sort(top_k_probs[:, 0], descending=True)
        
        selected_experts = torch.full((N, self.top_k), -1, dtype=torch.long, device=hidden_states.device)
        dropped_mask = torch.ones(N, dtype=torch.bool, device=hidden_states.device)
        
        current_usage = torch.zeros(self.num_experts, dtype=torch.long, device=hidden_states.device)
        
        # Greedily assign tokens
        for token_idx in sorted_tokens:
            assigned = 0
            for k in range(self.top_k):
                expert_idx = top_k_indices[token_idx, k]
                if current_usage[expert_idx] < expert_capacities[expert_idx]:
                    selected_experts[token_idx, k] = expert_idx
                    current_usage[expert_idx] += 1
                    assigned += 1
            
            if assigned > 0:
                dropped_mask[token_idx] = False

        # Normalize weights for selected experts
        routing_weights = top_k_probs.clone()
        # Zero out weights for dropped experts
        mask = selected_experts == -1
        routing_weights[mask] = 0.0
        
        # Renormalize
        sum_weights = routing_weights.sum(dim=-1, keepdim=True)
        # Avoid division by zero for fully dropped tokens
        sum_weights[sum_weights == 0] = 1.0
        routing_weights = routing_weights / sum_weights

        # 5. Load Balancing Loss
        f = (current_usage.float() / N)  # Fraction of tokens per expert
        p = probs.mean(0)                # Mean routing probability per expert
        aux_loss = (f * p).sum() * self.num_experts * 0.01

        return routing_weights, selected_experts, dropped_mask, aux_loss
