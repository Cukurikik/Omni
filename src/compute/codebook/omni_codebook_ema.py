"""
omni_codebook_ema.py — EMA-Updated Codebook for Vector Quantization
Inspired by: RQ-Transformer + SoundStorm VQ-VAE codebook
Layer: Compute / AI

Exponential moving average codebook updates for stable VQ training,
with codebook utilization monitoring and dead code revival.
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
from typing import Tuple, Dict
from dataclasses import dataclass


@dataclass
class CodebookConfig:
    codebook_size: int = 1024
    embedding_dim: int = 256
    ema_decay: float = 0.99
    epsilon: float = 1e-5
    dead_code_threshold: int = 2
    commitment_weight: float = 0.25


class EMACodebook(nn.Module):
    """Vector quantization codebook with EMA updates.

    Instead of backpropagating through the codebook, uses
    exponential moving averages of encoder outputs to update
    codebook entries, providing more stable training.
    """

    def __init__(self, config: CodebookConfig):
        super().__init__()
        self.config = config
        self.embedding_dim = config.embedding_dim
        self.codebook_size = config.codebook_size

        self.embedding = nn.Embedding(config.codebook_size, config.embedding_dim)
        nn.init.uniform_(self.embedding.weight, -1.0 / config.codebook_size,
                         1.0 / config.codebook_size)

        # EMA tracking buffers
        self.register_buffer("ema_cluster_size",
                             torch.zeros(config.codebook_size))
        self.register_buffer("ema_embed_sum",
                             self.embedding.weight.data.clone())
        self.register_buffer("usage_count",
                             torch.zeros(config.codebook_size, dtype=torch.long))

    def quantize(self, z: torch.Tensor) -> Tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
        """Quantize continuous vectors to nearest codebook entries.

        Args:
            z: (batch, seq_len, dim) continuous representations

        Returns:
            quantized: (batch, seq_len, dim) quantized vectors
            indices: (batch, seq_len) codebook indices
            distances: (batch, seq_len, codebook_size) L2 distances
        """
        flat_z = z.reshape(-1, self.embedding_dim)

        # L2 distance computation
        distances = (
            flat_z.pow(2).sum(dim=-1, keepdim=True)
            - 2 * flat_z @ self.embedding.weight.T
            + self.embedding.weight.pow(2).sum(dim=-1, keepdim=True).T
        )

        indices = distances.argmin(dim=-1)
        quantized = self.embedding(indices)

        # Reshape back
        batch_shape = z.shape[:-1]
        indices = indices.view(*batch_shape)
        quantized = quantized.view_as(z)
        distances = distances.view(*batch_shape, self.codebook_size)

        return quantized, indices, distances

    def forward(self, z: torch.Tensor) -> Dict[str, torch.Tensor]:
        """Forward pass with EMA codebook update during training."""
        quantized, indices, distances = self.quantize(z)

        if self.training:
            self._ema_update(z, indices)
            self._revive_dead_codes(z)

        # Straight-through estimator
        quantized_st = z + (quantized - z).detach()

        # Commitment loss
        commitment_loss = F.mse_loss(z, quantized.detach())

        # Codebook loss (for monitoring only — EMA handles updates)
        codebook_loss = F.mse_loss(quantized, z.detach())

        # Perplexity (codebook utilization metric)
        flat_indices = indices.reshape(-1)
        encodings = F.one_hot(flat_indices, self.codebook_size).float()
        avg_probs = encodings.mean(dim=0)
        perplexity = torch.exp(-torch.sum(avg_probs * torch.log(avg_probs + 1e-10)))

        return {
            "quantized": quantized_st,
            "indices": indices,
            "commitment_loss": commitment_loss * self.config.commitment_weight,
            "codebook_loss": codebook_loss,
            "perplexity": perplexity,
            "active_codes": (avg_probs > 0).sum().item(),
        }

    @torch.no_grad()
    def _ema_update(self, z: torch.Tensor, indices: torch.Tensor):
        """Update codebook entries using exponential moving average."""
        flat_z = z.reshape(-1, self.embedding_dim)
        flat_indices = indices.reshape(-1)

        encodings = F.one_hot(flat_indices, self.codebook_size).float()

        # Update cluster sizes
        self.ema_cluster_size.mul_(self.config.ema_decay).add_(
            encodings.sum(dim=0), alpha=1 - self.config.ema_decay
        )

        # Update embedding sums
        embed_sum = encodings.T @ flat_z
        self.ema_embed_sum.mul_(self.config.ema_decay).add_(
            embed_sum, alpha=1 - self.config.ema_decay
        )

        # Laplace smoothing
        n = self.ema_cluster_size.sum()
        cluster_size = (
            (self.ema_cluster_size + self.config.epsilon)
            / (n + self.codebook_size * self.config.epsilon)
            * n
        )

        # Update embeddings
        self.embedding.weight.data.copy_(
            self.ema_embed_sum / cluster_size.unsqueeze(-1)
        )

        # Track usage
        self.usage_count.add_(encodings.sum(dim=0).long())

    @torch.no_grad()
    def _revive_dead_codes(self, z: torch.Tensor):
        """Replace dead codebook entries with random encoder outputs."""
        flat_z = z.reshape(-1, self.embedding_dim)
        dead_mask = self.ema_cluster_size < self.config.dead_code_threshold

        num_dead = dead_mask.sum().item()
        if num_dead == 0 or flat_z.shape[0] == 0:
            return

        # Sample random encoder outputs
        replace_indices = torch.randperm(flat_z.shape[0],
                                         device=z.device)[:num_dead]
        replacements = flat_z[replace_indices]

        dead_indices = torch.where(dead_mask)[0][:num_dead]
        self.embedding.weight.data[dead_indices] = replacements
        self.ema_cluster_size[dead_indices] = 1.0
        self.ema_embed_sum[dead_indices] = replacements

    def get_utilization(self) -> float:
        """Return fraction of codebook entries being used."""
        return (self.usage_count > 0).float().mean().item()

    def lookup(self, indices: torch.Tensor) -> torch.Tensor:
        """Look up codebook entries by index."""
        return self.embedding(indices)


class ResidualCodebook(nn.Module):
    """Stacked residual vector quantization using EMA codebooks."""

    def __init__(self, num_levels: int = 8, config: CodebookConfig = None):
        super().__init__()
        if config is None:
            config = CodebookConfig()
        self.num_levels = num_levels
        self.codebooks = nn.ModuleList([
            EMACodebook(config) for _ in range(num_levels)
        ])

    def forward(self, z: torch.Tensor) -> Dict[str, torch.Tensor]:
        all_indices = []
        total_commitment_loss = torch.tensor(0.0, device=z.device)
        total_perplexity = 0.0
        residual = z

        for level, codebook in enumerate(self.codebooks):
            result = codebook(residual)
            all_indices.append(result["indices"])
            total_commitment_loss = total_commitment_loss + result["commitment_loss"]
            total_perplexity += result["perplexity"].item()
            residual = residual - result["quantized"].detach() + result["quantized"] - result["quantized"].detach()

        return {
            "codes": torch.stack(all_indices, dim=1),
            "quantized": z - residual.detach(),
            "commitment_loss": total_commitment_loss / self.num_levels,
            "avg_perplexity": total_perplexity / self.num_levels,
        }

    def decode(self, codes: torch.Tensor) -> torch.Tensor:
        """Reconstruct from stacked codebook indices."""
        quantized = torch.zeros_like(self.codebooks[0].embedding.weight[0]).unsqueeze(0).unsqueeze(0)
        quantized = quantized.expand(codes.shape[0], codes.shape[2], -1)
        quantized = quantized * 0

        for level in range(min(codes.shape[1], self.num_levels)):
            quantized = quantized + self.codebooks[level].lookup(codes[:, level])

        return quantized
