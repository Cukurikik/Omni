"""
OMNI LightFM Engine
===================
Production-grade pure NumPy abstraction inspired by lyst/lightfm.
Implements Matrix Factorization via Stochastic Gradient Descent (SGD)
with Latent Factors to model User-Item recommendations avoiding hard deps.

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

class LightFMError(Exception):
    """Base error for LightFM engine."""

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
# 2. MATRIX FACTORIZATION & SGD
# ---------------------------------------------------------------------------

class MatrixFactorization:
    """
    Standard Latent Factor model optimized with SGD using NumPy.
    Models interaction matrix R as dot product of User factors (P) and Item factors (Q).
    """

    def __init__(self, num_factors: int = 10, learning_rate: float = 0.01, regularization: float = 0.02):
        """Initialize MatrixFactorization."""
        self.num_factors = num_factors
        self.learning_rate = learning_rate
        self.regularization = regularization
        
        self.num_users: int = 0
        self.num_items: int = 0
        
        self.user_factors: Optional[np.ndarray] = None
        self.item_factors: Optional[np.ndarray] = None
        self.user_biases: Optional[np.ndarray] = None
        self.item_biases: Optional[np.ndarray] = None
        self.global_bias: float = 0.0
        
    def fit(self, interactions_matrix: np.ndarray, epochs: int = 10) -> Result:
        """
        Fits the latent factor model on a 2D interaction matrix 
        (users rows, items columns, values interaction weight/rating).
        Treats 0 as missing.
        """
        if interactions_matrix.ndim != 2:
            return Err("Interactions matrix must be 2-dimensional.")
            
        self.num_users, self.num_items = interactions_matrix.shape
        
        # Initialization
        # Normal distribution centered at 0 with 0.1 std
        self.user_factors = np.random.normal(0, 0.1, (self.num_users, self.num_factors))
        self.item_factors = np.random.normal(0, 0.1, (self.num_items, self.num_factors))
        self.user_biases = np.zeros(self.num_users)
        self.item_biases = np.zeros(self.num_items)
        
        # Get global bias from non-zero entries
        non_zero = interactions_matrix[interactions_matrix > 0]
        self.global_bias = np.mean(non_zero) if len(non_zero) > 0 else 0.0
        
        # Get non-zero indices for training (i, j)
        i_indices, j_indices = interactions_matrix.nonzero()
        
        if len(i_indices) == 0:
            return Err("Interaction matrix is completely empty (no non-zero elements).")

        # SGD Optimization Loop
        for epoch in range(epochs):
            # Shuffle indices
            p = np.random.permutation(len(i_indices))
            i_indices_shuffled = i_indices[p]
            j_indices_shuffled = j_indices[p]
            
            for index in range(len(i_indices)):
                i = i_indices_shuffled[index]
                j = j_indices_shuffled[index]
                
                # True value
                r_ij = float(interactions_matrix[i, j])
                
                # Predict
                prediction = self._predict_single(i, j)
                
                # Error
                e_ij = r_ij - prediction
                
                # Update Biases
                self.user_biases[i] += self.learning_rate * (e_ij - self.regularization * self.user_biases[i])
                self.item_biases[j] += self.learning_rate * (e_ij - self.regularization * self.item_biases[j])
                
                # Update Latent Factors
                p_i = self.user_factors[i, :].copy() # keep old state
                q_j = self.item_factors[j, :].copy()
                
                self.user_factors[i, :] += self.learning_rate * (e_ij * q_j - self.regularization * p_i)
                self.item_factors[j, :] += self.learning_rate * (e_ij * p_i - self.regularization * q_j)
                
        return Ok(True)

    def _predict_single(self, u: int, i: int) -> float:
        """Internal helper for SGD prediction scalar."""
        if self.user_biases is None or self.item_factors is None:
            return 0.0
        prediction = self.global_bias + self.user_biases[u] + self.item_biases[i]
        prediction += np.dot(self.user_factors[u, :], self.item_factors[i, :])
        return prediction

    def predict(self, user_indices: np.ndarray, item_indices: np.ndarray) -> Result:
        """Vectorized prediction for arrays of user and item indices."""
        if self.user_factors is None or self.item_factors is None:
            return Err("Model is not fitted. Cannot predict.")
            
        if user_indices.shape != item_indices.shape:
            return Err("user_indices and item_indices must have the same shape.")
            
        try:
            u_b = self.user_biases[user_indices]
            i_b = self.item_biases[item_indices]
            
            u_f = self.user_factors[user_indices]
            i_f = self.item_factors[item_indices]
            
            dot_products = np.sum(u_f * i_f, axis=1)
            
            predictions = self.global_bias + u_b + i_b + dot_products
            return Ok(predictions)
        except IndexError:
            return Err("Indices out of bounds for the fitted model size.")

    def recommend_for_user(self, user_id: int, top_k: int = 5) -> Result:
        """Recommends top K items for a specific user."""
        if self.user_factors is None or self.item_factors is None:
            return Err("Model is not fitted. Cannot predict.")
            
        if user_id < 0 or user_id >= self.num_users:
            return Err(f"User ID {user_id} is out of bounds.")
            
        # Predict score for ALL items for this user
        item_indices = np.arange(self.num_items)
        user_array = np.full(self.num_items, fill_value=user_id)
        
        res = self.predict(user_array, item_indices)
        if isinstance(res, Err):
            return res
            
        scores: np.ndarray = res.value
        
        # Get Top-K arguments
        # Using argsort (ascending), so we take [-top_k:] and reverse it
        top_indices = np.argsort(scores)[-top_k:][::-1]
        
        # Explicit bounds check not strictly needed because argsort bounds are safe,
        # but just map scores and return
        recommendations = [(int(idx), float(scores[idx])) for idx in top_indices]
        return Ok(recommendations)


# ---------------------------------------------------------------------------
# 3. OMNI ENGINE CLASS
# ---------------------------------------------------------------------------

class OmniLightFMEngine:
    """
    Production Engine for Matrix Factorization Recommender Systems.
    """

    def __init__(self, config=None):
        """Initialize OmniLightFMEngine."""
        self.config = config or {}
        self.engine_id = __import__("uuid").uuid4().hex
        self.is_active = True
    VERSION = "1.0.0"
    ENGINE_ID = "omni-lightfm"

    def create_model(self, num_factors: int = 10) -> MatrixFactorization:
        """Performs create model operation for OmniLightFMEngine."""
        return MatrixFactorization(num_factors=num_factors)

    def diagnostics(self) -> Dict[str, Any]:
        """Performs diagnostics operation for OmniLightFMEngine."""
        return {
            "engine_id": self.ENGINE_ID,
            "version": self.VERSION,
            "algorithms": ["MatrixFactorizationSGD"],
            "status": "operational",
        }
