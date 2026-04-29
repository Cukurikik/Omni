import numpy as np

# OMNI Python Compute Layer: EconML Double Machine Learning
# Hardcore matrix-based Double Machine Learning (DML) for estimating Average Treatment Effects (ATE).
# Extracted from ALICE EconML econometric methodology.

class DoubleMachineLearning:
    def __init__(self, alpha: float = 1e-4):
        self.alpha = alpha  # Ridge regularization parameter

    def _ridge_regression(self, X: np.ndarray, y: np.ndarray) -> np.ndarray:
        """
        Matrix resolution for Ridge Regression: w = (X^T X + alpha I)^-1 X^T y
        """
        n, m = X.shape
        I = np.eye(m)
        
        try:
            # Cholesky solver for numeric stability in large systems
            A = np.dot(X.T, X) + self.alpha * I
            b = np.dot(X.T, y)
            L = np.linalg.cholesky(A)
            z = np.linalg.solve(L, b)
            w = np.linalg.solve(L.T, z)
            return w
        except np.linalg.LinAlgError:
            # Fallback to pseudo-inverse
            return np.dot(np.linalg.pinv(np.dot(X.T, X) + self.alpha * I), np.dot(X.T, y))

    def fit_estimate(self, Y: np.ndarray, T: np.ndarray, X: np.ndarray) -> float:
        """
        Estimates the causal effect of T on Y, controlling for covariates X.
        Y: Outcomes [N]
        T: Treatments [N]
        X: Covariates [N, features]
        """
        if len(Y) != len(T) or len(Y) != len(X):
            raise ValueError("Dimensions of Y, T, and X must match.")

        # Stage 1: Partialling out X from Y (E[Y|X])
        w_Y = self._ridge_regression(X, Y)
        Y_res = Y - np.dot(X, w_Y)

        # Stage 2: Partialling out X from T (E[T|X])
        w_T = self._ridge_regression(X, T)
        T_res = T - np.dot(X, w_T)

        # Stage 3: Estimate Average Treatment Effect (ATE)
        # theta = (T_res^T * T_res)^-1 * T_res^T * Y_res
        denominator = np.dot(T_res.T, T_res)
        
        if denominator == 0:
            return 0.0
            
        ate = np.dot(T_res.T, Y_res) / denominator
        
        return float(ate)

def run_experiment(outcomes: np.ndarray, treatments: np.ndarray, covariates: np.ndarray) -> dict:
    dml = DoubleMachineLearning(alpha=0.01)
    ate = dml.fit_estimate(outcomes, treatments, covariates)
    return {"average_treatment_effect": ate, "status": "success"}
