"""
OMNI SuperGlue Engine — Feature matching via graph neural network primitives.

Assimilated from: magicleap/SuperGluePretrainedNetwork (3k ★)
Paper: "SuperGlue: Learning Feature Matching with Graph Neural Networks" (CVPR 2020)

Implements core feature matching building blocks:
  - Keypoint encoding (MLP + positional encoding)
  - Attention-based graph neural network (self + cross attention)
  - Optimal transport / Sinkhorn algorithm for assignment
  - Mutual nearest-neighbor matching
  - Match confidence scoring & filtering
  - Dual softmax matching

OMNI Domain: compute/ (Python)
CODE RULE 001-005 compliant. Only numpy dependency.
"""

from __future__ import annotations

import math
from typing import Any, Dict, List, Optional, Tuple

import numpy as np


ENGINE_VERSION: str = "1.0.0-omni"
ENGINE_NAME: str = "OmniSuperGlueEngine"


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


class OmniSuperGlueEngine:
    """Production-grade feature matching engine via graph attention primitives.

    Implements the SuperGlue architecture:
      - Keypoint encoding with positional + visual descriptors
      - Self-attention and cross-attention message passing
      - Sinkhorn optimal transport for soft assignment
      - Match filtering and confidence scoring

    @since 1.0.0
    @tags ["feature-matching", "graph-neural-network", "computer-vision", "compute"]
    """

    VERSION = ENGINE_VERSION
    ENGINE_ID = ENGINE_NAME

    def __init__(self, descriptor_dim: int = 256) -> None:
        """Initialize OmniSuperGlueEngine."""
        self.descriptor_dim = descriptor_dim

    def diagnostics(self) -> Result:
        """Performs diagnostics operation for OmniSuperGlueEngine."""
        return Ok({
            "engine": self.ENGINE_ID, "version": self.VERSION,
            "status": "operational",
            "capabilities": [
                "keypoint_encoding", "self_attention", "cross_attention",
                "sinkhorn", "dual_softmax", "mutual_nn", "match_filter",
            ],
        })

    # -----------------------------------------------------------------
    # 1. KEYPOINT ENCODING
    # -----------------------------------------------------------------

    def encode_keypoints(
        self, keypoints: np.ndarray, scores: np.ndarray, W_pos: np.ndarray, b_pos: np.ndarray
    ) -> Result:
        """Encode keypoint positions via learned MLP projection.

        out = ReLU(kp @ W^T + b) — projects (x, y) coords to descriptor space.

        @param keypoints: (N, 2) keypoint coordinates.
        @param scores: (N,) detection scores.
        @param W_pos: (D, 2) projection weight.
        @param b_pos: (D,) projection bias.
        @returns Result with (N, D) positional encodings.
        """
        if keypoints.ndim != 2 or keypoints.shape[1] != 2:
            return Err("keypoints must be (N, 2).")
        proj = keypoints @ W_pos.T + b_pos
        encoding = np.maximum(proj, 0)  # ReLU
        # Scale by detection score
        encoding = encoding * scores[:, None]
        return Ok(encoding)

    def fuse_descriptors(
        self, descriptors: np.ndarray, positional: np.ndarray
    ) -> Result:
        """Fuse visual descriptors with positional encodings via addition.

        @param descriptors: (N, D) visual feature descriptors.
        @param positional: (N, D) positional encodings.
        @returns Result with (N, D) fused representations.
        """
        if descriptors.shape != positional.shape:
            return Err("Shape mismatch.")
        return Ok(descriptors + positional)

    # -----------------------------------------------------------------
    # 2. ATTENTION (Self + Cross)
    # -----------------------------------------------------------------

    def attention(
        self, query: np.ndarray, key: np.ndarray, value: np.ndarray
    ) -> Result:
        """Scaled dot-product attention.

        @param query: (N, D).
        @param key: (M, D).
        @param value: (M, D).
        @returns Result with (N, D) attention output.
        """
        d = query.shape[-1]
        scores = query @ key.T / math.sqrt(d)
        max_s = np.max(scores, axis=-1, keepdims=True)
        exp_s = np.exp(scores - max_s)
        weights = exp_s / (np.sum(exp_s, axis=-1, keepdims=True) + 1e-10)
        return Ok(weights @ value)

    def self_attention_layer(
        self, features: np.ndarray, W_q: np.ndarray, W_k: np.ndarray, W_v: np.ndarray
    ) -> Result:
        """Self-attention graph message passing within one set of keypoints.

        @param features: (N, D) feature matrix.
        @param W_q, W_k, W_v: (D, D) projection matrices.
        @returns Result with (N, D) updated features (residual added).
        """
        Q = features @ W_q
        K = features @ W_k
        V = features @ W_v
        attn_res = self.attention(Q, K, V)
        if isinstance(attn_res, Err):
            return attn_res
        return Ok(features + attn_res.value)

    def cross_attention_layer(
        self, features_a: np.ndarray, features_b: np.ndarray,
        W_q: np.ndarray, W_k: np.ndarray, W_v: np.ndarray
    ) -> Result:
        """Cross-attention: features_a attends to features_b.

        @param features_a: (N, D) source features.
        @param features_b: (M, D) target features.
        @returns Result with (N, D) updated source features.
        """
        Q = features_a @ W_q
        K = features_b @ W_k
        V = features_b @ W_v
        attn_res = self.attention(Q, K, V)
        if isinstance(attn_res, Err):
            return attn_res
        return Ok(features_a + attn_res.value)

    # -----------------------------------------------------------------
    # 3. SINKHORN OPTIMAL TRANSPORT
    # -----------------------------------------------------------------

    def compute_score_matrix(
        self, desc_a: np.ndarray, desc_b: np.ndarray
    ) -> Result:
        """Compute pairwise similarity (dot product) score matrix.

        @param desc_a: (N, D) descriptors from image A.
        @param desc_b: (M, D) descriptors from image B.
        @returns Result with (N, M) score matrix.
        """
        if desc_a.shape[-1] != desc_b.shape[-1]:
            return Err("Descriptor dimension mismatch.")
        scores = desc_a @ desc_b.T
        return Ok(scores)

    def sinkhorn(
        self, scores: np.ndarray, dustbin: float = 1.0, iterations: int = 20
    ) -> Result:
        """Sinkhorn optimal transport on augmented score matrix.

        Augments the (N, M) scores with a dustbin row/column for unmatched
        keypoints, then iterates row/column log-space normalization.

        @param scores: (N, M) raw score matrix.
        @param dustbin: Dustbin (unmatched) score.
        @param iterations: Number of Sinkhorn iterations.
        @returns Result with (N+1, M+1) log-assignment matrix.
        """
        n, m = scores.shape
        # Augment with dustbin
        aug = np.full((n + 1, m + 1), dustbin, dtype=np.float64)
        aug[:n, :m] = scores

        log_alpha = np.log(aug + 1e-10)

        for _ in range(iterations):
            # Row normalization
            log_alpha -= np.log(np.sum(np.exp(log_alpha), axis=1, keepdims=True) + 1e-10)
            # Column normalization
            log_alpha -= np.log(np.sum(np.exp(log_alpha), axis=0, keepdims=True) + 1e-10)

        return Ok(log_alpha)

    # -----------------------------------------------------------------
    # 4. MATCHING
    # -----------------------------------------------------------------

    def mutual_nearest_neighbors(
        self, desc_a: np.ndarray, desc_b: np.ndarray
    ) -> Result:
        """Find mutual nearest-neighbor matches using L2 distance.

        @param desc_a: (N, D).
        @param desc_b: (M, D).
        @returns Result with dict: 'matches' (K, 2), 'distances' (K,).
        """
        # Pairwise L2
        diff = desc_a[:, None, :] - desc_b[None, :, :]
        dists = np.sqrt(np.sum(diff ** 2, axis=-1))  # (N, M)

        nn_a = np.argmin(dists, axis=1)  # for each a, nearest b
        nn_b = np.argmin(dists, axis=0)  # for each b, nearest a

        matches = []
        distances = []
        for i in range(len(desc_a)):
            j = nn_a[i]
            if nn_b[j] == i:
                matches.append([i, j])
                distances.append(float(dists[i, j]))

        if len(matches) == 0:
            return Ok({"matches": np.empty((0, 2), dtype=int), "distances": np.array([])})
        return Ok({"matches": np.array(matches), "distances": np.array(distances)})

    def dual_softmax_match(
        self, desc_a: np.ndarray, desc_b: np.ndarray, temperature: float = 0.1
    ) -> Result:
        """Dual-softmax matching: softmax along both dimensions, multiply.

        @param desc_a: (N, D) L2-normalized descriptors.
        @param desc_b: (M, D) L2-normalized descriptors.
        @param temperature: Softmax temperature.
        @returns Result with (N, M) confidence matrix.
        """
        scores = desc_a @ desc_b.T / temperature
        # Softmax per row
        row_max = np.max(scores, axis=1, keepdims=True)
        row_exp = np.exp(scores - row_max)
        row_soft = row_exp / (np.sum(row_exp, axis=1, keepdims=True) + 1e-10)
        # Softmax per column
        col_max = np.max(scores, axis=0, keepdims=True)
        col_exp = np.exp(scores - col_max)
        col_soft = col_exp / (np.sum(col_exp, axis=0, keepdims=True) + 1e-10)
        # Product
        return Ok(row_soft * col_soft)

    def filter_matches(
        self, matches: np.ndarray, confidences: np.ndarray, threshold: float = 0.5
    ) -> Result:
        """Filter matches by confidence threshold.

        @param matches: (K, 2) match indices.
        @param confidences: (K,) confidence scores.
        @param threshold: Minimum confidence.
        @returns Result with filtered matches and confidences.
        """
        if len(matches) == 0:
            return Ok({"matches": matches, "confidences": confidences})
        mask = confidences >= threshold
        return Ok({"matches": matches[mask], "confidences": confidences[mask]})

    def lowe_ratio_test(
        self, desc_a: np.ndarray, desc_b: np.ndarray, ratio: float = 0.75
    ) -> Result:
        """Lowe's ratio test for match filtering.

        For each descriptor in A, find two nearest in B.
        Keep match if dist1/dist2 < ratio.

        @param desc_a: (N, D).
        @param desc_b: (M, D).
        @param ratio: Maximum ratio (default 0.75).
        @returns Result with dict: 'matches' and 'ratios'.
        """
        if desc_b.shape[0] < 2:
            return Err("Need at least 2 descriptors in B.")

        diff = desc_a[:, None, :] - desc_b[None, :, :]
        dists = np.sqrt(np.sum(diff ** 2, axis=-1))

        sorted_idx = np.argsort(dists, axis=1)
        matches = []
        ratios = []
        for i in range(len(desc_a)):
            d1 = dists[i, sorted_idx[i, 0]]
            d2 = dists[i, sorted_idx[i, 1]]
            r = d1 / (d2 + 1e-10)
            if r < ratio:
                matches.append([i, sorted_idx[i, 0]])
                ratios.append(float(r))

        if len(matches) == 0:
            return Ok({"matches": np.empty((0, 2), dtype=int), "ratios": np.array([])})
        return Ok({"matches": np.array(matches), "ratios": np.array(ratios)})
