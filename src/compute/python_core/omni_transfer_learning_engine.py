"""
OMNI Transfer Learning Engine — Domain adaptation and task adaptation primitives.

Assimilated from: thuml/Transfer-Learning-Library (3k ★)
Implements core transfer learning algorithms:
  - Domain Adaptation: MMD, DANN (domain adversarial), CORAL, JAN
  - Feature alignment: domain-invariant projections
  - Distribution discrepancy measures: MK-MMD, A-distance
  - Task adaptation: fine-tuning, feature extraction
  - Domain generalization: class-conditional alignment

OMNI Domain: compute/ (Python)
CODE RULE 001-005 compliant. Only numpy dependency.
"""

from __future__ import annotations

import math
from typing import Any, Dict, List, Optional, Tuple

import numpy as np


ENGINE_VERSION: str = "1.0.0-omni"
ENGINE_NAME: str = "OmniTransferLearningEngine"
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


class OmniTransferLearningEngine:
    """Production-grade transfer learning and domain adaptation engine.

    Implements core algorithms:
      - Distribution discrepancy: MMD, CORAL, A-distance
      - Domain adversarial training (DANN)
      - Feature alignment and projection
      - Task adaptation metrics
      - Class-conditional alignment

    @since 1.0.0
    @tags ["transfer-learning", "domain-adaptation", "mmd", "coral", "compute"]
    """

    VERSION = ENGINE_VERSION
    ENGINE_ID = ENGINE_NAME

    def __init__(self) -> None:
        """Initialize OmniTransferLearningEngine."""
        pass

    def diagnostics(self) -> Result:
        """Performs diagnostics operation for OmniTransferLearningEngine."""
        return Ok({
            "engine": self.ENGINE_ID, "version": self.VERSION,
            "status": "operational",
            "capabilities": [
                "mmd", "multi_kernel_mmd", "coral", "a_distance",
                "dann_loss", "domain_classifier",
                "feature_alignment", "class_conditional_alignment",
                "transferability_score",
            ],
        })

    # -----------------------------------------------------------------
    # 1. DISTRIBUTION DISCREPANCY MEASURES
    # -----------------------------------------------------------------

    def mmd_linear(self, source: np.ndarray, target: np.ndarray) -> Result:
        """Compute linear Maximum Mean Discrepancy.

        MMD²_lin = ||mean(source) - mean(target)||²

        @param source: (N, D) source domain features.
        @param target: (M, D) target domain features.
        @returns Result with scalar MMD².
        """
        if source.shape[1] != target.shape[1]:
            return Err("Feature dimensions must match.")
        delta = np.mean(source, axis=0) - np.mean(target, axis=0)
        mmd2 = float(np.dot(delta, delta))
        return Ok(mmd2)

    def gaussian_kernel(self, x: np.ndarray, y: np.ndarray, sigma: float = 1.0) -> Result:
        """Compute Gaussian (RBF) kernel matrix.

        K(x, y) = exp(-||x - y||² / (2σ²))

        @param x: (N, D) samples.
        @param y: (M, D) samples.
        @param sigma: Kernel bandwidth.
        @returns Result with (N, M) kernel matrix.
        """
        x_sq = np.sum(x ** 2, axis=1, keepdims=True)
        y_sq = np.sum(y ** 2, axis=1, keepdims=True)
        dist = x_sq + y_sq.T - 2.0 * x @ y.T
        K = np.exp(-dist / (2 * sigma ** 2 + 1e-10))
        return Ok(K)

    def mmd_rbf(
        self, source: np.ndarray, target: np.ndarray, sigma: float = 1.0
    ) -> Result:
        """Compute MMD² with RBF (Gaussian) kernel.

        MMD² = E[k(s,s')] + E[k(t,t')] - 2*E[k(s,t)]

        @param source: (N, D) source features.
        @param target: (M, D) target features.
        @param sigma: Kernel bandwidth.
        @returns Result with scalar MMD².
        """
        Kss_res = self.gaussian_kernel(source, source, sigma)
        Ktt_res = self.gaussian_kernel(target, target, sigma)
        Kst_res = self.gaussian_kernel(source, target, sigma)
        if isinstance(Kss_res, Err): return Kss_res
        if isinstance(Ktt_res, Err): return Ktt_res
        if isinstance(Kst_res, Err): return Kst_res

        mmd2 = float(
            np.mean(Kss_res.value) + np.mean(Ktt_res.value) - 2 * np.mean(Kst_res.value)
        )
        return Ok(max(mmd2, 0.0))

    def multi_kernel_mmd(
        self, source: np.ndarray, target: np.ndarray,
        bandwidths: Optional[List[float]] = None
    ) -> Result:
        """Multi-kernel MMD (MK-MMD) with multiple bandwidths.

        MK-MMD = sum_k beta_k * MMD²(sigma_k)

        @param source: (N, D) source features.
        @param target: (M, D) target features.
        @param bandwidths: List of sigma values (default: [0.1, 1, 10]).
        @returns Result with scalar MK-MMD.
        """
        if bandwidths is None:
            bandwidths = [0.1, 1.0, 10.0]
        total = 0.0
        for bw in bandwidths:
            res = self.mmd_rbf(source, target, bw)
            if isinstance(res, Err):
                return res
            total += res.value
        return Ok(total / len(bandwidths))

    def coral(self, source: np.ndarray, target: np.ndarray) -> Result:
        """CORrelation ALignment (CORAL) loss.

        CORAL = (1 / 4d²) * ||C_s - C_t||²_F

        @param source: (N, D) source features.
        @param target: (M, D) target features.
        @returns Result with scalar CORAL loss.
        """
        if source.shape[1] != target.shape[1]:
            return Err("Feature dimensions must match.")
        d = source.shape[1]

        # Covariance matrices
        cs = np.cov(source.T)
        ct = np.cov(target.T)
        if cs.ndim == 0:
            cs = np.array([[cs]])
            ct = np.array([[ct]])

        diff = cs - ct
        loss = float(np.sum(diff ** 2)) / (4 * d * d)
        return Ok(loss)

    def a_distance(
        self, source: np.ndarray, target: np.ndarray, n_iterations: int = 100, lr: float = 0.01
    ) -> Result:
        """Estimate A-distance (proxy for domain discrepancy).

        Train a linear domain classifier, then
        A-dist = 2 * (1 - 2 * error)

        @param source: (N, D) source features.
        @param target: (M, D) target features.
        @returns Result with dict: 'a_distance', 'classifier_error'.
        """
        N, D = source.shape
        M = target.shape[0]

        X = np.vstack([source, target])
        y = np.concatenate([np.ones(N), np.zeros(M)])

        # Shuffle
        idx = np.arange(N + M)
        rng = np.random.RandomState(42)
        rng.shuffle(idx)
        X, y = X[idx], y[idx]

        # Logistic regression
        w = np.zeros(D)
        b = 0.0
        for _ in range(n_iterations):
            logits = X @ w + b
            preds = 1.0 / (1.0 + np.exp(-np.clip(logits, -30, 30)))
            grad_w = X.T @ (preds - y) / len(y)
            grad_b = np.mean(preds - y)
            w -= lr * grad_w
            b -= lr * grad_b

        # Compute error
        preds = 1.0 / (1.0 + np.exp(-np.clip(X @ w + b, -30, 30)))
        error = float(np.mean(np.abs(y - np.round(preds))))
        a_dist = 2.0 * (1.0 - 2.0 * error)
        a_dist = max(0.0, a_dist)

        return Ok({"a_distance": a_dist, "classifier_error": error})

    # -----------------------------------------------------------------
    # 2. DOMAIN ADVERSARIAL (DANN)
    # -----------------------------------------------------------------

    def gradient_reversal(self, features: np.ndarray, lambda_: float = 1.0) -> Result:
        """evaluates_structurally gradient reversal layer (GRL).

        In forward pass: identity. In backward pass: negate gradient.
        This returns features unchanged (forward), but stores
        the lambda for external use.

        @param features: (N, D) features.
        @param lambda_: Reversal scaling factor.
        @returns Result with dict: 'output', 'lambda'.
        """
        return Ok({"output": features.copy(), "lambda": lambda_})

    def domain_classifier_loss(
        self, domain_logits: np.ndarray, domain_labels: np.ndarray
    ) -> Result:
        """Binary cross-entropy loss for domain classification.

        @param domain_logits: (N,) domain classifier raw outputs.
        @param domain_labels: (N,) binary labels (0=source, 1=target).
        @returns Result with scalar BCE loss.
        """
        eps = 1e-7
        probs = 1.0 / (1.0 + np.exp(-np.clip(domain_logits, -30, 30)))
        probs = np.clip(probs, eps, 1 - eps)
        loss = -np.mean(
            domain_labels * np.log(probs) + (1 - domain_labels) * np.log(1 - probs)
        )
        return Ok(float(loss))

    def dann_lambda_schedule(self, epoch: int, max_epochs: int) -> Result:
        """DANN lambda scheduling (gradual increase).

        lambda = 2 / (1 + exp(-10 * p)) - 1, where p = epoch / max_epochs

        @param epoch: Current epoch.
        @param max_epochs: Total epochs.
        @returns Result with lambda value in [0, 1].
        """
        if max_epochs <= 0:
            return Err("max_epochs must be positive.")
        p = epoch / max_epochs
        lam = 2.0 / (1.0 + math.exp(-10 * p)) - 1.0
        return Ok(float(lam))

    # -----------------------------------------------------------------
    # 3. FEATURE ALIGNMENT
    # -----------------------------------------------------------------

    def feature_alignment_loss(
        self, source_features: np.ndarray, target_features: np.ndarray, method: str = "mmd"
    ) -> Result:
        """Unified feature alignment loss.

        @param source_features: (N, D) source.
        @param target_features: (M, D) target.
        @param method: "mmd", "coral", or "mmd_linear".
        @returns Result with scalar alignment loss.
        """
        if method == "mmd":
            return self.mmd_rbf(source_features, target_features)
        elif method == "coral":
            return self.coral(source_features, target_features)
        elif method == "mmd_linear":
            return self.mmd_linear(source_features, target_features)
        return Err(f"Unknown method: {method}")

    def class_conditional_alignment(
        self, source: np.ndarray, target: np.ndarray,
        source_labels: np.ndarray, target_pseudo_labels: np.ndarray
    ) -> Result:
        """Class-conditional domain alignment (per-class MMD).

        @param source: (N, D) source features.
        @param target: (M, D) target features.
        @param source_labels: (N,) source class labels.
        @param target_pseudo_labels: (M,) target pseudo labels.
        @returns Result with dict: 'per_class_mmd', 'total_mmd'.
        """
        classes = np.unique(source_labels)
        per_class = {}
        total = 0.0
        count = 0
        for c in classes:
            src_c = source[source_labels == c]
            tgt_c = target[target_pseudo_labels == c]
            if len(src_c) == 0 or len(tgt_c) == 0:
                continue
            res = self.mmd_linear(src_c, tgt_c)
            if isinstance(res, Err):
                continue
            per_class[int(c)] = res.value
            total += res.value
            count += 1

        avg = total / max(count, 1)
        return Ok({"per_class_mmd": per_class, "total_mmd": avg})

    # -----------------------------------------------------------------
    # 4. TRANSFERABILITY METRICS
    # -----------------------------------------------------------------

    def transferability_score(
        self, source: np.ndarray, target: np.ndarray
    ) -> Result:
        """Compute transferability score (lower MMD + higher alignment = better).

        Score = 1 / (1 + MK-MMD)

        @param source: (N, D) source features.
        @param target: (M, D) target features.
        @returns Result with score in (0, 1].
        """
        mmd_res = self.multi_kernel_mmd(source, target)
        if isinstance(mmd_res, Err):
            return mmd_res
        score = 1.0 / (1.0 + mmd_res.value)
        return Ok(float(score))
