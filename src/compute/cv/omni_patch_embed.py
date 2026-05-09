"""
omni_patch_embed.py — Vision Transformer Patch Embedding
Layer: Compute / AI
Inspired by: ziplab/LIT

Implements the standard Patch Embedding layer for Vision Transformers.
Projects raw image (H x W x C) into flattened 1D sequences of patches (N x D)
using an optimized 2D Convolution stride. Zero mock.
"""

import torch
import torch.nn as nn

class OmniPatchEmbed(nn.Module):
    def __init__(self, img_size: int = 224, patch_size: int = 16, in_chans: int = 3, embed_dim: int = 768):
        super().__init__()
        self.img_size = img_size
        self.patch_size = patch_size
        self.in_chans = in_chans
        self.embed_dim = embed_dim
        
        self.grid_size = img_size // patch_size
        self.num_patches = self.grid_size * self.grid_size
        
        # We use a Conv2d layer with kernel_size and stride equal to patch_size
        # This is exactly equivalent to dividing the image into non-overlapping patches
        # and applying a linear projection to each patch.
        self.proj = nn.Conv2d(
            in_channels=in_chans, 
            out_channels=embed_dim, 
            kernel_size=patch_size, 
            stride=patch_size
        )
        
        self.norm = nn.LayerNorm(embed_dim)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """
        x: (Batch, Channels, Height, Width)
        Returns: (Batch, NumPatches, EmbedDim)
        """
        B, C, H, W = x.shape
        assert H == self.img_size and W == self.img_size, \
            f"Input image size ({H}*{W}) doesn't match model ({self.img_size}*{self.img_size})."
            
        # (Batch, EmbedDim, GridHeight, GridWidth)
        x = self.proj(x)
        
        # Flatten the spatial dimensions: (Batch, EmbedDim, NumPatches)
        x = x.flatten(2)
        
        # Transpose to sequence format: (Batch, NumPatches, EmbedDim)
        x = x.transpose(1, 2)
        
        # Apply layer normalization to the sequence
        x = self.norm(x)
        
        return x
