"""
OMNI Merlion Engine
===================
Production-grade abstraction inspired by salesforce/Merlion.
Implements native Autoregressive structure to forecast short-term
patterns and detect anomalies on sequential data segments via Python primitives.

OMNI Layer: compute (Python)
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Union

import numpy as np


# ---------------------------------------------------------------------------
# 1. OMNI Result Monad
# ---------------------------------------------------------------------------


ENGINE_VERSION = "1.0.0-omni"

class MerlionError(Exception):
    """Base error for Merlion forecaster abstraction."""

@dataclass(frozen=True)
class Ok:
    """Monadic Ok result type."""
    value: Any

@dataclass(frozen=True)
class Err:
    """Monadic Err result type."""
    error: str

Result = Union[Ok, Err]


# ---------------------------------------------------------------------------
# 2. AUTO-REGRESSIVE FORECASTER
# ---------------------------------------------------------------------------

class AutoregressiveForecaster:
    """Predicts next states based on explicitly 'p' historically lagged metrics."""
    def __init__(self, p_lags: int):
        """Initialize AutoregressiveForecaster."""
        self.lags = p_lags
        self.weights = np.zeros(p_lags, dtype=np.float64)
        self.bias = 0.0
        
    def fit(self, timeseries: np.ndarray) -> Result:
        """Trains purely associative OLS bounds on the trailing structure."""
        if timeseries.ndim != 1:
            return Err("Timeseries must be a 1-dimensional numpy sequence.")
            
        N = len(timeseries)
        if N <= self.lags:
            return Err("Timeseries is entirely too short to construct lagged predictors.")
            
        try:
            # Construct feature matrix X and target y
            X = np.zeros((N - self.lags, self.lags))
            y = np.zeros(N - self.lags)
            
            for i in range(N - self.lags):
                X[i, :] = timeseries[i : i + self.lags]
                y[i] = timeseries[i + self.lags]
                
            # Direct OLS regression (X'X)^-1 X'Y
            X_b = np.c_[np.ones(N - self.lags), X]
            w = np.linalg.pinv(X_b.T.dot(X_b)).dot(X_b.T).dot(y)
            
            self.bias = w[0]
            self.weights = w[1:]
            
            return Ok(True)
        except Exception as e:
            return Err(f"AR fit projection failed: {e}")
            
    def forecast(self, trailing_window: np.ndarray, steps: int = 1) -> Result:
        """Iteratively injects recursive inferences into window to walk forward."""
        if len(trailing_window) < self.lags:
            return Err("Trailing context is not deep enough to cover lags representation.")
            
        try:
            predictions = []
            working_window = list(trailing_window[-self.lags:])
            
            for _ in range(steps):
                ctx = np.array(working_window[-self.lags:])
                next_val = float(np.dot(ctx, self.weights) + self.bias)
                predictions.append(next_val)
                working_window.append(next_val)
                
            return Ok(np.array(predictions))
        except Exception as e:
            return Err(f"Inference derivation halted: {e}")


# ---------------------------------------------------------------------------
# 3. OMNI ENGINE CLASS
# ---------------------------------------------------------------------------

class OmniMerlionEngine:
    """
    Production Engine for Lightweight Metric Forecasting.
    """

    def __init__(self, config=None):
        """Initialize OmniMerlionEngine."""
        self.config = config or {}
        self.engine_id = __import__("uuid").uuid4().hex
        self.is_active = True
    VERSION = "1.0.0"
    ENGINE_ID = "omni-merlion"

    def get_forecaster(self, lags: int = 3) -> AutoregressiveForecaster:
        """Performs get forecaster operation for OmniMerlionEngine."""
        return AutoregressiveForecaster(p_lags=lags)

    def diagnostics(self) -> Dict[str, Any]:
        """Performs diagnostics operation for OmniMerlionEngine."""
        return {
            "engine_id": self.ENGINE_ID,
            "version": self.VERSION,
            "architecture": "Autoregressive (AR) Time Series Predictor",
            "status": "operational",
        }
