"""
OMNI Transformer Engine — Multi-Head Attention Module
Production-grade MHA with support for GQA (Grouped-Query Attention),
MQA (Multi-Query Attention), and rotary position embeddings.

Learned from: huggingface/transformers, Shekswess/tiny-reasoning-language-model,
              jhcho99/CoFormer (CVPR'22)
"""

from __future__ import annotations

import math
from typing import Optional, Tuple

import torch
import torch.nn as nn
import torch.nn.functional as F

from .scaled_dot_product_attention import (
    AttentionConfig,
    AttentionType,
    scaled_dot_product_attention,
)


class RotaryPositionEmbedding(nn.Module):
    """
    Rotary Position Embedding (RoPE) as used in LLaMA, Qwen, Mistral.
    Applies rotation matrices to Q and K projections to encode relative position.
    """

    def __init__(self, dim: int, max_seq_len: int = 8192, base: float = 10000.0):
        super().__init__()
        self.dim = dim
        self.max_seq_len = max_seq_len

        inv_freq = 1.0 / (base ** (torch.arange(0, dim, 2).float() / dim))
        self.register_buffer("inv_freq", inv_freq, persistent=False)

        self._build_cache(max_seq_len)

    def _build_cache(self, seq_len: int) -> None:
        t = torch.arange(seq_len, device=self.inv_freq.device, dtype=self.inv_freq.dtype)
        freqs = torch.outer(t, self.inv_freq)
        emb = torch.cat([freqs, freqs], dim=-1)
        self.register_buffer("cos_cached", emb.cos(), persistent=False)
        self.register_buffer("sin_cached", emb.sin(), persistent=False)

    @staticmethod
    def _rotate_half(x: torch.Tensor) -> torch.Tensor:
        x1, x2 = x.chunk(2, dim=-1)
        return torch.cat([-x2, x1], dim=-1)

    def forward(
        self, q: torch.Tensor, k: torch.Tensor, position_ids: Optional[torch.Tensor] = None
    ) -> Tuple[torch.Tensor, torch.Tensor]:
        seq_len = q.shape[-2]

        if seq_len > self.max_seq_len:
            self._build_cache(seq_len)
            self.max_seq_len = seq_len

        if position_ids is not None:
            cos = self.cos_cached[position_ids].unsqueeze(1)
            sin = self.sin_cached[position_ids].unsqueeze(1)
        else:
            cos = self.cos_cached[:seq_len].unsqueeze(0).unsqueeze(0)
            sin = self.sin_cached[:seq_len].unsqueeze(0).unsqueeze(0)

        q_embed = (q * cos) + (self._rotate_half(q) * sin)
        k_embed = (k * cos) + (self._rotate_half(k) * sin)
        return q_embed, k_embed


