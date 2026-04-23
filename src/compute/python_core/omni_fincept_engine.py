"""
OMNI Fincept Engine
===================
Production-grade abstraction inspired by Fincept-Corporation/FinceptTerminal.
Decouples terminal UI components to focus entirely on
financial timeseries algorithms like Volatility Estimation and EMA.

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
from src.compute.python_core.omni_base_engine import Result, Ok, Err

class FinceptError(Exception):
    """Base error for Financial calculus abstractions."""

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
# 2. FINANCIAL TIMESERIES LOGIC
# ---------------------------------------------------------------------------

class VolatilityMetrics:
    """Calculates Exponential Moving Average and localized historical Volatility."""
    
    def __init__(self, ema_period: int = 14):
        """Initialize VolatilityMetrics."""
        self.ema_n = ema_period
        
    def calculate_ema(self, prices: np.ndarray) -> Result:
        """Calculate ema."""
        if len(prices) < self.ema_n:
            return Err("Insufficient historical series volume to compute moving average.")
            
        try:
            ema = np.zeros_like(prices, dtype=np.float64)
            multiplier = 2.0 / (self.ema_n + 1.0)
            
            # Simple average for the first point boundary
            ema[self.ema_n - 1] = np.mean(prices[:self.ema_n])
            
            # Exponential formula
            for i in range(self.ema_n, len(prices)):
                ema[i] = (prices[i] - ema[i-1]) * multiplier + ema[i-1]
                
            return Ok(ema)
            
        except Exception as e:
            return Err(f"Exponential decay aggregation fault: {e}")

    def calculate_volatility(self, prices: np.ndarray, window: int = 20) -> Result:
        """Returns localized standard deviation representing simulated price volatility."""
        if len(prices) < window:
            return Err("Volatility window broader than accessible price history.")
            
        try:
            # Using Numpy stride tricks or simple rolling variance for deterministic calculus
            returns = np.diff(prices) / (prices[:-1] + 1e-9)
            
            volatilities = np.zeros(len(returns), dtype=np.float64)
            for i in range(window - 1, len(returns)):
                volatilities[i] = np.std(returns[i - window + 1: i + 1])
                
            # Pad the missing front start point diffs to maintain dimensionality alignment
            padded_vols = np.insert(volatilities, 0, 0.0)
            
            return Ok(padded_vols)
            
        except Exception as e:
            return Err(f"Standard deviation localized fault: {e}")


# ---------------------------------------------------------------------------
# 3. OMNI ENGINE CLASS
# ---------------------------------------------------------------------------

class OmniFinceptEngine:
    """
    Production Engine for Hardcore Financial Algorithmic Core.
    """

    def __init__(self, config=None):
        """Initialize OmniFinceptEngine."""
        self.config = config or {}
        self.engine_id = __import__("uuid").uuid4().hex
        self.is_active = True
    VERSION = "1.0.0"
    ENGINE_ID = "omni-fincept"

    def get_metrics_analyzer(self, ema_window: int = 14) -> VolatilityMetrics:
        """Performs get metrics analyzer operation for OmniFinceptEngine."""
        return VolatilityMetrics(ema_period=ema_window)

    def diagnostics(self) -> Dict[str, Any]:
        """Performs diagnostics operation for OmniFinceptEngine."""
        return {
            "engine_id": self.ENGINE_ID,
            "version": self.VERSION,
            "architecture": "Deterministic Variance vs Moving Average Calculator",
            "status": "operational",
        }
