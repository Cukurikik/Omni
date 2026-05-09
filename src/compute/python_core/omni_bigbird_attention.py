"""
OMNI Compute — BigBird Sparse Attention (bigbird-inspired)
Block-sparse attention for long document processing.
"""
import math, torch, torch.nn as nn, torch.nn.functional as F
from typing import Optional

class BigBirdBlockSparseAttention(nn.Module):
    """Block-sparse attention combining global, sliding window, and random patterns."""
    def __init__(self, embed_dim: int, num_heads: int, block_size: int = 64,
                 num_global_tokens: int = 2, num_random_blocks: int = 3):
        super().__init__()
        self.embed_dim = embed_dim; self.num_heads = num_heads
        self.head_dim = embed_dim // num_heads; self.block_size = block_size
        self.num_global = num_global_tokens; self.num_random = num_random_blocks
        self.qkv = nn.Linear(embed_dim, 3 * embed_dim, bias=False)
        self.out_proj = nn.Linear(embed_dim, embed_dim, bias=False)
        self.scale = 1.0 / math.sqrt(self.head_dim)
    def _create_sparse_mask(self, seq_len: int, device: torch.device) -> torch.Tensor:
        """Create block-sparse attention mask."""
        num_blocks = (seq_len + self.block_size - 1) // self.block_size
        mask = torch.zeros(seq_len, seq_len, dtype=torch.bool, device=device)
        # Global tokens attend to all positions
        mask[:self.num_global, :] = True; mask[:, :self.num_global] = True
        # Sliding window (3 blocks)
        for i in range(seq_len):
            start = max(0, i - self.block_size); end = min(seq_len, i + self.block_size + 1)
            mask[i, start:end] = True
        # Random blocks
        for block_i in range(num_blocks):
            random_blocks = torch.randperm(num_blocks, device=device)[:self.num_random]
            for rb in random_blocks:
                r_start = block_i * self.block_size; r_end = min(r_start + self.block_size, seq_len)
                c_start = rb * self.block_size; c_end = min(c_start + self.block_size, seq_len)
                mask[r_start:r_end, c_start:c_end] = True
        return mask
    def forward(self, x: torch.Tensor, causal: bool = False) -> torch.Tensor:
        B, T, _ = x.shape
        qkv = self.qkv(x).reshape(B, T, 3, self.num_heads, self.head_dim).permute(2, 0, 3, 1, 4)
        q, k, v = qkv[0], qkv[1], qkv[2]
        attn = (q @ k.transpose(-2, -1)) * self.scale
        sparse_mask = self._create_sparse_mask(T, x.device)
        attn = attn.masked_fill(~sparse_mask.unsqueeze(0).unsqueeze(0), float('-inf'))
        if causal:
            causal_mask = torch.triu(torch.ones(T, T, device=x.device, dtype=torch.bool), 1)
            attn = attn.masked_fill(causal_mask.unsqueeze(0).unsqueeze(0), float('-inf'))
        attn = F.softmax(attn, dim=-1)
        out = (attn @ v).transpose(1, 2).reshape(B, T, self.embed_dim)
        return self.out_proj(out)
    def attention_complexity(self, seq_len: int) -> str:
        full = seq_len * seq_len
        sparse = (self.num_global * seq_len * 2 + seq_len * self.block_size * 3 +
                  seq_len * self.num_random * self.block_size)
        return f"Full: {full}, Sparse: ~{sparse}, Reduction: {(1-sparse/full)*100:.1f}%"
