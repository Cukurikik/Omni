# OMNI MOTHER - DIVINE MEMORY INTEGRATION
# Prefect Core (OMNI Zero-Mock Implementation)
# Implements declarative retries with exponential backoff math calculation.

from dataclasses import dataclass
from typing import List, Optional
import math

@dataclass
class Result:
    value: Optional[List[float]] # Wait times in seconds for each retry slot
    error: Optional[str]
    is_ok: bool

    @staticmethod
    def ok(val: List[float]) -> 'Result':
        return Result(value=val, error=None, is_ok=True)

    @staticmethod
    def err(err: str) -> 'Result':
        return Result(value=None, error=err, is_ok=False)

class PrefectBackoffEngine:
    def calculate_wait_times(self, max_retries: int, base_delay: float, retry_delay_factor: float) -> Result:
        """
        Calculates mathematically explicit timing bounds for task eviction handling policies.
        """
        if max_retries < 0:
            return Result.err("Retries cannot be negative.")
        if max_retries == 0:
            return Result.ok([])
        if base_delay <= 0.0 or retry_delay_factor < 1.0:
            return Result.err("Delay values must be structurally sound bounds.")
            
        waits = []
        for i in range(max_retries):
             # exponential backoff: base_delay * (factor ^ attempt)
             wait_t = base_delay * math.pow(retry_delay_factor, i)
             waits.append(wait_t)
             
        return Result.ok(waits)
