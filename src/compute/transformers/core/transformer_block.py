"""
OMNI Transformer Engine — Transformer Block
Full encoder/decoder transformer block with pre-norm and post-norm variants.
Learned from: GPT-2/3, LLaMA, BERT, mhuzaifadev/deep-learning-masterclass
"""

from __future__ import annotations

from enum import Enum, auto
from typing import Optional, Tuple

import torch
import torch.nn as nn

from .multi_head_attention import MultiHeadAttention, CrossAttention
from .feed_forward import PositionWiseFeedForward, FFNActivation
from .scaled_dot_product_attention import AttentionConfig, AttentionType


class NormType(Enum):
    LAYER_NORM = auto()
    RMS_NORM = auto()


class RMSNorm(nn.Module):
    """Root Mean Square Layer Normalization (used in LLaMA)."""

    def __init__(self, dim: int, eps: float = 1e-6):
        super().__init__()
        self.eps = eps
        self.weight = nn.Parameter(torch.ones(dim))

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        rms = torch.sqrt(x.pow(2).mean(dim=-1, keepdim=True) + self.eps)
        return x / rms * self.weight


def _build_norm(dim: int, norm_type: NormType, eps: float = 1e-6) -> nn.Module:
    if norm_type == NormType.RMS_NORM:
        return RMSNorm(dim, eps)
    return nn.LayerNorm(dim, eps=eps)


class TransformerEncoderBlock(nn.Module):
    """
    Single Transformer Encoder Block (Pre-Norm variant by default).
    Architecture: LN → MHA → Residual → LN → FFN → Residual
    """

    def __init__(
        self,
        embed_dim: int = 768,
        num_heads: int = 12,
        num_kv_heads: Optional[int] = None,
        ffn_dim: Optional[int] = None,
        dropout: float = 0.1,
        attention_dropout: float = 0.0,
        activation: FFNActivation = FFNActivation.GELU,
        norm_type: NormType = NormType.RMS_NORM,
        attention_type: AttentionType = AttentionType.FLASH,
        use_rope: bool = True,
        use_bias: bool = False,
        max_seq_len: int = 8192,
    ):
        super().__init__()

        attn_config = AttentionConfig(
            embed_dim=embed_dim,
            num_heads=num_heads,
            num_kv_heads=num_kv_heads,
            dropout=attention_dropout,
            causal=False,
            attention_type=attention_type,
            max_seq_len=max_seq_len,
        )

        self.self_attn = MultiHeadAttention(attn_config, use_rope=use_rope, use_bias=use_bias)
        self.ffn = PositionWiseFeedForward(
            embed_dim=embed_dim,
            ffn_dim=ffn_dim,
            activation=activation,
            dropout=dropout,
            use_bias=use_bias,
        )

        self.norm1 = _build_norm(embed_dim, norm_type)
        self.norm2 = _build_norm(embed_dim, norm_type)
        self.dropout1 = nn.Dropout(dropout)
        self.dropout2 = nn.Dropout(dropout)

    def forward(
        self,
        x: torch.Tensor,
        attention_mask: Optional[torch.Tensor] = None,
        position_ids: Optional[torch.Tensor] = None,
    ) -> torch.Tensor:
        # Pre-Norm Self-Attention
        residual = x
        x = self.norm1(x)
        x, _, _ = self.self_attn(x, attention_mask=attention_mask, position_ids=position_ids)
        x = self.dropout1(x) + residual

        # Pre-Norm FFN
        residual = x
        x = self.norm2(x)
        x = self.ffn(x)
        x = self.dropout2(x) + residual

        return x


