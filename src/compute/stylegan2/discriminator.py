import torch
import torch.nn as nn
from typing import Tuple, Optional

# OMNI STYLEGAN2: Discriminator
# Python PyTorch implementation of the progressive discriminator network.
# Source: lucidrains/stylegan2-pytorch

class DiscriminatorError(Exception):
    pass

class DiscriminatorBlock(nn.Module):
    def __init__(self, in_channels: int, out_channels: int):
        super().__init__()
        # Standard convolutions with LeakyReLU
        self.conv1 = nn.Conv2d(in_channels, in_channels, 3, padding=1)
        self.conv2 = nn.Conv2d(in_channels, out_channels, 3, padding=1)
        self.act = nn.LeakyReLU(0.2, inplace=True)
        self.downsample = nn.AvgPool2d(2)
        
        # Skip connection to match dimensions
        self.skip = nn.Sequential(
            nn.AvgPool2d(2),
            nn.Conv2d(in_channels, out_channels, 1, bias=False)
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        skip = self.skip(x)
        
        x = self.act(self.conv1(x))
        x = self.act(self.conv2(x))
        x = self.downsample(x)
        
        # Residual
        return x + skip

class StyleGAN2Discriminator(nn.Module):
    """
    Simplified structural representation of the StyleGAN2 Discriminator.
    """
    def __init__(self, image_size: int = 256, channels: int = 3):
        super().__init__()
        
        # Initial projection
        self.from_rgb = nn.Conv2d(channels, 64, 1)
        
        # Progressive blocks
        self.blocks = nn.Sequential(
            DiscriminatorBlock(64, 128),  # 128
            DiscriminatorBlock(128, 256), # 64
            DiscriminatorBlock(256, 512), # 32
            DiscriminatorBlock(512, 512), # 16
            DiscriminatorBlock(512, 512), # 8
            DiscriminatorBlock(512, 512), # 4
        )
        
        # Final output layer
        self.final_conv = nn.Conv2d(512, 512, 4)
        self.final_linear = nn.Linear(512, 1)

    def forward(self, x: torch.Tensor) -> Tuple[Optional[torch.Tensor], Optional[DiscriminatorError]]:
        try:
            x = self.from_rgb(x)
            x = self.blocks(x)
            
            x = self.final_conv(x)
            x = x.view(x.shape[0], -1)
            
            out = self.final_linear(x)
            return out, None
            
        except Exception as e:
            return None, DiscriminatorError(f"Discriminator Forward Failed: {str(e)}")
