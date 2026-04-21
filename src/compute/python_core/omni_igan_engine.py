"""
OMNI iGAN Engine — Interactive image generation via GAN primitives.

Assimilated from: junyanz/iGAN (4k ★)
Paper: "Generative Visual Manipulation on the Natural Image Manifold" (Zhu et al., ECCV 2016)

Implements core GAN algorithmic building blocks:
  - Latent space operations (sampling, interpolation, slerp)
  - Generator: transposed convolution with BatchNorm + ReLU
  - Discriminator: strided convolution with LeakyReLU
  - Loss functions: BCE, Wasserstein, Hinge
  - Manifold projection: latent nearest-neighbor
  - Spectral normalization: weight spectral norm computation
  - Image morphing via smooth latent trajectories

OMNI Domain: compute/ (Python)
CODE RULE 001-005 compliant. Only numpy dependency.
"""

from __future__ import annotations

import math
from typing import Any, Dict, List, Optional, Tuple

import numpy as np


ENGINE_VERSION: str = "1.0.0-omni"
ENGINE_NAME: str = "OmniIGANEngine"


# ---------------------------------------------------------------------------
# Monadic Result
# ---------------------------------------------------------------------------

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


# ---------------------------------------------------------------------------
# Engine
# ---------------------------------------------------------------------------

