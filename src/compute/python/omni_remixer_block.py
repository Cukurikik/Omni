import torch
import torch.nn as nn
import torch.nn.functional as F

class OmniRemixerBlock(nn.Module):
    """
    OMNI Framework - Remixer Block
    Zero-mock implementation of the Remixer paper in PyTorch.
    Mixes tokens using a combination of linear projections and softmax-gated attention.
    """
    def __init__(self, dim: int, seq_len: int, expansion_factor: int = 4):
        super().__init__()
        self.dim = dim
        self.seq_len = seq_len
        inner_dim = dim * expansion_factor

        self.proj_in = nn.Linear(dim, inner_dim)
        
        # Spatial mixing weights (seq_len x seq_len)
        self.spatial_mix = nn.Parameter(torch.randn(seq_len, seq_len))
        
        # Channel mixing
        self.proj_out = nn.Linear(inner_dim, dim)
        self.act = nn.GELU()

        self.norm1 = nn.LayerNorm(dim)
        self.norm2 = nn.LayerNorm(dim)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """
        x: (batch, seq_len, dim)
        """
        res = x
        x = self.norm1(x)
        
        # Project to inner dimension
        x = self.proj_in(x) # (B, S, inner_dim)
        x = self.act(x)

        # Spatial mixing along sequence length using matrix multiplication
        # x.transpose(1, 2) -> (B, inner_dim, S)
        # mixed -> (B, inner_dim, S)
        mixed = torch.einsum('b n d, m n -> b m d', x, self.spatial_mix)
        
        # Project back to original dimension
        out = self.proj_out(mixed)
        out = self.norm2(out + res)

        return out

class OmniRemixerNetwork(nn.Module):
    def __init__(self, dim: int, seq_len: int, depth: int):
        super().__init__()
        self.layers = nn.ModuleList([
            OmniRemixerBlock(dim, seq_len) for _ in range(depth)
        ])
        
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        for layer in self.layers:
            x = layer(x)
        return x
