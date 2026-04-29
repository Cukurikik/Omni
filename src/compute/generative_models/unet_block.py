import torch
import torch.nn as nn
from typing import Tuple, Optional

# OMNI GENERATIVE-MODELS: U-Net Block
# PyTorch implementation of the fundamental residual block used in Diffusion U-Nets.
# Source: Stability-AI/generative-models

class UNetError(Exception):
    pass

class ResnetBlock(nn.Module):
    """
    Standard ResNet block for Diffusion U-Net with time embedding conditioning.
    """
    def __init__(self, in_channels: int, out_channels: int, time_emb_dim: int, dropout: float = 0.1):
        super().__init__()
        
        self.in_channels = in_channels
        self.out_channels = out_channels
        
        # Time embedding projection
        self.time_emb_proj = nn.Sequential(
            nn.SiLU(),
            nn.Linear(time_emb_dim, out_channels)
        )
        
        # First convolution layer
        self.norm1 = nn.GroupNorm(32, in_channels)
        self.conv1 = nn.Conv2d(in_channels, out_channels, kernel_size=3, padding=1)
        
        # Second convolution layer
        self.norm2 = nn.GroupNorm(32, out_channels)
        self.dropout = nn.Dropout(dropout)
        self.conv2 = nn.Conv2d(out_channels, out_channels, kernel_size=3, padding=1)
        
        # Residual connection projection (if channel dimensions differ)
        if in_channels != out_channels:
            self.shortcut = nn.Conv2d(in_channels, out_channels, kernel_size=1)
        else:
            self.shortcut = nn.Identity()

    def forward(self, x: torch.Tensor, t_emb: torch.Tensor) -> Tuple[Optional[torch.Tensor], Optional[UNetError]]:
        try:
            # 1. First convolution
            h = x
            h = self.norm1(h)
            h = nn.functional.silu(h)
            h = self.conv1(h)
            
            # 2. Add time embedding conditioning
            # t_emb shape: (batch, time_emb_dim) -> project to (batch, out_channels)
            # Reshape to (batch, out_channels, 1, 1) for broadcasting
            t_hidden = self.time_emb_proj(t_emb)
            t_hidden = t_hidden.unsqueeze(-1).unsqueeze(-1)
            h = h + t_hidden
            
            # 3. Second convolution
            h = self.norm2(h)
            h = nn.functional.silu(h)
            h = self.dropout(h)
            h = self.conv2(h)
            
            # 4. Residual connection
            out = h + self.shortcut(x)
            
            return out, None
            
        except Exception as e:
            return None, UNetError(f"UNet Block Forward Failed: {str(e)}")
