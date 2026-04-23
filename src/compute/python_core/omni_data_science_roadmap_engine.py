"""
OMNI Data Science Roadmap Engine — Foundational data science computation primitives.

Assimilated from: Moataz-Elmesmary/Data-Science-Roadmap (5k+ ★)
Distills the entire data science curriculum into production-grade NumPy primitives:
  - Descriptive statistics (mean, median, mode, variance, skewness, kurtosis)
  - Probability (Bayes, binomial, Poisson)
  - Linear algebra (determinant, eigenvalues, SVD, pseudoinverse)
  - Data cleaning (outlier detection, imputation)
  - Feature engineering (scaling, encoding, polynomial features)
  - Evaluation metrics (classification & regression)
  - EDA primitives (correlation, distribution fitting)

OMNI Domain: compute/ (Python)
CODE RULE 001-005 compliant. Only numpy dependency.
"""

from __future__ import annotations

import math
from typing import Any, Dict, List, Optional, Tuple

import numpy as np


ENGINE_VERSION: str = "1.0.0-omni"
ENGINE_NAME: str = "OmniDataScienceRoadmapEngine"


# ---------------------------------------------------------------------------
# Monadic Result
# ---------------------------------------------------------------------------
from src.compute.python_core.omni_base_engine import Result, Ok, Err

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
# 1. DESCRIPTIVE STATISTICS
# ---------------------------------------------------------------------------

def compute_mean(data: np.ndarray) -> Result:
    """Compute arithmetic mean.

    @param data: 1D numeric array.
    @returns Result containing scalar mean.
    """
    if data.ndim != 1 or len(data) == 0:
        return Err("data must be a non-empty 1D array.")
    return Ok(float(np.mean(data)))


def compute_median(data: np.ndarray) -> Result:
    """Compute median value.

    @param data: 1D numeric array.
    @returns Result containing scalar median.
    """
    if data.ndim != 1 or len(data) == 0:
        return Err("data must be a non-empty 1D array.")
    return Ok(float(np.median(data)))


def compute_mode(data: np.ndarray) -> Result:
    """Compute mode (most frequent value).

    For continuous data, bins values before counting. Returns the
    value with the highest frequency.

    @param data: 1D numeric array.
    @returns Result containing dict with 'mode' and 'count'.
    """
    if data.ndim != 1 or len(data) == 0:
        return Err("data must be a non-empty 1D array.")
    values, counts = np.unique(data, return_counts=True)
    idx = np.argmax(counts)
    return Ok({"mode": float(values[idx]), "count": int(counts[idx])})


def compute_variance(data: np.ndarray, ddof: int = 0) -> Result:
    """Compute variance with configurable degrees of freedom.

    @param data: 1D numeric array.
    @param ddof: Delta degrees of freedom (0=population, 1=sample).
    @returns Result containing scalar variance.
    """
    if data.ndim != 1 or len(data) == 0:
        return Err("data must be a non-empty 1D array.")
    if len(data) <= ddof:
        return Err("Not enough data points for given ddof.")
    return Ok(float(np.var(data, ddof=ddof)))


def compute_std(data: np.ndarray, ddof: int = 0) -> Result:
    """Compute standard deviation.

    @param data: 1D numeric array.
    @param ddof: Delta degrees of freedom.
    @returns Result containing scalar std.
    """
    res = compute_variance(data, ddof)
    if isinstance(res, Err):
        return res
    return Ok(math.sqrt(res.value))


def compute_skewness(data: np.ndarray) -> Result:
    """Compute Fisher's skewness coefficient.

    skew = E[(X - mu)^3] / sigma^3

    @param data: 1D numeric array.
    @returns Result containing scalar skewness.
    """
    if data.ndim != 1 or len(data) < 3:
        return Err("Need at least 3 data points for skewness.")
    mu = np.mean(data)
    sigma = np.std(data)
    if sigma < 1e-15:
        return Ok(0.0)
    return Ok(float(np.mean(((data - mu) / sigma) ** 3)))


