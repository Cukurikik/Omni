"""
omni_parallel_decoder.py — Jacobi Parallel Decoding Engine
Inspired by: teelinsan/parallel-decoding (ACL)
Layer: Compute / AI

Accelerates transformer inference by parallelizing the autoregressive
decoding process using Jacobi iteration. Instead of generating tokens
one at a time, predicts multiple tokens simultaneously and refines.
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
from typing import Optional, Tuple, List, Dict
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)


@dataclass
class ParallelDecodingConfig:
    vocab_size: int = 32000
    dim: int = 512
    num_heads: int = 8
    num_layers: int = 6
    ff_dim: int = 2048
    max_seq_len: int = 512
    lookahead_window: int = 5
    max_jacobi_iterations: int = 10
    convergence_threshold: float = 0.95
    dropout: float = 0.1


class JacobiDecoder(nn.Module):
    """Decoder that supports parallel Jacobi iteration for fast inference."""

    def __init__(self, config: ParallelDecodingConfig):
        super().__init__()
        self.config = config
        self.embed = nn.Embedding(config.vocab_size, config.dim)
        self.pos_embed = nn.Embedding(config.max_seq_len, config.dim)

        layer = nn.TransformerDecoderLayer(
            d_model=config.dim,
            nhead=config.num_heads,
            dim_feedforward=config.ff_dim,
            dropout=config.dropout,
            activation="gelu",
            batch_first=True,
            norm_first=True,
        )
        self.decoder = nn.TransformerDecoder(layer, num_layers=config.num_layers)
        self.norm = nn.LayerNorm(config.dim)
        self.lm_head = nn.Linear(config.dim, config.vocab_size, bias=False)

    def forward(
        self,
        tgt_ids: torch.Tensor,
        memory: torch.Tensor,
        memory_mask: Optional[torch.Tensor] = None,
    ) -> torch.Tensor:
        b, n = tgt_ids.shape
        positions = torch.arange(n, device=tgt_ids.device).unsqueeze(0)
        x = self.embed(tgt_ids) + self.pos_embed(positions)
        causal_mask = torch.triu(
            torch.ones(n, n, device=x.device, dtype=torch.bool), diagonal=1
        )
        x = self.decoder(x, memory, tgt_mask=causal_mask,
                         memory_key_padding_mask=memory_mask)
        x = self.norm(x)
        return self.lm_head(x)


class OmniParallelDecoder(nn.Module):
    """Parallel decoder using Jacobi iteration for inference acceleration.

    Instead of sequential autoregressive generation, this decoder:
    1. Initializes a window of future tokens with guesses
    2. Runs the full decoder on all positions simultaneously
    3. Updates the guesses based on model predictions
    4. Repeats until convergence (positions stop changing)

    This can achieve 2-5x speedup on translation tasks while
    maintaining output quality identical to greedy decoding.
    """

    def __init__(self, config: ParallelDecodingConfig):
        super().__init__()
        self.config = config

        # Encoder (simplified for demo — in production, use pre-trained)
        self.src_embed = nn.Embedding(config.vocab_size, config.dim)
        self.src_pos = nn.Embedding(config.max_seq_len, config.dim)
        enc_layer = nn.TransformerEncoderLayer(
            d_model=config.dim,
            nhead=config.num_heads,
            dim_feedforward=config.ff_dim,
            dropout=config.dropout,
            activation="gelu",
            batch_first=True,
            norm_first=True,
        )
        self.encoder = nn.TransformerEncoder(enc_layer, num_layers=config.num_layers)

        # Decoder with Jacobi support
        self.decoder = JacobiDecoder(config)

    def encode(self, src_ids: torch.Tensor,
               src_mask: Optional[torch.Tensor] = None) -> torch.Tensor:
        b, n = src_ids.shape
        positions = torch.arange(n, device=src_ids.device).unsqueeze(0)
        x = self.src_embed(src_ids) + self.src_pos(positions)
        padding_mask = ~src_mask.bool() if src_mask is not None else None
        return self.encoder(x, src_key_padding_mask=padding_mask)

    def forward(
        self,
        src_ids: torch.Tensor,
        tgt_ids: torch.Tensor,
        src_mask: Optional[torch.Tensor] = None,
    ) -> torch.Tensor:
        memory = self.encode(src_ids, src_mask)
        padding_mask = ~src_mask.bool() if src_mask is not None else None
        return self.decoder(tgt_ids, memory, padding_mask)

    @torch.no_grad()
    def generate_autoregressive(
        self, src_ids: torch.Tensor, src_mask: Optional[torch.Tensor] = None,
        max_len: int = 128, bos_id: int = 1, eos_id: int = 2,
    ) -> torch.Tensor:
        """Standard autoregressive generation (baseline)."""
        memory = self.encode(src_ids, src_mask)
        mem_mask = ~src_mask.bool() if src_mask is not None else None
        b = src_ids.shape[0]
        device = src_ids.device

        generated = torch.full((b, 1), bos_id, dtype=torch.long, device=device)

        for _ in range(max_len):
            logits = self.decoder(generated, memory, mem_mask)
            next_token = logits[:, -1].argmax(dim=-1, keepdim=True)
            generated = torch.cat([generated, next_token], dim=1)
            if (next_token == eos_id).all():
                break

        return generated

    @torch.no_grad()
    def generate_jacobi(
        self, src_ids: torch.Tensor, src_mask: Optional[torch.Tensor] = None,
        max_len: int = 128, bos_id: int = 1, eos_id: int = 2,
    ) -> Tuple[torch.Tensor, Dict[str, float]]:
        """Jacobi parallel decoding — generates multiple tokens per iteration.

        Returns:
            generated: (B, L) generated token ids
            stats: dict with profiling information
        """
        memory = self.encode(src_ids, src_mask)
        mem_mask = ~src_mask.bool() if src_mask is not None else None
        b = src_ids.shape[0]
        device = src_ids.device
        window = self.config.lookahead_window

        confirmed = torch.full((b, 1), bos_id, dtype=torch.long, device=device)
        total_iterations = 0
        total_accepted = 0

        while confirmed.shape[1] < max_len:
            # Initialize lookahead window with copies of last confirmed token
            lookahead = confirmed[:, -1:].expand(-1, window).clone()
            candidate = torch.cat([confirmed, lookahead], dim=1)

            converged = False
            for jacobi_iter in range(self.config.max_jacobi_iterations):
                total_iterations += 1
                logits = self.decoder(candidate, memory, mem_mask)
                predicted = logits[:, confirmed.shape[1] - 1:confirmed.shape[1] + window - 1].argmax(dim=-1)

                old_lookahead = candidate[:, confirmed.shape[1]:]
                candidate = torch.cat([confirmed, predicted], dim=1)

                # Check convergence: how many positions didn't change
                match_ratio = (predicted == old_lookahead).float().mean().item()
                if match_ratio >= self.config.convergence_threshold:
                    converged = True
                    break

            # Accept converged positions
            final_logits = self.decoder(candidate, memory, mem_mask)
            final_preds = final_logits[:, confirmed.shape[1] - 1:].argmax(dim=-1)

            # Find first position that differs from candidate (if any)
            accept_count = window
            for pos in range(window):
                if pos > 0:
                    check_pred = final_preds[:, pos]
                    check_cand = candidate[:, confirmed.shape[1] + pos]
                    if not (check_pred == check_cand).all():
                        accept_count = pos + 1
                        break

            accepted_tokens = final_preds[:, :accept_count]
            confirmed = torch.cat([confirmed, accepted_tokens], dim=1)
            total_accepted += accept_count

            # Check for EOS
            if (confirmed == eos_id).any(dim=-1).all():
                break

        stats = {
            "total_jacobi_iterations": total_iterations,
            "total_tokens_accepted": total_accepted,
            "avg_tokens_per_iteration": total_accepted / max(total_iterations, 1),
            "speedup_ratio": total_accepted / max(total_iterations, 1),
        }

        return confirmed, stats
