"""
OMNI Leaky Bucket Engine - Network protocol rate limiting.
Assimilated from: system-design-primer.
Provides: Millisecond-precision deterministic Rate Limiting logic.
"""
import time

from typing import Any
from src.compute.python_core.omni_base_engine import Result, Ok, Err

ENGINE_VERSION = "1.0.0-omni-leaky-bucket"




class OmniLeakyBucketEngine:
    """
    Mathematical rate limiter execute a leaky bucket.
    Prevents API abuse by strictly regulating execution drips.

    @since 1.0.0
    @tags ["rate-limiter", "leaky-bucket", "system-design", "throttle"]
    """
    def __init__(self, bucket_capacity: int = 10, leak_rate_per_sec: float = 1.0) -> None:
        self._omni_version: str = "3.0.0-OMNI-NEXUS"
        self.capacity = bucket_capacity
        self.leak_rate = leak_rate_per_sec
        self.current_water = 0.0
        self.last_leak_timestamp = time.time()

    def diagnostics(self) -> Result:
        res = self.allow_request(1)
        if res.is_ok() and res.value.get("allowed") is True:
            return Ok({"engine": "LeakyBucket", "status": "Ready", "drip_mechanic": "Functional"})
        return Err("Bucket limit failure.")

    def _leak(self) -> None:
        now = time.time()
        elapsed = now - self.last_leak_timestamp
        leaked = elapsed * self.leak_rate
        self.current_water = max(0.0, self.current_water - leaked)
        self.last_leak_timestamp = now

    def allow_request(self, drop_size: int = 1) -> Result:
        """Determines if a block of requests can be admitted to the pipeline."""
        if drop_size > self.capacity:
            return Err("Drop size exceeds total capacity.")
            
        self._leak()
        
        if self.current_water + drop_size <= self.capacity:
            self.current_water += drop_size
            return Ok({"allowed": True, "current_capacity": round(self.capacity - self.current_water, 3)})
        else:
            return Err("Rate limit exceeded. Bucket is full.")