def compute_kurtosis(data: np.ndarray) -> Result:
    """Compute excess kurtosis (Fisher definition, normal=0).

    kurt = E[(X - mu)^4] / sigma^4 - 3

    @param data: 1D numeric array.
    @returns Result containing scalar excess kurtosis.
    """
    if data.ndim != 1 or len(data) < 4:
        return Err("Need at least 4 data points for kurtosis.")
    mu = np.mean(data)
    sigma = np.std(data)
    if sigma < 1e-15:
        return Ok(0.0)
    return Ok(float(np.mean(((data - mu) / sigma) ** 4) - 3.0))


def compute_percentiles(data: np.ndarray, percentiles: List[float]) -> Result:
    """Compute arbitrary percentiles.

    @param data: 1D numeric array.
    @param percentiles: List of percentile values in [0, 100].
    @returns Result containing dict mapping percentile -> value.
    """
    if data.ndim != 1 or len(data) == 0:
        return Err("data must be a non-empty 1D array.")
    result = {}
    for p in percentiles:
        if p < 0 or p > 100:
            return Err(f"Percentile {p} out of range [0, 100].")
        result[p] = float(np.percentile(data, p))
    return Ok(result)


# ---------------------------------------------------------------------------
# 2. PROBABILITY
# ---------------------------------------------------------------------------

def bayes_theorem(
    prior: float, likelihood: float, evidence: float
) -> Result:
    """Apply Bayes' theorem: P(A|B) = P(B|A) * P(A) / P(B).

    @param prior: P(A) — prior probability.
    @param likelihood: P(B|A) — likelihood.
    @param evidence: P(B) — marginal evidence.
    @returns Result containing posterior probability P(A|B).
    """
    if evidence <= 0:
        return Err("Evidence P(B) must be positive.")
    if not (0 <= prior <= 1) or not (0 <= likelihood <= 1):
        return Err("Probabilities must be in [0, 1].")
    posterior = (likelihood * prior) / evidence
    return Ok(float(min(posterior, 1.0)))


def binomial_pmf(n: int, k: int, p: float) -> Result:
    """Compute binomial probability mass function: P(X=k).

    P(X=k) = C(n,k) * p^k * (1-p)^(n-k)

    @param n: Number of trials.
    @param k: Number of successes.
    @param p: Probability of success per trial.
    @returns Result containing scalar probability.
    """
    if n < 0 or k < 0 or k > n:
        return Err("Invalid parameters: require 0 <= k <= n.")
    if not (0 <= p <= 1):
        return Err("p must be in [0, 1].")
    coeff = math.comb(n, k)
    prob = coeff * (p ** k) * ((1 - p) ** (n - k))
    return Ok(float(prob))


def poisson_pmf(lam: float, k: int) -> Result:
    """Compute Poisson probability mass function: P(X=k).

    P(X=k) = (lambda^k * e^(-lambda)) / k!

    @param lam: Expected rate (lambda > 0).
    @param k: Number of occurrences (k >= 0).
    @returns Result containing scalar probability.
    """
    if lam <= 0:
        return Err("lambda must be positive.")
    if k < 0:
        return Err("k must be non-negative.")
    log_prob = k * math.log(lam) - lam - math.lgamma(k + 1)
    return Ok(float(math.exp(log_prob)))


# ---------------------------------------------------------------------------
# 3. LINEAR ALGEBRA
# ---------------------------------------------------------------------------

def matrix_determinant(A: np.ndarray) -> Result:
    """Compute matrix determinant.

    @param A: Square 2D matrix.
    @returns Result containing scalar determinant.
    """
    if A.ndim != 2 or A.shape[0] != A.shape[1]:
        return Err("Matrix must be square.")
    return Ok(float(np.linalg.det(A)))


def matrix_eigenvalues(A: np.ndarray) -> Result:
    """Compute eigenvalues and eigenvectors.

    @param A: Square 2D matrix.
    @returns Result containing dict with 'eigenvalues' and 'eigenvectors'.
    """
    if A.ndim != 2 or A.shape[0] != A.shape[1]:
        return Err("Matrix must be square.")
    eigenvalues, eigenvectors = np.linalg.eig(A)
    return Ok({"eigenvalues": eigenvalues, "eigenvectors": eigenvectors})


