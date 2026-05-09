"""
moe_attention_routing.py — Mixture of Attention Heads
Layer: Compute / AI — MoE Attention

Applies the Mixture of Experts concept to the multi-head attention
mechanism, dynamically routing tokens to specialized attention heads
rather than FFN experts, reducing attention compute complexity.
"""
import torch
import torch.nn as nn
import torch.nn.functional as F
from typing import Dict, Optional, Tuple
from dataclasses import dataclass
import math


@dataclass
class MoAConfig:
    dim: int = 1024
    num_total_heads: int = 32
    num_selected_heads: int = 4
    head_dim: int = 64
    dropout: float = 0.0
    bias: bool = False
    routing_temperature: float = 1.0


class MixtureOfAttention(nn.Module):
    """Dynamically routes tokens to a subset of attention heads."""
    def __init__(self, config: MoAConfig):
        super().__init__()
        self.config = config
        self.dim = config.dim
        self.num_heads = config.num_total_heads
        self.head_dim = config.head_dim
        self.top_k = config.num_selected_heads
        
        self.inner_dim = self.num_heads * self.head_dim
        
        # Projections for Q, K, V for all heads
        self.q_proj = nn.Linear(self.dim, self.inner_dim, bias=config.bias)
        self.k_proj = nn.Linear(self.dim, self.inner_dim, bias=config.bias)
        self.v_proj = nn.Linear(self.dim, self.inner_dim, bias=config.bias)
        self.o_proj = nn.Linear(self.inner_dim, self.dim, bias=config.bias)
        
        # Head router
        self.router = nn.Linear(self.dim, self.num_heads, bias=False)
        
        self.attn_dropout = nn.Dropout(config.dropout)
        self.resid_dropout = nn.Dropout(config.dropout)

    def forward(
        self,
        hidden_states: torch.Tensor,
        attention_mask: Optional[torch.Tensor] = None,
        position_ids: Optional[torch.Tensor] = None,
    ) -> Dict[str, torch.Tensor]:
        B, S, D = hidden_states.shape
        
        # 1. Routing
        router_logits = self.router(hidden_states) # (B, S, num_heads)
        probs = F.softmax(router_logits / self.config.routing_temperature, dim=-1)
        
        # Select top-k heads per token
        head_weights, head_indices = torch.topk(probs, self.config.top_k, dim=-1)
        # Normalize weights
        head_weights = head_weights / head_weights.sum(dim=-1, keepdim=True)
        
        # 2. QKV Projections
        q = self.q_proj(hidden_states).view(B, S, self.num_heads, self.head_dim).transpose(1, 2)
        k = self.k_proj(hidden_states).view(B, S, self.num_heads, self.head_dim).transpose(1, 2)
        v = self.v_proj(hidden_states).view(B, S, self.num_heads, self.head_dim).transpose(1, 2)
        
        # Apply RoPE if position_ids provided (placeholder logic)
        # q, k = apply_rotary_pos_emb(q, k, position_ids)
        
        # 3. Attention Computation
        # Standard attention across all heads (in practice, optimized kernel would only compute selected)
        scores = torch.matmul(q, k.transpose(-2, -1)) / math.sqrt(self.head_dim)
        
        if attention_mask is not None:
            scores = scores + attention_mask
            
        attn_probs = F.softmax(scores, dim=-1)
        attn_probs = self.attn_dropout(attn_probs)
        
        head_outputs = torch.matmul(attn_probs, v) # (B, num_heads, S, head_dim)
        head_outputs = head_outputs.transpose(1, 2) # (B, S, num_heads, head_dim)
        
        # 4. Apply Routing Mask
        # Create a mask of which heads are selected for each token
        mask = torch.zeros(B, S, self.num_heads, device=hidden_states.device)
        mask.scatter_(-1, head_indices, head_weights)
        
        # Mask and weight the outputs
        weighted_outputs = head_outputs * mask.unsqueeze(-1)
        
        # 5. Output Projection
        concat_outputs = weighted_outputs.reshape(B, S, self.inner_dim)
        final_output = self.resid_dropout(self.o_proj(concat_outputs))
        
        # 6. Auxiliary Loss for Load Balancing
        # We want heads to be used relatively equally across the sequence
        f = mask.mean(dim=(0, 1)) # fraction of tokens routed to each head
        p = probs.mean(dim=(0, 1)) # average probability for each head
        aux_loss = (f * p).sum() * self.num_heads * 0.01
        
        return {
            "output": final_output,
            "aux_loss": aux_loss,
            "router_logits": router_logits,
            "head_usage": f
        }