class OmniIGANEngine:
    """Production-grade interactive GAN primitives engine.

    Provides the mathematical components for interactive image generation:
      - Latent space sampling & interpolation
      - Generator/discriminator forward pass simulation
      - GAN loss functions (BCE, Wasserstein, Hinge)
      - Manifold projection and image morphing
      - Spectral normalization for training stability

    @since 1.0.0
    @tags ["gan", "generative-model", "image-generation", "latent-space", "compute"]
    """

    VERSION = ENGINE_VERSION
    ENGINE_ID = ENGINE_NAME

    def __init__(self, latent_dim: int = 128) -> None:
        """Initialize engine.

        @param latent_dim: Dimensionality of the latent space (default 128).
        """
        self.latent_dim = latent_dim
        self._omni_version: str = "3.0.0-OMNI-NEXUS"

    def diagnostics(self) -> Result:
        """Return engine health diagnostics."""
        return Ok({
            "engine": self.ENGINE_ID,
            "version": self.VERSION,
            "status": "operational",
            "latent_dim": self.latent_dim,
            "capabilities": [
                "latent_sampling", "lerp", "slerp",
                "generator_forward", "discriminator_forward",
                "bce_loss", "wasserstein_loss", "hinge_loss",
                "manifold_projection", "spectral_norm",
            ],
        })

    # -----------------------------------------------------------------
    # 1. LATENT SPACE OPERATIONS
    # -----------------------------------------------------------------

    def sample_latent(
        self, batch_size: int, seed: Optional[int] = None
    ) -> Result:
        """Sample random latent vectors from N(0, 1).

        @param batch_size: Number of vectors to sample.
        @param seed: Optional random seed.
        @returns Result containing (batch_size, latent_dim) array.
        """
        if batch_size < 1:
            return Err("batch_size must be >= 1.")
        rng = np.random.RandomState(seed)
        z = rng.randn(batch_size, self.latent_dim)
        return Ok(z)

    def lerp(self, z1: np.ndarray, z2: np.ndarray, t: float) -> Result:
        """Linear interpolation in latent space.

        z_interp = (1 - t) * z1 + t * z2

        @param z1: Start latent vector.
        @param z2: End latent vector.
        @param t: Interpolation parameter in [0, 1].
        @returns Result containing interpolated vector.
        """
        if z1.shape != z2.shape:
            return Err("z1 and z2 must have the same shape.")
        if not 0 <= t <= 1:
            return Err("t must be in [0, 1].")
        return Ok((1 - t) * z1 + t * z2)

    def slerp(self, z1: np.ndarray, z2: np.ndarray, t: float) -> Result:
        """Spherical linear interpolation in latent space.

        Interpolates along the great circle arc on the hypersphere,
        producing smoother transitions than linear interpolation.

        @param z1: Start latent vector (1D).
        @param z2: End latent vector (1D).
        @param t: Interpolation parameter in [0, 1].
        @returns Result containing slerp-interpolated vector.
        """
        if z1.shape != z2.shape or z1.ndim != 1:
            return Err("z1 and z2 must be 1D with same shape.")
        if not 0 <= t <= 1:
            return Err("t must be in [0, 1].")

        n1 = np.linalg.norm(z1)
        n2 = np.linalg.norm(z2)
        if n1 < 1e-10 or n2 < 1e-10:
            return Ok((1 - t) * z1 + t * z2)  # fall back to lerp

        z1_n = z1 / n1
        z2_n = z2 / n2
        dot = np.clip(np.dot(z1_n, z2_n), -1.0, 1.0)
        omega = math.acos(dot)

        if abs(omega) < 1e-10:
            return Ok((1 - t) * z1 + t * z2)  # nearly parallel

        sin_omega = math.sin(omega)
        interp = (math.sin((1 - t) * omega) / sin_omega) * z1 + \
                 (math.sin(t * omega) / sin_omega) * z2
        return Ok(interp)

    def latent_trajectory(
        self, z1: np.ndarray, z2: np.ndarray, n_steps: int = 10, method: str = "slerp"
    ) -> Result:
        """Generate smooth trajectory between two latent codes.

        @param z1: Start latent vector (1D).
        @param z2: End latent vector (1D).
        @param n_steps: Number of interpolation steps.
        @param method: "lerp" or "slerp".
        @returns Result containing (n_steps, latent_dim) trajectory.
        """
        if n_steps < 2:
            return Err("n_steps must be >= 2.")

        trajectory = []
        for i in range(n_steps):
            t = i / (n_steps - 1)
            if method == "slerp":
                res = self.slerp(z1, z2, t)
            else:
                res = self.lerp(z1, z2, t)
            if isinstance(res, Err):
                return res
            trajectory.append(res.value)

        return Ok(np.array(trajectory))

    # -----------------------------------------------------------------
    # 2. GENERATOR (Transposed Convolution Simulation)
    # -----------------------------------------------------------------

    def generator_linear_block(
        self, z: np.ndarray, weight: np.ndarray, bias: np.ndarray
    ) -> Result:
        """Generator fully-connected projection block.

        out = ReLU(z @ W^T + b)

        @param z: Input latent batch (N, in_features).
        @param weight: Weight matrix (out_features, in_features).
        @param bias: Bias vector (out_features,).
        @returns Result containing (N, out_features) activated output.
        """
        if z.ndim != 2 or weight.ndim != 2:
            return Err("z must be 2D, weight must be 2D.")
        if z.shape[1] != weight.shape[1]:
            return Err("Feature dimension mismatch.")

        out = z @ weight.T + bias
        # ReLU activation
        out = np.maximum(out, 0)
        return Ok(out)

    def batch_norm_1d(
        self, x: np.ndarray, gamma: np.ndarray, beta: np.ndarray, eps: float = 1e-5
    ) -> Result:
        """1D Batch Normalization (per-feature across batch).

        @param x: (N, C) input.
        @param gamma: (C,) scale.
        @param beta: (C,) shift.
        @returns Result containing normalized output.
        """
        if x.ndim != 2:
            return Err("x must be 2D.")
        mu = np.mean(x, axis=0)
        var = np.var(x, axis=0)
        x_norm = (x - mu) / np.sqrt(var + eps)
        return Ok(gamma * x_norm + beta)

    # -----------------------------------------------------------------
    # 3. DISCRIMINATOR (Convolutional Feature Extraction)
    # -----------------------------------------------------------------

    def leaky_relu(self, x: np.ndarray, alpha: float = 0.2) -> Result:
        """LeakyReLU activation: f(x) = max(alpha*x, x).

        @param x: Input array.
        @param alpha: Negative slope (default 0.2).
        @returns Result containing activated output.
        """
        return Ok(np.where(x > 0, x, alpha * x))

    def discriminator_linear_block(
        self, x: np.ndarray, weight: np.ndarray, bias: np.ndarray, alpha: float = 0.2
    ) -> Result:
        """Discriminator linear block with LeakyReLU.

        out = LeakyReLU(x @ W^T + b, alpha)

        @param x: Input (N, in_features).
        @param weight: Weight matrix (out_features, in_features).
        @param bias: Bias vector (out_features,).
        @param alpha: LeakyReLU negative slope.
        @returns Result containing (N, out_features) output.
        """
        if x.ndim != 2 or weight.ndim != 2:
            return Err("x and weight must be 2D.")
        if x.shape[1] != weight.shape[1]:
            return Err("Feature dimension mismatch.")

        out = x @ weight.T + bias
        return self.leaky_relu(out, alpha)

    # -----------------------------------------------------------------
    # 4. GAN LOSS FUNCTIONS
    # -----------------------------------------------------------------

    def bce_loss(self, predictions: np.ndarray, targets: np.ndarray) -> Result:
        """Binary Cross-Entropy loss for GAN training.

        BCE = -mean(t * log(p) + (1-t) * log(1-p))

        @param predictions: Predicted probabilities in (0, 1).
        @param targets: Binary targets (0 or 1).
        @returns Result containing scalar loss.
        """
        if predictions.shape != targets.shape:
            return Err("Shape mismatch.")
        eps = 1e-7
        p = np.clip(predictions, eps, 1 - eps)
        loss = -np.mean(targets * np.log(p) + (1 - targets) * np.log(1 - p))
        return Ok(float(loss))

    def wasserstein_loss(
        self, real_scores: np.ndarray, fake_scores: np.ndarray
    ) -> Result:
        """Wasserstein (WGAN) loss.

        D_loss = mean(fake_scores) - mean(real_scores)  (minimize)
        G_loss = -mean(fake_scores)                      (minimize)

        @param real_scores: Discriminator outputs for real samples.
        @param fake_scores: Discriminator outputs for fake samples.
        @returns Result containing dict with 'd_loss' and 'g_loss'.
        """
        d_loss = float(np.mean(fake_scores) - np.mean(real_scores))
        g_loss = float(-np.mean(fake_scores))
        return Ok({"d_loss": d_loss, "g_loss": g_loss})

    def hinge_loss(
        self, real_scores: np.ndarray, fake_scores: np.ndarray
    ) -> Result:
        """Hinge loss for GAN (Spectral Normalization GAN).

        D_loss = mean(max(0, 1 - real)) + mean(max(0, 1 + fake))
        G_loss = -mean(fake)

        @param real_scores: Discriminator scores for real samples.
        @param fake_scores: Discriminator scores for fake samples.
        @returns Result containing dict with 'd_loss' and 'g_loss'.
        """
        d_real = float(np.mean(np.maximum(0, 1 - real_scores)))
        d_fake = float(np.mean(np.maximum(0, 1 + fake_scores)))
        d_loss = d_real + d_fake
        g_loss = float(-np.mean(fake_scores))
        return Ok({"d_loss": d_loss, "g_loss": g_loss})

    # -----------------------------------------------------------------
    # 5. MANIFOLD PROJECTION
    # -----------------------------------------------------------------

    def manifold_project(
        self, target_features: np.ndarray, latent_bank: np.ndarray, feature_bank: np.ndarray
    ) -> Result:
        """Project target features to nearest latent code (manifold projection).

        Finds the latent vector whose generated features are closest
        to the target features (L2 nearest-neighbor search).

        @param target_features: (D,) target feature vector.
        @param latent_bank: (M, latent_dim) bank of latent codes.
        @param feature_bank: (M, D) corresponding feature vectors.
        @returns Result containing dict with 'latent', 'distance', 'index'.
        """
        if target_features.ndim != 1 or latent_bank.ndim != 2 or feature_bank.ndim != 2:
            return Err("Invalid dimensions.")
        if latent_bank.shape[0] != feature_bank.shape[0]:
            return Err("Bank size mismatch.")

        distances = np.linalg.norm(feature_bank - target_features, axis=1)
        idx = int(np.argmin(distances))

        return Ok({
            "latent": latent_bank[idx],
            "distance": float(distances[idx]),
            "index": idx,
        })

    # -----------------------------------------------------------------
    # 6. SPECTRAL NORMALIZATION
    # -----------------------------------------------------------------

    def spectral_norm(self, weight: np.ndarray, n_power_iterations: int = 1) -> Result:
        """Compute spectral norm of a weight matrix via power iteration.

        σ(W) = max singular value of W.

        @param weight: 2D weight matrix.
        @param n_power_iterations: Number of power iteration steps.
        @returns Result containing dict with 'sigma', 'normalized_weight'.
        """
        if weight.ndim != 2:
            return Err("weight must be 2D.")

        h, w_ = weight.shape
        u = np.random.randn(h)
        u = u / (np.linalg.norm(u) + 1e-12)

        for _ in range(n_power_iterations):
            v = weight.T @ u
            v = v / (np.linalg.norm(v) + 1e-12)
            u = weight @ v
            u = u / (np.linalg.norm(u) + 1e-12)

        sigma = float(u @ weight @ v)
        sigma = max(abs(sigma), 1e-12)
        normalized = weight / sigma

        return Ok({"sigma": sigma, "normalized_weight": normalized})

    # -----------------------------------------------------------------
    # 7. SIGMOID UTILITY
    # -----------------------------------------------------------------

    def sigmoid(self, x: np.ndarray) -> Result:
        """Numerically stable sigmoid activation.

        @param x: Input array.
        @returns Result containing sigmoid(x).
        """
        pos_mask = x >= 0
        neg_mask = ~pos_mask
        z = np.zeros_like(x, dtype=np.float64)
        z[pos_mask] = 1.0 / (1.0 + np.exp(-x[pos_mask]))
        exp_x = np.exp(x[neg_mask])
        z[neg_mask] = exp_x / (1.0 + exp_x)
        return Ok(z)