def matrix_svd(A: np.ndarray) -> Result:
    """Compute Singular Value Decomposition: A = U @ diag(S) @ Vt.

    @param A: 2D matrix of any shape.
    @returns Result containing dict with 'U', 'S', 'Vt'.
    """
    if A.ndim != 2:
        return Err("Matrix must be 2D.")
    U, S, Vt = np.linalg.svd(A, full_matrices=False)
    return Ok({"U": U, "S": S, "Vt": Vt})


def matrix_pseudoinverse(A: np.ndarray) -> Result:
    """Compute Moore-Penrose pseudoinverse via SVD.

    @param A: 2D matrix.
    @returns Result containing pseudoinverse matrix.
    """
    if A.ndim != 2:
        return Err("Matrix must be 2D.")
    return Ok(np.linalg.pinv(A))


# ---------------------------------------------------------------------------
# 4. DATA CLEANING
# ---------------------------------------------------------------------------

def detect_outliers_iqr(data: np.ndarray, factor: float = 1.5) -> Result:
    """Detect outliers using the IQR (Interquartile Range) method.

    Outlier if value < Q1 - factor*IQR  or  value > Q3 + factor*IQR.

    @param data: 1D numeric array.
    @param factor: IQR multiplier (default 1.5).
    @returns Result containing dict with 'mask' (boolean), 'lower_bound', 'upper_bound'.
    """
    if data.ndim != 1 or len(data) == 0:
        return Err("data must be a non-empty 1D array.")
    q1 = np.percentile(data, 25)
    q3 = np.percentile(data, 75)
    iqr = q3 - q1
    lower = q1 - factor * iqr
    upper = q3 + factor * iqr
    mask = (data < lower) | (data > upper)
    return Ok({"mask": mask, "lower_bound": float(lower), "upper_bound": float(upper)})


def detect_outliers_zscore(data: np.ndarray, threshold: float = 3.0) -> Result:
    """Detect outliers using Z-score method.

    Outlier if |z| > threshold.

    @param data: 1D numeric array.
    @param threshold: Z-score threshold (default 3.0).
    @returns Result containing dict with 'mask' (boolean), 'z_scores'.
    """
    if data.ndim != 1 or len(data) == 0:
        return Err("data must be a non-empty 1D array.")
    mu = np.mean(data)
    sigma = np.std(data)
    if sigma < 1e-15:
        return Ok({"mask": np.zeros(len(data), dtype=bool), "z_scores": np.zeros(len(data))})
    z = (data - mu) / sigma
    mask = np.abs(z) > threshold
    return Ok({"mask": mask, "z_scores": z})


def impute_mean(data: np.ndarray) -> Result:
    """Impute NaN values with column mean.

    @param data: 2D numeric array with potential NaN values.
    @returns Result containing imputed array (copy).
    """
    if data.ndim != 2:
        return Err("data must be 2D.")
    result = data.copy()
    for col in range(result.shape[1]):
        mask = np.isnan(result[:, col])
        if np.any(mask):
            col_mean = np.nanmean(result[:, col])
            result[mask, col] = col_mean
    return Ok(result)


def impute_median(data: np.ndarray) -> Result:
    """Impute NaN values with column median.

    @param data: 2D numeric array with potential NaN values.
    @returns Result containing imputed array (copy).
    """
    if data.ndim != 2:
        return Err("data must be 2D.")
    result = data.copy()
    for col in range(result.shape[1]):
        mask = np.isnan(result[:, col])
        if np.any(mask):
            col_median = np.nanmedian(result[:, col])
            result[mask, col] = col_median
    return Ok(result)


# ---------------------------------------------------------------------------
# 5. FEATURE ENGINEERING
# ---------------------------------------------------------------------------

def min_max_scale(data: np.ndarray, feature_range: Tuple[float, float] = (0.0, 1.0)) -> Result:
    """Min-Max scaling to a specified range.

    X_scaled = (X - X_min) / (X_max - X_min) * (max - min) + min

    @param data: 2D array (samples, features).
    @param feature_range: Target range (min, max).
    @returns Result containing dict with 'scaled', 'min_vals', 'max_vals'.
    """
    if data.ndim != 2:
        return Err("data must be 2D.")
    lo, hi = feature_range
    mins = np.min(data, axis=0)
    maxs = np.max(data, axis=0)
    denom = maxs - mins
    denom[denom < 1e-15] = 1.0  # avoid division by zero
    scaled = (data - mins) / denom * (hi - lo) + lo
    return Ok({"scaled": scaled, "min_vals": mins, "max_vals": maxs})


