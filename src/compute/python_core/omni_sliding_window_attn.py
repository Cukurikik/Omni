"""OMNI Compute — Sliding Window Attention (Mistral-style)"""
import math; from typing import List

class SlidingWindowAttention:
    """Local attention with sliding window for O(n*w) complexity."""
    def __init__(self, embed_dim: int, num_heads: int, window_size: int = 4096):
        self.embed_dim = embed_dim; self.num_heads = num_heads
        self.head_dim = embed_dim // num_heads; self.window = window_size
        self.scale = 1.0 / math.sqrt(self.head_dim)
    def compute_attention_mask(self, seq_len: int) -> List[List[bool]]:
        mask = [[False] * seq_len for _ in range(seq_len)]
        for i in range(seq_len):
            start = max(0, i - self.window + 1)
            for j in range(start, i + 1): mask[i][j] = True
        return mask
    def effective_context(self, num_layers: int) -> int:
        return self.window * num_layers
    def memory_vs_full(self, seq_len: int) -> dict:
        full = seq_len * seq_len
        window = seq_len * min(self.window, seq_len)
        return {"full_attention": full, "sliding_window": window,
                "reduction": f"{(1-window/full)*100:.1f}%", "window_size": self.window}
