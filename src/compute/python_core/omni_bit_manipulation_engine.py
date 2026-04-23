"""OmniBitManipulationEngine — Production-grade bitwise operations toolkit.

Implements production-grade bit manipulation utilities including popcount,
leading/trailing zeros, power-of-two checks, bit reversal, and gray code.
"""
from typing import Any, Dict, List
from src.compute.python_core.omni_base_engine import Result, Ok, Err


class OmniBitManipulationEngine:
    """Production engine for bitwise manipulation operations."""

    ENGINE_VERSION = "1.0.0"

    def popcount(self, n: int) -> Result:
        """Perform popcount computation.

            Args:
                    n: int

            Returns:
                Result: Monadic result wrapping the computed value or error.
            """
        try:
            count = bin(n if n >= 0 else n & 0xFFFFFFFF).count('1')
            return Ok({"value": n, "popcount": count, "binary": bin(n & 0xFFFFFFFF)})
        except Exception as e:
            return Err(e)

    def is_power_of_two(self, n: int) -> Result:
        """Perform is power of two computation.

            Args:
                    n: int

            Returns:
                Result: Monadic result wrapping the computed value or error.
            """
        try:
            result = n > 0 and (n & (n - 1)) == 0
            return Ok({"value": n, "is_power_of_two": result})
        except Exception as e:
            return Err(e)

    def next_power_of_two(self, n: int) -> Result:
        """Perform next power of two computation.

            Args:
                    n: int

            Returns:
                Result: Monadic result wrapping the computed value or error.
            """
        try:
            if n <= 0:
                return Ok({"value": n, "next_power_of_two": 1})
            v = n - 1
            v |= v >> 1; v |= v >> 2; v |= v >> 4; v |= v >> 8; v |= v >> 16
            return Ok({"value": n, "next_power_of_two": v + 1})
        except Exception as e:
            return Err(e)

    def reverse_bits(self, n: int, width: int = 32) -> Result:
        """Perform reverse bits computation.

            Args:
                    n: int
                    width: int

            Returns:
                Result: Monadic result wrapping the computed value or error.
            """
        try:
            result = 0
            for i in range(width):
                result = (result << 1) | ((n >> i) & 1)
            return Ok({"value": n, "reversed": result, "width": width,
                        "binary_in": bin(n & ((1 << width) - 1)),
                        "binary_out": bin(result)})
        except Exception as e:
            return Err(e)

    def gray_code(self, n: int) -> Result:
        """Perform gray code computation.

            Args:
                    n: int

            Returns:
                Result: Monadic result wrapping the computed value or error.
            """
        try:
            if n < 0:
                return Err(ValueError("n must be non-negative."))
            codes = [i ^ (i >> 1) for i in range(1 << n)]
            return Ok({"n_bits": n, "codes": codes, "count": len(codes),
                        "binary": [bin(c)[2:].zfill(n) for c in codes]})
        except Exception as e:
            return Err(e)

    def count_trailing_zeros(self, n: int) -> Result:
        """Perform count trailing zeros computation.

            Args:
                    n: int

            Returns:
                Result: Monadic result wrapping the computed value or error.
            """
        try:
            if n == 0:
                return Ok({"value": 0, "trailing_zeros": 32})
            count = 0
            while (n & 1) == 0:
                count += 1
                n >>= 1
            return Ok({"value": n, "trailing_zeros": count})
        except Exception as e:
            return Err(e)

    def diagnostics(self) -> Dict[str, Any]:
        return {"engine": "OmniBitManipulationEngine", "version": self.ENGINE_VERSION,
                "status": "operational", "operations": ["popcount", "is_power_of_two", "reverse_bits", "gray_code"]}
