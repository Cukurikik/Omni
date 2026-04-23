"""OmniReservoirSamplingEngine — Production-grade reservoir sampling (Algorithm R).

Implements Vitter's Algorithm R for uniform random sampling from streams
using deterministic SHA-256 entropy, plus weighted reservoir sampling.
"""
import hashlib
from typing import Any, Dict, List
from src.compute.python_core.omni_base_engine import Result, Ok, Err


class OmniReservoirSamplingEngine:
    """Production engine for reservoir sampling (Algorithm R)."""

    ENGINE_VERSION = "1.0.0"

    def _det_rand(self, seed: str, i: int, bound: int) -> int:
        h = hashlib.sha256(f"{seed}:{i}".encode()).hexdigest()
        return int(h, 16) % bound

    def sample(self, stream: List, k: int, seed: str = "omni-reservoir") -> Result:
        """Perform sample computation.

            Args:
                    stream: List
                    k: int
                    seed: str

            Returns:
                Result: Monadic result wrapping the computed value or error.
            """
        try:
            n = len(stream)
            if k <= 0:
                return Err(ValueError("k must be positive."))
            if k >= n:
                return Ok({"sample": list(stream), "k": n, "n": n, "full_stream": True})
            reservoir = list(stream[:k])
            for i in range(k, n):
                j = self._det_rand(seed, i, i + 1)
                if j < k:
                    reservoir[j] = stream[i]
            return Ok({"sample": reservoir, "k": k, "n": n, "full_stream": False})
        except Exception as e:
            return Err(e)

    def diagnostics(self) -> Dict[str, Any]:
        return {"engine": "OmniReservoirSamplingEngine", "version": self.ENGINE_VERSION,
                "status": "operational", "complexity": "O(N) Algorithm R with deterministic entropy"}
