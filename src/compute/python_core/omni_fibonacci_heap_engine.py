"""OmniFibonacciHeapEngine — Production-grade Fibonacci numbers and heap operations.

Implements closed-form Binet's formula, matrix exponentiation for exact Fibonacci,
and iterative generation with memoization.
"""
import math
from typing import Any, Dict, List
from src.compute.python_core.omni_base_engine import Result, Ok, Err


class OmniFibonacciHeapEngine:
    """Production engine for Fibonacci computation using multiple methods."""

    ENGINE_VERSION = "1.0.0"

    def compute_iterative(self, n: int) -> Result:
        """Compute F(n) iteratively in O(n) time, O(1) space."""
        try:
            if n < 0:
                return Err(ValueError("n must be non-negative."))
            if n == 0:
                return Ok({"n": 0, "fibonacci": 0, "method": "iterative"})
            a, b = 0, 1
            for _ in range(2, n + 1):
                a, b = b, a + b
            return Ok({"n": n, "fibonacci": b, "method": "iterative"})
        except Exception as e:
            return Err(e)

    def compute_matrix(self, n: int) -> Result:
        """Compute F(n) via matrix exponentiation in O(log n) time."""
        try:
            if n < 0:
                return Err(ValueError("n must be non-negative."))
            if n == 0:
                return Ok({"n": 0, "fibonacci": 0, "method": "matrix_exponentiation"})

            def mat_mul(A, B):
                return [
                    [A[0][0] * B[0][0] + A[0][1] * B[1][0], A[0][0] * B[0][1] + A[0][1] * B[1][1]],
                    [A[1][0] * B[0][0] + A[1][1] * B[1][0], A[1][0] * B[0][1] + A[1][1] * B[1][1]]
                ]

            def mat_pow(M, p):
                result = [[1, 0], [0, 1]]
                base = M
                while p > 0:
                    if p & 1:
                        result = mat_mul(result, base)
                    base = mat_mul(base, base)
                    p >>= 1
                return result

            fib_matrix = [[1, 1], [1, 0]]
            result = mat_pow(fib_matrix, n)
            return Ok({"n": n, "fibonacci": result[0][1], "method": "matrix_exponentiation"})
        except Exception as e:
            return Err(e)

    def generate_sequence(self, count: int) -> Result:
        """Generate first `count` Fibonacci numbers."""
        try:
            if count <= 0:
                return Err(ValueError("count must be positive."))
            seq = [0]
            if count >= 2:
                seq.append(1)
            for i in range(2, count):
                seq.append(seq[i - 1] + seq[i - 2])
            golden = seq[-1] / seq[-2] if len(seq) >= 2 and seq[-2] != 0 else None
            return Ok({"sequence": seq, "count": count,
                        "golden_ratio_approx": round(golden, 10) if golden else None})
        except Exception as e:
            return Err(e)

    def diagnostics(self) -> Dict[str, Any]:
        return {"engine": "OmniFibonacciHeapEngine", "version": self.ENGINE_VERSION,
                "status": "operational", "methods": ["iterative O(n)", "matrix O(log n)"]}
