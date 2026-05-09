import torch
import torch.nn as nn

class OmniBolTFusionBlock(nn.Module):
    """
    OMNI Framework - BolT: Fused Window Transformers for fMRI
    Zero-mock implementation combining local windowed attention and global context for fMRI time series.
    """
    def __init__(self, dim: int, num_heads: int, window_size: int = 16):
        super().__init__()
        self.dim = dim
        self.num_heads = num_heads
        self.window_size = window_size

        self.local_attn = nn.MultiheadAttention(embed_dim=dim, num_heads=num_heads, batch_first=True)
        self.global_attn = nn.MultiheadAttention(embed_dim=dim, num_heads=num_heads, batch_first=True)
        
        self.norm1 = nn.LayerNorm(dim)
        self.norm2 = nn.LayerNorm(dim)
        
        self.ffn = nn.Sequential(
            nn.Linear(dim, dim * 4),
            nn.GELU(),
            nn.Linear(dim * 4, dim)
        )
        self.norm3 = nn.LayerNorm(dim)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        # x shape: (Batch, Time, ROI_Features)
        B, T, C = x.shape
        
        # 1. Local Windowed Attention
        # Pad if necessary
        pad_len = (self.window_size - T % self.window_size) % self.window_size
        if pad_len > 0:
            x = torch.cat([x, torch.zeros(B, pad_len, C, device=x.device)], dim=1)
        
        padded_T = x.shape[1]
        x_reshaped = x.view(B * (padded_T // self.window_size), self.window_size, C)
        
        local_out, _ = self.local_attn(x_reshaped, x_reshaped, x_reshaped)
        local_out = local_out.view(B, padded_T, C)
        
        # Remove padding
        if pad_len > 0:
            local_out = local_out[:, :T, :]
            x = x[:, :T, :]
            
        x = self.norm1(x + local_out)

        # 2. Global Attention (Cross-window fusion)
        global_out, _ = self.global_attn(x, x, x)
        x = self.norm2(x + global_out)

        # 3. FFN
        x = self.norm3(x + self.ffn(x))
        return x

class OmniBolTModel(nn.Module):
    def __init__(self, in_features: int, dim: int, num_classes: int, depth: int = 4):
        super().__init__()
        self.proj = nn.Linear(in_features, dim)
        self.blocks = nn.ModuleList([OmniBolTFusionBlock(dim, 8) for _ in range(depth)])
        self.head = nn.Linear(dim, num_classes)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        x = self.proj(x)
        for blk in self.blocks:
            x = blk(x)
        # Global pooling
        x = x.mean(dim=1)
        return self.head(x)
