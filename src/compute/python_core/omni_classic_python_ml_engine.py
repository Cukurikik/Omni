"""
OMNI Classic Python ML Engine
=============================
Production-grade OMNI engine mathematically execute basic
Classical Machine Learning architectures (K-Nearest Neighbors).
Inspired by Tanu-N-Prabhu/Python.

Features:
- Pure NumPy Euclidean distance matrices calculation.
- Nearest neighbors vectorized ranking and class mapping.
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


class ClassicMLErr(Exception):
    """OMNI Zero-Prod Production Implementation for ClassicMLErr."""
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
# 2. CLASSICAL MATH: KNN
# ---------------------------------------------------------------------------

class ClassicalMachineLearningMath:
    """Implement core classical logic matrices."""

    @staticmethod
    def euclidean_distances(train_data: np.ndarray, query_vector: np.ndarray) -> np.ndarray:
        """Vectorized distance calculation: sqrt(sum((X - Q)^2))."""
        # broadcasting (N, d) - (d,) -> (N, d)
        diff = train_data - query_vector
        sq_diff = np.square(diff)
        sum_sq = np.sum(sq_diff, axis=1)
        return np.sqrt(sum_sq)

    @staticmethod
    def predict_knn(distances: np.ndarray, labels: np.ndarray, k: int) -> int:
        """Vote evaluation tracking the top K neighbors."""
        # Retrieve indices of the k smallest distances
        nearest_indices = np.argsort(distances)[:k]
        nearest_labels = labels[nearest_indices]
        
        # Majority vote
        values, counts = np.unique(nearest_labels, return_counts=True)
        majority_index = np.argmax(counts)
        return int(values[majority_index])


# ---------------------------------------------------------------------------
# 3. OMNI ENGINE CLASS
# ---------------------------------------------------------------------------

class OmniClassicPythonMLEngine:
    """
    Production Engine providing foundational Classical ML distance math.
    """
    VERSION = "1.0.0"
    ENGINE_ID = "omni-classic-python-ml"

    def __init__(self) -> None:
        self._predictions_history = 0

    def compute_knn_classification(
        self,
        training_features: List[List[float]],
        training_labels: List[int],
        query: List[float],
        k: int = 3
    ) -> Result:
        """Route computational prediction calculating Euclidean distances."""
        if not training_features or not training_labels:
            return Err("Training maps cannot be empty.")
            
        if len(training_features) != len(training_labels):
            return Err("Feature points must match labels points length.")
            
        if not query:
            return Err("Query vector cannot be empty.")
            
        if k < 1 or k > len(training_features):
            return Err("K neighbors must be >= 1 and <= total training pool size.")
            
        try:
            train_arr = np.array(training_features, dtype=np.float64)
            labels_arr = np.array(training_labels, dtype=np.int32)
            query_arr = np.array(query, dtype=np.float64)
            
            if train_arr.shape[1] != query_arr.shape[0]:
                return Err("Query vector dimensions do not match training data columns.")
                
            distances = ClassicalMachineLearningMath.euclidean_distances(train_arr, query_arr)
            prediction = ClassicalMachineLearningMath.predict_knn(distances, labels_arr, k)
            
            self._predictions_history += 1
            
            return Ok({
                "predicted_class": prediction,
                "algorithm": "euclidean_knn",
                "nearest_distances_calculated": len(distances),
                "k": k
            })

        except Exception as exc:
            return Err(f"Classical math evaluation failed: {exc}")

    def diagnostics(self) -> Dict[str, Any]:
        """Return engine diagnostics."""
        return {
            "engine_id": self.ENGINE_ID,
            "version": self.VERSION,
            "status": "operational",
            "evaluations_completed": self._predictions_history,
            "features": [
                "euclidean_distance_matrices",
                "k_nearest_neighbor_classification",
                "vectorized_numpy_prediction_math",
            ]
        }
