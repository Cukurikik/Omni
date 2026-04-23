"""
OMNI Scenic Engine — Vision research primitives (ViT, attention, image processing).

Assimilated from: google-research/scenic (3.2k ★)
Scenic: A JAX Library for Computer Vision Research and Beyond.

Implements core vision research building blocks:
  - Patch embedding: image → patch → linear projection
  - Positional encoding (sinusoidal 2D, learnable)
  - Multi-head self-attention (MHSA)
  - Vision Transformer (ViT) block: Norm → MHSA → Norm → MLP
  - Classification token ([CLS]) pooling
  - Image preprocessing (resize, normalize, random erasing)
  - Feature pyramid construction

OMNI Domain: compute/ (Python)
CODE RULE 001-005 compliant. Only numpy dependency.
"""

from __future__ import annotations

import math
from typing import Any, Dict, List, Optional, Tuple

import numpy as np


ENGINE_VERSION: str = "1.0.0-omni"
ENGINE_NAME: str = "OmniScenicEngine"
from src.compute.python_core.omni_base_engine import Result, Ok, Err


class Result:
    """Monadic Result type for error handling."""
    pass

class Ok(Result):
    """Monadic Ok result type."""
    def __init__(self, value: Any) -> None:
        """Initialize Ok."""
        self.value = value

class Err(Result):
    """Monadic Err result type."""
    def __init__(self, error: str) -> None:
        """Initialize Err."""
        self.error = error