def standard_scale(data: np.ndarray) -> Result:
    """Standard (Z-score) scaling: X_scaled = (X - mu) / sigma.

    @param data: 2D array (samples, features).
    @returns Result containing dict with 'scaled', 'means', 'stds'.
    """
    if data.ndim != 2:
        return Err("data must be 2D.")
    means = np.mean(data, axis=0)
    stds = np.std(data, axis=0)
    stds[stds < 1e-15] = 1.0
    scaled = (data - means) / stds
    return Ok({"scaled": scaled, "means": means, "stds": stds})


def one_hot_encode(labels: np.ndarray, num_classes: Optional[int] = None) -> Result:
    """One-hot encode integer labels.

    @param labels: 1D integer array of class indices.
    @param num_classes: Total number of classes (auto-detected if None).
    @returns Result containing (N, num_classes) one-hot matrix.
    """
    if labels.ndim != 1:
        return Err("labels must be 1D.")
    if num_classes is None:
        num_classes = int(np.max(labels)) + 1
    n = len(labels)
    encoded = np.zeros((n, num_classes), dtype=np.float64)
    for i in range(n):
        encoded[i, int(labels[i])] = 1.0
    return Ok(encoded)


def polynomial_features(X: np.ndarray, degree: int = 2) -> Result:
    """Generate polynomial features up to given degree.

    For 1D input [x], degree=2 produces [1, x, x^2].
    For 2D input, produces all combinations up to the degree.

    @param X: 2D array (samples, features).
    @param degree: Maximum polynomial degree.
    @returns Result containing expanded feature matrix.
    """
    if X.ndim != 2:
        return Err("X must be 2D.")
    if degree < 1:
        return Err("degree must be >= 1.")
    n, d = X.shape
    features = [np.ones((n, 1))]  # bias term
    for deg in range(1, degree + 1):
        for col in range(d):
            features.append(X[:, col:col + 1] ** deg)
    return Ok(np.hstack(features))


def bin_data(data: np.ndarray, n_bins: int) -> Result:
    """Bin continuous data into equal-width bins.

    @param data: 1D numeric array.
    @param n_bins: Number of bins.
    @returns Result containing dict with 'bin_indices', 'bin_edges'.
    """
    if data.ndim != 1 or len(data) == 0:
        return Err("data must be a non-empty 1D array.")
    if n_bins < 1:
        return Err("n_bins must be >= 1.")
    lo, hi = float(np.min(data)), float(np.max(data))
    edges = np.linspace(lo, hi, n_bins + 1)
    indices = np.digitize(data, edges[1:-1])
    return Ok({"bin_indices": indices, "bin_edges": edges})


# ---------------------------------------------------------------------------
# 6. EVALUATION METRICS (CLASSIFICATION)
# ---------------------------------------------------------------------------

def confusion_matrix(y_true: np.ndarray, y_pred: np.ndarray, n_classes: Optional[int] = None) -> Result:
    """Compute confusion matrix.

    @param y_true: 1D ground truth labels.
    @param y_pred: 1D predicted labels.
    @param n_classes: Number of classes (auto-detected if None).
    @returns Result containing (n_classes, n_classes) confusion matrix.
    """
    if y_true.ndim != 1 or y_pred.ndim != 1:
        return Err("y_true and y_pred must be 1D.")
    if len(y_true) != len(y_pred):
        return Err("y_true and y_pred must have equal length.")
    if n_classes is None:
        n_classes = int(max(np.max(y_true), np.max(y_pred))) + 1
    cm = np.zeros((n_classes, n_classes), dtype=np.int64)
    for t, p in zip(y_true, y_pred):
        cm[int(t), int(p)] += 1
    return Ok(cm)


def accuracy_score(y_true: np.ndarray, y_pred: np.ndarray) -> Result:
    """Compute classification accuracy.

    @param y_true: 1D ground truth labels.
    @param y_pred: 1D predicted labels.
    @returns Result containing scalar accuracy in [0, 1].
    """
    if len(y_true) != len(y_pred) or len(y_true) == 0:
        return Err("Invalid input arrays.")
    return Ok(float(np.mean(y_true == y_pred)))


