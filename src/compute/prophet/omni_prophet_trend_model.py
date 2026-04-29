# OMNI MOTHER - DIVINE MEMORY INTEGRATION
# Prophet Additive Trend Model (OMNI Zero-Mock Implementation)
# Implements piecewise linear trend with changepoints.

from dataclasses import dataclass
from typing import List, Tuple, Optional
import math

@dataclass
class Result:
    value: Optional[List[float]]
    error: Optional[str]
    is_ok: bool

    @staticmethod
    def ok(val: List[float]) -> 'Result':
        return Result(value=val, error=None, is_ok=True)

    @staticmethod
    def err(err: str) -> 'Result':
        return Result(value=None, error=err, is_ok=False)

class ProphetTrend:
    def __init__(self, changepoints: List[float], deltas: List[float], base_k: float, base_m: float):
        self.changepoints = changepoints
        self.deltas = deltas
        self.base_k = base_k
        self.base_m = base_m

    def predict(self, times: List[float]) -> Result:
        if len(self.changepoints) != len(self.deltas):
            return Result.err("Changepoints and deltas must have the same length.")
            
        predictions = []
        for t in times:
            k = self.base_k
            m = self.base_m
            
            # Adjust growth and offset for all changepoints prior to t
            for i, cp in enumerate(self.changepoints):
                if t >= cp:
                    k += self.deltas[i]
                    m -= cp * self.deltas[i] 
            
            y_hat = k * t + m
            predictions.append(y_hat)
            
        return Result.ok(predictions)
