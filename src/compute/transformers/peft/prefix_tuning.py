"""
OMNI Transformer — Prefix Tuning for Parameter-Efficient Fine-Tuning
Learned from: Li & Liang (2021), prefix-tuning patterns
"""
import torch
import torch.nn as nn
from typing import Optional


class PrefixTuning(nn.Module):
    """Prefix tuning: learn continuous task-specific prefix tokens."""
    def __init__(self, num_layers: int, num_heads: int, head_dim: int,
                 prefix_length: int = 20, hidden_dim: int = 512):
        super().__init__()
        self.prefix_length = prefix_length
        self.num_layers = num_layers
        total_dim = num_layers * 2 * num_heads * head_dim  # 2 for key+value

        self.prefix_tokens = nn.Embedding(prefix_length, hidden_dim)
        self.reparam = nn.Sequential(
            nn.Linear(hidden_dim, hidden_dim),
            nn.Tanh(),
            nn.Linear(hidden_dim, total_dim),
        )
        self.num_heads = num_heads
        self.head_dim = head_dim

    def forward(self, batch_size: int) -> list:
        prefix_idx = torch.arange(self.prefix_length, device=self.prefix_tokens.weight.device)
        prefix = self.reparam(self.prefix_tokens(prefix_idx))
        prefix = prefix.unsqueeze(0).expand(batch_size, -1, -1)

        # Split into per-layer key-value pairs
        prefix = prefix.view(batch_size, self.prefix_length, self.num_layers, 2, self.num_heads, self.head_dim)
        prefix = prefix.permute(2, 3, 0, 4, 1, 5)  # (layers, 2, B, H, prefix_len, D)
        kv_pairs = []
        for i in range(self.num_layers):
            k = prefix[i, 0]  # (B, H, prefix_len, D)
            v = prefix[i, 1]
            kv_pairs.append((k, v))
        return kv_pairs
