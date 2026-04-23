"""OmniMatrixDecompositionEngine — Production-grade matrix decomposition (LU).

Implements LU decomposition with partial pivoting (Doolittle's method),
determinant computation, and forward/backward substitution for solving Ax=b.
"""
from typing import Any, Dict, List, Optional
from src.compute.python_core.omni_base_engine import Result, Ok, Err


class OmniMatrixDecompositionEngine:
    """Production engine for LU matrix decomposition."""

    ENGINE_VERSION = "1.0.0"

    def lu_decompose(self, matrix: List[List[float]]) -> Result:
        """
        Compute LU decomposition with partial pivoting.

        Returns L, U, P such that PA = LU.
        """
        try:
            n = len(matrix)
            if n == 0:
                return Err(ValueError("Matrix must be non-empty."))
            for row in matrix:
                if len(row) != n:
                    return Err(ValueError("Matrix must be square."))

            A = [row[:] for row in matrix]
            L = [[0.0] * n for _ in range(n)]
            P = list(range(n))

            for k in range(n):
                # Partial pivoting
                max_val = abs(A[k][k])
                max_idx = k
                for i in range(k + 1, n):
                    if abs(A[i][k]) > max_val:
                        max_val = abs(A[i][k])
                        max_idx = i
                if max_val < 1e-15:
                    return Err(ValueError("Matrix is singular (or near-singular)."))
                if max_idx != k:
                    A[k], A[max_idx] = A[max_idx], A[k]
                    L[k], L[max_idx] = L[max_idx], L[k]
                    P[k], P[max_idx] = P[max_idx], P[k]

                for i in range(k + 1, n):
                    L[i][k] = A[i][k] / A[k][k]
                    for j in range(k, n):
                        A[i][j] -= L[i][k] * A[k][j]

            for i in range(n):
                L[i][i] = 1.0
            U = A

            return Ok({"L": [[round(v, 10) for v in row] for row in L],
                        "U": [[round(v, 10) for v in row] for row in U],
                        "P": P, "n": n})
        except Exception as e:
            return Err(e)

    def determinant(self, matrix: List[List[float]]) -> Result:
        """Compute determinant via LU decomposition."""
        try:
            res = self.lu_decompose(matrix)
            if not res.is_ok():
                return res
            U = res.value["U"]
            P = res.value["P"]
            n = res.value["n"]
            det = 1.0
            for i in range(n):
                det *= U[i][i]
            # Count swaps in permutation
            swaps = 0
            visited = [False] * n
            for i in range(n):
                if not visited[i]:
                    j = i
                    cycle_len = 0
                    while not visited[j]:
                        visited[j] = True
                        j = P[j]
                        cycle_len += 1
                    swaps += cycle_len - 1
            if swaps % 2 == 1:
                det = -det
            return Ok({"determinant": round(det, 10), "n": n})
        except Exception as e:
            return Err(e)

    def solve(self, matrix: List[List[float]], b: List[float]) -> Result:
        """Solve Ax = b using LU decomposition."""
        try:
            n = len(matrix)
            if len(b) != n:
                return Err(ValueError("b length must match matrix dimension."))
            res = self.lu_decompose(matrix)
            if not res.is_ok():
                return res
            L, U, P = res.value["L"], res.value["U"], res.value["P"]

            # Apply permutation to b
            pb = [b[P[i]] for i in range(n)]

            # Forward substitution: Ly = Pb
            y = [0.0] * n
            for i in range(n):
                y[i] = pb[i] - sum(L[i][j] * y[j] for j in range(i))

            # Backward substitution: Ux = y
            x = [0.0] * n
            for i in range(n - 1, -1, -1):
                x[i] = (y[i] - sum(U[i][j] * x[j] for j in range(i + 1, n))) / U[i][i]

            return Ok({"solution": [round(v, 10) for v in x], "n": n})
        except Exception as e:
            return Err(e)

    def diagnostics(self) -> Dict[str, Any]:
        return {"engine": "OmniMatrixDecompositionEngine", "version": self.ENGINE_VERSION,
                "status": "operational", "complexity": "O(N³) Doolittle LU with partial pivoting"}
