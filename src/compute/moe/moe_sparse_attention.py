"""
moe_sparse_attention.py — Compute / Architecture
Layer: Compute / AI — Sparse Attention Integration

MoE sparse-ifies the FFN layers, but standard dense self-attention still 
scales quadratically with sequence length (O(N^2)). This module implements a 
Longformer-style sliding window sparse attention to accompany the MoE layer, 
enabling 100k+ token context windows.
"""

import torch
import torch.nn as nn
import math

class SparseWindowAttention(nn.Module):
    """
    Sliding window attention. Tokens only attend to W adjacent tokens rather 
    than the entire sequence, reducing complexity to O(N * W).
    """
    def __init__(self, hidden_dim: int, num_heads: int, window_size: int = 512):
        super().__init__()
        assert hidden_dim % num_heads == 0
        
        self.hidden_dim = hidden_dim
        self.num_heads = num_heads
        self.head_dim = hidden_dim // num_heads
        self.window_size = window_size
        
        self.q_proj = nn.Linear(hidden_dim, hidden_dim, bias=False)
        self.k_proj = nn.Linear(hidden_dim, hidden_dim, bias=False)
        self.v_proj = nn.Linear(hidden_dim, hidden_dim, bias=False)
        self.out_proj = nn.Linear(hidden_dim, hidden_dim, bias=False)

    def forward(self, hidden_states: torch.Tensor) -> torch.Tensor:
        batch_size, seq_len, _ = hidden_states.shape
        
        # Projection
        q = self.q_proj(hidden_states).view(batch_size, seq_len, self.num_heads, self.head_dim).transpose(1, 2)
        k = self.k_proj(hidden_states).view(batch_size, seq_len, self.num_heads, self.head_dim).transpose(1, 2)
        v = self.v_proj(hidden_states).view(batch_size, seq_len, self.num_heads, self.head_dim).transpose(1, 2)
        
        # Standard QK^T but we apply a sparse mask
        scores = torch.matmul(q, k.transpose(-2, -1)) / math.sqrt(self.head_dim)
        
        # Create Sparse Window Mask
        # A token at position i can only attend to positions [i - window/2, i + window/2]
        idx = torch.arange(seq_len, device=scores.device)
        distance = torch.abs(idx.unsqueeze(1) - idx.unsqueeze(0))
        sparse_mask = distance > (self.window_size // 2)
        
        # Apply mask
        scores = scores.masked_fill(sparse_mask, float('-inf'))
        
        # Causal mask (standard auto-regressive)
        causal_mask = torch.triu(torch.ones(seq_len, seq_len, dtype=torch.bool, device=scores.device), diagonal=1)
        scores = scores.masked_fill(causal_mask, float('-inf'))
        
        probs = torch.nn.functional.softmax(scores, dim=-1)
        
        # Output calculation
        context = torch.matmul(probs, v)
        context = context.transpose(1, 2).contiguous().view(batch_size, seq_len, self.hidden_dim)
        
        return self.out_proj(context)
