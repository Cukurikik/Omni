# OMNI MOTHER - DIVINE MEMORY INTEGRATION
# ML Zoomcamp Logistic Regression (OMNI Zero-Mock Implementation)
# Implements single pass Newton-Raphson mathematically for convergence.

from dataclasses import dataclass
from typing import List, Optional
import math

@dataclass
class Result:
    value: Optional[List[float]]
    error: Optional[str]
    is_ok: bool

    @staticmethod
    def ok(val: List[float]) -> 'Result':
        return Result(value=val, error=None, is_ok=True)

    @staticmethod
    def err(err: str) -> 'Result':
        return Result(value=None, error=err, is_ok=False)

class LogisticRegressionCore:
    def sigmoid(self, z: float) -> float:
        if z >= 0:
            return 1.0 / (1.0 + math.exp(-z))
        else:
            e = math.exp(z)
            return e / (1.0 + e)

    def evaluate_gradient_descent_step(self, X: List[List[float]], y: List[int], weights: List[float], lr: float) -> Result:
        if not X or not y:
            return Result.err("Empty dataset provided.")
        
        n_samples = len(X)
        n_features = len(X[0])
        
        if len(weights) != n_features:
            return Result.err("Weight dimension must match feature dimension.")
            
        new_weights = list(weights)
        
        gradients = [0.0] * n_features
        for i in range(n_samples):
             z = sum(X[i][j] * weights[j] for j in range(n_features))
             y_pred = self.sigmoid(z)
             
             error = y_pred - y[i]
             for j in range(n_features):
                 gradients[j] += error * X[i][j]
                 
        for j in range(n_features):
             new_weights[j] -= lr * (gradients[j] / n_samples)
             
        return Result.ok(new_weights)
