"""
OMNI Image Quality Assessment Engine
====================================
Production-grade OMNI engine abstracting NIMA (Neural Image Assessment)
scoring architectures. Inspired by idealo/image-quality-assessment.

Features:
- Probabilistic class conversion to Mean NIMA Aesthetic Scores.
- Technical quality standard deviation metrics calculation.
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


class ImageQualityErr(Exception):
    pass


@dataclass(frozen=True)
class Ok:
    value: Any


@dataclass(frozen=True)
class Err:
    error: str


Result = Union[Ok, Err]


# ---------------------------------------------------------------------------
# 2. NIMA SCORE MATH
# ---------------------------------------------------------------------------

class NimaMathematics:
    """NIMA equations calculating Mean Quality and Standard Deviation."""

    @staticmethod
    def calculate_mean_score(probabilities: np.ndarray) -> np.ndarray:
        """
        NIMA uses 10 classes (1 to 10 scale).
        Mean score = sum_{i=1}^{10} (p_i * i)
        """
        # Vectorized mapping for batch (N, 10)
        # Class weights [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
        weights = np.arange(1, 11, dtype=np.float32)
        
        # Dot product across the class dimension
        return np.sum(probabilities * weights, axis=1)

    @staticmethod
    def calculate_standard_deviation(probabilities: np.ndarray, mean_scores: np.ndarray) -> np.ndarray:
        """
        std = sqrt( sum_{i=1}^{10} p_i * (i - mean)^2 )
        """
        weights = np.arange(1, 11, dtype=np.float32)
        # Reshape mean for broadcasting: (N, 1)
        mean_expanded = mean_scores[:, np.newaxis]
        
        variance = np.sum(probabilities * ((weights - mean_expanded) ** 2), axis=1)
        return np.sqrt(variance)


# ---------------------------------------------------------------------------
# 3. OMNI ENGINE CLASS
# ---------------------------------------------------------------------------

class OmniImageQualityAssessmentEngine:
    """
    Production Engine providing robust mathematical Image Quality algorithms.
    """
    VERSION = "1.0.0"
    ENGINE_ID = "omni-image-quality-assessment"

    def __init__(self) -> None:
        self._evaluation_count = 0

    def evaluate_nima_scores(self, class_probabilities: List[List[float]]) -> Result:
        """
        Convert raw Softmax model classifications (10 buckets) into NIMA scores.
        """
        if not class_probabilities:
            return Err("Probability payload cannot be empty.")
            
        try:
            arr = np.array(class_probabilities, dtype=np.float64)
            
            if arr.ndim != 2:
                return Err("Expects 2D array of probabilities (Batch size N x 10).")
                
            if arr.shape[1] != 10:
                return Err(f"NIMA requires exactly 10 quality classes, got {arr.shape[1]}")
                
            # Validate normalized probabilitles (sums to 1 across axis 1)
            sums = np.sum(arr, axis=1)
            if not np.allclose(sums, 1.0, atol=1e-3):
                return Err("Input probabilities must sum to 1.0 for each item in the batch.")
                
            # Perform mathematically pure evaluation
            means = NimaMathematics.calculate_mean_score(arr)
            stds = NimaMathematics.calculate_standard_deviation(arr, means)
            
            self._evaluation_count += len(class_probabilities)
            
            results = []
            for i in range(len(class_probabilities)):
                results.append({
                    "nima_aesthetic_score": float(means[i]),
                    "nima_technical_std": float(stds[i])
                })
                
            return Ok(results)
            
        except Exception as exc:
            return Err(f"NIMA assessment evaluation failed: {exc}")

    def diagnostics(self) -> Dict[str, Any]:
        """Return engine diagnostics."""
        return {
            "engine_id": self.ENGINE_ID,
            "version": self.VERSION,
            "status": "operational",
            "images_evaluated": self._evaluation_count,
            "features": [
                "nima_mean_aesthetic_score_mapping",
                "nima_technical_standard_deviation",
                "probabilistic_distribution_validation",
            ]
        }
