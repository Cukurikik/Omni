"""
omni_lit_vit_block.py — Less is More: Vision Transformer (LIT) Block
Layer: Compute / AI
Inspired by: ziplab/LIT

Implements an efficient Vision Transformer block that "pays less attention"
by restricting self-attention to early layers and relying purely on MLPs 
in deeper layers, saving immense VRAM while preserving accuracy. Zero mock.
"""

import torch
import torch.nn as nn

class OmniLITBlock(nn.Module):
    def __init__(self, d_model: int, n_heads: int, mlp_ratio: float = 4.0, use_attention: bool = True):
        super().__init__()
        self.use_attention = use_attention
        self.norm1 = nn.LayerNorm(d_model)
        
        if use_attention:
            self.attn = nn.MultiheadAttention(embed_dim=d_model, num_heads=n_heads, batch_first=True)
        else:
            self.attn = None

        self.norm2 = nn.LayerNorm(d_model)
        self.mlp = nn.Sequential(
            nn.Linear(d_model, int(d_model * mlp_ratio)),
            nn.GELU(),
            nn.Linear(int(d_model * mlp_ratio), d_model)
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        # Attention path (Only executed in early layers)
        if self.use_attention:
            x_norm = self.norm1(x)
            attn_out, _ = self.attn(query=x_norm, key=x_norm, value=x_norm, need_weights=False)
            x = x + attn_out

        # MLP path (Always executed)
        x = x + self.mlp(self.norm2(x))
        return x

class OmniLITVisionTransformer(nn.Module):
    def __init__(self, d_model: int, n_heads: int, depth: int, attention_depth: int):
        super().__init__()
        assert attention_depth <= depth, "Attention depth cannot exceed total depth"
        
        self.layers = nn.ModuleList()
        for i in range(depth):
            # First `attention_depth` layers use MHSA, the rest are pure MLPs
            use_attn = (i < attention_depth)
            self.layers.append(OmniLITBlock(d_model, n_heads, use_attention=use_attn))
            
        self.final_norm = nn.LayerNorm(d_model)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """
        x: (Batch, NumPatches, D)
        """
        for layer in self.layers:
            x = layer(x)
        return self.final_norm(x)
