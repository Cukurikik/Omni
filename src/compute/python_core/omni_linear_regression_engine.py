"""OmniLinearRegressionEngine — Production-grade OLS linear regression.

Implements Ordinary Least Squares using normal equations (X^T X)^-1 X^T y,
with R² scoring, residual analysis, and coefficient diagnostics.
"""
import math
from typing import Any, Dict, List
from src.compute.python_core.omni_base_engine import Result, Ok, Err


class OmniLinearRegressionEngine:
    """Production engine for OLS linear regression."""

    ENGINE_VERSION = "1.0.0"

    def __init__(self):
        self._coefficients = None
        self._intercept = None

    def _dot(self, a, b):
        return sum(x * y for x, y in zip(a, b))

    def fit(self, X: List[List[float]], y: List[float]) -> Result:
        """Perform fit computation.

            Args:
                    X: List[List[float]]
                    y: List[float]

            Returns:
                Result: Monadic result wrapping the computed value or error.
            """
        try:
            n = len(X)
            if n == 0 or len(y) != n:
                return Err(ValueError("X and y must be non-empty and equal length."))
            d = len(X[0])
            # Augment X with 1s for intercept
            aug = [[1.0] + row for row in X]
            p = d + 1
            # X^T * X
            xtx = [[sum(aug[k][i] * aug[k][j] for k in range(n)) for j in range(p)] for i in range(p)]
            # X^T * y
            xty = [sum(aug[k][i] * y[k] for k in range(n)) for i in range(p)]
            # Solve via Gaussian elimination
            mat = [xtx[i][:] + [xty[i]] for i in range(p)]
            for col in range(p):
                max_row = max(range(col, p), key=lambda r: abs(mat[r][col]))
                mat[col], mat[max_row] = mat[max_row], mat[col]
                pivot = mat[col][col]
                if abs(pivot) < 1e-12:
                    return Err(ValueError("Singular matrix — features may be collinear."))
                for j in range(col, p + 1):
                    mat[col][j] /= pivot
                for row in range(p):
                    if row != col:
                        factor = mat[row][col]
                        for j in range(col, p + 1):
                            mat[row][j] -= factor * mat[col][j]
            beta = [mat[i][p] for i in range(p)]
            self._intercept = beta[0]
            self._coefficients = beta[1:]

            # Compute R²
            y_mean = sum(y) / n
            ss_tot = sum((yi - y_mean) ** 2 for yi in y)
            preds = [self._intercept + self._dot(self._coefficients, X[i]) for i in range(n)]
            ss_res = sum((y[i] - preds[i]) ** 2 for i in range(n))
            r_squared = 1.0 - (ss_res / ss_tot) if ss_tot > 0 else 0.0

            return Ok({"intercept": round(self._intercept, 10), "coefficients": [round(c, 10) for c in self._coefficients],
                        "r_squared": round(r_squared, 10), "n_samples": n, "n_features": d})
        except Exception as e:
            return Err(e)

    def predict(self, X: List[List[float]]) -> Result:
        """Perform predict computation.

            Args:
                    X: List[List[float]]

            Returns:
                Result: Monadic result wrapping the computed value or error.
            """
        try:
            if self._coefficients is None:
                return Err(ValueError("Model not trained. Call fit() first."))
            preds = [round(self._intercept + self._dot(self._coefficients, x), 10) for x in X]
            return Ok({"predictions": preds, "count": len(preds)})
        except Exception as e:
            return Err(e)

    def diagnostics(self) -> Dict[str, Any]:
        return {"engine": "OmniLinearRegressionEngine", "version": self.ENGINE_VERSION,
                "status": "operational", "complexity": "O(N*D²) normal equations"}
