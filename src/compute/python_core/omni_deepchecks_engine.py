"""
OMNI Deepchecks Engine — ML model and data validation primitives.

Assimilated from: deepchecks/deepchecks (3.5k ★)
Implements continuous validation checks for ML models and data:
  - Data drift detection (KL-divergence, PSI, KS-test)
  - Label drift (Chi-squared, Jensen-Shannon divergence)
  - Feature importance (permutation-based)
  - Data integrity (missing values, duplicates, outlier %)
  - Model performance tracking & degradation detection
  - Train-test distribution comparison
  - Configurable check suite with pass/fail status

OMNI Domain: compute/ (Python)
CODE RULE 001-005 compliant. Only numpy dependency.
"""

from __future__ import annotations

import math
from typing import Any, Dict, List, Optional, Tuple

import numpy as np


ENGINE_VERSION: str = "1.0.0-omni"
ENGINE_NAME: str = "OmniDeepchecksEngine"


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

class OmniDeepchecksEngine:
    """Production-grade ML validation engine.

    Provides data and model checks for continuous ML validation:
      - Distribution drift detection
      - Data integrity auditing
      - Feature importance estimation
      - Model performance comparison
      - Automated check suites with thresholds

    @since 1.0.0
    @tags ["ml-validation", "data-quality", "drift-detection", "deepchecks", "compute"]
    """

    VERSION = ENGINE_VERSION
    ENGINE_ID = ENGINE_NAME

    def __init__(self) -> None:
        """Initialize OmniDeepchecksEngine."""
        self._omni_version: str = "3.0.0-OMNI-NEXUS"

    def diagnostics(self) -> Result:
        """Return engine health diagnostics."""
        return Ok({
            "engine": self.ENGINE_ID,
            "version": self.VERSION,
            "status": "operational",
            "capabilities": [
                "kl_divergence", "psi", "ks_test", "js_divergence",
                "feature_importance", "data_integrity",
                "performance_comparison", "check_suite",
            ],
        })

    # -----------------------------------------------------------------
    # 1. DATA DRIFT DETECTION
    # -----------------------------------------------------------------

    def kl_divergence(
        self,
        p: np.ndarray,
        q: np.ndarray,
        n_bins: int = 50,
    ) -> Result:
        """Compute KL divergence KL(P || Q) from empirical distributions.

        Bins both distributions and computes:
        KL = sum(p_i * log(p_i / q_i))

        @param p: 1D reference (training) distribution samples.
        @param q: 1D test (production) distribution samples.
        @param n_bins: Number of histogram bins.
        @returns Result containing scalar KL divergence.
        """
        if p.ndim != 1 or q.ndim != 1:
            return Err("Both inputs must be 1D.")
        if len(p) == 0 or len(q) == 0:
            return Err("Empty distribution.")

        lo = min(float(np.min(p)), float(np.min(q)))
        hi = max(float(np.max(p)), float(np.max(q)))
        edges = np.linspace(lo - 1e-10, hi + 1e-10, n_bins + 1)

        p_hist, _ = np.histogram(p, bins=edges, density=True)
        q_hist, _ = np.histogram(q, bins=edges, density=True)

        # Add epsilon to avoid log(0)
        eps = 1e-10
        p_hist = p_hist + eps
        q_hist = q_hist + eps

        # Normalize to proper distributions
        p_hist = p_hist / p_hist.sum()
        q_hist = q_hist / q_hist.sum()

        kl = float(np.sum(p_hist * np.log(p_hist / q_hist)))
        return Ok(kl)

    def js_divergence(self, p: np.ndarray, q: np.ndarray, n_bins: int = 50) -> Result:
        """Compute Jensen-Shannon divergence (symmetric KL).

        JS(P, Q) = 0.5 * KL(P || M) + 0.5 * KL(Q || M), where M = 0.5*(P+Q)

        @param p: 1D reference samples.
        @param q: 1D comparison samples.
        @param n_bins: Number of bins.
        @returns Result containing scalar JS divergence in [0, ln(2)].
        """
        if p.ndim != 1 or q.ndim != 1:
            return Err("Both inputs must be 1D.")

        lo = min(float(np.min(p)), float(np.min(q)))
        hi = max(float(np.max(p)), float(np.max(q)))
        edges = np.linspace(lo - 1e-10, hi + 1e-10, n_bins + 1)

        eps = 1e-10
        p_h, _ = np.histogram(p, bins=edges)
        q_h, _ = np.histogram(q, bins=edges)
        p_h = (p_h + eps).astype(np.float64)
        q_h = (q_h + eps).astype(np.float64)
        p_h /= p_h.sum()
        q_h /= q_h.sum()
        m = 0.5 * (p_h + q_h)

        kl_pm = float(np.sum(p_h * np.log(p_h / m)))
        kl_qm = float(np.sum(q_h * np.log(q_h / m)))
        return Ok(0.5 * kl_pm + 0.5 * kl_qm)

    def psi(self, reference: np.ndarray, test: np.ndarray, n_bins: int = 10) -> Result:
        """Compute Population Stability Index (PSI).

        PSI = sum((test_% - ref_%) * ln(test_% / ref_%))
        PSI < 0.1 → no shift; 0.1-0.25 → moderate; >0.25 → significant.

        @param reference: 1D reference distribution.
        @param test: 1D test distribution.
        @param n_bins: Number of bins.
        @returns Result containing dict with 'psi', 'interpretation'.
        """
        if reference.ndim != 1 or test.ndim != 1:
            return Err("Both must be 1D.")

        lo = min(float(np.min(reference)), float(np.min(test)))
        hi = max(float(np.max(reference)), float(np.max(test)))
        edges = np.linspace(lo, hi, n_bins + 1)

        ref_counts, _ = np.histogram(reference, bins=edges)
        test_counts, _ = np.histogram(test, bins=edges)

        eps = 1e-4
        ref_pct = (ref_counts + eps) / (len(reference) + eps * n_bins)
        test_pct = (test_counts + eps) / (len(test) + eps * n_bins)

        psi_val = float(np.sum((test_pct - ref_pct) * np.log(test_pct / ref_pct)))

        if psi_val < 0.1:
            interp = "no_shift"
        elif psi_val < 0.25:
            interp = "moderate_shift"
        else:
            interp = "significant_shift"

        return Ok({"psi": psi_val, "interpretation": interp})

    def ks_test(self, p: np.ndarray, q: np.ndarray) -> Result:
        """Two-sample Kolmogorov-Smirnov test statistic.

        KS = max |F_p(x) - F_q(x)|

        @param p: 1D reference samples.
        @param q: 1D test samples.
        @returns Result containing dict with 'statistic' and 'critical_value' (α=0.05).
        """
        if p.ndim != 1 or q.ndim != 1:
            return Err("Both must be 1D.")
        if len(p) == 0 or len(q) == 0:
            return Err("Empty distribution.")

        all_vals = np.sort(np.concatenate([p, q]))
        cdf_p = np.searchsorted(np.sort(p), all_vals, side='right') / len(p)
        cdf_q = np.searchsorted(np.sort(q), all_vals, side='right') / len(q)

        ks_stat = float(np.max(np.abs(cdf_p - cdf_q)))
        # Critical value at α=0.05 (two-sample)
        n_eff = (len(p) * len(q)) / (len(p) + len(q))
        critical = 1.36 / math.sqrt(n_eff) if n_eff > 0 else float('inf')

        return Ok({
            "statistic": ks_stat,
            "critical_value": critical,
            "significant": ks_stat > critical,
        })

    # -----------------------------------------------------------------
    # 2. DATA INTEGRITY CHECKS
    # -----------------------------------------------------------------

    def check_missing_values(self, data: np.ndarray) -> Result:
        """Check percentage of missing (NaN) values per column.

        @param data: 2D numeric array.
        @returns Result containing dict with per-column missing percentages.
        """
        if data.ndim != 2:
            return Err("data must be 2D.")
        n_rows = data.shape[0]
        missing = {}
        for col in range(data.shape[1]):
            pct = float(np.sum(np.isnan(data[:, col]))) / n_rows * 100
            missing[f"col_{col}"] = round(pct, 2)
        total_pct = float(np.sum(np.isnan(data))) / data.size * 100
        return Ok({"per_column": missing, "total_pct": round(total_pct, 2)})

    def check_duplicates(self, data: np.ndarray) -> Result:
        """Check for duplicate rows in dataset.

        @param data: 2D numeric array.
        @returns Result containing dict with 'n_duplicates', 'pct'.
        """
        if data.ndim != 2:
            return Err("data must be 2D.")
        unique_rows = np.unique(data, axis=0)
        n_dup = data.shape[0] - unique_rows.shape[0]
        pct = n_dup / data.shape[0] * 100 if data.shape[0] > 0 else 0
        return Ok({"n_duplicates": int(n_dup), "pct": round(pct, 2)})

    def check_outlier_ratio(
        self, data: np.ndarray, threshold: float = 3.0
    ) -> Result:
        """Check percentage of outliers per column (Z-score method).

        @param data: 2D numeric array.
        @param threshold: Z-score threshold.
        @returns Result containing per-column outlier percentages.
        """
        if data.ndim != 2:
            return Err("data must be 2D.")
        result = {}
        for col in range(data.shape[1]):
            col_data = data[:, col]
            valid = col_data[~np.isnan(col_data)]
            if len(valid) < 2:
                result[f"col_{col}"] = 0.0
                continue
            mu = np.mean(valid)
            sigma = np.std(valid)
            if sigma < 1e-15:
                result[f"col_{col}"] = 0.0
                continue
            z = np.abs((valid - mu) / sigma)
            pct = float(np.sum(z > threshold)) / len(valid) * 100
            result[f"col_{col}"] = round(pct, 2)
        return Ok(result)

    # -----------------------------------------------------------------
    # 3. FEATURE IMPORTANCE
    # -----------------------------------------------------------------

    def permutation_importance(
        self,
        weights: np.ndarray,
        X: np.ndarray,
        y: np.ndarray,
        n_repeats: int = 10,
        seed: int = 42,
    ) -> Result:
        """Estimate feature importance via permutation.

        For each feature j: shuffle column j, compute MSE increase.
        Higher increase → more important feature.

        Uses a simple linear model: y_hat = X @ w.

        @param weights: 1D model weights.
        @param X: 2D input data (N, D).
        @param y: 1D target vector (N,).
        @param n_repeats: Number of permutation repeats.
        @param seed: Random seed.
        @returns Result containing dict with 'importance' array and 'ranking'.
        """
        if X.ndim != 2 or y.ndim != 1:
            return Err("X must be 2D, y must be 1D.")
        if X.shape[1] != len(weights):
            return Err("Dimension mismatch.")

        rng = np.random.RandomState(seed)
        base_pred = X @ weights
        base_mse = float(np.mean((y - base_pred) ** 2))

        importances = np.zeros(X.shape[1], dtype=np.float64)
        for j in range(X.shape[1]):
            deltas = []
            for _ in range(n_repeats):
                X_perm = X.copy()
                rng.shuffle(X_perm[:, j])
                perm_pred = X_perm @ weights
                perm_mse = float(np.mean((y - perm_pred) ** 2))
                deltas.append(perm_mse - base_mse)
            importances[j] = np.mean(deltas)

        ranking = np.argsort(-importances).tolist()
        return Ok({
            "importance": importances,
            "ranking": ranking,
            "base_mse": base_mse,
        })

    # -----------------------------------------------------------------
    # 4. MODEL PERFORMANCE COMPARISON
    # -----------------------------------------------------------------

    def performance_comparison(
        self,
        y_true: np.ndarray,
        y_pred_baseline: np.ndarray,
        y_pred_new: np.ndarray,
    ) -> Result:
        """Compare model performance between baseline and new model.

        Computes accuracy for classification and flags degradation.

        @param y_true: 1D ground truth labels.
        @param y_pred_baseline: 1D baseline predictions.
        @param y_pred_new: 1D new model predictions.
        @returns Result containing performance comparison dict.
        """
        if len(y_true) != len(y_pred_baseline) or len(y_true) != len(y_pred_new):
            return Err("Array lengths must match.")

        acc_base = float(np.mean(y_true == y_pred_baseline))
        acc_new = float(np.mean(y_true == y_pred_new))
        delta = acc_new - acc_base

        return Ok({
            "baseline_accuracy": acc_base,
            "new_accuracy": acc_new,
            "delta": delta,
            "degraded": delta < -0.01,
        })

    # -----------------------------------------------------------------
    # 5. TRAIN-TEST LEAKAGE DETECTION
    # -----------------------------------------------------------------

    def check_train_test_leakage(
        self, train: np.ndarray, test: np.ndarray
    ) -> Result:
        """Detect exact-row overlap between train and test sets.

        @param train: 2D training data.
        @param test: 2D test data.
        @returns Result containing dict with 'n_leaked', 'pct'.
        """
        if train.ndim != 2 or test.ndim != 2:
            return Err("Both must be 2D.")
        if train.shape[1] != test.shape[1]:
            return Err("Feature count mismatch.")

        # Convert rows to hashable tuples for set intersection
        train_set = set(map(tuple, train))
        test_set = set(map(tuple, test))
        leaked = train_set & test_set
        n = len(leaked)
        pct = n / len(test_set) * 100 if len(test_set) > 0 else 0

        return Ok({"n_leaked": n, "pct": round(pct, 2)})

    # -----------------------------------------------------------------
    # 6. CHECK SUITE RUNNER
    # -----------------------------------------------------------------

    def run_check_suite(
        self,
        data: np.ndarray,
        reference: Optional[np.ndarray] = None,
        missing_threshold: float = 5.0,
        duplicate_threshold: float = 1.0,
        outlier_threshold: float = 5.0,
        drift_threshold: float = 0.25,
    ) -> Result:
        """Run a complete data quality check suite.

        @param data: 2D current data to validate.
        @param reference: 2D reference data (for drift checks). Optional.
        @param missing_threshold: Max allowed missing % per column.
        @param duplicate_threshold: Max allowed duplicate %.
        @param outlier_threshold: Max allowed outlier %.
        @param drift_threshold: PSI threshold for drift.
        @returns Result containing list of check results with pass/fail.
        """
        if data.ndim != 2:
            return Err("data must be 2D.")

        checks = []

        # Missing values
        mv = self.check_missing_values(data)
        if isinstance(mv, Ok):
            passed = mv.value["total_pct"] <= missing_threshold
            checks.append({"check": "missing_values", "value": mv.value["total_pct"], "passed": passed})

        # Duplicates
        dup = self.check_duplicates(data)
        if isinstance(dup, Ok):
            passed = dup.value["pct"] <= duplicate_threshold
            checks.append({"check": "duplicates", "value": dup.value["pct"], "passed": passed})

        # Outliers (average across columns)
        out = self.check_outlier_ratio(data)
        if isinstance(out, Ok):
            avg_outlier = float(np.mean(list(out.value.values())))
            passed = avg_outlier <= outlier_threshold
            checks.append({"check": "outlier_ratio", "value": round(avg_outlier, 2), "passed": passed})

        # Drift (if reference provided)
        if reference is not None and reference.ndim == 2:
            n_cols = min(data.shape[1], reference.shape[1])
            max_psi = 0.0
            for col in range(n_cols):
                psi_res = self.psi(reference[:, col], data[:, col])
                if isinstance(psi_res, Ok):
                    max_psi = max(max_psi, psi_res.value["psi"])
            passed = max_psi <= drift_threshold
            checks.append({"check": "data_drift_psi", "value": round(max_psi, 4), "passed": passed})

        all_passed = all(c["passed"] for c in checks)
        return Ok({"checks": checks, "suite_passed": all_passed})
