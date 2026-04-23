"""OmniMovingAverageEngine — Production-grade time series moving average.

Implements Simple Moving Average (SMA), Exponential Moving Average (EMA),
and Weighted Moving Average (WMA) for time series smoothing and analysis.
"""
from typing import Any, Dict, List
from src.compute.python_core.omni_base_engine import Result, Ok, Err


class OmniMovingAverageEngine:
    """Production engine for time series moving averages."""

    ENGINE_VERSION = "1.0.0"

    def sma(self, data: List[float], window: int) -> Result:
        """Compute Simple Moving Average."""
        try:
            if not data:
                return Err(ValueError("Data must be non-empty."))
            if window <= 0 or window > len(data):
                return Err(ValueError(f"Window must be in [1, {len(data)}]."))

            result = []
            window_sum = sum(data[:window])
            result.append(round(window_sum / window, 8))
            for i in range(window, len(data)):
                window_sum += data[i] - data[i - window]
                result.append(round(window_sum / window, 8))

            return Ok({"sma": result, "window": window, "input_length": len(data),
                        "output_length": len(result)})
        except Exception as e:
            return Err(e)

    def ema(self, data: List[float], span: int) -> Result:
        """Compute Exponential Moving Average."""
        try:
            if not data:
                return Err(ValueError("Data must be non-empty."))
            if span <= 0:
                return Err(ValueError("Span must be positive."))

            alpha = 2.0 / (span + 1)
            result = [data[0]]
            for i in range(1, len(data)):
                ema_val = alpha * data[i] + (1 - alpha) * result[-1]
                result.append(round(ema_val, 8))

            return Ok({"ema": result, "span": span, "alpha": round(alpha, 6),
                        "input_length": len(data), "output_length": len(result)})
        except Exception as e:
            return Err(e)

    def wma(self, data: List[float], window: int) -> Result:
        """Compute Weighted Moving Average (linear weights)."""
        try:
            if not data:
                return Err(ValueError("Data must be non-empty."))
            if window <= 0 or window > len(data):
                return Err(ValueError(f"Window must be in [1, {len(data)}]."))

            weight_sum = window * (window + 1) / 2
            result = []
            for i in range(window - 1, len(data)):
                wma_val = sum((j + 1) * data[i - window + 1 + j] for j in range(window)) / weight_sum
                result.append(round(wma_val, 8))

            return Ok({"wma": result, "window": window, "input_length": len(data),
                        "output_length": len(result)})
        except Exception as e:
            return Err(e)

    def diagnostics(self) -> Dict[str, Any]:
        return {"engine": "OmniMovingAverageEngine", "version": self.ENGINE_VERSION,
                "status": "operational", "methods": ["SMA O(N)", "EMA O(N)", "WMA O(N*W)"]}
