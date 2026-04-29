# OMNI MOTHER - DIVINE MEMORY INTEGRATION
# Jack Cherish Machine Learning (OMNI Zero-Mock Implementation)
# Implements Support Vector Machine (SVM) Soft-Margin objective calculator.

from dataclasses import dataclass
from typing import List, Optional

@dataclass
class Result:
    value: Optional[float] # Computed loss objective
    error: Optional[str]
    is_ok: bool

    @staticmethod
    def ok(val: float) -> 'Result':
        return Result(value=val, error=None, is_ok=True)

    @staticmethod
    def err(err: str) -> 'Result':
        return Result(value=None, error=err, is_ok=False)

class SVMObjectiveEngine:
    def _dot(self, w: List[float], x: List[float]) -> float:
        return sum(wi * xi for wi, xi in zip(w, x))

    def calculate_hinge_loss(self, X: List[List[float]], y: List[int], w: List[float], b: float, C: float) -> Result:
        """
        y must be in {-1, 1}
        Objective: 0.5 * ||w||^2 + C * sum(max(0, 1 - y_i * (w^T * x_i + b)))
        """
        if not X or not y:
            return Result.err("Data arrays cannot be empty.")
            
        if len(X) != len(y):
            return Result.err("Data and label dimension mismatch.")
            
        if len(X[0]) != len(w):
            return Result.err("Feature vector and weight dimension mismatch.")
            
        for label in y:
            if label not in [-1, 1]:
                 return Result.err("Labels must be strictly -1 or 1 for Binary SVM.")
                 
        regularization = 0.5 * sum(wi * wi for wi in w)
        
        hinge_loss_sum = 0.0
        for i in range(len(X)):
             margin = y[i] * (self._dot(w, X[i]) + b)
             loss_i = max(0.0, 1.0 - margin)
             hinge_loss_sum += loss_i
             
        objective = regularization + (C * hinge_loss_sum)
        
        return Result.ok(objective)