class MultiHeadAttention(nn.Module):
    """
    Production Multi-Head Attention supporting:
    - Standard MHA (num_kv_heads == num_heads)
    - Grouped-Query Attention (num_kv_heads < num_heads)
    - Multi-Query Attention (num_kv_heads == 1)
    - Optional Rotary Position Embeddings
    - KV-Cache for autoregressive inference
    """

    def __init__(
        self,
        config: AttentionConfig,
        use_rope: bool = True,
        use_bias: bool = False,
    ):
        super().__init__()
        self.config = config
        self.use_rope = use_rope

        self.q_proj = nn.Linear(
            config.embed_dim, config.num_heads * config.head_dim, bias=use_bias
        )
        self.k_proj = nn.Linear(
            config.embed_dim, config.num_kv_heads * config.head_dim, bias=use_bias
        )
        self.v_proj = nn.Linear(
            config.embed_dim, config.num_kv_heads * config.head_dim, bias=use_bias
        )
        self.o_proj = nn.Linear(
            config.num_heads * config.head_dim, config.embed_dim, bias=use_bias
        )

        if use_rope:
            self.rope = RotaryPositionEmbedding(
                config.head_dim, max_seq_len=config.max_seq_len
            )
        else:
            self.rope = None

        self._init_weights()

    def _init_weights(self) -> None:
        for module in [self.q_proj, self.k_proj, self.v_proj, self.o_proj]:
            nn.init.xavier_uniform_(module.weight)
            if module.bias is not None:
                nn.init.zeros_(module.bias)

    def forward(
        self,
        hidden_states: torch.Tensor,
        attention_mask: Optional[torch.Tensor] = None,
        position_ids: Optional[torch.Tensor] = None,
        kv_cache: Optional[Tuple[torch.Tensor, torch.Tensor]] = None,
        use_cache: bool = False,
    ) -> Tuple[torch.Tensor, Optional[torch.Tensor], Optional[Tuple[torch.Tensor, torch.Tensor]]]:
        """
        Args:
            hidden_states: (B, S, D)
            attention_mask: Optional additive mask
            position_ids: Optional position indices for RoPE
            kv_cache: Tuple of (cached_key, cached_value) for inference
            use_cache: Whether to return updated KV cache

        Returns:
            output: (B, S, D)
            attn_weights: Optional attention weights
            new_kv_cache: Optional updated cache
        """
        B, S, _ = hidden_states.shape

        # Project Q, K, V
        query = self.q_proj(hidden_states).view(
            B, S, self.config.num_heads, self.config.head_dim
        ).transpose(1, 2)

        key = self.k_proj(hidden_states).view(
            B, S, self.config.num_kv_heads, self.config.head_dim
        ).transpose(1, 2)

        value = self.v_proj(hidden_states).view(
            B, S, self.config.num_kv_heads, self.config.head_dim
        ).transpose(1, 2)

        # Apply Rotary Position Embeddings
        if self.rope is not None:
            query, key = self.rope(query, key, position_ids)

        # Handle KV cache for autoregressive decoding
        if kv_cache is not None:
            cached_k, cached_v = kv_cache
            key = torch.cat([cached_k, key], dim=2)
            value = torch.cat([cached_v, value], dim=2)

        new_kv_cache = (key, value) if use_cache else None

        # Compute attention
        attn_output, attn_weights = scaled_dot_product_attention(
            query, key, value, self.config, attention_mask, self.training
        )

        # Reshape and project output
        attn_output = attn_output.transpose(1, 2).contiguous().view(B, S, -1)
        output = self.o_proj(attn_output)

        return output, attn_weights, new_kv_cache

    def extra_repr(self) -> str:
        return (
            f"embed_dim={self.config.embed_dim}, "
            f"num_heads={self.config.num_heads}, "
            f"num_kv_heads={self.config.num_kv_heads}, "
            f"head_dim={self.config.head_dim}, "
            f"rope={self.use_rope}"
        )


class CrossAttention(nn.Module):
    """
    Cross-attention for encoder-decoder architectures.
    Used in machine translation, multimodal fusion, etc.
    Learned from: jhcho99/CoFormer collaborative transformers.
    """

    def __init__(self, config: AttentionConfig, use_bias: bool = False):
        super().__init__()
        self.config = config

        self.q_proj = nn.Linear(
            config.embed_dim, config.num_heads * config.head_dim, bias=use_bias
        )
        self.k_proj = nn.Linear(
            config.embed_dim, config.num_kv_heads * config.head_dim, bias=use_bias
        )
        self.v_proj = nn.Linear(
            config.embed_dim, config.num_kv_heads * config.head_dim, bias=use_bias
        )
        self.o_proj = nn.Linear(
            config.num_heads * config.head_dim, config.embed_dim, bias=use_bias
        )

    def forward(
        self,
        query_states: torch.Tensor,
        encoder_hidden_states: torch.Tensor,
        attention_mask: Optional[torch.Tensor] = None,
    ) -> Tuple[torch.Tensor, Optional[torch.Tensor]]:
        B, S_q, _ = query_states.shape
        S_k = encoder_hidden_states.shape[1]

        query = self.q_proj(query_states).view(
            B, S_q, self.config.num_heads, self.config.head_dim
        ).transpose(1, 2)

        key = self.k_proj(encoder_hidden_states).view(
            B, S_k, self.config.num_kv_heads, self.config.head_dim
        ).transpose(1, 2)

        value = self.v_proj(encoder_hidden_states).view(
            B, S_k, self.config.num_kv_heads, self.config.head_dim
        ).transpose(1, 2)

        cross_config = AttentionConfig(
            embed_dim=self.config.embed_dim,
            num_heads=self.config.num_heads,
            num_kv_heads=self.config.num_kv_heads,
            head_dim=self.config.head_dim,
            dropout=self.config.dropout,
            causal=False,
            attention_type=self.config.attention_type,
        )

        attn_output, attn_weights = scaled_dot_product_attention(
            query, key, value, cross_config, attention_mask, self.training
        )

        attn_output = attn_output.transpose(1, 2).contiguous().view(B, S_q, -1)
        output = self.o_proj(attn_output)
        return output, attn_weights
