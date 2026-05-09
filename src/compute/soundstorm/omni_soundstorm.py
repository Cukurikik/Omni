"""
omni_soundstorm.py — Parallel Audio Generation Engine
Inspired by: rishikksh20/SoundStorm-pytorch (Google SoundStorm)
Layer: Compute / AI

MaskGIT-style parallel decoding for neural audio codec tokens.
Generates all residual VQ levels simultaneously using iterative
confidence-based unmasking over a conformer backbone.
"""

import math
import torch
import torch.nn as nn
import torch.nn.functional as F
from typing import Optional, Tuple, List
from dataclasses import dataclass


@dataclass
class SoundStormConfig:
    num_tokens: int = 1024
    num_quantizers: int = 8
    dim: int = 512
    depth: int = 12
    heads: int = 8
    dim_head: int = 64
    ff_mult: int = 4
    conv_kernel: int = 31
    max_seq_len: int = 2048
    mask_token_id: int = 1024
    num_iterations: int = 16


class ConformerConvModule(nn.Module):
    """Conformer convolution module with depthwise separable convolution."""

    def __init__(self, dim: int, kernel_size: int = 31, dropout: float = 0.1):
        super().__init__()
        assert kernel_size % 2 == 1
        self.net = nn.Sequential(
            nn.LayerNorm(dim),
            nn.Linear(dim, dim * 2),
            nn.GLU(dim=-1),
            nn.Conv1d(dim, dim, kernel_size, padding=kernel_size // 2, groups=dim),
            nn.BatchNorm1d(dim),
            nn.SiLU(),
            nn.Conv1d(dim, dim, 1),
            nn.Dropout(dropout),
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        residual = x
        x = self.net[0](x)  # LayerNorm
        x = self.net[1](x)  # Linear
        x = self.net[2](x)  # GLU
        x = x.transpose(1, 2)  # (B, D, T) for Conv1d
        x = self.net[3](x)  # Depthwise Conv
        x = self.net[4](x)  # BatchNorm
        x = self.net[5](x)  # SiLU
        x = self.net[6](x)  # Pointwise Conv
        x = self.net[7](x)  # Dropout
        x = x.transpose(1, 2)  # Back to (B, T, D)
        return x + residual


class ConformerBlock(nn.Module):
    """Single Conformer block: FFN-half + MHSA + Conv + FFN-half."""

    def __init__(self, dim: int, heads: int = 8, dim_head: int = 64,
                 ff_mult: int = 4, conv_kernel: int = 31, dropout: float = 0.1):
        super().__init__()
        self.ff1 = nn.Sequential(
            nn.LayerNorm(dim),
            nn.Linear(dim, dim * ff_mult),
            nn.SiLU(),
            nn.Dropout(dropout),
            nn.Linear(dim * ff_mult, dim),
            nn.Dropout(dropout),
        )
        self.attn_norm = nn.LayerNorm(dim)
        self.attn = nn.MultiheadAttention(dim, heads, dropout=dropout, batch_first=True)
        self.conv = ConformerConvModule(dim, conv_kernel, dropout)
        self.ff2 = nn.Sequential(
            nn.LayerNorm(dim),
            nn.Linear(dim, dim * ff_mult),
            nn.SiLU(),
            nn.Dropout(dropout),
            nn.Linear(dim * ff_mult, dim),
            nn.Dropout(dropout),
        )
        self.final_norm = nn.LayerNorm(dim)

    def forward(self, x: torch.Tensor, mask: Optional[torch.Tensor] = None) -> torch.Tensor:
        x = x + 0.5 * self.ff1(x)
        normed = self.attn_norm(x)
        attn_out, _ = self.attn(normed, normed, normed, key_padding_mask=mask)
        x = x + attn_out
        x = self.conv(x)
        x = x + 0.5 * self.ff2(x)
        return self.final_norm(x)


class MaskScheduler:
    """Cosine schedule for iterative parallel unmasking."""

    @staticmethod
    def schedule(iteration: int, total_iterations: int) -> float:
        ratio = iteration / total_iterations
        return math.cos(ratio * math.pi * 0.5)

    @staticmethod
    def select_masks_to_unmask(
        confidences: torch.Tensor, mask: torch.Tensor,
        num_to_unmask: int,
    ) -> torch.Tensor:
        """Select tokens to unmask based on model confidence."""
        confidences = confidences.masked_fill(~mask, -float('inf'))
        _, indices = confidences.topk(num_to_unmask, dim=-1)
        new_mask = mask.clone()
        new_mask.scatter_(1, indices, False)
        return new_mask


class OmniSoundStorm(nn.Module):
    """SoundStorm: Parallel audio generation via iterative MaskGIT decoding.

    Processes multi-level VQ tokens from a neural audio codec (e.g., SoundStream)
    and generates all residual quantization levels in parallel using a
    confidence-based iterative unmasking strategy over a Conformer backbone.
    """

    def __init__(self, config: SoundStormConfig):
        super().__init__()
        self.config = config
        self.dim = config.dim

        # Separate embeddings per quantizer level
        self.token_embeddings = nn.ModuleList([
            nn.Embedding(config.num_tokens + 1, config.dim)  # +1 for mask token
            for _ in range(config.num_quantizers)
        ])
        self.level_embeddings = nn.Embedding(config.num_quantizers, config.dim)
        self.pos_embedding = nn.Embedding(config.max_seq_len, config.dim)

        self.conformer_blocks = nn.ModuleList([
            ConformerBlock(
                dim=config.dim,
                heads=config.heads,
                dim_head=config.dim_head,
                ff_mult=config.ff_mult,
                conv_kernel=config.conv_kernel,
            )
            for _ in range(config.depth)
        ])

        # Per-level prediction heads
        self.output_heads = nn.ModuleList([
            nn.Sequential(
                nn.LayerNorm(config.dim),
                nn.Linear(config.dim, config.num_tokens),
            )
            for _ in range(config.num_quantizers)
        ])

    def _embed_tokens(
        self, codes: torch.Tensor, level: int
    ) -> torch.Tensor:
        """Embed tokens for a specific quantizer level."""
        batch_size, seq_len = codes.shape
        device = codes.device
        tok_emb = self.token_embeddings[level](codes)
        pos_emb = self.pos_embedding(torch.arange(seq_len, device=device))
        lvl_emb = self.level_embeddings(torch.tensor(level, device=device))
        return tok_emb + pos_emb + lvl_emb

    def forward_train(
        self,
        codes: torch.Tensor,  # (B, Q, T) — multi-level VQ codes
        target_level: int,
    ) -> torch.Tensor:
        """Training forward: predict masked tokens at target_level given conditioning levels."""
        batch_size, num_q, seq_len = codes.shape
        device = codes.device

        # Embed all conditioning levels (levels < target_level)
        embeddings = torch.zeros(batch_size, seq_len, self.dim, device=device)
        for lvl in range(target_level):
            embeddings = embeddings + self._embed_tokens(codes[:, lvl], lvl)

        # Random masking of target level
        target_codes = codes[:, target_level]
        mask_ratio = torch.rand(1).item() * 0.8 + 0.1  # 10% to 90%
        mask = torch.rand(batch_size, seq_len, device=device) < mask_ratio
        masked_codes = target_codes.clone()
        masked_codes[mask] = self.config.mask_token_id
        embeddings = embeddings + self._embed_tokens(masked_codes, target_level)

        # Run through conformer
        for block in self.conformer_blocks:
            embeddings = block(embeddings)

        logits = self.output_heads[target_level](embeddings)
        loss = F.cross_entropy(
            logits[mask].view(-1, self.config.num_tokens),
            target_codes[mask].view(-1),
        )
        return loss

    @torch.no_grad()
    def generate(
        self,
        conditioning_codes: torch.Tensor,  # (B, num_conditioning_levels, T)
        num_generate_levels: int = 7,
        num_iterations: int = 16,
        temperature: float = 1.0,
    ) -> torch.Tensor:
        """Parallel generation of remaining VQ levels via iterative unmasking."""
        batch_size, num_cond, seq_len = conditioning_codes.shape
        device = conditioning_codes.device
        scheduler = MaskScheduler()

        all_codes = [conditioning_codes[:, i] for i in range(num_cond)]

        for level in range(num_cond, num_cond + num_generate_levels):
            current_codes = torch.full(
                (batch_size, seq_len), self.config.mask_token_id,
                dtype=torch.long, device=device,
            )
            mask = torch.ones(batch_size, seq_len, dtype=torch.bool, device=device)

            for iteration in range(num_iterations):
                embeddings = torch.zeros(batch_size, seq_len, self.dim, device=device)
                for lvl_idx, lvl_codes in enumerate(all_codes):
                    embeddings += self._embed_tokens(lvl_codes, lvl_idx)
                embeddings += self._embed_tokens(current_codes, level)

                for block in self.conformer_blocks:
                    embeddings = block(embeddings)

                logits = self.output_heads[min(level, len(self.output_heads) - 1)](embeddings)
                logits = logits / max(temperature, 1e-10)
                probs = F.softmax(logits, dim=-1)
                predicted = probs.argmax(dim=-1)
                confidences = probs.max(dim=-1).values

                current_codes = torch.where(mask, predicted, current_codes)

                # Determine how many to keep masked
                ratio = scheduler.schedule(iteration + 1, num_iterations)
                num_masked = max(1, int(mask.sum(-1).float().mean().item() * ratio))
                if num_masked > 0 and iteration < num_iterations - 1:
                    mask = scheduler.select_masks_to_unmask(
                        confidences, mask, mask.sum(-1).min().item() - num_masked
                    )
                else:
                    mask.fill_(False)

            all_codes.append(current_codes)

        return torch.stack(all_codes, dim=1)
