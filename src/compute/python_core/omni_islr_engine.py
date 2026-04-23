"""
OMNI ISLR Engine
================
Production-grade abstraction inspired by JWarmenhoven/ISLR-python.
Implements core statistical learning algorithms directly in Numpy, focusing
on deterministic L2 Regularized Ridge Regression for causal feature bounds.

OMNI Layer: compute (Python)
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Union

import numpy as np


# ---------------------------------------------------------------------------
# 1. OMNI Result Monad
# ---------------------------------------------------------------------------


ENGINE_VERSION = "1.0.0-omni"
from src.compute.python_core.omni_base_engine import Result, Ok, Err

class ISLRError(Exception):
    """Base error for ISLR abstraction."""

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
# 2. STATISTICAL LEARNING (RIDGE REGRESSION)
# ---------------------------------------------------------------------------

class RidgeRegression:
    """Numpy-native L2 Penalized Linear Learning (beta estimator)."""
    
    def __init__(self, alpha: float = 1.0):
        """Initialize RidgeRegression."""
        self.alpha = alpha
        self.weights = np.array([])
        
    def fit(self, X: np.ndarray, y: np.ndarray) -> Result:
        """
        Executes analytic derivation: w = (X^T X + alpha*I)^{-1} X^T y
        """
        if X.ndim != 2:
            return Err("Input features X must be 2-Dimensional numpy array.")
        if y.ndim != 1:
            return Err("Target y must be a 1-Dimensional numpy array.")
            
        N, M = X.shape
        if len(y) != N:
            return Err("Feature inputs length and target inputs length distinctly disagree.")
            
        try:
            # Concatenate a column of ones for intercept
            X_bias = np.c_[np.ones(N), X]
            
            # Identity matrix for L2 penalty (exclude intercept from penalty)
            I_penalty = np.eye(M + 1)
            I_penalty[0, 0] = 0.0 # Do not penalize bias
            
            # (X^T * X + alpha * I)^-1 * X^T * Y
            inverse_term = np.linalg.pinv(X_bias.T.dot(X_bias) + self.alpha * I_penalty)
            w = inverse_term.dot(X_bias.T).dot(y)
            
            self.weights = w
            return Ok(True)
            
        except Exception as e:
            return Err(f"Eigen-decomposition inversion fault: {e}")

    def predict(self, X: np.ndarray) -> Result:
        """Generate prediction for predict."""
        if self.weights.size == 0:
            return Err("Ridge matrix model is completely uninitialized (requires fit).")
        if X.ndim != 2:
            return Err("Input features X must be 2-Dimensional numpy array.")
            
        try:
            N = X.shape[0]
            X_bias = np.c_[np.ones(N), X]
            
            predictions = X_bias.dot(self.weights)
            return Ok(predictions)
            
        except Exception as e:
            return Err(f"Inference synthesis failed: {e}")


# ---------------------------------------------------------------------------
# 3. OMNI ENGINE CLASS
# ---------------------------------------------------------------------------

class OmniISLREngine:
    """
    Production Engine for Classical Statistical Learning Vectors.
    """

    def __init__(self, config=None):
        """Initialize OmniISLREngine."""
        self.config = config or {}
        self.engine_id = __import__("uuid").uuid4().hex
        self.is_active = True
    VERSION = "1.0.0"
    ENGINE_ID = "omni-islr"

    def get_model(self, l2_penalty: float = 1.0) -> RidgeRegression:
        """Performs get model operation for OmniISLREngine."""
        return RidgeRegression(alpha=l2_penalty)

    def diagnostics(self) -> Dict[str, Any]:
        """Performs diagnostics operation for OmniISLREngine."""
        return {
            "engine_id": self.ENGINE_ID,
            "version": self.VERSION,
            "architecture": "Deterministic Analytic Ridge Extractor (L2)",
            "status": "operational",
        }
