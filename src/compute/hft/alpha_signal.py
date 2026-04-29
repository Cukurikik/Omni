import numpy as np
from typing import Any

class OmniResult:
    def __init__(self, success: bool, value: Any = None, error: str = None):
        self.success = success
        self.value = value
        self.error = error
    @classmethod
    def ok(cls, value: Any): return cls(True, value=value)
    @classmethod
    def err(cls, error: str): return cls(False, error=error)

class AlphaSignalGenerator:
    def __init__(self, window_size: int = 50):
        self.window_size = window_size

    def calculate_momentum_signal(self, prices: np.ndarray) -> OmniResult:
        """
        Calculates a momentum alpha signal based on short-term price history.
        Expected input: 1D numpy array of float prices.
        """
        if prices is None or len(prices) < self.window_size:
            return OmniResult.err(f"Need at least {self.window_size} prices for momentum signal")
            
        try:
            # Simple momentum: (Current Price / Price N periods ago) - 1
            current_price = prices[-1]
            past_price = prices[-self.window_size]
            
            if past_price == 0:
                return OmniResult.err("Division by zero in momentum calculation (past price is 0)")
                
            momentum = (current_price / past_price) - 1.0
            
            # Normalize to [-1.0, 1.0] signal
            signal = np.clip(momentum * 10.0, -1.0, 1.0)
            
            return OmniResult.ok(float(signal))
        except Exception as e:
            return OmniResult.err(f"Alpha calculation failed: {str(e)}")