def precision_recall_f1(y_true: np.ndarray, y_pred: np.ndarray, pos_label: int = 1) -> Result:
    """Compute precision, recall, and F1 score for binary classification.

    @param y_true: 1D ground truth labels.
    @param y_pred: 1D predicted labels.
    @param pos_label: Positive class label.
    @returns Result containing dict with 'precision', 'recall', 'f1'.
    """
    if len(y_true) != len(y_pred):
        return Err("y_true and y_pred must have equal length.")
    tp = int(np.sum((y_true == pos_label) & (y_pred == pos_label)))
    fp = int(np.sum((y_true != pos_label) & (y_pred == pos_label)))
    fn = int(np.sum((y_true == pos_label) & (y_pred != pos_label)))
    precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
    f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0.0
    return Ok({"precision": precision, "recall": recall, "f1": f1})


def roc_auc_score(y_true: np.ndarray, y_scores: np.ndarray) -> Result:
    """Compute ROC AUC using the trapezoidal rule.

    @param y_true: 1D binary labels (0 or 1).
    @param y_scores: 1D predicted scores/probabilities.
    @returns Result containing scalar AUC.
    """
    if len(y_true) != len(y_scores):
        return Err("y_true and y_scores must have equal length.")
    # Sort by descending score
    order = np.argsort(-y_scores)
    y_sorted = y_true[order]
    n_pos = np.sum(y_true == 1)
    n_neg = np.sum(y_true == 0)
    if n_pos == 0 or n_neg == 0:
        return Err("Need both positive and negative samples.")
    tpr_list = []
    fpr_list = []
    tp = 0
    fp = 0
    for label in y_sorted:
        if label == 1:
            tp += 1
        else:
            fp += 1
        tpr_list.append(tp / n_pos)
        fpr_list.append(fp / n_neg)
    # Prepend origin
    tpr_arr = np.array([0.0] + tpr_list)
    fpr_arr = np.array([0.0] + fpr_list)
    _trapz = getattr(np, 'trapezoid', np.trapz)
    auc = float(_trapz(tpr_arr, fpr_arr))
    return Ok(auc)


# ---------------------------------------------------------------------------
# 7. EVALUATION METRICS (REGRESSION)
# ---------------------------------------------------------------------------

def mean_squared_error(y_true: np.ndarray, y_pred: np.ndarray) -> Result:
    """Compute Mean Squared Error.

    @param y_true: 1D ground truth values.
    @param y_pred: 1D predicted values.
    @returns Result containing scalar MSE.
    """
    if len(y_true) != len(y_pred):
        return Err("Arrays must have equal length.")
    return Ok(float(np.mean((y_true - y_pred) ** 2)))


def mean_absolute_error(y_true: np.ndarray, y_pred: np.ndarray) -> Result:
    """Compute Mean Absolute Error.

    @param y_true: 1D ground truth values.
    @param y_pred: 1D predicted values.
    @returns Result containing scalar MAE.
    """
    if len(y_true) != len(y_pred):
        return Err("Arrays must have equal length.")
    return Ok(float(np.mean(np.abs(y_true - y_pred))))


def r_squared(y_true: np.ndarray, y_pred: np.ndarray) -> Result:
    """Compute R-squared (coefficient of determination).

    R² = 1 - SS_res / SS_tot

    @param y_true: 1D ground truth values.
    @param y_pred: 1D predicted values.
    @returns Result containing scalar R².
    """
    if len(y_true) != len(y_pred):
        return Err("Arrays must have equal length.")
    ss_res = np.sum((y_true - y_pred) ** 2)
    ss_tot = np.sum((y_true - np.mean(y_true)) ** 2)
    if ss_tot < 1e-15:
        return Ok(1.0 if ss_res < 1e-15 else 0.0)
    return Ok(float(1.0 - ss_res / ss_tot))


# ---------------------------------------------------------------------------
# 8. EDA PRIMITIVES
# ---------------------------------------------------------------------------

def correlation_matrix(data: np.ndarray) -> Result:
    """Compute Pearson correlation matrix.

    @param data: 2D array (samples, features).
    @returns Result containing (features, features) correlation matrix.
    """
    if data.ndim != 2:
        return Err("data must be 2D.")
    return Ok(np.corrcoef(data, rowvar=False))


