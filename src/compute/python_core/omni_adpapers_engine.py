"""
OMNI Ad Papers Engine
=====================
Production-grade abstraction inspired by wzhe06/Ad-papers.
Implements Factorization Machine (FM) algorithm for Click-Through Rate (CTR)
predictions on highly sparse interaction vectors, zero-mocked in Numpy.

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

class AdPapersError(Exception):
    """Base error for Factorization Machine abstraction."""

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
# 2. FACTORIZATION MACHINE
# ---------------------------------------------------------------------------

class FactorizationMachine:
    """Models degree-2 pairwise feature interactions over latent factorization."""
    
    def __init__(self, k_latent: int = 4, learning_rate: float = 0.01):
        """Initialize FactorizationMachine."""
        self.k = k_latent
        self.lr = learning_rate
        self.w0 = 0.0
        self.W = np.array([])
        self.V = np.array([])
        
    def _sigmoid(self, x: np.ndarray) -> np.ndarray:
        # np.clip to prevent overflow
        x_safe = np.clip(x, -500, 500)
        return 1.0 / (1.0 + np.exp(-x_safe))
        
    def fit(self, X: np.ndarray, y: np.ndarray, epochs: int = 100) -> Result:
        """
        X: dense/numpy representation of sparse features (N x M)
        y: target labels 0 or 1
        """
        if X.ndim != 2:
            return Err("FM expects 2-Dimensional numeric observation matrix.")
        if y.ndim != 1:
            return Err("Target y must be a 1-Dimensional array.")
            
        N, M = X.shape
        if len(y) != N:
            return Err("Distribution mismatch between inputs and labels.")
            
        try:
            self.w0 = 0.0
            self.W = np.zeros(M)
            # Initialize latent vector factors stochastically
            self.V = np.random.normal(scale=0.1, size=(M, self.k))
            
            for _ in range(epochs):
                for i in range(N):
                    x_i = X[i]
                    y_i = y[i]
                    
                    # Compute interaction terms: sum(V_i * x_i)^2 - sum((V_i * x_i)^2)
                    inter_sum = np.dot(x_i, self.V)  # (k,)
                    inter_sq_sum = np.dot(x_i**2, self.V**2) # (k,)
                    
                    interaction = 0.5 * np.sum(inter_sum**2 - inter_sq_sum)
                    linear = self.w0 + np.dot(self.W, x_i)
                    
                    y_pred = self._sigmoid(np.array(linear + interaction))
                    
                    # Error for LogLoss (binary classification)
                    # For SGD: (y_pred - y)
                    loss_grad = float(y_pred - y_i)
                    
                    # Update parameters
                    self.w0 -= self.lr * loss_grad
                    self.W -= self.lr * loss_grad * x_i
                    
                    # Update Latent Factors V
                    for f in range(self.k):
                        # V_jf update: grad_V_jf = loss_grad * (x_j * sum(V_if x_i) - V_jf x_j^2)
                        v_grad = loss_grad * (x_i * inter_sum[f] - self.V[:, f] * (x_i**2))
                        self.V[:, f] -= self.lr * v_grad
            
            return Ok(True)
            
        except Exception as e:
            return Err(f"Algorithmic gradient destabilization: {e}")

    def predict(self, X: np.ndarray) -> Result:
        """Outputs CTR probability [0, 1]."""
        if self.W.size == 0 or self.V.size == 0:
            return Err("Model parameters are completely unfitted.")
            
        try:
            N = X.shape[0]
            preds = np.zeros(N)
            for i in range(N):
                x_i = X[i]
                inter_sum = np.dot(x_i, self.V)
                inter_sq_sum = np.dot(x_i**2, self.V**2)
                interaction = 0.5 * np.sum(inter_sum**2 - inter_sq_sum)
                linear = self.w0 + np.dot(self.W, x_i)
                preds[i] = self._sigmoid(np.array(linear + interaction))
                
            return Ok(preds)
        except Exception as e:
            return Err(f"CTR prediction extrapolation failed: {e}")


# ---------------------------------------------------------------------------
# 3. OMNI ENGINE CLASS
# ---------------------------------------------------------------------------

class OmniAdPapersEngine:
    """
    Production Engine for Click-Through Interaction Optimization.
    """

    def __init__(self, config=None):
        """Initialize OmniAdPapersEngine."""
        self.config = config or {}
        self.engine_id = __import__("uuid").uuid4().hex
        self.is_active = True
    VERSION = "1.0.0"
    ENGINE_ID = "omni-adpapers"

    def get_ctr_model(self, latent_dim: int = 4) -> FactorizationMachine:
        """Performs get ctr model operation for OmniAdPapersEngine."""
        return FactorizationMachine(k_latent=latent_dim)

    def diagnostics(self) -> Dict[str, Any]:
        """Performs diagnostics operation for OmniAdPapersEngine."""
        return {
            "engine_id": self.ENGINE_ID,
            "version": self.VERSION,
            "architecture": "Stochastic SGD Factorization Machine (Degree 2)",
            "status": "operational",
        }
