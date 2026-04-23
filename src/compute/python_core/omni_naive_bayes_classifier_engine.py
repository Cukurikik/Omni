"""OmniNaiveBayesClassifierEngine — Production-grade Naive Bayes classifier.

Implements Gaussian Naive Bayes from scratch using probability density functions,
prior computation, and MAP classification with log probabilities to avoid underflow.
"""
import math
from typing import Any, Dict, List
from src.compute.python_core.omni_base_engine import Result, Ok, Err


class OmniNaiveBayesClassifierEngine:
    """Production engine for Gaussian Naive Bayes classification."""

    ENGINE_VERSION = "1.0.0"

    def __init__(self):
        self._class_stats: Dict[Any, Dict] = {}
        self._priors: Dict[Any, float] = {}
        self._classes: List = []
        self._trained = False

    @staticmethod
    def _gaussian_pdf(x: float, mean: float, var: float) -> float:
        """Compute probability density of x under Gaussian(mean, var)."""
        if var < 1e-12:
            return 1.0 if abs(x - mean) < 1e-12 else 1e-300
        coeff = 1.0 / math.sqrt(2 * math.pi * var)
        exponent = -((x - mean) ** 2) / (2 * var)
        return coeff * math.exp(exponent)

    def fit(self, X: List[List[float]], y: List) -> Result:
        """
        Train Gaussian Naive Bayes on labeled data.

        Args:
            X: Feature matrix (list of feature vectors).
            y: Class labels.

        Returns:
            Result with class statistics and priors.
        """
        try:
            n = len(X)
            if n == 0:
                return Err(ValueError("Training data must be non-empty."))
            if n != len(y):
                return Err(ValueError("X and y must have equal length."))

            class_data: Dict[Any, List[List[float]]] = {}
            for xi, yi in zip(X, y):
                class_data.setdefault(yi, []).append(xi)

            self._classes = sorted(class_data.keys(), key=str)
            d = len(X[0])

            for cls in self._classes:
                samples = class_data[cls]
                self._priors[cls] = len(samples) / n
                stats = []
                for j in range(d):
                    col = [s[j] for s in samples]
                    mean = sum(col) / len(col)
                    var = sum((x - mean) ** 2 for x in col) / len(col)
                    stats.append({"mean": mean, "variance": var})
                self._class_stats[cls] = stats

            self._trained = True
            return Ok({"classes": self._classes, "priors": {str(k): round(v, 6) for k, v in self._priors.items()},
                        "n_samples": n, "n_features": d})
        except Exception as e:
            return Err(e)

    def predict(self, X: List[List[float]]) -> Result:
        """Predict class labels for feature vectors using MAP estimation."""
        try:
            if not self._trained:
                return Err(ValueError("Model not trained. Call fit() first."))

            predictions = []
            for xi in X:
                best_cls = None
                best_log_prob = float('-inf')
                for cls in self._classes:
                    log_prob = math.log(self._priors[cls])
                    for j, xj in enumerate(xi):
                        stats = self._class_stats[cls][j]
                        pdf = self._gaussian_pdf(xj, stats["mean"], stats["variance"])
                        log_prob += math.log(max(pdf, 1e-300))
                    if log_prob > best_log_prob:
                        best_log_prob = log_prob
                        best_cls = cls
                predictions.append(best_cls)

            return Ok({"predictions": predictions, "n_predicted": len(predictions)})
        except Exception as e:
            return Err(e)

    def diagnostics(self) -> Dict[str, Any]:
        return {"engine": "OmniNaiveBayesClassifierEngine", "version": self.ENGINE_VERSION,
                "status": "operational", "trained": self._trained,
                "complexity": "O(N*D*C) training, O(D*C) prediction"}
