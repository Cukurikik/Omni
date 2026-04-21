"""
OMNI FedML Engine — Federated learning primitives for distributed ML training.

Assimilated from: FedML-AI/FedML (4.2k ★)
Implements the core algorithmic building blocks of federated learning:
  - FedAvg weighted parameter aggregation (McMahan et al., 2017)
  - Local SGD-style client training simulation
  - Non-IID data partitioning via Dirichlet allocation
  - Differential privacy: Gaussian & Laplacian mechanisms
  - Secure aggregation via additive masking
  - Client selection strategies
  - Convergence metrics & weight divergence

OMNI Domain: compute/ (Python)
CODE RULE 001-005 compliant. Only numpy dependency.
"""

from __future__ import annotations

import math
from typing import Any, Dict, List, Optional, Tuple

import numpy as np


ENGINE_VERSION: str = "1.0.0-omni"
ENGINE_NAME: str = "OmniFedMLEngine"


# ---------------------------------------------------------------------------
# Monadic Result
# ---------------------------------------------------------------------------

class Result:
    """Monadic Result base."""
    pass


class Ok(Result):
    """Success variant."""
    def __init__(self, value: Any) -> None:
        """Initialize Ok."""
        self.value = value


class Err(Result):
    """Error variant."""
    def __init__(self, error: str) -> None:
        """Initialize Err."""
        self.error = error


# ---------------------------------------------------------------------------
# Engine
# ---------------------------------------------------------------------------

