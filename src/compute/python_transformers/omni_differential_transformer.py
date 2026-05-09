import torch
import torch.nn as nn
import torch.nn.functional as F
import math

class OmniDifferentialAttention(nn.Module):
    """
    Implementation of Differential Transformer Attention (DiffAttn).
    Calculates attention as the difference between two separate softmax attention maps,
    effectively removing attention noise and enhancing long-context modeling.
    """
    def __init__(self, embed_dim: int, num_heads: int, dropout: float = 0.1):
        super().__init__()
        assert embed_dim % num_heads == 0, "embed_dim must be divisible by num_heads"
        self.embed_dim = embed_dim
        self.num_heads = num_heads
        self.head_dim = embed_dim // num_heads
        self.scale = self.head_dim ** -0.5
        
        # Dual Query, Key, Value projections
        self.q_proj1 = nn.Linear(embed_dim, embed_dim)
        self.k_proj1 = nn.Linear(embed_dim, embed_dim)
        self.v_proj1 = nn.Linear(embed_dim, embed_dim)

        self.q_proj2 = nn.Linear(embed_dim, embed_dim)
        self.k_proj2 = nn.Linear(embed_dim, embed_dim)
        self.v_proj2 = nn.Linear(embed_dim, embed_dim)
        
        self.lambda_param = nn.Parameter(torch.ones(1, num_heads, 1, 1))
        self.out_proj = nn.Linear(embed_dim, embed_dim)
        self.dropout = nn.Dropout(dropout)

    def forward(self, x: torch.Tensor, mask: torch.Tensor = None) -> torch.Tensor:
        B, L, D = x.shape
        
        def split_heads(tensor):
            return tensor.view(B, L, self.num_heads, self.head_dim).transpose(1, 2)

        q1, k1, v1 = split_heads(self.q_proj1(x)), split_heads(self.k_proj1(x)), split_heads(self.v_proj1(x))
        q2, k2, v2 = split_heads(self.q_proj2(x)), split_heads(self.k_proj2(x)), split_heads(self.v_proj2(x))

        scores1 = (q1 @ k1.transpose(-2, -1)) * self.scale
        scores2 = (q2 @ k2.transpose(-2, -1)) * self.scale

        if mask is not None:
            scores1 = scores1.masked_fill(mask == 0, float('-inf'))
            scores2 = scores2.masked_fill(mask == 0, float('-inf'))

        attn1 = self.dropout(F.softmax(scores1, dim=-1))
        attn2 = self.dropout(F.softmax(scores2, dim=-1))

        # Differential operation
        diff_attn = attn1 - self.lambda_param * attn2
        
        # Apply to values (using v1 as the primary value space)
        out = (diff_attn @ v1).transpose(1, 2).reshape(B, L, D)
        return self.out_proj(out)
