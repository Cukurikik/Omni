import datetime
import math
from typing import Any, Dict
from src.compute.python_core.omni_base_engine import Result, Ok, Err


class OmniExponentialBackoffJitterEngine:
    """
    OmniExponentialBackoffJitterEngine
    Batch: 28 (Semester 10)
    
    A zero-mock systems resilience computing engine that implements 
    exponential backoff with deterministic pseudo-random jitter.
    Calculates interval bounds to eliminate thundering herd limits.
    """
    
    def __init__(self, base_delay_ms: float, max_delay_ms: float, jitter_factor: float):
        """
        :param base_delay_ms: Initial starting delay (e.g., 100ms)
        :param max_delay_ms: Absolute cap ceiling limit (e.g., 10000ms)
        :param jitter_factor: Float describing degree of noise (0.0 to 1.0)
        """
        self.base_delay = base_delay_ms
        self.max_delay = max_delay_ms
        self.jitter_factor = max(0.0, min(1.0, jitter_factor))

    def diagnostics(self) -> Dict[str, Any]:
        return {
            "engine": self.__class__.__name__,
            "status": "operational",
            "base_delay_ms": self.base_delay,
            "max_delay_ms": self.max_delay,
            "jitter_factor": self.jitter_factor,
            "timestamp": datetime.datetime.utcnow().isoformat()
        }

    def _pseudo_random_hash(self, attempt: int, seed: int) -> float:
        """
        Deterministic fraction generator [0, 1) to execute random jitter computationally
        without breaking zero-mock purity rules.
        """
        val = (attempt * 1103515245 + seed * 12345) & 0x7fffffff
        return float(val) / 0x80000000

    def compute_backoff(self, attempt: int, seed: int = 100) -> Result[Dict[str, Any], Exception]:
        """
        Computes exact bounds and selects a jittered delay within the frame limit constraints.
        Returns the interval in MS.
        """
        try:
            if attempt < 0:
                return Err(ValueError("Attempt count must be >= 0"))
                
            # exponential computation limit clamping to avoid overflow
            try:
                raw_exp = self.base_delay * math.pow(2, attempt)
            except OverflowError:
                raw_exp = float('inf')
                
            capped_delay = min(raw_exp, self.max_delay)
            
            # Application of "Full Jitter" strategy bounds:
            # Jitter is applied as: delay = base_jitter + random * range
            # Range is scaled by jitter factor.
            
            jitter_range = capped_delay * self.jitter_factor
            min_boundary = capped_delay - jitter_range
            
            random_fraction = self._pseudo_random_hash(attempt, seed)
            jitter_value = min_boundary + (jitter_range * random_fraction)
            
            return Ok({
                "attempt": attempt,
                "raw_exponential_ms": round(capped_delay, 4),
                "jittered_delay_ms": round(jitter_value, 4),
                "min_boundary_ms": round(min_boundary, 4),
                "max_delay_cap_ms": self.max_delay
            })
            
        except Exception as e:
            return Err(e)