class OmniFedMLEngine:
    """Production-grade federated learning engine.

    Provides the mathematical foundation for privacy-preserving distributed
    machine learning following the FedML framework architecture:
      - Server-side aggregation (FedAvg, weighted averaging)
      - Client-side local training (SGD simulation)
      - Data heterogeneity handling (non-IID partitioning)
      - Privacy mechanisms (differential privacy, secure aggregation)
      - Client management and selection

    @since 1.0.0
    @tags ["federated-learning", "distributed-ml", "privacy", "aggregation", "compute"]
    """

    VERSION = ENGINE_VERSION
    ENGINE_ID = ENGINE_NAME

    def __init__(self) -> None:
        """Initialize OmniFedMLEngine."""
        self._omni_version: str = "3.0.0-OMNI-NEXUS"

    def diagnostics(self) -> Result:
        """Return engine health diagnostics."""
        return Ok({
            "engine": self.ENGINE_ID,
            "version": self.VERSION,
            "status": "operational",
            "capabilities": [
                "fedavg", "local_sgd", "non_iid_partition",
                "differential_privacy", "secure_aggregation",
                "client_selection", "convergence_metrics",
            ],
        })

    # -----------------------------------------------------------------
    # 1. FEDERATED AVERAGING (FedAvg)
    # -----------------------------------------------------------------

    def fedavg_aggregate(
        self,
        client_params: List[Dict[str, np.ndarray]],
        sample_counts: List[int],
    ) -> Result:
        """Aggregate client model parameters using Federated Averaging.

        Weighted average: w_global = sum(n_k * w_k) / sum(n_k)
        (McMahan et al., "Communication-Efficient Learning of Deep Networks
        from Decentralized Data", AISTATS 2017)

        @param client_params: List of dicts mapping param name to ndarray.
        @param sample_counts: Number of local samples per client.
        @returns Result containing aggregated parameter dict.
        """
        if len(client_params) == 0:
            return Err("No client parameters provided.")
        if len(client_params) != len(sample_counts):
            return Err("client_params and sample_counts length mismatch.")

        total_samples = sum(sample_counts)
        if total_samples == 0:
            return Err("Total sample count is zero.")

        weights = [n / total_samples for n in sample_counts]
        keys = list(client_params[0].keys())

        aggregated = {}
        for key in keys:
            aggregated[key] = sum(
                w * client_params[i][key]
                for i, w in enumerate(weights)
            )

        return Ok(aggregated)

    def fedavg_aggregate_arrays(
        self,
        client_weights: List[np.ndarray],
        sample_counts: List[int],
    ) -> Result:
        """Simplified FedAvg for flat weight arrays.

        @param client_weights: List of 1D weight arrays from each client.
        @param sample_counts: Number of samples per client.
        @returns Result containing 1D aggregated weight array.
        """
        if len(client_weights) == 0:
            return Err("No client weights provided.")
        if len(client_weights) != len(sample_counts):
            return Err("Length mismatch.")

        total = sum(sample_counts)
        if total == 0:
            return Err("Zero total samples.")

        result = np.zeros_like(client_weights[0], dtype=np.float64)
        for w, n in zip(client_weights, sample_counts):
            result += (n / total) * w
        return Ok(result)

    # -----------------------------------------------------------------
    # 2. LOCAL TRAINING (Client-side SGD)
    # -----------------------------------------------------------------

    def local_sgd_step(
        self,
        weights: np.ndarray,
        gradient: np.ndarray,
        lr: float = 0.01,
    ) -> Result:
        """Perform single SGD step: w = w - lr * grad.

        @param weights: Current model weights (1D).
        @param gradient: Computed gradient (same shape).
        @param lr: Learning rate.
        @returns Result containing updated weights.
        """
        if weights.shape != gradient.shape:
            return Err("Weights and gradient shape mismatch.")
        if lr <= 0:
            return Err("Learning rate must be positive.")
        updated = weights - lr * gradient
        return Ok(updated)

    def local_train_epochs(
        self,
        weights: np.ndarray,
        data: np.ndarray,
        labels: np.ndarray,
        lr: float = 0.01,
        epochs: int = 1,
    ) -> Result:
        """Simulate local training with linear model over multiple epochs.

        For simulation purposes, computes MSE gradient for a simple linear
        model: y_hat = X @ w, loss = ||y - y_hat||^2 / N.

        @param weights: 1D model weight vector.
        @param data: 2D input matrix (N, D).
        @param labels: 1D target vector (N,).
        @param lr: Learning rate.
        @param epochs: Number of local epochs.
        @returns Result containing dict with 'weights' and 'final_loss'.
        """
        if data.ndim != 2 or labels.ndim != 1:
            return Err("data must be 2D, labels must be 1D.")
        if data.shape[0] != len(labels):
            return Err("Sample count mismatch.")
        if data.shape[1] != len(weights):
            return Err("Feature dimension mismatch with weights.")

        w = weights.copy().astype(np.float64)
        n = len(labels)
        for _ in range(epochs):
            pred = data @ w
            error = pred - labels
            grad = (2.0 / n) * (data.T @ error)
            w -= lr * grad

        final_loss = float(np.mean((data @ w - labels) ** 2))
        return Ok({"weights": w, "final_loss": final_loss})

    # -----------------------------------------------------------------
    # 3. NON-IID DATA PARTITIONING
    # -----------------------------------------------------------------

    def partition_dirichlet(
        self,
        labels: np.ndarray,
        n_clients: int,
        alpha: float = 0.5,
        seed: int = 42,
    ) -> Result:
        """Partition data indices into non-IID splits via Dirichlet distribution.

        Lower alpha → more heterogeneous (non-IID) distribution.
        Each client gets a proportion of each class drawn from Dir(alpha).

        @param labels: 1D integer class labels for the dataset.
        @param n_clients: Number of federated clients.
        @param alpha: Dirichlet concentration parameter.
        @param seed: Random seed for reproducibility.
        @returns Result containing dict mapping client_id → list of indices.
        """
        if labels.ndim != 1 or len(labels) == 0:
            return Err("labels must be non-empty 1D.")
        if n_clients < 1:
            return Err("n_clients must be >= 1.")
        if alpha <= 0:
            return Err("alpha must be positive.")

        rng = np.random.RandomState(seed)
        classes = np.unique(labels)
        client_indices: Dict[int, List[int]] = {i: [] for i in range(n_clients)}

        for cls in classes:
            cls_indices = np.where(labels == cls)[0]
            rng.shuffle(cls_indices)

            # Draw proportions from Dirichlet
            proportions = rng.dirichlet(np.repeat(alpha, n_clients))
            # Convert proportions to counts
            counts = (proportions * len(cls_indices)).astype(int)
            # Fix rounding to match total
            diff = len(cls_indices) - counts.sum()
            for i in range(abs(diff)):
                counts[i % n_clients] += 1 if diff > 0 else -1

            start = 0
            for c in range(n_clients):
                end = start + max(0, counts[c])
                client_indices[c].extend(cls_indices[start:end].tolist())
                start = end

        return Ok(client_indices)

    def partition_iid(
        self,
        n_samples: int,
        n_clients: int,
        seed: int = 42,
    ) -> Result:
        """Partition data indices into IID (uniform random) splits.

        @param n_samples: Total number of samples.
        @param n_clients: Number of clients.
        @param seed: Random seed.
        @returns Result containing dict mapping client_id → list of indices.
        """
        if n_samples < 1 or n_clients < 1:
            return Err("n_samples and n_clients must be >= 1.")

        rng = np.random.RandomState(seed)
        indices = rng.permutation(n_samples)
        splits = np.array_split(indices, n_clients)
        return Ok({i: s.tolist() for i, s in enumerate(splits)})

    # -----------------------------------------------------------------
    # 4. DIFFERENTIAL PRIVACY
    # -----------------------------------------------------------------

    def add_gaussian_noise(
        self,
        params: np.ndarray,
        sensitivity: float,
        epsilon: float,
        delta: float = 1e-5,
        seed: Optional[int] = None,
    ) -> Result:
        """Add calibrated Gaussian noise for (ε, δ)-differential privacy.

        σ = sensitivity * sqrt(2 * ln(1.25 / δ)) / ε

        @param params: Parameter array to privatize.
        @param sensitivity: L2 sensitivity of the query.
        @param epsilon: Privacy budget ε (smaller = more private).
        @param delta: Privacy parameter δ.
        @param seed: Optional random seed.
        @returns Result containing dict with 'noisy_params' and 'sigma'.
        """
        if epsilon <= 0 or delta <= 0 or sensitivity <= 0:
            return Err("epsilon, delta, sensitivity must all be positive.")

        sigma = sensitivity * math.sqrt(2.0 * math.log(1.25 / delta)) / epsilon

        rng = np.random.RandomState(seed)
        noise = rng.normal(0, sigma, size=params.shape)
        noisy = params + noise

        return Ok({"noisy_params": noisy, "sigma": sigma})

    def add_laplacian_noise(
        self,
        params: np.ndarray,
        sensitivity: float,
        epsilon: float,
        seed: Optional[int] = None,
    ) -> Result:
        """Add Laplacian noise for ε-differential privacy.

        scale = sensitivity / ε

        @param params: Parameter array to privatize.
        @param sensitivity: L1 sensitivity.
        @param epsilon: Privacy budget.
        @param seed: Optional random seed.
        @returns Result containing dict with 'noisy_params' and 'scale'.
        """
        if epsilon <= 0 or sensitivity <= 0:
            return Err("epsilon and sensitivity must be positive.")

        scale = sensitivity / epsilon
        rng = np.random.RandomState(seed)
        noise = rng.laplace(0, scale, size=params.shape)
        noisy = params + noise

        return Ok({"noisy_params": noisy, "scale": scale})

    def clip_gradients(
        self, gradient: np.ndarray, max_norm: float
    ) -> Result:
        """Clip gradient to max L2 norm (required for DP-SGD).

        @param gradient: Gradient array.
        @param max_norm: Maximum allowed L2 norm.
        @returns Result containing clipped gradient.
        """
        if max_norm <= 0:
            return Err("max_norm must be positive.")
        norm = float(np.linalg.norm(gradient))
        if norm > max_norm:
            gradient = gradient * (max_norm / norm)
        return Ok(gradient)

    # -----------------------------------------------------------------
    # 5. SECURE AGGREGATION
    # -----------------------------------------------------------------

    def generate_pairwise_masks(
        self, n_clients: int, param_shape: Tuple[int, ...], seed: int = 42
    ) -> Result:
        """Generate additive pairwise masks for secure aggregation.

        For each pair (i, j) with i < j, generate mask m_ij.
        Client i adds m_ij, client j subtracts m_ij.
        When summed at server, all masks cancel out.

        @param n_clients: Number of participating clients.
        @param param_shape: Shape of the parameter tensor.
        @param seed: Random seed.
        @returns Result containing dict mapping client_id → total mask to add.
        """
        if n_clients < 2:
            return Err("Need at least 2 clients for secure aggregation.")

        rng = np.random.RandomState(seed)
        client_masks: Dict[int, np.ndarray] = {
            i: np.zeros(param_shape, dtype=np.float64) for i in range(n_clients)
        }

        for i in range(n_clients):
            for j in range(i + 1, n_clients):
                mask = rng.normal(0, 1, size=param_shape)
                client_masks[i] = client_masks[i] + mask
                client_masks[j] = client_masks[j] - mask

        return Ok(client_masks)

    def secure_aggregate(
        self,
        masked_params: List[np.ndarray],
    ) -> Result:
        """Sum masked parameters (masks cancel out).

        @param masked_params: List of masked weight arrays from clients.
        @returns Result containing aggregated (unmasked) sum.
        """
        if len(masked_params) == 0:
            return Err("No masked parameters provided.")
        total = np.sum(masked_params, axis=0)
        return Ok(total)

    # -----------------------------------------------------------------
    # 6. CLIENT SELECTION
    # -----------------------------------------------------------------

    def select_clients_random(
        self,
        n_total: int,
        n_select: int,
        seed: Optional[int] = None,
    ) -> Result:
        """Randomly select a subset of clients for a training round.

        @param n_total: Total number of available clients.
        @param n_select: Number of clients to select.
        @param seed: Optional random seed.
        @returns Result containing list of selected client indices.
        """
        if n_select > n_total:
            return Err("Cannot select more clients than available.")
        if n_select < 1 or n_total < 1:
            return Err("n_total and n_select must be >= 1.")

        rng = np.random.RandomState(seed)
        selected = rng.choice(n_total, size=n_select, replace=False)
        return Ok(sorted(selected.tolist()))

    # -----------------------------------------------------------------
    # 7. CONVERGENCE METRICS
    # -----------------------------------------------------------------

    def compute_weight_divergence(
        self,
        global_weights: np.ndarray,
        client_weights: List[np.ndarray],
    ) -> Result:
        """Compute L2 weight divergence of each client from global model.

        @param global_weights: 1D global model weights.
        @param client_weights: List of 1D client weight arrays.
        @returns Result containing dict with 'mean_divergence', 'per_client'.
        """
        if len(client_weights) == 0:
            return Err("No client weights provided.")

        divergences = []
        for cw in client_weights:
            if cw.shape != global_weights.shape:
                return Err("Shape mismatch between global and client weights.")
            div = float(np.linalg.norm(cw - global_weights))
            divergences.append(div)

        return Ok({
            "mean_divergence": float(np.mean(divergences)),
            "max_divergence": float(np.max(divergences)),
            "per_client": divergences,
        })

    def compute_global_loss(
        self,
        client_losses: List[float],
        sample_counts: List[int],
    ) -> Result:
        """Compute weighted global loss from client losses.

        @param client_losses: Per-client loss values.
        @param sample_counts: Number of samples per client.
        @returns Result containing weighted global loss scalar.
        """
        if len(client_losses) != len(sample_counts):
            return Err("Length mismatch.")
        total = sum(sample_counts)
        if total == 0:
            return Err("Zero total samples.")
        gloss = sum(l * n for l, n in zip(client_losses, sample_counts)) / total
        return Ok(float(gloss))
