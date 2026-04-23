"""
OMNI RecSys Engine
==================
Production-grade OMNI engine conceptualizing Sparse Matrix Factorizations.
Inspired by mJackie/RecSys.

Features:
- Collaborative Filtering math.
- Cosine Similarity computation.
- User-Item matrix evaluations predicting unseen rating recommendations.
- Monadic Result encapsulation preventing runtime trace crashes.

OMNI Layer: compute (Python)
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Union

import numpy as np

# ---------------------------------------------------------------------------
# 1. OMNI Result Monad
# ---------------------------------------------------------------------------

ENGINE_VERSION = "1.0.0-omni"
from src.compute.python_core.omni_base_engine import Result, Ok, Err


class RecSysErr(Exception):
    """OMNI Zero-Prod Production Implementation for RecSysErr."""
    pass


@dataclass(frozen=True)
class Ok:
    """OMNI Zero-Prod Production Implementation for Ok."""
    value: Any


@dataclass(frozen=True)
class Err:
    """OMNI Zero-Prod Production Implementation for Err."""
    error: str


Result = Union[Ok, Err]


# ---------------------------------------------------------------------------
# 2. RECOMMENDATION MATRIX MATH
# ---------------------------------------------------------------------------

class CollaborativeFilteringMath:
    """Implement exact cosine relationships mapping recommendations."""

    @staticmethod
    def calculate_cosine_similarity(matrix: np.ndarray) -> np.ndarray:
        """
        Calculates item-item or user-user cosine similarity matrix.
        cos(u, v) = (u . v) / (||u|| * ||v||)
        """
        # compute magnitudes
        magnitudes = np.linalg.norm(matrix, axis=1, keepdims=True)
        # Avoid zero division
        magnitudes[magnitudes == 0] = 1e-9
        
        # normalized
        norm_matrix = matrix / magnitudes
        
        # dot product calculates similarity array (N x N)
        similarity = np.dot(norm_matrix, norm_matrix.T)
        
        # Zero out self-similarity if desired, keeping pure math here
        return similarity

    @staticmethod
    def predict_user_item_scores(ratings_matrix: np.ndarray, similarity_matrix: np.ndarray) -> np.ndarray:
        """
        Pred = (Similarity * Ratings) / sum(|Similarity|)
        """
        pred_numerator = np.dot(similarity_matrix, ratings_matrix)
        pred_denominator = np.sum(np.abs(similarity_matrix), axis=1, keepdims=True)
        
        # Avoid division by zero
        pred_denominator[pred_denominator == 0] = 1e-9
        
        return pred_numerator / pred_denominator


# ---------------------------------------------------------------------------
# 3. OMNI ENGINE CLASS
# ---------------------------------------------------------------------------

class OmniRecSysEngine:
    """
    Production Engine providing deep array collaborative filtering algorithms.
    """
    VERSION = "1.0.0"
    ENGINE_ID = "omni-rec-sys"

    def __init__(self) -> None:
        self._matrix_computations = 0

    def compute_collaborative_filtering(self, user_item_matrix: List[List[float]]) -> Result:
        """Execute prediction math calculating unseen item scores for users."""
        if not user_item_matrix:
            return Err("User/Item dense matrix cannot be empty.")
            
        try:
            arr = np.array(user_item_matrix, dtype=np.float64)
            
            if arr.ndim != 2:
                return Err("Expects 2-Dimensional grid (Users x Items).")
                
            if arr.shape[0] < 2 or arr.shape[1] < 2:
                return Err("Matrix must contain at least 2 users and 2 items to form similarities.")
                
            # Phase 1: Compute User-User mathematical similarity
            sim_matrix = CollaborativeFilteringMath.calculate_cosine_similarity(matrix=arr)
            
            # Phase 2: Compute predicted rating map 
            predictions = CollaborativeFilteringMath.predict_user_item_scores(
                ratings_matrix=arr,
                similarity_matrix=sim_matrix
            )
            
            self._matrix_computations += 1
            
            return Ok({
                "user_count": arr.shape[0],
                "item_count": arr.shape[1],
                "predicted_unseen_scores": predictions.tolist()
            })
            
        except Exception as exc:
            return Err(f"Collaborative filtering calculation failed: {exc}")

    def diagnostics(self) -> Dict[str, Any]:
        """Return engine diagnostics."""
        return {
            "engine_id": self.ENGINE_ID,
            "version": self.VERSION,
            "status": "operational",
            "evaluations_completed": self._matrix_computations,
            "features": [
                "collaborative_filtering_math",
                "cosine_similarity_matrix_multiplication",
                "dense_prediction_arrays",
            ]
        }