class TransformerDecoderBlock(nn.Module):
    """
    Single Transformer Decoder Block with causal self-attention and cross-attention.
    Architecture: LN → CausalMHA → Residual → LN → CrossAttn → Residual → LN → FFN → Residual
    """

    def __init__(
        self,
        embed_dim: int = 768,
        num_heads: int = 12,
        num_kv_heads: Optional[int] = None,
        ffn_dim: Optional[int] = None,
        dropout: float = 0.1,
        attention_dropout: float = 0.0,
        activation: FFNActivation = FFNActivation.SWIGLU,
        norm_type: NormType = NormType.RMS_NORM,
        attention_type: AttentionType = AttentionType.FLASH,
        use_rope: bool = True,
        use_bias: bool = False,
        has_cross_attention: bool = True,
        max_seq_len: int = 8192,
    ):
        super().__init__()

        causal_config = AttentionConfig(
            embed_dim=embed_dim,
            num_heads=num_heads,
            num_kv_heads=num_kv_heads,
            dropout=attention_dropout,
            causal=True,
            attention_type=attention_type,
            max_seq_len=max_seq_len,
        )

        self.self_attn = MultiHeadAttention(causal_config, use_rope=use_rope, use_bias=use_bias)
        self.norm1 = _build_norm(embed_dim, norm_type)
        self.dropout1 = nn.Dropout(dropout)

        self.has_cross_attention = has_cross_attention
        if has_cross_attention:
            cross_config = AttentionConfig(
                embed_dim=embed_dim,
                num_heads=num_heads,
                num_kv_heads=num_kv_heads,
                dropout=attention_dropout,
                causal=False,
                attention_type=attention_type,
            )
            self.cross_attn = CrossAttention(cross_config, use_bias=use_bias)
            self.norm2 = _build_norm(embed_dim, norm_type)
            self.dropout2 = nn.Dropout(dropout)

        ffn_norm_idx = 3 if has_cross_attention else 2
        self.ffn = PositionWiseFeedForward(
            embed_dim=embed_dim,
            ffn_dim=ffn_dim,
            activation=activation,
            dropout=dropout,
            use_bias=use_bias,
        )
        self.norm_ffn = _build_norm(embed_dim, norm_type)
        self.dropout_ffn = nn.Dropout(dropout)

    def forward(
        self,
        x: torch.Tensor,
        encoder_hidden_states: Optional[torch.Tensor] = None,
        attention_mask: Optional[torch.Tensor] = None,
        encoder_attention_mask: Optional[torch.Tensor] = None,
        position_ids: Optional[torch.Tensor] = None,
        kv_cache: Optional[Tuple[torch.Tensor, torch.Tensor]] = None,
        use_cache: bool = False,
    ) -> Tuple[torch.Tensor, Optional[Tuple[torch.Tensor, torch.Tensor]]]:

        # Causal Self-Attention
        residual = x
        x = self.norm1(x)
        x, _, new_kv_cache = self.self_attn(
            x, attention_mask=attention_mask, position_ids=position_ids,
            kv_cache=kv_cache, use_cache=use_cache,
        )
        x = self.dropout1(x) + residual

        # Cross-Attention (if encoder states provided)
        if self.has_cross_attention and encoder_hidden_states is not None:
            residual = x
            x = self.norm2(x)
            x, _ = self.cross_attn(x, encoder_hidden_states, encoder_attention_mask)
            x = self.dropout2(x) + residual

        # FFN
        residual = x
        x = self.norm_ffn(x)
        x = self.ffn(x)
        x = self.dropout_ffn(x) + residual

        return x, new_kv_cache


class CausalLMBlock(nn.Module):
    """
    Decoder-only Transformer Block (GPT/LLaMA style).
    No cross-attention, always causal.
    Optimized for autoregressive language model generation.
    """

    def __init__(
        self,
        embed_dim: int = 4096,
        num_heads: int = 32,
        num_kv_heads: int = 8,
        ffn_dim: int = 14336,
        dropout: float = 0.0,
        norm_type: NormType = NormType.RMS_NORM,
        attention_type: AttentionType = AttentionType.FLASH,
        max_seq_len: int = 8192,
    ):
        super().__init__()
        self.block = TransformerDecoderBlock(
            embed_dim=embed_dim,
            num_heads=num_heads,
            num_kv_heads=num_kv_heads,
            ffn_dim=ffn_dim,
            dropout=dropout,
            activation=FFNActivation.SWIGLU,
            norm_type=norm_type,
            attention_type=attention_type,
            use_rope=True,
            use_bias=False,
            has_cross_attention=False,
            max_seq_len=max_seq_len,
        )

    def forward(
        self,
        x: torch.Tensor,
        attention_mask: Optional[torch.Tensor] = None,
        position_ids: Optional[torch.Tensor] = None,
        kv_cache: Optional[Tuple[torch.Tensor, torch.Tensor]] = None,
        use_cache: bool = False,
    ) -> Tuple[torch.Tensor, Optional[Tuple[torch.Tensor, torch.Tensor]]]:
        return self.block(
            x,
            attention_mask=attention_mask,
            position_ids=position_ids,
            kv_cache=kv_cache,
            use_cache=use_cache,
        )
