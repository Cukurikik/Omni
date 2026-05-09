import torch
import torch.nn as nn
from einops import rearrange

class OmniTimeSformer(nn.Module):
    """
    TimeSformer: Is Space-Time Attention All You Need for Video Understanding?
    Uses divided space-time attention to process video sequences efficiently.
    """
    def __init__(self, img_size=224, patch_size=16, num_frames=8, num_classes=400, embed_dim=768, num_heads=12):
        super().__init__()
        self.num_frames = num_frames
        self.num_patches = (img_size // patch_size) ** 2
        
        self.patch_embed = nn.Conv3d(3, embed_dim, kernel_size=(1, patch_size, patch_size), stride=(1, patch_size, patch_size))
        
        self.cls_token = nn.Parameter(torch.zeros(1, 1, embed_dim))
        self.pos_embed = nn.Parameter(torch.zeros(1, self.num_patches + 1, embed_dim))
        self.time_embed = nn.Parameter(torch.zeros(1, num_frames, embed_dim))
        
        # Temporal Attention Layer
        self.temporal_attn = nn.MultiheadAttention(embed_dim, num_heads, batch_first=True)
        self.temporal_norm1 = nn.LayerNorm(embed_dim)
        self.temporal_mlp = nn.Sequential(
            nn.Linear(embed_dim, embed_dim * 4), nn.GELU(), nn.Linear(embed_dim * 4, embed_dim)
        )
        self.temporal_norm2 = nn.LayerNorm(embed_dim)

        # Spatial Attention Layer
        self.spatial_attn = nn.MultiheadAttention(embed_dim, num_heads, batch_first=True)
        self.spatial_norm1 = nn.LayerNorm(embed_dim)
        self.spatial_mlp = nn.Sequential(
            nn.Linear(embed_dim, embed_dim * 4), nn.GELU(), nn.Linear(embed_dim * 4, embed_dim)
        )
        self.spatial_norm2 = nn.LayerNorm(embed_dim)
        
        self.head = nn.Linear(embed_dim, num_classes)

    def forward(self, x):
        # x: [B, C, T, H, W]
        B, C, T, H, W = x.shape
        x = self.patch_embed(x) # [B, D, T, H/P, W/P]
        x = rearrange(x, 'b d t h w -> b t (h w) d')
        
        # Add spatial pos embedding
        cls_tokens = self.cls_token.expand(B, T, -1, -1)
        x = torch.cat((cls_tokens, x), dim=2)
        x = x + self.pos_embed
        
        # Add temporal pos embedding
        x = rearrange(x, 'b t p d -> b p t d')
        x = x + self.time_embed
        
        # Temporal Attention
        x_flat = rearrange(x, 'b p t d -> (b p) t d')
        residual = x_flat
        x_flat = self.temporal_norm1(x_flat)
        x_flat, _ = self.temporal_attn(x_flat, x_flat, x_flat)
        x_flat = residual + x_flat
        x_flat = x_flat + self.temporal_mlp(self.temporal_norm2(x_flat))
        
        # Spatial Attention
        x = rearrange(x_flat, '(b p) t d -> (b t) p d', b=B)
        residual = x
        x = self.spatial_norm1(x)
        x, _ = self.spatial_attn(x, x, x)
        x = residual + x
        x = x + self.spatial_mlp(self.spatial_norm2(x))
        
        # Classification head on CLS token, averaged over time
        x = rearrange(x, '(b t) p d -> b t p d', b=B)
        cls_output = x[:, :, 0, :].mean(dim=1)
        return self.head(cls_output)
