"""
omni_polygon_extractor.py — Polygonal Building Footprint Extraction
Inspired by: Pix2Poly (Sequence Prediction Method for End-to-end extraction)
Layer: Compute / AI

Transforms remote sensing imagery directly into vector polygon sequences
using a Transformer encoder-decoder architecture.
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
from typing import Tuple, Dict

class PolyEncoder(nn.Module):
    """CNN + Transformer encoder to extract spatial features from images."""
    def __init__(self, in_channels: int = 3, hidden_dim: int = 256):
        super().__init__()
        # Simplified ResNet-like backbone for feature extraction
        self.backbone = nn.Sequential(
            nn.Conv2d(in_channels, 64, kernel_size=7, stride=2, padding=3, bias=False),
            nn.BatchNorm2d(64),
            nn.ReLU(inplace=True),
            nn.MaxPool2d(kernel_size=3, stride=2, padding=1),
            nn.Conv2d(64, 128, kernel_size=3, stride=2, padding=1, bias=False),
            nn.BatchNorm2d(128),
            nn.ReLU(inplace=True),
            nn.Conv2d(128, hidden_dim, kernel_size=3, stride=2, padding=1, bias=False),
            nn.BatchNorm2d(hidden_dim),
            nn.ReLU(inplace=True),
        )
        
        # Transformer encoder layers
        encoder_layer = nn.TransformerEncoderLayer(d_model=hidden_dim, nhead=8, dim_feedforward=1024)
        self.transformer = nn.TransformerEncoder(encoder_layer, num_layers=4)
        
    def forward(self, images: torch.Tensor) -> torch.Tensor:
        """
        Args:
            images: (B, C, H, W)
        Returns:
            memory: (B, N, D)
        """
        features = self.backbone(images)  # (B, D, H', W')
        B, D, H, W = features.shape
        
        # Flatten spatial dimensions
        flat_features = features.flatten(2).permute(2, 0, 1)  # (H'*W', B, D)
        
        # Add 2D absolute positional embeddings (omitted for brevity)
        
        encoded = self.transformer(flat_features)
        return encoded.permute(1, 0, 2)  # (B, H'*W', D)


class PolyDecoder(nn.Module):
    """Transformer decoder predicting vertex coordinates as discrete tokens."""
    def __init__(self, hidden_dim: int = 256, max_vertices: int = 60, grid_size: int = 256):
        super().__init__()
        self.max_vertices = max_vertices
        self.grid_size = grid_size
        
        # Tokens: [0, grid_size-1] are coordinate bins. 
        # grid_size is EOS token
        self.vocab_size = grid_size + 1
        self.eos_token = grid_size
        
        self.embedding = nn.Embedding(self.vocab_size, hidden_dim)
        
        decoder_layer = nn.TransformerDecoderLayer(d_model=hidden_dim, nhead=8, dim_feedforward=1024)
        self.transformer = nn.TransformerDecoder(decoder_layer, num_layers=4)
        
        self.head = nn.Linear(hidden_dim, self.vocab_size)
        
    def forward(self, target_seq: torch.Tensor, memory: torch.Tensor) -> torch.Tensor:
        """
        Args:
            target_seq: (B, S) integer coordinates
            memory: (B, N, D) encoded image features
        Returns:
            logits: (B, S, V)
        """
        B, S = target_seq.shape
        
        # (S, B, D)
        tgt_emb = self.embedding(target_seq).permute(1, 0, 2)
        mem_perm = memory.permute(1, 0, 2)
        
        # Causal mask
        tgt_mask = nn.Transformer.generate_square_subsequent_mask(S).to(target_seq.device)
        
        decoded = self.transformer(tgt_emb, mem_perm, tgt_mask=tgt_mask)
        
        # (B, S, V)
        logits = self.head(decoded.permute(1, 0, 2))
        return logits


class OmniPix2Poly(nn.Module):
    """Full End-to-end model mapping imagery to polygon vertices."""
    def __init__(self, in_channels: int = 3, hidden_dim: int = 256, grid_size: int = 256):
        super().__init__()
        self.encoder = PolyEncoder(in_channels, hidden_dim)
        self.decoder = PolyDecoder(hidden_dim, max_vertices=60, grid_size=grid_size)
        
    def forward(self, images: torch.Tensor, target_seq: torch.Tensor) -> torch.Tensor:
        """Training forward pass."""
        memory = self.encoder(images)
        logits = self.decoder(target_seq, memory)
        return logits
        
    @torch.no_grad()
    def extract_polygons(self, images: torch.Tensor, max_len: int = 60) -> torch.Tensor:
        """Inference mode: autoregressive generation of vertices."""
        B = images.size(0)
        device = images.device
        
        memory = self.encoder(images)
        
        # Start with SOS (assuming EOS serves as SOS for simplicity here)
        current_seq = torch.full((B, 1), self.decoder.eos_token, dtype=torch.long, device=device)
        
        for _ in range(max_len):
            logits = self.decoder(current_seq, memory)
            next_token = logits[:, -1, :].argmax(dim=-1, keepdim=True)
            current_seq = torch.cat([current_seq, next_token], dim=1)
            
            # If all batches generated EOS, we can stop early
            if (next_token == self.decoder.eos_token).all():
                break
                
        return current_seq
