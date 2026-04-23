"""OmniMarkovChainEngine — Production-grade Markov Chain simulation.

Implements discrete-time Markov chains with transition matrix validation,
stationary distribution computation via power iteration, and n-step
transition probability calculation.
"""
from typing import Any, Dict, List
from src.compute.python_core.omni_base_engine import Result, Ok, Err


class OmniMarkovChainEngine:
    """Production engine for discrete Markov chain analysis."""

    ENGINE_VERSION = "1.0.0"

    def validate_transition_matrix(self, matrix: List[List[float]]) -> Result:
        """Validate that matrix is a valid stochastic transition matrix."""
        try:
            n = len(matrix)
            if n == 0:
                return Err(ValueError("Matrix must be non-empty."))
            for i, row in enumerate(matrix):
                if len(row) != n:
                    return Err(ValueError(f"Row {i} has {len(row)} cols, expected {n}."))
                for j, val in enumerate(row):
                    if val < 0:
                        return Err(ValueError(f"Negative probability at [{i}][{j}]: {val}."))
                row_sum = sum(row)
                if abs(row_sum - 1.0) > 1e-6:
                    return Err(ValueError(f"Row {i} sums to {row_sum}, expected 1.0."))
            return Ok({"valid": True, "states": n})
        except Exception as e:
            return Err(e)

    def n_step_transition(self, matrix: List[List[float]], steps: int) -> Result:
        """Compute n-step transition matrix via matrix exponentiation."""
        try:
            v = self.validate_transition_matrix(matrix)
            if not v.is_ok():
                return v
            n = len(matrix)
            if steps < 0:
                return Err(ValueError("Steps must be non-negative."))

            # Initialize result as identity
            result = [[1.0 if i == j else 0.0 for j in range(n)] for i in range(n)]

            def mat_mul(A, B):
                sz = len(A)
                C = [[0.0] * sz for _ in range(sz)]
                for i in range(sz):
                    for k in range(sz):
                        if A[i][k] == 0:
                            continue
                        for j in range(sz):
                            C[i][j] += A[i][k] * B[k][j]
                return C

            base = [row[:] for row in matrix]
            s = steps
            while s > 0:
                if s & 1:
                    result = mat_mul(result, base)
                base = mat_mul(base, base)
                s >>= 1

            return Ok({"transition_matrix": [[round(v, 10) for v in row] for row in result],
                        "steps": steps, "states": n})
        except Exception as e:
            return Err(e)

    def stationary_distribution(self, matrix: List[List[float]], max_iter: int = 1000, tol: float = 1e-10) -> Result:
        """Compute stationary distribution via power iteration."""
        try:
            v = self.validate_transition_matrix(matrix)
            if not v.is_ok():
                return v
            n = len(matrix)
            pi = [1.0 / n] * n

            for it in range(max_iter):
                new_pi = [0.0] * n
                for j in range(n):
                    for i in range(n):
                        new_pi[j] += pi[i] * matrix[i][j]
                diff = sum(abs(new_pi[i] - pi[i]) for i in range(n))
                pi = new_pi
                if diff < tol:
                    return Ok({"distribution": [round(p, 10) for p in pi], "converged": True,
                                "iterations": it + 1, "states": n})
            return Ok({"distribution": [round(p, 10) for p in pi], "converged": False,
                        "iterations": max_iter, "states": n})
        except Exception as e:
            return Err(e)

    def diagnostics(self) -> Dict[str, Any]:
        return {"engine": "OmniMarkovChainEngine", "version": self.ENGINE_VERSION,
                "status": "operational", "complexity": "O(N³ log S) matrix exponentiation"}
