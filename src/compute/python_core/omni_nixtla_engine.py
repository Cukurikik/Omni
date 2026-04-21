"""
OMNI Nixtla Engine — Time series forecasting and anomaly detection primitives.

Assimilated from: Nixtla/nixtla (6k ★)
TimeGPT-1: Production-ready Time Series Foundation Model.

Implements core time series forecasting building blocks:
  - Statistical forecasting: naive, seasonal naive, moving average, ETS
  - Feature engineering: lags, rolling stats, calendar features
  - Anomaly detection: z-score, IQR, isolation score
  - Trend decomposition: STL-like decomposition (trend + season + residual)
  - Forecast evaluation metrics: MAE, RMSE, MAPE, SMAPE, MASE
  - Conformal prediction intervals

OMNI Domain: compute/ (Python)
CODE RULE 001-005 compliant. Only numpy dependency.
"""

from __future__ import annotations

import math
from typing import Any, Dict, List, Optional, Tuple

import numpy as np


ENGINE_VERSION: str = "1.0.0-omni"
ENGINE_NAME: str = "OmniNixtlaEngine"


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


class OmniNixtlaEngine:
    """Production-grade time series forecasting and anomaly detection engine.

    Implements core forecasting primitives:
      - Statistical baselines (naive, seasonal naive, SMA, ETS)
      - Feature engineering (lags, rolling windows, calendar)
      - Anomaly detection (z-score, IQR, isolation)
      - Trend-season decomposition
      - Forecast evaluation (MAE, RMSE, MAPE, SMAPE, MASE)
      - Conformal prediction intervals

    @since 1.0.0
    @tags ["time-series", "forecasting", "anomaly-detection", "nixtla", "compute"]
    """

    VERSION = ENGINE_VERSION
    ENGINE_ID = ENGINE_NAME

    def __init__(self) -> None:
        """Initialize OmniNixtlaEngine."""
        pass

    def diagnostics(self) -> Result:
        """Performs diagnostics operation for OmniNixtlaEngine."""
        return Ok({
            "engine": self.ENGINE_ID, "version": self.VERSION,
            "status": "operational",
            "capabilities": [
                "naive_forecast", "seasonal_naive", "moving_average",
                "exponential_smoothing", "decompose",
                "lag_features", "rolling_features", "calendar_features",
                "anomaly_zscore", "anomaly_iqr",
                "mae", "rmse", "mape", "smape", "mase",
                "conformal_interval",
            ],
        })

    # -----------------------------------------------------------------
    # 1. STATISTICAL FORECASTING
    # -----------------------------------------------------------------

    def naive_forecast(self, series: np.ndarray, horizon: int) -> Result:
        """Naive forecast: repeat last value.

        @param series: (T,) historical time series.
        @param horizon: Number of future steps.
        @returns Result with (horizon,) forecast.
        """
        if len(series) == 0:
            return Err("Empty series.")
        return Ok(np.full(horizon, series[-1]))

    def seasonal_naive(self, series: np.ndarray, horizon: int, season_length: int) -> Result:
        """Seasonal naive: repeat last season.

        @param series: (T,) historical series.
        @param horizon: Forecast horizon.
        @param season_length: Length of one seasonal period.
        @returns Result with (horizon,) forecast.
        """
        if len(series) < season_length:
            return Err("Series shorter than season_length.")
        last_season = series[-season_length:]
        reps = int(math.ceil(horizon / season_length))
        forecast = np.tile(last_season, reps)[:horizon]
        return Ok(forecast)

    def moving_average(self, series: np.ndarray, horizon: int, window: int) -> Result:
        """Simple moving average forecast.

        @param series: (T,) historical series.
        @param horizon: Steps to forecast.
        @param window: MA window size.
        @returns Result with (horizon,) forecast.
        """
        if len(series) < window:
            return Err("Series shorter than window.")
        ma = float(np.mean(series[-window:]))
        return Ok(np.full(horizon, ma))

    def exponential_smoothing(
        self, series: np.ndarray, horizon: int, alpha: float = 0.3
    ) -> Result:
        """Simple exponential smoothing (SES) forecast.

        s_t = alpha * y_t + (1 - alpha) * s_{t-1}

        @param series: (T,) historical series.
        @param horizon: Forecast horizon.
        @param alpha: Smoothing parameter in (0, 1).
        @returns Result with dict: 'forecast', 'fitted'.
        """
        if alpha <= 0 or alpha >= 1:
            return Err("alpha must be in (0, 1).")
        if len(series) == 0:
            return Err("Empty series.")

        fitted = np.zeros(len(series))
        fitted[0] = series[0]
        for t in range(1, len(series)):
            fitted[t] = alpha * series[t] + (1 - alpha) * fitted[t - 1]

        forecast = np.full(horizon, fitted[-1])
        return Ok({"forecast": forecast, "fitted": fitted})

    # -----------------------------------------------------------------
    # 2. DECOMPOSITION
    # -----------------------------------------------------------------

    def decompose(self, series: np.ndarray, period: int) -> Result:
        """Additive time series decomposition: Trend + Seasonal + Residual.

        Uses centered moving average for trend extraction.

        @param series: (T,) time series.
        @param period: Seasonal period.
        @returns Result with dict: 'trend', 'seasonal', 'residual'.
        """
        T = len(series)
        if T < 2 * period:
            return Err("Series too short for decomposition.")

        # Trend via centered moving average
        trend = np.full(T, np.nan)
        half = period // 2
        for t in range(half, T - half):
            trend[t] = np.mean(series[max(0, t - half):t + half + 1])

        # Seasonal component
        detrended = series - trend
        seasonal = np.zeros(T)
        for i in range(period):
            indices = np.arange(i, T, period)
            valid = [j for j in indices if not np.isnan(detrended[j])]
            if valid:
                seasonal_avg = np.mean(detrended[valid])
            else:
                seasonal_avg = 0.0
            for j in indices:
                seasonal[j] = seasonal_avg

        # Residual
        residual = series - trend - seasonal
        # Fill NaN in trend edges
        trend = np.nan_to_num(trend, nan=float(np.nanmean(trend)))
        residual = np.nan_to_num(residual, nan=0.0)

        return Ok({"trend": trend, "seasonal": seasonal, "residual": residual})

    # -----------------------------------------------------------------
    # 3. FEATURE ENGINEERING
    # -----------------------------------------------------------------

    def lag_features(self, series: np.ndarray, lags: List[int]) -> Result:
        """Create lag features from time series.

        @param series: (T,) time series.
        @param lags: List of lag values (e.g., [1, 7, 14]).
        @returns Result with (T, len(lags)) feature matrix.
        """
        T = len(series)
        features = np.full((T, len(lags)), np.nan)
        for col, lag in enumerate(lags):
            if lag < T:
                features[lag:, col] = series[:T - lag]
        return Ok(features)

    def rolling_features(self, series: np.ndarray, window: int) -> Result:
        """Compute rolling mean and std features.

        @param series: (T,) time series.
        @param window: Rolling window size.
        @returns Result with dict: 'rolling_mean', 'rolling_std'.
        """
        if len(series) < window:
            return Err("Series shorter than window.")
        T = len(series)
        r_mean = np.full(T, np.nan)
        r_std = np.full(T, np.nan)
        for t in range(window - 1, T):
            segment = series[t - window + 1:t + 1]
            r_mean[t] = np.mean(segment)
            r_std[t] = np.std(segment)
        return Ok({"rolling_mean": r_mean, "rolling_std": r_std})

    def calendar_features(self, timestamps_day_of_year: np.ndarray) -> Result:
        """Generate cyclical calendar features (sin/cos encoding).

        @param timestamps_day_of_year: (T,) day-of-year values (1-366).
        @returns Result with dict: 'sin_day', 'cos_day'.
        """
        rad = 2.0 * np.pi * timestamps_day_of_year / 365.25
        return Ok({"sin_day": np.sin(rad), "cos_day": np.cos(rad)})

    # -----------------------------------------------------------------
    # 4. ANOMALY DETECTION
    # -----------------------------------------------------------------

    def anomaly_zscore(self, series: np.ndarray, threshold: float = 3.0) -> Result:
        """Z-score based anomaly detection.

        @param series: (T,) time series.
        @param threshold: Z-score threshold for anomaly.
        @returns Result with dict: 'is_anomaly' (bool array), 'z_scores'.
        """
        mean = np.mean(series)
        std = np.std(series) + 1e-10
        z = np.abs((series - mean) / std)
        return Ok({"is_anomaly": z > threshold, "z_scores": z})

    def anomaly_iqr(self, series: np.ndarray, multiplier: float = 1.5) -> Result:
        """IQR-based anomaly detection.

        @param series: (T,) time series.
        @param multiplier: IQR multiplier (default 1.5).
        @returns Result with dict: 'is_anomaly', 'lower', 'upper'.
        """
        q1 = np.percentile(series, 25)
        q3 = np.percentile(series, 75)
        iqr = q3 - q1
        lower = q1 - multiplier * iqr
        upper = q3 + multiplier * iqr
        is_anomaly = (series < lower) | (series > upper)
        return Ok({"is_anomaly": is_anomaly, "lower": lower, "upper": upper})

    # -----------------------------------------------------------------
    # 5. EVALUATION METRICS
    # -----------------------------------------------------------------

    def mae(self, actual: np.ndarray, predicted: np.ndarray) -> Result:
        """Mean Absolute Error."""
        return Ok(float(np.mean(np.abs(actual - predicted))))

    def rmse(self, actual: np.ndarray, predicted: np.ndarray) -> Result:
        """Root Mean Squared Error."""
        return Ok(float(np.sqrt(np.mean((actual - predicted) ** 2))))

    def mape(self, actual: np.ndarray, predicted: np.ndarray) -> Result:
        """Mean Absolute Percentage Error."""
        mask = actual != 0
        if not np.any(mask):
            return Err("All actual values are zero.")
        return Ok(float(np.mean(np.abs((actual[mask] - predicted[mask]) / actual[mask])) * 100))

    def smape(self, actual: np.ndarray, predicted: np.ndarray) -> Result:
        """Symmetric Mean Absolute Percentage Error."""
        denom = np.abs(actual) + np.abs(predicted)
        mask = denom > 0
        if not np.any(mask):
            return Ok(0.0)
        return Ok(float(np.mean(2.0 * np.abs(actual[mask] - predicted[mask]) / denom[mask]) * 100))

    def mase(self, actual: np.ndarray, predicted: np.ndarray, season_length: int = 1) -> Result:
        """Mean Absolute Scaled Error.

        Scaled by in-sample seasonal naive error.

        @param actual: (T,) actual values.
        @param predicted: (T,) predicted values.
        @param season_length: Seasonal period for naive baseline.
        @returns Result with scalar MASE.
        """
        naive_err = np.mean(np.abs(actual[season_length:] - actual[:-season_length]))
        if naive_err < 1e-10:
            return Err("Naive error is zero; MASE undefined.")
        mae_val = np.mean(np.abs(actual - predicted))
        return Ok(float(mae_val / naive_err))

    # -----------------------------------------------------------------
    # 6. CONFORMAL PREDICTION
    # -----------------------------------------------------------------

    def conformal_interval(
        self, residuals: np.ndarray, forecast: np.ndarray, alpha: float = 0.1
    ) -> Result:
        """Compute conformal prediction intervals.

        @param residuals: (N,) calibration residuals (actual - predicted).
        @param forecast: (H,) point forecast.
        @param alpha: Significance level (default 0.1 → 90% interval).
        @returns Result with dict: 'lower', 'upper', 'width'.
        """
        if alpha <= 0 or alpha >= 1:
            return Err("alpha must be in (0, 1).")
        q = np.percentile(np.abs(residuals), (1 - alpha) * 100)
        lower = forecast - q
        upper = forecast + q
        return Ok({"lower": lower, "upper": upper, "width": float(2 * q)})
