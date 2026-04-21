"""
OmniXTransformersEngine — Native Advanced Transformer Architecture Engine.

Studied from: lucidrains/x-transformers (4.8k★)
Implements: Configurable transformer with multiple attention variants
(RoPE, ALiBi, sinusoidal PE), normalization options (LayerNorm, RMSNorm),
feed-forward variants (standard, SwiGLU, GEGLU, ReGLU), memory tokens,
autoregressive generation, and full forward pass with language modeling head.

OMNI Domain: compute/ (Python)
CODE RULE 001-005 compliant. Only numpy dependency.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple

import numpy as np


ENGINE_VERSION: str = "1.1.0-omni"
ENGINE_NAME: str = "OmniXTransformersEngine"


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------

class NormType(Enum):
    """Normalization type selection."""
    LAYER_NORM = "layer_norm"
    RMS_NORM = "rms_norm"


class GLUVariant(Enum):
    """GLU feed-forward variant."""
    NONE = "none"
    GEGLU = "geglu"
    SWIGLU = "swiglu"
    REGLU = "reglu"


# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

@dataclass
class TransformerConfig:
    """Full transformer configuration.

    Attributes:
        d_model: Hidden dimension.
        n_heads: Number of attention heads.
        n_layers: Number of transformer blocks.
        d_ff: Feed-forward intermediate dimension.
        vocab_size: Vocabulary size.
        max_seq_len: Maximum sequence length.
        use_rope: Whether to use Rotary Positional Embeddings.
        use_alibi: Whether to use ALiBi attention bias.
        norm_type: Normalization type (LayerNorm or RMSNorm).
        glu_variant: GLU variant for feed-forward layers.
        dropout: Dropout rate (for future use).
        n_memory_tokens: Number of learnable memory tokens (0=disabled).
    """
    d_model: int = 128
    n_heads: int = 4
    n_layers: int = 4
    d_ff: int = 512
    vocab_size: int = 10000
    max_seq_len: int = 512
    use_rope: bool = True
    use_alibi: bool = False
    norm_type: NormType = NormType.LAYER_NORM
    glu_variant: GLUVariant = GLUVariant.NONE
    dropout: float = 0.0
    n_memory_tokens: int = 0


# ---------------------------------------------------------------------------
# Module-level positional encoding functions (importable)
# ---------------------------------------------------------------------------

def sinusoidal_pe(seq_len: int, d_model: int) -> np.ndarray:
    """Generate sinusoidal positional encodings.

    Args:
        seq_len: Maximum sequence length.
        d_model: Model dimension.

    Returns:
        Array of shape (seq_len, d_model).
    """
    pe = np.zeros((seq_len, d_model), dtype=np.float32)
    position = np.arange(seq_len, dtype=np.float32)[:, np.newaxis]
    div_term = np.exp(
        np.arange(0, d_model, 2, dtype=np.float32) * -(math.log(10000.0) / d_model)
    )
    pe[:, 0::2] = np.sin(position * div_term)
    pe[:, 1::2] = np.cos(position * div_term[: d_model // 2])
    return pe


def rotary_embedding(
    x: np.ndarray, seq_dim: int = 2, base: float = 10000.0
) -> np.ndarray:
    """Apply Rotary Positional Embedding (RoPE).

    Args:
        x: Input tensor of shape (..., seq_len, d_head) where d_head is even.
        seq_dim: Dimension index of the sequence axis.
        base: Base for geometric frequency schedule.

    Returns:
        Tensor with RoPE applied, same shape as input.
    """
    shape = x.shape
    S = shape[seq_dim]
    D = shape[-1]
    half = D // 2

    theta = base ** (-2.0 * np.arange(half, dtype=np.float32) / D)
    positions = np.arange(S, dtype=np.float32)
    freqs = np.outer(positions, theta)  # (S, half)
    cos_f = np.cos(freqs)  # (S, half)
    sin_f = np.sin(freqs)  # (S, half)

    # Broadcast to match x shape
    # x shape: (..., S, D)
    # We need cos/sin shape broadcast-compatible
    ndim = x.ndim
    for _ in range(seq_dim):
        cos_f = np.expand_dims(cos_f, 0)
        sin_f = np.expand_dims(sin_f, 0)

    cos_full = np.concatenate([cos_f, cos_f], axis=-1)
    sin_full = np.concatenate([sin_f, sin_f], axis=-1)

    x1 = x[..., :half]
    x2 = x[..., half:]
    rotated = np.concatenate([-x2, x1], axis=-1)

    return (x * cos_full + rotated * sin_full).astype(x.dtype)


def alibi_bias(n_heads: int, max_seq_len: int) -> np.ndarray:
    """Compute ALiBi (Attention with Linear Biases) position bias.

    Args:
        n_heads: Number of attention heads.
        max_seq_len: Maximum sequence length.

    Returns:
        Bias array of shape (n_heads, max_seq_len, max_seq_len).
    """
    # Slopes: geometric sequence from 2^(-8/n_heads) base
    slopes = np.array(
        [2.0 ** (-(8.0 * (i + 1)) / n_heads) for i in range(n_heads)],
        dtype=np.float32,
    )
    # Distance matrix: relative position differences
    positions = np.arange(max_seq_len, dtype=np.float32)
    dist = positions[np.newaxis, :] - positions[:, np.newaxis]  # (S, S)
    # Bias per head: slope * distance, causal (only look at past)
    bias = slopes[:, np.newaxis, np.newaxis] * dist[np.newaxis, :, :]
    return bias


# ---------------------------------------------------------------------------
# Normalization
# ---------------------------------------------------------------------------

def _layer_norm(x: np.ndarray, eps: float = 1e-5) -> np.ndarray:
    """Standard layer normalization."""
    mean = np.mean(x, axis=-1, keepdims=True)
    var = np.var(x, axis=-1, keepdims=True)
    return (x - mean) / np.sqrt(var + eps)


def _rms_norm(x: np.ndarray, eps: float = 1e-5) -> np.ndarray:
    """Root Mean Square layer normalization."""
    rms = np.sqrt(np.mean(x ** 2, axis=-1, keepdims=True) + eps)
    return x / rms


def _get_norm_fn(norm_type: NormType):
    """Select normalization function."""
    return _rms_norm if norm_type == NormType.RMS_NORM else _layer_norm


# ---------------------------------------------------------------------------
# Activation functions
# ---------------------------------------------------------------------------

def _gelu(x: np.ndarray) -> np.ndarray:
    return 0.5 * x * (1 + np.tanh(np.sqrt(2 / np.pi) * (x + 0.044715 * x ** 3)))

def _silu(x: np.ndarray) -> np.ndarray:
    return x / (1 + np.exp(-np.clip(x, -500, 500)))

def _relu(x: np.ndarray) -> np.ndarray:
    return np.maximum(0, x)


# ---------------------------------------------------------------------------
# Transformer block
# ---------------------------------------------------------------------------

class _TransformerBlock:
    """Single transformer decoder block with configurable components.

    Args:
        config: TransformerConfig instance.
    """

    def __init__(self, config: TransformerConfig) -> None:
        """Initialize _TransformerBlock."""
        d = config.d_model
        d_ff = config.d_ff
        self.config = config
        self.n_heads = config.n_heads
        self.d_head = d // config.n_heads
        self._norm = _get_norm_fn(config.norm_type)

        limit = np.sqrt(6.0 / (d + d))
        self.W_q = np.random.uniform(-limit, limit, (d, d)).astype(np.float32)
        self.W_k = np.random.uniform(-limit, limit, (d, d)).astype(np.float32)
        self.W_v = np.random.uniform(-limit, limit, (d, d)).astype(np.float32)
        self.W_o = np.random.uniform(-limit, limit, (d, d)).astype(np.float32)

        # Feed-forward weights
        glu = config.glu_variant
        if glu in (GLUVariant.GEGLU, GLUVariant.SWIGLU, GLUVariant.REGLU):
            # GLU variants need double intermediate dim for gate
            limit2 = np.sqrt(6.0 / (d + d_ff * 2))
            self.W_ff1 = np.random.uniform(-limit2, limit2, (d, d_ff * 2)).astype(np.float32)
        else:
            limit2 = np.sqrt(6.0 / (d + d_ff))
            self.W_ff1 = np.random.uniform(-limit2, limit2, (d, d_ff)).astype(np.float32)

        limit3 = np.sqrt(6.0 / (d_ff + d))
        self.W_ff2 = np.random.uniform(-limit3, limit3, (d_ff, d)).astype(np.float32)

    def _attention(
        self, x: np.ndarray, alibi: Optional[np.ndarray] = None
    ) -> np.ndarray:
        """Multi-head self-attention with optional RoPE or ALiBi.

        Args:
            x: Input (B, S, d_model).
            alibi: Optional ALiBi bias (n_heads, S, S).

        Returns:
            Attention output (B, S, d_model).
        """
        B, S, d = x.shape
        h = self.n_heads
        dh = self.d_head

        q = (x @ self.W_q).reshape(B, S, h, dh).transpose(0, 2, 1, 3)
        k = (x @ self.W_k).reshape(B, S, h, dh).transpose(0, 2, 1, 3)
        v = (x @ self.W_v).reshape(B, S, h, dh).transpose(0, 2, 1, 3)

        # RoPE
        if self.config.use_rope:
            q = rotary_embedding(q, seq_dim=2)
            k = rotary_embedding(k, seq_dim=2)

        # Scaled dot-product
        scores = np.matmul(q, k.transpose(0, 1, 3, 2)) / np.sqrt(dh)

        # Causal mask
        mask = np.triu(np.ones((S, S), dtype=np.float32) * -1e9, k=1)
        scores = scores + mask

        # ALiBi
        if alibi is not None:
            scores = scores + alibi[:, :S, :S]

        # Softmax
        scores_max = np.max(scores, axis=-1, keepdims=True)
        exp_s = np.exp(scores - scores_max)
        attn = exp_s / (np.sum(exp_s, axis=-1, keepdims=True) + 1e-12)

        out = np.matmul(attn, v)  # (B, h, S, dh)
        out = out.transpose(0, 2, 1, 3).reshape(B, S, d)
        return out @ self.W_o

    def _ff(self, x: np.ndarray) -> np.ndarray:
        """Feed-forward network with optional GLU variant.

        Args:
            x: Input (B, S, d_model).

        Returns:
            Output (B, S, d_model).
        """
        glu = self.config.glu_variant
        h = x @ self.W_ff1

        if glu == GLUVariant.SWIGLU:
            half = h.shape[-1] // 2
            return (_silu(h[..., :half]) * h[..., half:]) @ self.W_ff2
        elif glu == GLUVariant.GEGLU:
            half = h.shape[-1] // 2
            return (_gelu(h[..., :half]) * h[..., half:]) @ self.W_ff2
        elif glu == GLUVariant.REGLU:
            half = h.shape[-1] // 2
            return (_relu(h[..., :half]) * h[..., half:]) @ self.W_ff2
        else:
            return _gelu(h) @ self.W_ff2

    def forward(
        self, x: np.ndarray, alibi: Optional[np.ndarray] = None
    ) -> np.ndarray:
        """Forward pass with pre-norm residual connections.

        Args:
            x: Input (B, S, d_model).
            alibi: Optional ALiBi bias.

        Returns:
            Output (B, S, d_model).
        """
        x = x + self._attention(self._norm(x), alibi)
        x = x + self._ff(self._norm(x))
        return x

    @property
    def param_count(self) -> int:
        """Execute param count operation for _TransformerBlock."""
        return (
            self.W_q.size + self.W_k.size + self.W_v.size + self.W_o.size
            + self.W_ff1.size + self.W_ff2.size
        )


# ---------------------------------------------------------------------------
# Core engine
# ---------------------------------------------------------------------------

class OmniXTransformersEngine:
    """Production-grade configurable Transformer engine.

    Capabilities:
        - Multi-head causal self-attention
        - RoPE / ALiBi / Sinusoidal positional encodings
        - LayerNorm / RMSNorm normalization
        - SwiGLU / GEGLU / ReGLU feed-forward variants
        - Learnable memory tokens
        - Autoregressive generation (greedy / sampling)
        - Language modeling head

    Args:
        config: TransformerConfig instance.
    """

    def __init__(self, config: Optional[TransformerConfig] = None) -> None:
        """Initialize OmniXTransformersEngine."""
        if config is None:
            config = TransformerConfig()
        self.config = config
        self._norm = _get_norm_fn(config.norm_type)

        np.random.seed(42)

        # Token embeddings
        self.token_embed = (
            np.random.randn(config.vocab_size, config.d_model).astype(np.float32) * 0.02
        )

        # Positional embeddings (learned, used when neither RoPE nor ALiBi)
        self.pos_embed = (
            np.random.randn(1, config.max_seq_len, config.d_model).astype(np.float32) * 0.02
        )

        # Memory tokens
        if config.n_memory_tokens > 0:
            self.memory_tokens = (
                np.random.randn(1, config.n_memory_tokens, config.d_model).astype(np.float32)
                * 0.02
            )
        else:
            self.memory_tokens = None

        # Transformer blocks
        self.blocks = [_TransformerBlock(config) for _ in range(config.n_layers)]

        # ALiBi bias (precomputed if enabled)
        if config.use_alibi:
            self._alibi = alibi_bias(config.n_heads, config.max_seq_len)
        else:
            self._alibi = None

        # LM head (tied to token embeddings transpose)
        self.lm_head = self.token_embed.T.copy()  # (d_model, vocab_size)

    # -- Factory Methods ---------------------------------------------------

    @classmethod
    def tiny(cls) -> OmniXTransformersEngine:
        """Create a tiny model for testing.

        Config: d_model=64, 4 heads, 2 layers, d_ff=128, vocab=1000, max_seq=32.

        Returns:
            OmniXTransformersEngine instance.
        """
        return cls(TransformerConfig(
            d_model=64, n_heads=4, n_layers=2, d_ff=128,
            vocab_size=1000, max_seq_len=32,
        ))

    @classmethod
    def with_alibi(cls) -> OmniXTransformersEngine:
        """Create a model with ALiBi instead of RoPE.

        Returns:
            OmniXTransformersEngine instance with ALiBi enabled.
        """
        return cls(TransformerConfig(
            d_model=64, n_heads=4, n_layers=2, d_ff=128,
            vocab_size=1000, max_seq_len=32,
            use_rope=False, use_alibi=True,
        ))

    @classmethod
    def with_memory(cls, n_tokens: int = 4) -> OmniXTransformersEngine:
        """Create a model with learnable memory tokens.

        Args:
            n_tokens: Number of memory tokens.

        Returns:
            OmniXTransformersEngine instance with memory tokens.
        """
        return cls(TransformerConfig(
            d_model=64, n_heads=4, n_layers=2, d_ff=128,
            vocab_size=1000, max_seq_len=32,
            n_memory_tokens=n_tokens,
        ))

    # -- Forward Pass -------------------------------------------------------

    def forward(self, token_ids: np.ndarray) -> np.ndarray:
        """Forward pass through the transformer.

        Args:
            token_ids: Integer token IDs of shape (B, S).

        Returns:
            Logits array of shape (B, S, vocab_size).
        """
        B, S = token_ids.shape
        x = self.token_embed[token_ids]  # (B, S, d_model)

        # Add positional encoding (learned) when not using RoPE/ALiBi
        if not self.config.use_rope and not self.config.use_alibi:
            x = x + self.pos_embed[:, :S, :]

        # Prepend memory tokens if applicable
        mem_len = 0
        if self.memory_tokens is not None:
            mem = np.broadcast_to(self.memory_tokens, (B, self.config.n_memory_tokens, self.config.d_model)).copy()
            x = np.concatenate([mem, x], axis=1)
            mem_len = self.config.n_memory_tokens

        # Transformer blocks
        for block in self.blocks:
            x = block.forward(x, alibi=self._alibi)

        # Strip memory tokens from output
        if mem_len > 0:
            x = x[:, mem_len:, :]

        # LM head
        x = self._norm(x)
        logits = x @ self.lm_head  # (B, S, vocab_size)
        return logits

    # -- Generation ---------------------------------------------------------

    def generate(
        self,
        prompt_ids: np.ndarray,
        max_new_tokens: int = 16,
        temperature: float = 1.0,
        greedy: bool = False,
    ) -> np.ndarray:
        """Autoregressive generation.

        Args:
            prompt_ids: Prompt token IDs of shape (B, S_prompt).
            max_new_tokens: Number of new tokens to generate.
            temperature: Sampling temperature.
            greedy: If True, always pick argmax.

        Returns:
            Full sequence including prompt + generated tokens.
        """
        ids = prompt_ids.copy()

        for _ in range(max_new_tokens):
            # Truncate to max_seq_len
            context = ids[:, -self.config.max_seq_len:]
            logits = self.forward(context)  # (B, S, V)
            next_logits = logits[:, -1, :]  # (B, V)

            if greedy:
                next_token = np.argmax(next_logits, axis=-1, keepdims=True)
            else:
                # Temperature-scaled sampling
                scaled = next_logits / max(temperature, 1e-8)
                exp_l = np.exp(scaled - np.max(scaled, axis=-1, keepdims=True))
                probs = exp_l / np.sum(exp_l, axis=-1, keepdims=True)
                next_token = np.array([
                    [np.random.choice(probs.shape[-1], p=probs[b])]
                    for b in range(ids.shape[0])
                ])

            ids = np.concatenate([ids, next_token], axis=1)

        return ids

    # -- Introspection -------------------------------------------------------

    def param_count(self) -> int:
        """Count total trainable parameters.

        Returns:
            Total parameter count.
        """
        count = self.token_embed.size + self.pos_embed.size + self.lm_head.size
        for block in self.blocks:
            count += block.param_count
        if self.memory_tokens is not None:
            count += self.memory_tokens.size
        return count

    def diagnostics(self) -> Dict[str, Any]:
        """Return engine health diagnostics.

        Returns:
            Dictionary with engine status information.
        """
        return {
            "engine": ENGINE_NAME,
            "version": ENGINE_VERSION,
            "status": "operational",
            "config": {
                "d_model": self.config.d_model,
                "n_heads": self.config.n_heads,
                "n_layers": self.config.n_layers,
                "use_rope": self.config.use_rope,
                "use_alibi": self.config.use_alibi,
                "norm_type": self.config.norm_type.value,
                "glu_variant": self.config.glu_variant.value,
            },
            "param_count": self.param_count(),
            "capabilities": [
                "multi_head_attention", "rope", "alibi", "sinusoidal_pe",
                "layer_norm", "rms_norm", "swiglu", "geglu", "reglu",
                "memory_tokens", "autoregressive_generation",
            ],
        }