class OmniScenicEngine:
    """Production-grade vision research engine (ViT / Scenic patterns).

    Implements vision transformer building blocks:
      - Patch embedding (image to tokens)
      - 2D sinusoidal positional encoding
      - Multi-head self-attention (MHSA)
      - ViT encoder block (LayerNorm → MHSA → MLP)
      - CLS token pooling
      - Image preprocessing utilities
      - Feature pyramid construction

    @since 1.0.0
    @tags ["vision", "vit", "attention", "scenic", "compute"]
    """

    VERSION = ENGINE_VERSION
    ENGINE_ID = ENGINE_NAME

    def __init__(self) -> None:
        """Initialize OmniScenicEngine."""
        pass

    def diagnostics(self) -> Result:
        """Performs diagnostics operation for OmniScenicEngine."""
        return Ok({
            "engine": self.ENGINE_ID, "version": self.VERSION,
            "status": "operational",
            "capabilities": [
                "patch_embed", "sinusoidal_pos_enc_2d",
                "multi_head_self_attention", "mlp_block",
                "vit_block", "cls_pool", "layer_norm",
                "image_normalize", "random_erasing",
                "feature_pyramid",
            ],
        })

    # -----------------------------------------------------------------
    # 1. PATCH EMBEDDING
    # -----------------------------------------------------------------

    def patch_embed(
        self, image: np.ndarray, patch_size: int, W_proj: np.ndarray
    ) -> Result:
        """Convert image to patch embeddings.

        @param image: (H, W, C) image array.
        @param patch_size: Size of each patch (P×P).
        @param W_proj: (P*P*C, D) linear projection matrix.
        @returns Result with (N_patches, D) token embeddings.
        """
        H, W, C = image.shape
        if H % patch_size != 0 or W % patch_size != 0:
            return Err(f"Image ({H},{W}) not divisible by patch_size {patch_size}.")

        nH = H // patch_size
        nW = W // patch_size
        patches = []
        for i in range(nH):
            for j in range(nW):
                patch = image[i * patch_size:(i + 1) * patch_size,
                              j * patch_size:(j + 1) * patch_size, :]
                patches.append(patch.flatten())

        patches_arr = np.array(patches)  # (N, P*P*C)
        tokens = patches_arr @ W_proj     # (N, D)
        return Ok(tokens)

    # -----------------------------------------------------------------
    # 2. POSITIONAL ENCODING
    # -----------------------------------------------------------------

    def sinusoidal_pos_enc_2d(self, n_h: int, n_w: int, d_model: int) -> Result:
        """2D sinusoidal positional encoding for vision tokens.

        @param n_h: Number of patches along height.
        @param n_w: Number of patches along width.
        @param d_model: Embedding dimension.
        @returns Result with (n_h * n_w, d_model) positional encoding.
        """
        pe = np.zeros((n_h * n_w, d_model))
        d_half = d_model // 2

        for pos in range(n_h * n_w):
            row = pos // n_w
            col = pos % n_w
            for i in range(d_half):
                div_term = 10000.0 ** (2 * i / d_half)
                pe[pos, 2 * i] = math.sin(row / div_term)
                pe[pos, 2 * i + 1] = math.cos(col / div_term)

        return Ok(pe)

    def sinusoidal_pos_enc_1d(self, seq_len: int, d_model: int) -> Result:
        """1D sinusoidal positional encoding.

        @param seq_len: Sequence length.
        @param d_model: Embedding dimension.
        @returns Result with (seq_len, d_model) encoding.
        """
        pe = np.zeros((seq_len, d_model))
        positions = np.arange(seq_len)[:, None]
        div_term = np.exp(np.arange(0, d_model, 2) * (-math.log(10000.0) / d_model))

        pe[:, 0::2] = np.sin(positions * div_term)
        pe[:, 1::2] = np.cos(positions * div_term[:d_model // 2] if d_model % 2 else positions * div_term)

        return Ok(pe)

    # -----------------------------------------------------------------
    # 3. LAYER NORMALIZATION
    # -----------------------------------------------------------------

    def layer_norm(self, x: np.ndarray, gamma: np.ndarray, beta: np.ndarray, eps: float = 1e-5) -> Result:
        """Layer normalization.

        @param x: (..., D) input.
        @param gamma: (D,) scale.
        @param beta: (D,) shift.
        @returns Result with normalized x.
        """
        mean = np.mean(x, axis=-1, keepdims=True)
        var = np.var(x, axis=-1, keepdims=True)
        x_norm = (x - mean) / np.sqrt(var + eps)
        return Ok(gamma * x_norm + beta)

    # -----------------------------------------------------------------
    # 4. MULTI-HEAD SELF-ATTENTION
    # -----------------------------------------------------------------

    def multi_head_self_attention(
        self, x: np.ndarray,
        Wq: np.ndarray, Wk: np.ndarray, Wv: np.ndarray, Wo: np.ndarray,
        n_heads: int
    ) -> Result:
        """Multi-head self-attention (MHSA).

        @param x: (N, D) token embeddings.
        @param Wq: (D, D) query projection.
        @param Wk: (D, D) key projection.
        @param Wv: (D, D) value projection.
        @param Wo: (D, D) output projection.
        @param n_heads: Number of attention heads.
        @returns Result with (N, D) output.
        """
        N, D = x.shape
        if D % n_heads != 0:
            return Err(f"D={D} not divisible by n_heads={n_heads}.")

        d_k = D // n_heads
        Q = x @ Wq  # (N, D)
        K = x @ Wk
        V = x @ Wv

        # Reshape for multi-head
        Q = Q.reshape(N, n_heads, d_k).transpose(1, 0, 2)  # (H, N, d_k)
        K = K.reshape(N, n_heads, d_k).transpose(1, 0, 2)
        V = V.reshape(N, n_heads, d_k).transpose(1, 0, 2)

        # Scaled dot-product attention
        scores = Q @ K.transpose(0, 2, 1) / math.sqrt(d_k)  # (H, N, N)
        mx = np.max(scores, axis=-1, keepdims=True)
        attn = np.exp(scores - mx) / (np.sum(np.exp(scores - mx), axis=-1, keepdims=True) + 1e-10)
        out = attn @ V  # (H, N, d_k)

        # Concatenate heads
        out = out.transpose(1, 0, 2).reshape(N, D)  # (N, D)
        return Ok(out @ Wo)

    # -----------------------------------------------------------------
    # 5. MLP BLOCK
    # -----------------------------------------------------------------

    def mlp_block(self, x: np.ndarray, W1: np.ndarray, b1: np.ndarray, W2: np.ndarray, b2: np.ndarray) -> Result:
        """MLP block with GELU activation.

        y = W2 @ GELU(W1 @ x + b1) + b2

        @param x: (N, D) input.
        @param W1: (D, D_ff) first projection.
        @param b1: (D_ff,) bias.
        @param W2: (D_ff, D) second projection.
        @param b2: (D,) bias.
        @returns Result with (N, D) output.
        """
        h = x @ W1 + b1
        # GELU approximation: x * 0.5 * (1 + tanh(sqrt(2/pi) * (x + 0.044715 * x^3)))
        gelu = h * 0.5 * (1 + np.tanh(math.sqrt(2 / math.pi) * (h + 0.044715 * h ** 3)))
        return Ok(gelu @ W2 + b2)

    # -----------------------------------------------------------------
    # 6. VIT BLOCK
    # -----------------------------------------------------------------

    def vit_block(
        self, x: np.ndarray,
        gamma1: np.ndarray, beta1: np.ndarray,
        Wq: np.ndarray, Wk: np.ndarray, Wv: np.ndarray, Wo: np.ndarray,
        n_heads: int,
        gamma2: np.ndarray, beta2: np.ndarray,
        W_ff1: np.ndarray, b_ff1: np.ndarray,
        W_ff2: np.ndarray, b_ff2: np.ndarray,
    ) -> Result:
        """Full Vision Transformer block.

        x = x + MHSA(LayerNorm(x))
        x = x + MLP(LayerNorm(x))

        @param x: (N, D) input tokens.
        @returns Result with (N, D) output tokens.
        """
        # Pre-norm MHSA
        ln1_res = self.layer_norm(x, gamma1, beta1)
        if isinstance(ln1_res, Err): return ln1_res
        attn_res = self.multi_head_self_attention(ln1_res.value, Wq, Wk, Wv, Wo, n_heads)
        if isinstance(attn_res, Err): return attn_res
        x = x + attn_res.value

        # Pre-norm MLP
        ln2_res = self.layer_norm(x, gamma2, beta2)
        if isinstance(ln2_res, Err): return ln2_res
        mlp_res = self.mlp_block(ln2_res.value, W_ff1, b_ff1, W_ff2, b_ff2)
        if isinstance(mlp_res, Err): return mlp_res
        x = x + mlp_res.value

        return Ok(x)

    # -----------------------------------------------------------------
    # 7. POOLING
    # -----------------------------------------------------------------

    def cls_pool(self, tokens: np.ndarray) -> Result:
        """Extract [CLS] token (first token) for classification.

        @param tokens: (N, D) sequence tokens.
        @returns Result with (D,) CLS vector.
        """
        return Ok(tokens[0])

    def global_avg_pool(self, tokens: np.ndarray) -> Result:
        """Global average pooling over tokens.

        @param tokens: (N, D) sequence tokens.
        @returns Result with (D,) averaged vector.
        """
        return Ok(np.mean(tokens, axis=0))

    # -----------------------------------------------------------------
    # 8. IMAGE PREPROCESSING
    # -----------------------------------------------------------------

    def image_normalize(self, image: np.ndarray, mean: np.ndarray, std: np.ndarray) -> Result:
        """Normalize image with channel-wise mean/std.

        @param image: (H, W, C) image.
        @param mean: (C,) channel means.
        @param std: (C,) channel stds.
        @returns Result with normalized image.
        """
        return Ok((image - mean) / (std + 1e-10))

    def random_erasing(self, image: np.ndarray, p: float = 0.5, scale: Tuple[float, float] = (0.02, 0.33), seed: int = 0) -> Result:
        """Random erasing augmentation.

        @param image: (H, W, C) image.
        @param p: Probability of erasing.
        @param scale: Area fraction range.
        @returns Result with processed image.
        """
        rng = np.random.RandomState(seed)
        if rng.rand() > p:
            return Ok(image.copy())

        H, W = image.shape[:2]
        area = H * W
        target_area = rng.uniform(scale[0], scale[1]) * area
        aspect = rng.uniform(0.3, 1 / 0.3)
        eH = int(round(math.sqrt(target_area * aspect)))
        eW = int(round(math.sqrt(target_area / aspect)))

        if eH < H and eW < W:
            y = rng.randint(0, H - eH)
            x = rng.randint(0, W - eW)
            img = image.copy()
            img[y:y + eH, x:x + eW] = rng.rand(eH, eW, image.shape[2]) if image.ndim == 3 else rng.rand(eH, eW)
            return Ok(img)
        return Ok(image.copy())

    # -----------------------------------------------------------------
    # 9. FEATURE PYRAMID
    # -----------------------------------------------------------------

    def feature_pyramid(self, feature_maps: List[np.ndarray]) -> Result:
        """Construct feature pyramid by computing spatial statistics.

        @param feature_maps: List of (C, H, W) feature maps at different scales.
        @returns Result with list of (C,) pooled feature vectors.
        """
        pyramid = []
        for fm in feature_maps:
            pooled = np.mean(fm, axis=(1, 2))  # global average pool per channel
            pyramid.append(pooled)
        return Ok(pyramid)
