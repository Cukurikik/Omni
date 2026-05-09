"""
omni_vision_tokenizer.py — ViT Patch Tokenizer with RQ
Inspired by: RQ-Transformer image tokenization + FashionCLIP
Layer: Compute / AI

Converts images to discrete residual-quantized codes via ViT encoder
and cascading codebook lookup for use in autoregressive generation.
"""

import torch
import torch.nn as nn
import torch.nn.functional as F

class PatchEmbed(nn.Module):
    def __init__(self, img_size=224, patch_size=16, in_chans=3, embed_dim=768):
        super().__init__()
        self.num_patches = (img_size // patch_size) ** 2
        self.proj = nn.Conv2d(in_chans, embed_dim, kernel_size=patch_size, stride=patch_size)
        self.norm = nn.LayerNorm(embed_dim)

    def forward(self, x):
        return self.norm(self.proj(x).flatten(2).transpose(1, 2))

class VisionTokenQuantizer(nn.Module):
    def __init__(self, dim=768, codebook_size=8192, num_levels=8):
        super().__init__()
        self.codebooks = nn.ModuleList([nn.Embedding(codebook_size, dim) for _ in range(num_levels)])
        self.pre_quant = nn.Linear(dim, dim)

    def quantize_level(self, x, level):
        cb = self.codebooks[level]
        dists = torch.cdist(x, cb.weight)
        indices = dists.argmin(dim=-1)
        quantized = cb(indices)
        return quantized, indices

    def forward(self, x):
        x = self.pre_quant(x)
        all_indices = []
        residual = x.clone()
        for level in range(len(self.codebooks)):
            quantized, indices = self.quantize_level(residual, level)
            all_indices.append(indices)
            residual = residual - quantized.detach() + quantized - quantized.detach()
        return torch.stack(all_indices, dim=1), residual

class OmniVisionTokenizer(nn.Module):
    def __init__(self, img_size=224, patch_size=16, dim=768, codebook_size=8192,
                 num_levels=8, depth=6, heads=12):
        super().__init__()
        self.patch_embed = PatchEmbed(img_size, patch_size, 3, dim)
        self.cls_token = nn.Parameter(torch.randn(1, 1, dim))
        self.pos_embed = nn.Parameter(torch.randn(1, (img_size // patch_size) ** 2 + 1, dim))
        enc_layer = nn.TransformerEncoderLayer(
            d_model=dim, nhead=heads, dim_feedforward=dim * 4,
            dropout=0.1, activation="gelu", batch_first=True, norm_first=True,
        )
        self.encoder = nn.TransformerEncoder(enc_layer, num_layers=depth)
        self.quantizer = VisionTokenQuantizer(dim, codebook_size, num_levels)
        self.decoder_proj = nn.Linear(dim, 3 * patch_size * patch_size)
        self.patch_size = patch_size

    def encode(self, images):
        x = self.patch_embed(images)
        b = x.shape[0]
        cls = self.cls_token.expand(b, -1, -1)
        x = torch.cat([cls, x], dim=1) + self.pos_embed
        x = self.encoder(x)
        return x[:, 1:]

    def tokenize(self, images):
        features = self.encode(images)
        codes, _ = self.quantizer(features)
        return codes

    def forward(self, images):
        features = self.encode(images)
        codes, residual = self.quantizer(features)
        commitment_loss = F.mse_loss(residual.detach(), torch.zeros_like(residual))
        recon = self.decoder_proj(features - residual)
        return {"codes": codes, "commitment_loss": commitment_loss, "reconstruction": recon}
