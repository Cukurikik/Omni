"""
OMNI Machine Learning Complete Engine
=====================================
Production-grade OMNI engine for comprehensive classical mathematics.
Inspired by Nyandwi/machine_learning_complete.

Features:
- Pure NumPy primitive modeling (Logistic Regression).
- Complete data pipeline representations and Metrics grids (Precision/Recall).
- Mathematical derivatives mapped securely.

OMNI Layer: compute (Python)
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple, Union

import numpy as np

# ---------------------------------------------------------------------------
# 1. OMNI Result Monad
# ---------------------------------------------------------------------------


ENGINE_VERSION = "1.0.0-omni"

class MLCompleteErr(Exception):
    pass

@dataclass(frozen=True)
class Ok:
    """Monadic Ok result type."""
    value: Any

@dataclass(frozen=True)
class Err:
    """Monadic Err result type."""
    error: str

Result = Union[Ok, Err]


# ---------------------------------------------------------------------------
# 2. CLASSICAL ALGORITHMS & METRICS ABSTRACTION
# ---------------------------------------------------------------------------

class OmniLogisticRegression:
    """
    Mathematical primitive demonstrating Gradient Descent for binomial combinations.
    """
    def __init__(self, learning_rate: float = 0.01, iterations: int = 1000):
        """Initialize OmniLogisticRegression."""
        self.learning_rate = learning_rate
        self.iterations = iterations
        self.weights = None
        self.bias = None

    def _sigmoid(self, z: np.ndarray) -> np.ndarray:
        # np.clip to prevent extremely large exponentials
        return 1 / (1 + np.exp(-np.clip(z, -250, 250)))

    def fit(self, X: np.ndarray, y: np.ndarray) -> Result:
        """Fit OmniLogisticRegression to data."""
        try:
            if X.ndim != 2:
                return Err("X must be a 2D matrix.")
            
            n_samples, n_features = X.shape
            self.weights = np.zeros(n_features)
            self.bias = 0.0
            
            for _ in range(self.iterations):
                linear_model = np.dot(X, self.weights) + self.bias
                y_predicted = self._sigmoid(linear_model)
                
                # Calculus derivatives
                dw = (1 / n_samples) * np.dot(X.T, (y_predicted - y))
                db = (1 / n_samples) * np.sum(y_predicted - y)
                
                self.weights -= self.learning_rate * dw
                self.bias -= self.learning_rate * db
                
            return Ok(True)
        except Exception as e:
            return Err(f"Fitting algorithm crashed: {str(e)}")

    def predict(self, X: np.ndarray) -> Result:
        """Generate prediction for predict."""
        try:
            if self.weights is None:
                return Err("Model is not fitted prior to prediction.")
                
            linear_model = np.dot(X, self.weights) + self.bias
            y_predicted = self._sigmoid(linear_model)
            y_predicted_cls = [1 if i > 0.5 else 0 for i in y_predicted]
            return Ok(np.array(y_predicted_cls))
        except Exception as e:
            return Err(f"Prediction crashed: {str(e)}")


class OmniMetricsGrid:
    """Calculates Evaluation Metrics natively."""
    
    @staticmethod
    def classification_report(y_true: np.ndarray, y_pred: np.ndarray) -> Result:
        """Execute classification report operation for OmniMetricsGrid."""
        try:
            if len(y_true) != len(y_pred):
                return Err("Label arrays possess differing lengths.")
                
            tp = np.sum((y_true == 1) & (y_pred == 1))
            tn = np.sum((y_true == 0) & (y_pred == 0))
            fp = np.sum((y_true == 0) & (y_pred == 1))
            fn = np.sum((y_true == 1) & (y_pred == 0))
            
            # Avoid Division by Zero
            precision = tp / (tp + fp) if (tp + fp) else 0.0
            recall = tp / (tp + fn) if (tp + fn) else 0.0
            accuracy = (tp + tn) / len(y_true)
            
            f1_score = 2 * (precision * recall) / (precision + recall) if (precision + recall) else 0.0
            
            return Ok({
                "accuracy": accuracy,
                "precision": precision,
                "recall": recall,
                "f1_score": f1_score
            })
        except Exception as e:
            return Err(f"Metrics evaluation failed: {str(e)}")


# ---------------------------------------------------------------------------
# 3. OMNI ENGINE CLASS
# ---------------------------------------------------------------------------

class OmniMLCompleteEngine:
    """
    Production Engine binding native Classical Machine Learning operations stably.
    """

    def __init__(self, config=None):
        """Initialize OmniMLCompleteEngine."""
        self.config = config or {}
        self.engine_id = __import__("uuid").uuid4().hex
        self.is_active = True
    VERSION = "1.0.0"
    ENGINE_ID = "omni-ml-complete"

    def get_logistic_regression(self, lr: float = 0.01, iter: int = 1000) -> OmniLogisticRegression:
        """Performs get logistic regression operation for OmniMLCompleteEngine."""
        return OmniLogisticRegression(learning_rate=lr, iterations=iter)

    def get_metrics_grid(self) -> OmniMetricsGrid:
        """Performs get metrics grid operation for OmniMLCompleteEngine."""
        return OmniMetricsGrid()

    def diagnostics(self) -> Dict[str, Any]:
        """Performs diagnostics operation for OmniMLCompleteEngine."""
        return {
            "engine_id": self.ENGINE_ID,
            "version": self.VERSION,
            "capabilities": ["Native Logistic Gradient Descent", "Metrics Analysis"],
            "status": "operational",
        }
