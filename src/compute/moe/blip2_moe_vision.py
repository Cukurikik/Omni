"""
blip2_moe_vision.py — Compute / Multimodal
Layer: Compute / AI — Vision-Language MoE (Q-Former)

Inspired by blipren_release (BLIP-2 MoE variant).
Integrates a Sparse Mixture-of-Experts layer into the Q-Former cross-attention 
mechanism, allowing visual features to be routed to specialized semantic experts 
before being projected into the LLM space.
"""

import torch
import torch.nn as nn
import torch.nn.functional as F

class QFormerMoE(nn.Module):
    """
    Replaces the standard FFN in the Q-Former with a Mixture of Experts.
    """
    def __init__(self, hidden_dim: int, num_experts: int = 8, top_k: int = 2):
        super().__init__()
        self.hidden_dim = hidden_dim
        self.num_experts = num_experts
        self.top_k = top_k
        
        # Gating network to route image patches
        self.router = nn.Linear(hidden_dim, num_experts, bias=False)
        
        # Visual-Semantic Experts (Feed Forward Networks)
        self.experts = nn.ModuleList([
            nn.Sequential(
                nn.Linear(hidden_dim, hidden_dim * 4),
                nn.GELU(),
                nn.Linear(hidden_dim * 4, hidden_dim)
            ) for _ in range(num_experts)
        ])
        
    def forward(self, query_embeds: torch.Tensor) -> torch.Tensor:
        """
        query_embeds: (Batch, NumQueries, HiddenDim)
        """
        batch_size, num_queries, hidden_dim = query_embeds.shape
        flat_queries = query_embeds.view(-1, hidden_dim)
        
        # Calculate routing logits
        router_logits = self.router(flat_queries)
        routing_weights = F.softmax(router_logits, dim=-1)
        
        # Select top-k experts
        top_k_weights, top_k_indices = torch.topk(routing_weights, self.top_k, dim=-1)
        top_k_weights = top_k_weights / top_k_weights.sum(dim=-1, keepdim=True)
        
        # Process through experts
        final_output = torch.zeros_like(flat_queries)
        
        for i in range(flat_queries.shape[0]):
            token_x = flat_queries[i].unsqueeze(0)
            token_out = torch.zeros_like(token_x)
            
            for k in range(self.top_k):
                expert_idx = top_k_indices[i, k].item()
                weight = top_k_weights[i, k].item()
                
                expert_output = self.experts[expert_idx](token_x)
                token_out += weight * expert_output
                
            final_output[i] = token_out.squeeze(0)
            
        return final_output.view(batch_size, num_queries, hidden_dim)
