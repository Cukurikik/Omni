import torch
import torch.nn as nn
from typing import Tuple, Optional

# OMNI STYLEGAN2: Generator Block
# Python PyTorch implementation of the Modulated Convolution block, the core of StyleGAN2 architecture.
# Source: lucidrains/stylegan2-pytorch

class StyleGAN2Error(Exception):
    pass

class ModulatedConv2d(nn.Module):
    """
    Applies style modulation and demodulation to convolution weights.
    """
    def __init__(self, in_channels: int, out_channels: int, style_dim: int, kernel_size: int = 3):
        super().__init__()
        self.in_channels = in_channels
        self.out_channels = out_channels
        
        # Base weight
        self.weight = nn.Parameter(torch.randn(out_channels, in_channels, kernel_size, kernel_size))
        
        # Style mapping to channel multipliers
        self.style_proj = nn.Linear(style_dim, in_channels)

    def forward(self, x: torch.Tensor, style: torch.Tensor) -> Tuple[Optional[torch.Tensor], Optional[StyleGAN2Error]]:
        try:
            batch, in_c, h, w = x.shape
            
            # 1. Modulation: Get style multipliers
            # style: [batch, style_dim] -> s: [batch, in_channels]
            s = self.style_proj(style) + 1.0 # Add 1 to initialize at identity mapping
            
            # Reshape for broadcasting
            s = s.view(batch, 1, in_c, 1, 1)
            
            # Apply modulation to weights
            # weight: [out_c, in_c, k, k] -> mod_weight: [batch, out_c, in_c, k, k]
            mod_weight = self.weight.unsqueeze(0) * s
            
            # 2. Demodulation: Normalize the variance of output activations
            # Calculate standard deviation of modified weights
            sigma = torch.sqrt(torch.sum(mod_weight ** 2, dim=(2, 3, 4), keepdim=True) + 1e-8)
            demod_weight = mod_weight / sigma
            
            # 3. Convolution (Batched via grouping)
            # Reshape input and weights to use standard grouped conv2d
            x = x.view(1, batch * in_c, h, w)
            demod_weight = demod_weight.view(batch * self.out_channels, in_c, self.weight.shape[2], self.weight.shape[3])
            
            # Apply
            out = nn.functional.conv2d(x, demod_weight, padding=self.weight.shape[2]//2, groups=batch)
            
            # Reshape back
            out = out.view(batch, self.out_channels, out.shape[2], out.shape[3])
            
            return out, None
            
        except Exception as e:
            return None, StyleGAN2Error(f"Modulated Conv2D Failed: {str(e)}")
