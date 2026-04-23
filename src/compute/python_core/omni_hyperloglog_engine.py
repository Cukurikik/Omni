"""OmniHyperloglogEngine — Production-grade HyperLogLog cardinality estimator.

Implements HyperLogLog algorithm for approximate distinct count estimation
with configurable precision (p), using SHA-256 hashing and harmonic mean.
"""
import hashlib
import math
from typing import Any, Dict, List
from src.compute.python_core.omni_base_engine import Result, Ok, Err


class OmniHyperloglogEngine:
    """Production engine for probabilistic cardinality estimation."""

    ENGINE_VERSION = "1.0.0"

    def __init__(self, precision: int = 14):
        if not (4 <= precision <= 16):
            raise ValueError("Precision must be in [4, 16].")
        self.p = precision
        self.m = 1 << precision  # number of registers
        self.registers = [0] * self.m
        self._count = 0
        self._alpha = self._compute_alpha(self.m)

    @staticmethod
    def _compute_alpha(m: int) -> float:
        if m == 16:
            return 0.673
        elif m == 32:
            return 0.697
        elif m == 64:
            return 0.709
        else:
            return 0.7213 / (1 + 1.079 / m)

    @staticmethod
    def _hash64(item: str) -> int:
        return int(hashlib.sha256(item.encode()).hexdigest()[:16], 16)

    def _leading_zeros(self, value: int, bits: int) -> int:
        """Count leading zeros in the lower `bits` bits."""
        if value == 0:
            return bits
        count = 0
        for i in range(bits - 1, -1, -1):
            if (value >> i) & 1 == 0:
                count += 1
            else:
                break
        return count

    def add(self, item: str) -> Result:
        """Add an item to the HyperLogLog sketch."""
        try:
            h = self._hash64(item)
            idx = h & (self.m - 1)
            w = h >> self.p
            rho = self._leading_zeros(w, 64 - self.p) + 1
            self.registers[idx] = max(self.registers[idx], rho)
            self._count += 1
            return Ok({"item": item, "register": idx, "rho": rho})
        except Exception as e:
            return Err(e)

    def estimate(self) -> Result:
        """Estimate the number of distinct items."""
        try:
            indicator = sum(2.0 ** (-r) for r in self.registers)
            raw_estimate = self._alpha * self.m * self.m / indicator

            # Small range correction
            if raw_estimate <= 2.5 * self.m:
                zeros = self.registers.count(0)
                if zeros > 0:
                    estimate = self.m * math.log(self.m / zeros)
                else:
                    estimate = raw_estimate
            elif raw_estimate <= (1 << 32) / 30.0:
                estimate = raw_estimate
            else:
                estimate = -(1 << 32) * math.log(1 - raw_estimate / (1 << 32))

            return Ok({"estimated_cardinality": int(round(estimate)), "raw_estimate": round(raw_estimate, 2),
                        "items_added": self._count, "registers": self.m, "precision": self.p,
                        "relative_error": round(1.04 / math.sqrt(self.m), 4)})
        except Exception as e:
            return Err(e)

    def diagnostics(self) -> Dict[str, Any]:
        return {"engine": "OmniHyperloglogEngine", "version": self.ENGINE_VERSION,
                "status": "operational", "precision": self.p, "registers": self.m}
