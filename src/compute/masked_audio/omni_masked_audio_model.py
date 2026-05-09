"""
omni_masked_audio_model.py — Masked Audio Modeling Pretraining
Inspired by: SoundStorm MaskGIT + Audio-MAE
Layer: Compute / AI

Self-supervised pretraining via masked audio token prediction.
Supports random masking, span masking, and structured masking strategies.
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
from typing import Dict, Optional, Tuple
from dataclasses import dataclass
import math


@dataclass
class MAMConfig:
    dim: int = 512
    depth: int = 8
    heads: int = 8
    vocab_size: int = 1024
    num_quantizer_levels: int = 8
    max_seq_len: int = 1500
    mask_token_id: int = 1025
    mask_ratio: float = 0.15
    dropout: float = 0.1


class MaskingStrategy:
    """Different masking strategies for audio tokens."""

    @staticmethod
    def random_mask(seq_len: int, mask_ratio: float,
                    device: torch.device) -> torch.Tensor:
        num_mask = max(1, int(seq_len * mask_ratio))
        mask_indices = torch.randperm(seq_len, device=device)[:num_mask]
        mask = torch.zeros(seq_len, dtype=torch.bool, device=device)
        mask[mask_indices] = True
        return mask

    @staticmethod
    def span_mask(seq_len: int, mask_ratio: float,
                  avg_span_len: int = 10,
                  device: torch.device = torch.device("cpu")) -> torch.Tensor:
        mask = torch.zeros(seq_len, dtype=torch.bool, device=device)
        num_mask = max(1, int(seq_len * mask_ratio))
        masked_count = 0

        while masked_count < num_mask:
            start = torch.randint(0, seq_len, (1,)).item()
            span_len = max(1, int(torch.empty(1).geometric_(1.0 / avg_span_len).item()))
            span_len = min(span_len, num_mask - masked_count, seq_len - start)
            mask[start:start + span_len] = True
            masked_count = mask.sum().item()

        return mask

    @staticmethod
    def cosine_schedule_mask(seq_len: int, iteration: int,
                             total_iterations: int,
                             device: torch.device) -> torch.Tensor:
        ratio = math.cos(math.pi / 2 * iteration / total_iterations)
        return MaskingStrategy.random_mask(seq_len, ratio, device)


class OmniMaskedAudioModel(nn.Module):
    """Masked audio modeling for self-supervised pretraining.

    Learns to predict masked audio codec tokens from unmasked context,
    supporting multi-level quantizer tokens.
    """

    def __init__(self, config: MAMConfig):
        super().__init__()
        self.config = config

        self.token_embed = nn.Embedding(config.vocab_size + 1, config.dim)
        self.level_embed = nn.Embedding(config.num_quantizer_levels, config.dim)
        self.pos_embed = nn.Parameter(torch.randn(1, config.max_seq_len, config.dim) * 0.02)
        self.mask_token = nn.Parameter(torch.randn(config.dim))

        encoder_layer = nn.TransformerEncoderLayer(
            d_model=config.dim, nhead=config.heads,
            dim_feedforward=config.dim * 4, dropout=config.dropout,
            activation="gelu", batch_first=True, norm_first=True,
        )
        self.encoder = nn.TransformerEncoder(encoder_layer, num_layers=config.depth)

        self.output_norm = nn.LayerNorm(config.dim)
        self.prediction_head = nn.Sequential(
            nn.Linear(config.dim, config.dim * 2),
            nn.GELU(),
            nn.LayerNorm(config.dim * 2),
            nn.Linear(config.dim * 2, config.vocab_size),
        )

    def _apply_mask(self, tokens: torch.Tensor,
                    mask: torch.Tensor) -> torch.Tensor:
        """Replace masked positions with the learned mask embedding."""
        embedded = self.token_embed(tokens)
        mask_expanded = mask.unsqueeze(-1).expand_as(embedded)
        embedded = torch.where(mask_expanded, self.mask_token.expand_as(embedded), embedded)
        return embedded

    def forward(
        self,
        token_ids: torch.Tensor,
        quantizer_level: int = 0,
        mask: Optional[torch.Tensor] = None,
    ) -> Dict[str, torch.Tensor]:
        B, T = token_ids.shape
        device = token_ids.device

        if mask is None:
            mask = torch.stack([
                MaskingStrategy.random_mask(T, self.config.mask_ratio, device)
                for _ in range(B)
            ])

        x = self._apply_mask(token_ids, mask)
        x = x + self.level_embed(torch.full((B, 1), quantizer_level,
                                            dtype=torch.long, device=device))
        x = x + self.pos_embed[:, :T]

        x = self.encoder(x)
        x = self.output_norm(x)
        logits = self.prediction_head(x)

        # Loss only on masked positions
        loss_mask = mask.view(-1)
        masked_logits = logits.view(-1, self.config.vocab_size)[loss_mask]
        masked_targets = token_ids.view(-1)[loss_mask]
        loss = F.cross_entropy(masked_logits, masked_targets)

        accuracy = (masked_logits.argmax(dim=-1) == masked_targets).float().mean()

        return {
            "loss": loss,
            "logits": logits,
            "accuracy": accuracy,
            "mask": mask,
            "num_masked": mask.sum().item(),
        }

    @torch.no_grad()
    def predict_masked(self, token_ids: torch.Tensor,
                       mask: torch.Tensor,
                       quantizer_level: int = 0,
                       temperature: float = 1.0) -> Tuple[torch.Tensor, torch.Tensor]:
        """Predict tokens at masked positions."""
        B, T = token_ids.shape
        x = self._apply_mask(token_ids, mask)
        x = x + self.level_embed(torch.full((B, 1), quantizer_level,
                                            dtype=torch.long, device=token_ids.device))
        x = x + self.pos_embed[:, :T]
        x = self.encoder(x)
        x = self.output_norm(x)
        logits = self.prediction_head(x) / max(temperature, 1e-8)

        probs = F.softmax(logits, dim=-1)
        predicted = probs.argmax(dim=-1)
        confidence = probs.max(dim=-1).values

        output = token_ids.clone()
        output[mask] = predicted[mask]

        return output, confidence