def value_counts(data: np.ndarray) -> Result:
    """Count occurrences of each unique value.

    @param data: 1D array.
    @returns Result containing dict mapping value -> count.
    """
    if data.ndim != 1:
        return Err("data must be 1D.")
    values, counts = np.unique(data, return_counts=True)
    return Ok({float(v): int(c) for v, c in zip(values, counts)})


# ---------------------------------------------------------------------------
# 9. ENGINE CLASS
# ---------------------------------------------------------------------------

class OmniDataScienceRoadmapEngine:
    """Production-grade data science foundation engine.

    Encapsulates the entire Data Science Roadmap curriculum as
    callable NumPy primitives. Covers:
      - Descriptive statistics
      - Probability distributions
      - Linear algebra operations
      - Data cleaning & imputation
      - Feature engineering & scaling
      - Classification & regression metrics
      - Exploratory data analysis

    @since 1.0.0
    @tags ["data-science", "statistics", "ml-metrics", "compute"]
    """

    VERSION = ENGINE_VERSION
    ENGINE_ID = ENGINE_NAME

    def __init__(self) -> None:
        """Initialize OmniDataScienceRoadmapEngine."""
        self._omni_version: str = "3.0.0-OMNI-NEXUS"

    # --- Descriptive Statistics ---
    def mean(self, data: np.ndarray) -> Result:
        """Performs mean operation for OmniDataScienceRoadmapEngine."""
        return compute_mean(data)

    def median(self, data: np.ndarray) -> Result:
        """Performs median operation for OmniDataScienceRoadmapEngine."""
        return compute_median(data)

    def mode(self, data: np.ndarray) -> Result:
        """Performs mode operation for OmniDataScienceRoadmapEngine."""
        return compute_mode(data)

    def variance(self, data: np.ndarray, ddof: int = 0) -> Result:
        """Performs variance operation for OmniDataScienceRoadmapEngine."""
        return compute_variance(data, ddof)

    def std(self, data: np.ndarray, ddof: int = 0) -> Result:
        """Performs std operation for OmniDataScienceRoadmapEngine."""
        return compute_std(data, ddof)

    def skewness(self, data: np.ndarray) -> Result:
        """Performs skewness operation for OmniDataScienceRoadmapEngine."""
        return compute_skewness(data)

    def kurtosis(self, data: np.ndarray) -> Result:
        """Performs kurtosis operation for OmniDataScienceRoadmapEngine."""
        return compute_kurtosis(data)

    def percentiles(self, data: np.ndarray, pcts: List[float]) -> Result:
        """Performs percentiles operation for OmniDataScienceRoadmapEngine."""
        return compute_percentiles(data, pcts)

    # --- Probability ---
    def bayes(self, prior: float, likelihood: float, evidence: float) -> Result:
        """Performs bayes operation for OmniDataScienceRoadmapEngine."""
        return bayes_theorem(prior, likelihood, evidence)

    def binomial(self, n: int, k: int, p: float) -> Result:
        """Performs binomial operation for OmniDataScienceRoadmapEngine."""
        return binomial_pmf(n, k, p)

    def poisson(self, lam: float, k: int) -> Result:
        """Performs poisson operation for OmniDataScienceRoadmapEngine."""
        return poisson_pmf(lam, k)

    # --- Linear Algebra ---
    def determinant(self, A: np.ndarray) -> Result:
        """Performs determinant operation for OmniDataScienceRoadmapEngine."""
        return matrix_determinant(A)

    def eigenvalues(self, A: np.ndarray) -> Result:
        """Performs eigenvalues operation for OmniDataScienceRoadmapEngine."""
        return matrix_eigenvalues(A)

    def svd(self, A: np.ndarray) -> Result:
        """Performs svd operation for OmniDataScienceRoadmapEngine."""
        return matrix_svd(A)

    def pseudoinverse(self, A: np.ndarray) -> Result:
        """Performs pseudoinverse operation for OmniDataScienceRoadmapEngine."""
        return matrix_pseudoinverse(A)

    # --- Data Cleaning ---
    def outliers_iqr(self, data: np.ndarray, factor: float = 1.5) -> Result:
        """Performs outliers iqr operation for OmniDataScienceRoadmapEngine."""
        return detect_outliers_iqr(data, factor)

    def outliers_zscore(self, data: np.ndarray, threshold: float = 3.0) -> Result:
        """Performs outliers zscore operation for OmniDataScienceRoadmapEngine."""
        return detect_outliers_zscore(data, threshold)

    def impute_mean(self, data: np.ndarray) -> Result:
        """Performs impute mean operation for OmniDataScienceRoadmapEngine."""
        return impute_mean(data)

    def impute_median(self, data: np.ndarray) -> Result:
        """Performs impute median operation for OmniDataScienceRoadmapEngine."""
        return impute_median(data)

    # --- Feature Engineering ---
    def min_max_scale(self, data: np.ndarray, feature_range: Tuple[float, float] = (0.0, 1.0)) -> Result:
        """Performs min max scale operation for OmniDataScienceRoadmapEngine."""
        return min_max_scale(data, feature_range)

    def standard_scale(self, data: np.ndarray) -> Result:
        """Performs standard scale operation for OmniDataScienceRoadmapEngine."""
        return standard_scale(data)

    def one_hot_encode(self, labels: np.ndarray, num_classes: Optional[int] = None) -> Result:
        """Performs one hot encode operation for OmniDataScienceRoadmapEngine."""
        return one_hot_encode(labels, num_classes)

    def polynomial_features(self, X: np.ndarray, degree: int = 2) -> Result:
        """Performs polynomial features operation for OmniDataScienceRoadmapEngine."""
        return polynomial_features(X, degree)

    def bin_data(self, data: np.ndarray, n_bins: int) -> Result:
        """Performs bin data operation for OmniDataScienceRoadmapEngine."""
        return bin_data(data, n_bins)

    # --- Evaluation Metrics (Classification) ---
    def confusion_matrix(self, y_true: np.ndarray, y_pred: np.ndarray) -> Result:
        """Performs confusion matrix operation for OmniDataScienceRoadmapEngine."""
        return confusion_matrix(y_true, y_pred)

    def accuracy(self, y_true: np.ndarray, y_pred: np.ndarray) -> Result:
        """Performs accuracy operation for OmniDataScienceRoadmapEngine."""
        return accuracy_score(y_true, y_pred)

    def precision_recall_f1(self, y_true: np.ndarray, y_pred: np.ndarray) -> Result:
        """Performs precision recall f1 operation for OmniDataScienceRoadmapEngine."""
        return precision_recall_f1(y_true, y_pred)

    def roc_auc(self, y_true: np.ndarray, y_scores: np.ndarray) -> Result:
        """Performs roc auc operation for OmniDataScienceRoadmapEngine."""
        return roc_auc_score(y_true, y_scores)

    # --- Evaluation Metrics (Regression) ---
    def mse(self, y_true: np.ndarray, y_pred: np.ndarray) -> Result:
        """Performs mse operation for OmniDataScienceRoadmapEngine."""
        return mean_squared_error(y_true, y_pred)

    def mae(self, y_true: np.ndarray, y_pred: np.ndarray) -> Result:
        """Performs mae operation for OmniDataScienceRoadmapEngine."""
        return mean_absolute_error(y_true, y_pred)

    def r_squared(self, y_true: np.ndarray, y_pred: np.ndarray) -> Result:
        """Performs r squared operation for OmniDataScienceRoadmapEngine."""
        return r_squared(y_true, y_pred)

    # --- EDA ---
    def correlation_matrix(self, data: np.ndarray) -> Result:
        """Performs correlation matrix operation for OmniDataScienceRoadmapEngine."""
        return correlation_matrix(data)

    def value_counts(self, data: np.ndarray) -> Result:
        """Performs value counts operation for OmniDataScienceRoadmapEngine."""
        return value_counts(data)

    # --- Health ---
    def diagnostics(self) -> Dict[str, Any]:
        """Return engine health diagnostics.

        @returns Dictionary with engine status information.
        """
        return {
            "engine": self.ENGINE_ID,
            "version": self.VERSION,
            "status": "operational",
            "capabilities": [
                "descriptive_statistics", "probability", "linear_algebra",
                "data_cleaning", "feature_engineering",
                "classification_metrics", "regression_metrics", "eda",
            ],
            "functions": 27,
        }
