"""
omni_moe_router.py — Mixture of Experts (MoE) Router
Layer: Compute / AI

Implements the routing mechanism for Sparse Mixture of Experts.
Dynamically routes tokens to the top-K experts based on a learned gating network.
Zero-mock, incorporating load balancing loss.
"""

import torch
import torch.nn as nn
import torch.nn.functional as F

class OmniMoERouter(nn.Module):
    def __init__(self, hidden_dim: int, num_experts: int, top_k: int = 2):
        super().__init__()
        self.num_experts = num_experts
        self.top_k = top_k
        self.gate = nn.Linear(hidden_dim, num_experts, bias=False)

    def forward(self, hidden_states: torch.Tensor):
        """
        hidden_states: (Batch, SeqLen, HiddenDim)
        
        Returns:
            routing_weights: (Batch * SeqLen, TopK)
            selected_experts: (Batch * SeqLen, TopK)
            load_balancing_loss: Scalar tensor
        """
        batch_size, seq_len, hidden_dim = hidden_states.size()
        hidden_states_flat = hidden_states.view(-1, hidden_dim) # (B*S, H)

        # 1. Compute gating logits
        logits = self.gate(hidden_states_flat) # (B*S, NumExperts)

        # 2. Select top-K experts
        routing_weights, selected_experts = torch.topk(logits, self.top_k, dim=-1)

        # 3. Softmax over the top-K experts only
        routing_weights = F.softmax(routing_weights, dim=-1)

        # 4. Compute Load Balancing Loss (Auxiliary Loss)
        # We want to encourage all experts to be utilized equally.
        # Probability of routing to each expert: Softmax over all experts
        probs = F.softmax(logits, dim=-1) # (B*S, NumExperts)
        
        # Fraction of tokens routed to each expert (based on top-1 choice)
        expert_mask = F.one_hot(selected_experts[:, 0], num_classes=self.num_experts).float() # (B*S, NumExperts)
        
        # Mean probability per expert
        meam_probs = probs.mean(dim=0) # (NumExperts,)
        # Mean fraction of tokens per expert
        mean_mask = expert_mask.mean(dim=0) # (NumExperts,)
        
        # Load balancing loss: N * sum(mean_probs * mean_mask)
        load_balancing_loss = self.num_experts * torch.sum(meam_probs * mean_mask)

        return routing_weights, selected_experts, load_balancing_loss
