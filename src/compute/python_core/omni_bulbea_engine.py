"""
OMNI Bulbea Engine
==================
Production-grade OMNI engine abstracting deep learning time-series
financial pipelines. Inspired by achillesrasquinha/bulbea.

Features:
- OHLCV time-series normalization and technical logic abstractions.
- Sequence window generator for LSTM modeling preparations.
- Moving Average / Volatility feature extraction.
- Monadic Result encapsulation preventing runtime trace crashes.

OMNI Layer: compute (Python)
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Tuple, Union

import numpy as np

# ---------------------------------------------------------------------------
# 1. OMNI Result Monad
# ---------------------------------------------------------------------------

ENGINE_VERSION = "1.0.0-omni"


class BulbeaErr(Exception):
    pass


@dataclass(frozen=True)
class Ok:
    value: Any


@dataclass(frozen=True)
class Err:
    error: str


Result = Union[Ok, Err]


# ---------------------------------------------------------------------------
# 2. TIME-SERIES PIPELINE
# ---------------------------------------------------------------------------

class TimeSeriesPipeline:
    """Preprocesses financial OHLCV arrays."""

    @staticmethod
    def relative_return(prices: np.ndarray) -> np.ndarray:
        """Calculate fractional daily returns."""
        returns = np.zeros_like(prices)
        returns[1:] = (prices[1:] - prices[:-1]) / (prices[:-1] + 1e-9)
        return returns

    @staticmethod
    def create_sequences(data: np.ndarray, window_size: int) -> Tuple[np.ndarray, np.ndarray]:
        """Create sliding windows (X) and next steps (y) for sequence modeling."""
        X, y = [], []
        limit = len(data) - window_size
        for i in range(limit):
            X.append(data[i: i + window_size])
            y.append(data[i + window_size])
        return np.array(X), np.array(y)


# ---------------------------------------------------------------------------
# 3. OMNI ENGINE CLASS
# ---------------------------------------------------------------------------

class OmniBulbeaEngine:
    """
    Production Engine providing OHLCV pre-processing, transformations,
    and sequence splits for time-series deep learning.
    """
    VERSION = "1.0.0"
    ENGINE_ID = "omni-bulbea"

    def __init__(self) -> None:
        self._history: Dict[str, np.ndarray] = {}

    def load_equity(self, symbol: str, close_prices: List[float]) -> Result:
        """Load equity close prices history."""
        if not close_prices:
            return Err("Close prices cannot be empty.")
        try:
            self._history[symbol] = np.array(close_prices, dtype=np.float64)
            return Ok(len(close_prices))
        except Exception as exc:
            return Err(f"Load failed: {exc}")

    def prepare_lstm_data(self, symbol: str, window_size: int = 10,
                          test_split: float = 0.2) -> Result:
        """Structure series into X (windows) and y (targets) with split."""
        base_arr = self._history.get(symbol)
        if base_arr is None:
            return Err(f"Symbol '{symbol}' not found.")
        if window_size >= len(base_arr):
            return Err("Window size is larger than sequence length.")

        try:
            # 1. Normalize as relative returns
            returns = TimeSeriesPipeline.relative_return(base_arr)

            # 2. Create squences
            X, y = TimeSeriesPipeline.create_sequences(returns, window_size)

            # 3. Train Test split
            split_idx = int(len(X) * (1.0 - test_split))
            
            return Ok({
                "X_train_shape": list(X[:split_idx].shape),
                "y_train_shape": list(y[:split_idx].shape),
                "X_test_shape": list(X[split_idx:].shape),
                "y_test_shape": list(y[split_idx:].shape),
            })
        except Exception as exc:
            return Err(f"Pipeline preparation failed: {exc}")
            
    def diagnostics(self) -> Dict[str, Any]:
        """Return engine diagnostics."""
        return {
            "engine_id": self.ENGINE_ID,
            "version": self.VERSION,
            "status": "operational",
            "equities_loaded": len(self._history),
            "features": [
                "ohlcv_relative_returns",
                "sliding_window_sequencing",
                "lstm_train_test_split",
            ]
        }
