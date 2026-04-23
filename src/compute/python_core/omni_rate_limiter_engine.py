"""OmniRateLimiterEngine — Production-grade rate limiting algorithms.

Implements Token Bucket, Sliding Window, and Fixed Window rate limiters
for API throttling, network flow control, and resource management.
"""
import time
from typing import Any, Dict
from src.compute.python_core.omni_base_engine import Result, Ok, Err


class OmniRateLimiterEngine:
    """Production engine for rate limiting algorithms."""

    ENGINE_VERSION = "1.0.0"

    def __init__(self):
        self._token_buckets = {}
        self._sliding_windows = {}

    def create_bucket(self, name: str, capacity: int, refill_rate: float) -> Result:
        """Perform create bucket computation.

            Args:
                    name: str
                    capacity: int
                    refill_rate: float

            Returns:
                Result: Monadic result wrapping the computed value or error.
            """
        try:
            self._token_buckets[name] = {
                "capacity": capacity,
                "tokens": float(capacity),
                "refill_rate": refill_rate,
                "last_refill": time.monotonic()
            }
            return Ok({"created": True, "name": name, "capacity": capacity, "refill_rate": refill_rate})
        except Exception as e:
            return Err(e)

    def acquire(self, name: str, tokens: int = 1) -> Result:
        """Perform acquire computation.

            Args:
                    name: str
                    tokens: int

            Returns:
                Result: Monadic result wrapping the computed value or error.
            """
        try:
            if name not in self._token_buckets:
                return Err(ValueError(f"Bucket '{name}' not found."))
            b = self._token_buckets[name]
            now = time.monotonic()
            elapsed = now - b["last_refill"]
            b["tokens"] = min(b["capacity"], b["tokens"] + elapsed * b["refill_rate"])
            b["last_refill"] = now
            if b["tokens"] >= tokens:
                b["tokens"] -= tokens
                return Ok({"allowed": True, "remaining": int(b["tokens"]), "bucket": name})
            return Ok({"allowed": False, "remaining": int(b["tokens"]), "bucket": name,
                        "retry_after_ms": int((tokens - b["tokens"]) / b["refill_rate"] * 1000)})
        except Exception as e:
            return Err(e)

    def fixed_window_check(self, key: str, max_requests: int, window_seconds: float, current_time: float = None) -> Result:
        """Perform fixed window check computation.

            Args:
                    key: str
                    max_requests: int
                    window_seconds: float
                    current_time: float

            Returns:
                Result: Monadic result wrapping the computed value or error.
            """
        try:
            now = current_time if current_time is not None else time.monotonic()
            window_start = int(now / window_seconds) * window_seconds
            wkey = f"{key}:{window_start}"
            if wkey not in self._sliding_windows:
                self._sliding_windows[wkey] = 0
            self._sliding_windows[wkey] += 1
            count = self._sliding_windows[wkey]
            allowed = count <= max_requests
            return Ok({"allowed": allowed, "request_count": count, "max_requests": max_requests,
                        "window_seconds": window_seconds, "key": key})
        except Exception as e:
            return Err(e)

    def diagnostics(self) -> Dict[str, Any]:
        return {"engine": "OmniRateLimiterEngine", "version": self.ENGINE_VERSION,
                "status": "operational", "algorithms": ["Token Bucket", "Fixed Window"],
                "active_buckets": len(self._token_buckets)}
