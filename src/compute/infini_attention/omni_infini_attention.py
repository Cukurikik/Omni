"""
omni_infini_attention.py — Infini-Attention
Inspired by: Infini-Transformer (Continuous Memory for Infinite Context)
Layer: Compute / AI

Implementation of Infini-attention which introduces a compressive memory 
alongside local dot-product attention to process infinitely long contexts.
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
from typing import Optional, Tuple, Dict
from dataclasses import dataclass


@dataclass
class InfiniAttentionConfig:
    dim: int = 768
    heads: int = 12
    dim_head: int = 64
    segment_length: int = 2048
    dropout: float = 0.0
    update_type: str = "linear"  # "linear" or "delta"


class CompressiveMemory(nn.Module):
    """Continuous compressive memory for Infini-attention."""

    def __init__(self, config: InfiniAttentionConfig):
        super().__init__()
        self.config = config
        self.heads = config.heads
        self.dim_head = config.dim_head
        
        # Memory states: M (key-value associations) and Z (normalization term)
        self.register_buffer("memory_m", torch.zeros(1, config.heads, config.dim_head, config.dim_head))
        self.register_buffer("memory_z", torch.zeros(1, config.heads, config.dim_head, 1))

    def reset_memory(self, batch_size: int, device: torch.device, dtype: torch.dtype):
        """Initialize or reset memory states for a new sequence."""
        self.memory_m = torch.zeros(batch_size, self.heads, self.dim_head, self.dim_head, 
                                    device=device, dtype=dtype)
        self.memory_z = torch.zeros(batch_size, self.heads, self.dim_head, 1, 
                                    device=device, dtype=dtype)

    def retrieve(self, query: torch.Tensor) -> torch.Tensor:
        """Retrieve from compressive memory using the query.
        
        Args:
            query: (B, H, N, D)
        Returns:
            retrieved: (B, H, N, D)
        """
        # A = sigma(Q) * M / (sigma(Q) * Z)
        sigma_q = F.elu(query) + 1.0  # Non-linear activation for queries (ELU + 1 > 0)
        
        # Numerator: sigma_q @ M -> (B, H, N, D)
        numerator = torch.matmul(sigma_q, self.memory_m)
        
        # Denominator: sigma_q @ Z -> (B, H, N, 1)
        denominator = torch.matmul(sigma_q, self.memory_z)
        denominator = torch.clamp(denominator, min=1e-6)
        
        return numerator / denominator

    def update(self, key: torch.Tensor, value: torch.Tensor):
        """Update compressive memory with new key-value pairs.
        
        Args:
            key: (B, H, N, D)
            value: (B, H, N, D)
        """
        sigma_k = F.elu(key) + 1.0
        
        if self.config.update_type == "linear":
            # M_new = M_old + sigma(K)^T @ V
            # Z_new = Z_old + sum(sigma(K)^T, dim=-1)
            self.memory_m = self.memory_m + torch.matmul(sigma_k.transpose(-2, -1), value)
            self.memory_z = self.memory_z + sigma_k.transpose(-2, -1).sum(dim=-1, keepdim=True)
            
        elif self.config.update_type == "delta":
            # Delta rule: V_target = V - retrieve(K)
            # M_new = M_old + sigma(K)^T @ V_target
            retrieved_v = self.retrieve(key)
            v_delta = value - retrieved_v
            self.memory_m = self.memory_m + torch.matmul(sigma_k.transpose(-2, -1), v_delta)
            self.memory_z = self.memory_z + sigma_k.transpose(-2, -1).sum(dim=-1, keepdim=True)


class OmniInfiniAttention(nn.Module):
    """Infini-attention layer combining local attention and compressive memory."""

    def __init__(self, config: InfiniAttentionConfig):
        super().__init__()
        self.config = config
        self.heads = config.heads
        self.dim_head = config.dim_head
        self.inner_dim = config.heads * config.dim_head
        
        self.to_qkv = nn.Linear(config.dim, self.inner_dim * 3, bias=False)
        self.to_out = nn.Linear(self.inner_dim, config.dim, bias=False)
        
        self.memory = CompressiveMemory(config)
        self.gating = nn.Parameter(torch.zeros(1, config.heads, 1, config.dim_head))
        self.dropout = nn.Dropout(config.dropout)

    def forward(self, x: torch.Tensor, is_first_segment: bool = True) -> torch.Tensor:
        """Forward pass for a segment of the sequence.
        
        Args:
            x: (B, N, D) token embeddings for current segment
            is_first_segment: If True, resets the compressive memory
        """
        B, N, D = x.shape
        
        if is_first_segment:
            self.memory.reset_memory(B, x.device, x.dtype)
            
        qkv = self.to_qkv(x).chunk(3, dim=-1)
        q, k, v = map(lambda t: t.view(B, N, self.heads, self.dim_head).transpose(1, 2), qkv)
        
        # 1. Local Causal Attention
        scale = self.dim_head ** -0.5
        sim = torch.matmul(q, k.transpose(-2, -1)) * scale
        
        causal_mask = torch.ones(N, N, dtype=torch.bool, device=x.device).triu(1)
        sim = sim.masked_fill(causal_mask, float('-inf'))
        
        attn = F.softmax(sim, dim=-1)
        attn = self.dropout(attn)
        local_out = torch.matmul(attn, v)  # (B, H, N, D)
        
        # 2. Memory Retrieval
        memory_out = self.memory.retrieve(q)  # (B, H, N, D)
        
        # 3. Memory Update
        self.memory.update(k.detach(), v.detach())
        
        # 4. Combine Local and Memory Outputs using learned gating
        beta = torch.sigmoid(self.gating)
        combined_out = beta * memory_out + (1 - beta) * local_out
        
        # Merge heads
        combined_out = combined_out.transpose(1, 2).reshape(B, N, self.inner_dim)
        
        return self.to_out(combined_out)
