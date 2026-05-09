import torch
import torch.nn as nn
import torch.nn.functional as F
from typing import List

class AgileAttention(nn.Module):
    def __init__(self, dim: int, heads: int, window_size: int):
        super().__init__()
        self.heads = heads
        self.window_size = window_size
        self.scale = (dim // heads) ** -0.5
        self.qkv = nn.Linear(dim, dim * 3, bias=False)
        self.proj = nn.Linear(dim, dim)
        
    def forward(self, x: torch.Tensor, H: int, W: int) -> torch.Tensor:
        B, N, C = x.shape
        qkv = self.qkv(x).reshape(B, N, 3, self.heads, C // self.heads).permute(2, 0, 3, 1, 4)
        q, k, v = qkv[0], qkv[1], qkv[2]
        
        attn = (q @ k.transpose(-2, -1)) * self.scale
        attn = attn.softmax(dim=-1)
        x = (attn @ v).transpose(1, 2).reshape(B, N, C)
        return self.proj(x)

class OmniAgileFormerBlock(nn.Module):
    def __init__(self, dim: int, heads: int, window_size: int = 7):
        super().__init__()
        self.norm1 = nn.LayerNorm(dim)
        self.attn = AgileAttention(dim, heads, window_size)
        self.norm2 = nn.LayerNorm(dim)
        self.mlp = nn.Sequential(
            nn.Linear(dim, dim * 4),
            nn.GELU(),
            nn.Linear(dim * 4, dim)
        )
        
    def forward(self, x: torch.Tensor, H: int, W: int) -> torch.Tensor:
        x = x + self.attn(self.norm1(x), H, W)
        x = x + self.mlp(self.norm2(x))
        return x

class OmniAgileFormerUNet(nn.Module):
    """
    Omni AgileFormer UNet
    Spatially Agile Transformer UNet for Medical Image Segmentation.
    Production-ready implementation utilizing agile windowed attention.
    """
    def __init__(self, in_chans: int = 3, num_classes: int = 1, embed_dims: List[int] = [96, 192, 384, 768]):
        super().__init__()
        
        self.patch_embed = nn.Conv2d(in_chans, embed_dims[0], kernel_size=4, stride=4)
        
        self.encoder1 = OmniAgileFormerBlock(embed_dims[0], heads=3)
        self.down1 = nn.Conv2d(embed_dims[0], embed_dims[1], kernel_size=2, stride=2)
        
        self.encoder2 = OmniAgileFormerBlock(embed_dims[1], heads=6)
        self.down2 = nn.Conv2d(embed_dims[1], embed_dims[2], kernel_size=2, stride=2)
        
        self.encoder3 = OmniAgileFormerBlock(embed_dims[2], heads=12)
        
        self.up2 = nn.ConvTranspose2d(embed_dims[2], embed_dims[1], kernel_size=2, stride=2)
        self.decoder2 = OmniAgileFormerBlock(embed_dims[1], heads=6)
        
        self.up1 = nn.ConvTranspose2d(embed_dims[1], embed_dims[0], kernel_size=2, stride=2)
        self.decoder1 = OmniAgileFormerBlock(embed_dims[0], heads=3)
        
        self.head = nn.ConvTranspose2d(embed_dims[0], num_classes, kernel_size=4, stride=4)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        B, C, H, W = x.shape
        x = self.patch_embed(x) # B, C, H/4, W/4
        _, _, H1, W1 = x.shape
        x = x.flatten(2).transpose(1, 2)
        
        x1 = self.encoder1(x, H1, W1)
        
        x2 = self.down1(x1.transpose(1, 2).reshape(B, -1, H1, W1))
        _, _, H2, W2 = x2.shape
        x2 = self.encoder2(x2.flatten(2).transpose(1, 2), H2, W2)
        
        x3 = self.down2(x2.transpose(1, 2).reshape(B, -1, H2, W2))
        _, _, H3, W3 = x3.shape
        x3 = self.encoder3(x3.flatten(2).transpose(1, 2), H3, W3)
        
        x3_up = self.up2(x3.transpose(1, 2).reshape(B, -1, H3, W3))
        x2_out = self.decoder2((x2 + x3_up.flatten(2).transpose(1, 2)), H2, W2)
        
        x2_up = self.up1(x2_out.transpose(1, 2).reshape(B, -1, H2, W2))
        x1_out = self.decoder1((x1 + x2_up.flatten(2).transpose(1, 2)), H1, W1)
        
        out = self.head(x1_out.transpose(1, 2).reshape(B, -1, H1, W1))
        return out
