"""
OMNI NeuralProphet Engine — Time series forecasting decomposition primitives.
Assimilated from: ourownstory/neural_prophet
Provides: Trend estimation, Fourier seasonality, autoregressive components, changepoint detection.
"""
import numpy as np
from typing import Optional, List



ENGINE_VERSION = "1.0.0-omni"
from src.compute.python_core.omni_base_engine import Result, Ok, Err

class Result:
    """Monadic Result base."""
    pass


class Ok(Result):
    """Success variant."""
    def __init__(self, value):
        """Initialize Ok."""
        self.value = value


class Err(Result):
    """Error variant."""
    def __init__(self, error: str):
        """Initialize Err."""
        self.error = error


class OmniNeuralProphetEngine:
    """
    Pure NumPy time-series forecasting engine inspired by NeuralProphet / Facebook Prophet.

    Decomposes a time series y(t) into:
        y(t) = g(t) + s(t) + ar(t)
    where:
        g(t)  = piecewise linear trend with changepoints
        s(t)  = Fourier-based seasonality
        ar(t) = autoregressive component (lagged linear regression)

    @since 1.0.0
    @tags ["timeseries", "forecasting", "trend", "seasonality", "compute"]
    """

    def __init__(self) -> None:
        """Initialize OmniNeuralProphetEngine."""
        self._omni_version: str = "3.0.0-OMNI-NEXUS"

    def diagnostics(self) -> Result:
        """Returns engine health status."""
        return Ok({"status": "active", "engine": "NeuralProphet", "capability": "TimeSeriesDecomposition"})

    def fit_linear_trend(self, t: np.ndarray, y: np.ndarray) -> Result:
        """
        Fits a simple linear trend via ordinary least squares.

        g(t) = k * t + m

        @param t: 1D array of time indices (normalized to [0, 1] recommended).
        @param y: 1D array of observed values.
        @returns Result containing dict with 'slope' (k), 'intercept' (m), 'trend' array.
        """
        if t.ndim != 1 or y.ndim != 1:
            return Err("Both t and y must be 1D arrays.")
        if len(t) != len(y):
            return Err("t and y must have equal length.")
        if len(t) < 2:
            return Err("Need at least 2 data points for trend fitting.")

        # OLS via normal equations: [k, m] = (A^T A)^-1 A^T y
        A = np.column_stack([t, np.ones_like(t)])
        params, _, _, _ = np.linalg.lstsq(A, y, rcond=None)
        k, m = params[0], params[1]
        trend = k * t + m

        return Ok({"slope": float(k), "intercept": float(m), "trend": trend})

    def fit_piecewise_trend(self, t: np.ndarray, y: np.ndarray, changepoints: np.ndarray) -> Result:
        """
        Fits a piecewise linear trend with specified changepoints.

        g(t) = (k + A @ delta) * t + (m + A @ gamma)

        where A is a binary matrix indicating which changepoints are active at time t,
        and delta/gamma are slope/offset adjustments at each changepoint.

        @param t: 1D normalized time array.
        @param y: 1D observed values.
        @param changepoints: 1D array of changepoint positions (same scale as t).
        @returns Result containing dict with 'trend' array and 'deltas' for each changepoint.
        """
        if t.ndim != 1 or y.ndim != 1:
            return Err("t and y must be 1D arrays.")
        if len(t) != len(y):
            return Err("t and y must have equal length.")
        if changepoints.ndim != 1 or len(changepoints) == 0:
            return Err("changepoints must be a non-empty 1D array.")

        n = len(t)
        n_cp = len(changepoints)

        # Build change indicator matrix A: A[i, j] = 1 if t[i] >= changepoints[j]
        A = (t[:, np.newaxis] >= changepoints[np.newaxis, :]).astype(np.float64)

        # Build design matrix: [t, 1, A * t_shifted_by_cp, A]
        t_shifted = A * (t[:, np.newaxis] - changepoints[np.newaxis, :])
        design = np.column_stack([t, np.ones(n), t_shifted, A])

        params, _, _, _ = np.linalg.lstsq(design, y, rcond=None)
        trend = design @ params

        k_base = params[0]
        m_base = params[1]
        deltas = params[2:2 + n_cp]
        gammas = params[2 + n_cp:]

        return Ok({
            "trend": trend,
            "base_slope": float(k_base),
            "base_intercept": float(m_base),
            "slope_deltas": deltas,
            "offset_gammas": gammas,
        })

    def fourier_seasonality(self, t: np.ndarray, period: float, n_harmonics: int) -> Result:
        """
        Generates Fourier feature matrix for seasonal components.

        For each harmonic k in [1, n_harmonics]:
            features include sin(2*pi*k*t/period) and cos(2*pi*k*t/period)

        @param t: 1D time array.
        @param period: Length of one seasonal cycle (e.g. 365.25 for yearly).
        @param n_harmonics: Number of Fourier harmonics.
        @returns Result containing (len(t), 2*n_harmonics) feature matrix.
        """
        if t.ndim != 1:
            return Err("t must be a 1D array.")
        if period <= 0:
            return Err("period must be positive.")
        if n_harmonics <= 0:
            return Err("n_harmonics must be a positive integer.")

        features = np.zeros((len(t), 2 * n_harmonics), dtype=np.float64)
        for k in range(1, n_harmonics + 1):
            angle = 2.0 * np.pi * k * t / period
            features[:, 2 * (k - 1)] = np.sin(angle)
            features[:, 2 * (k - 1) + 1] = np.cos(angle)

        return Ok(features)

    def fit_seasonality(self, t: np.ndarray, residuals: np.ndarray, period: float, n_harmonics: int) -> Result:
        """
        Fits seasonal coefficients to residuals using Fourier features.

        @param t: 1D time array.
        @param residuals: 1D array of (y - trend).
        @param period: Seasonal period.
        @param n_harmonics: Number of harmonics.
        @returns Result containing dict with 'coefficients' and 'seasonal' component.
        """
        feat_res = self.fourier_seasonality(t, period, n_harmonics)
        if isinstance(feat_res, Err):
            return feat_res
        features = feat_res.value

        coeffs, _, _, _ = np.linalg.lstsq(features, residuals, rcond=None)
        seasonal = features @ coeffs

        return Ok({"coefficients": coeffs, "seasonal": seasonal})

    def autoregressive_predict(self, y: np.ndarray, ar_order: int) -> Result:
        """
        Fits and predicts using a simple AR(p) model via linear regression on lagged values.

        y[t] = sum_{i=1}^{p} phi_i * y[t-i] + noise

        @param y: 1D time series array.
        @param ar_order: Number of lag terms (p).
        @returns Result containing dict with 'coefficients' (phi), 'fitted' predictions, 'residuals'.
        """
        if y.ndim != 1:
            return Err("y must be a 1D array.")
        if ar_order <= 0:
            return Err("ar_order must be a positive integer.")
        if len(y) <= ar_order:
            return Err("Time series length must exceed ar_order.")

        n = len(y)
        # Build lag matrix
        X = np.zeros((n - ar_order, ar_order), dtype=np.float64)
        for lag in range(1, ar_order + 1):
            X[:, lag - 1] = y[ar_order - lag:n - lag]

        target = y[ar_order:]
        phi, _, _, _ = np.linalg.lstsq(X, target, rcond=None)
        fitted = X @ phi
        residuals = target - fitted

        return Ok({"coefficients": phi, "fitted": fitted, "residuals": residuals})

    def detect_changepoints(self, y: np.ndarray, n_changepoints: int, quantile_range: float = 0.8) -> Result:
        """
        Automatically selects changepoint locations uniformly within the central quantile range.
        Mirrors NeuralProphet / Prophet's default changepoint placement strategy.

        @param y: 1D time series.
        @param n_changepoints: Number of changepoints to place.
        @param quantile_range: Fraction of the series within which to place changepoints (default 0.8).
        @returns Result containing 1D array of changepoint indices.
        """
        if y.ndim != 1:
            return Err("y must be 1D.")
        if n_changepoints <= 0:
            return Err("n_changepoints must be positive.")

        n = len(y)
        margin = int(n * (1 - quantile_range) / 2)
        start_idx = max(1, margin)
        end_idx = max(start_idx + 1, n - margin)

        cp_indices = np.linspace(start_idx, end_idx, n_changepoints, endpoint=False, dtype=np.intp)
        return Ok(cp_indices)
