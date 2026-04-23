"""OmniStatsmodelsLinearRegressionEngine — Production-grade OLS linear regression.

Implements Ordinary Least Squares regression using the Normal Equations
β̂ = (XᵀX)⁻¹Xᵀy with pure-Python matrix operations. Computes coefficients,
R², residuals, and standard errors without external numerical libraries.
"""
import math
from typing import Any, Dict, List, Tuple
from src.compute.python_core.omni_base_engine import Result, Ok, Err


class OmniStatsmodelsLinearRegressionEngine:
    """Production engine for OLS linear regression via Normal Equations."""

    ENGINE_VERSION = "1.0.0"

    def __init__(self, add_intercept: bool = True):
        """
        Initialize regression engine.

        Args:
            add_intercept: Whether to prepend a column of 1s to the design matrix.
        """
        self.add_intercept = add_intercept

    @staticmethod
    def _transpose(M: List[List[float]]) -> List[List[float]]:
        """Transpose a matrix represented as list of lists."""
        return [list(row) for row in zip(*M)]

    @staticmethod
    def _mat_mul(A: List[List[float]], B: List[List[float]]) -> List[List[float]]:
        """Multiply two matrices A (m×n) × B (n×p) = C (m×p)."""
        rows_a, cols_b = len(A), len(B[0])
        cols_a = len(A[0])
        result = [[0.0] * cols_b for _ in range(rows_a)]
        for i in range(rows_a):
            for j in range(cols_b):
                s = 0.0
                for k in range(cols_a):
                    s += A[i][k] * B[k][j]
                result[i][j] = s
        return result

    @staticmethod
    def _mat_vec_mul(A: List[List[float]], v: List[float]) -> List[float]:
        """Multiply matrix A (m×n) by column vector v (n) -> result (m)."""
        return [sum(A[i][j] * v[j] for j in range(len(v))) for i in range(len(A))]

    @staticmethod
    def _invert_2x2(M: List[List[float]]) -> List[List[float]]:
        """Invert a 2×2 matrix."""
        det = M[0][0] * M[1][1] - M[0][1] * M[1][0]
        if abs(det) < 1e-15:
            raise ValueError("Matrix is singular (det ≈ 0).")
        inv_det = 1.0 / det
        return [
            [M[1][1] * inv_det, -M[0][1] * inv_det],
            [-M[1][0] * inv_det, M[0][0] * inv_det],
        ]

    @staticmethod
    def _invert_matrix(M: List[List[float]]) -> List[List[float]]:
        """Invert a square matrix via Gauss-Jordan elimination."""
        n = len(M)
        # Augment with identity
        aug = [row[:] + [1.0 if i == j else 0.0 for j in range(n)] for i, row in enumerate(M)]

        for col in range(n):
            # Partial pivot
            max_row = col
            for row in range(col + 1, n):
                if abs(aug[row][col]) > abs(aug[max_row][col]):
                    max_row = row
            aug[col], aug[max_row] = aug[max_row], aug[col]

            if abs(aug[col][col]) < 1e-15:
                raise ValueError("Matrix is singular or near-singular.")

            pivot = aug[col][col]
            aug[col] = [x / pivot for x in aug[col]]

            for row in range(n):
                if row != col:
                    factor = aug[row][col]
                    aug[row] = [aug[row][j] - factor * aug[col][j] for j in range(2 * n)]

        return [row[n:] for row in aug]

    def fit(self, X: List[List[float]], y: List[float]) -> Result:
        """
        Fit OLS regression model using the Normal Equations: β̂ = (XᵀX)⁻¹Xᵀy.

        Args:
            X: Feature matrix (n_samples × n_features).
            y: Target vector (n_samples).

        Returns:
            Result with coefficients, R², residuals, and standard errors.
        """
        try:
            if not X or not y:
                return Err(ValueError("X and y must be non-empty."))
            if len(X) != len(y):
                return Err(ValueError("X and y must have same number of rows."))

            n = len(X)
            # Add intercept column if requested
            if self.add_intercept:
                X_design = [[1.0] + row for row in X]
            else:
                X_design = [row[:] for row in X]

            p = len(X_design[0])  # number of parameters
            if n <= p:
                return Err(ValueError(f"Insufficient samples ({n}) for {p} parameters."))

            # XᵀX
            Xt = self._transpose(X_design)
            XtX = self._mat_mul(Xt, X_design)

            # (XᵀX)⁻¹
            XtX_inv = self._invert_matrix(XtX)

            # Xᵀy
            Xty_flat = [sum(Xt[i][j] * y[j] for j in range(n)) for i in range(p)]

            # β̂ = (XᵀX)⁻¹ Xᵀy
            coefficients = self._mat_vec_mul(XtX_inv, Xty_flat)

            # Predictions and residuals
            y_pred = [sum(X_design[i][j] * coefficients[j] for j in range(p)) for i in range(n)]
            residuals = [y[i] - y_pred[i] for i in range(n)]

            # R² = 1 - SS_res / SS_tot
            y_mean = sum(y) / n
            ss_res = sum(r ** 2 for r in residuals)
            ss_tot = sum((yi - y_mean) ** 2 for yi in y)
            r_squared = 1.0 - (ss_res / ss_tot) if ss_tot > 1e-15 else 0.0

            # Standard error of coefficients: sqrt(diag(σ² (XᵀX)⁻¹))
            mse = ss_res / (n - p) if n > p else 0.0
            std_errors = [math.sqrt(max(0, mse * XtX_inv[j][j])) for j in range(p)]

            return Ok({
                "coefficients": [round(c, 10) for c in coefficients],
                "r_squared": round(r_squared, 10),
                "residual_sum_of_squares": round(ss_res, 10),
                "total_sum_of_squares": round(ss_tot, 10),
                "mean_squared_error": round(mse, 10),
                "standard_errors": [round(se, 10) for se in std_errors],
                "n_samples": n,
                "n_parameters": p,
                "has_intercept": self.add_intercept,
            })

        except Exception as e:
            return Err(e)

    def diagnostics(self) -> Dict[str, Any]:
        """Provides engine operational status and metadata."""
        return {
            "engine": "OmniStatsmodelsLinearRegressionEngine",
            "version": self.ENGINE_VERSION,
            "status": "operational",
            "add_intercept": self.add_intercept,
            "complexity": "O(p² * N + p³) OLS via Normal Equations with Gauss-Jordan inversion",
        }
