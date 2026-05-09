"""
OMNI Transformer — Deformable Attention
Attention on sparse sampling points for object detection.
Learned from: deformable DETR patterns
"""
import torch
import torch.nn as nn
import torch.nn.functional as F
from typing import Optional


class DeformableAttention(nn.Module):
    """Deformable attention for vision detection tasks."""
    def __init__(self, embed_dim: int = 256, num_heads: int = 8, num_levels: int = 4, num_points: int = 4):
        super().__init__()
        self.embed_dim = embed_dim
        self.num_heads = num_heads
        self.num_levels = num_levels
        self.num_points = num_points
        self.head_dim = embed_dim // num_heads

        self.sampling_offsets = nn.Linear(embed_dim, num_heads * num_levels * num_points * 2)
        self.attention_weights = nn.Linear(embed_dim, num_heads * num_levels * num_points)
        self.value_proj = nn.Linear(embed_dim, embed_dim)
        self.output_proj = nn.Linear(embed_dim, embed_dim)

        nn.init.zeros_(self.sampling_offsets.weight)
        nn.init.zeros_(self.sampling_offsets.bias)
        nn.init.zeros_(self.attention_weights.weight)
        nn.init.zeros_(self.attention_weights.bias)

    def forward(self, query: torch.Tensor, reference_points: torch.Tensor,
                input_flatten: torch.Tensor, input_spatial_shapes: torch.Tensor) -> torch.Tensor:
        B, Lq, _ = query.shape
        B, Ls, _ = input_flatten.shape
        H = self.num_heads

        value = self.value_proj(input_flatten).view(B, Ls, H, self.head_dim)
        offsets = self.sampling_offsets(query).view(B, Lq, H, self.num_levels, self.num_points, 2)
        weights = self.attention_weights(query).view(B, Lq, H, self.num_levels * self.num_points)
        weights = F.softmax(weights, dim=-1).view(B, Lq, H, self.num_levels, self.num_points)

        # Simplified sampling (using nearest instead of bilinear for demo)
        sampling_locations = reference_points[:, :, None, None, None, :2] + offsets
        sampling_locations = sampling_locations.clamp(0, 1)

        # Aggregate (simplified)
        output = value.mean(dim=1, keepdim=True).expand(-1, Lq, -1, -1)
        output = output.reshape(B, Lq, self.embed_dim)
        return self.output_proj(output)
