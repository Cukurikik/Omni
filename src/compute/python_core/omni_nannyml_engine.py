"""
OMNI NannyML Engine
===================
Production-grade OMNI engine mathematically simulating Data Drift tracking.
Inspired by NannyML/nannyml.

Features:
- Population Stability Index (PSI) distribution drift detection.
- Employs bounded probability math evaluating structural dataset drifts.
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


class NannyMLErr(Exception):
    pass


@dataclass(frozen=True)
class Ok:
    value: Any


@dataclass(frozen=True)
class Err:
    error: str


Result = Union[Ok, Err]


# ---------------------------------------------------------------------------
# 2. PSI DRIFT MATHEMATICS
# ---------------------------------------------------------------------------

class MathematicalDriftTracker:
    """Implement NannyML's exact functional calculations for PSI."""

    @staticmethod
    def calculate_psi(expected_dist: np.ndarray, actual_dist: np.ndarray, bins: int = 10) -> float:
        """
        Calculates Population Stability Index.
        Formula: sum( (Actual_freq - Expected_freq) * ln(Actual_freq / Expected_freq) )
        """
        # Determine strict bounds covering both distributions
        min_val = min(np.min(expected_dist), np.min(actual_dist))
        max_val = max(np.max(expected_dist), np.max(actual_dist))
        
        # Calculate histograms (bucket proportions/frequencies)
        expected_counts, _ = np.histogram(expected_dist, bins=bins, range=(min_val, max_val))
        actual_counts, _ = np.histogram(actual_dist, bins=bins, range=(min_val, max_val))
        
        # To percentages
        expected_percents = expected_counts / len(expected_dist)
        actual_percents = actual_counts / len(actual_dist)
        
        # Prevent division by zero and log(0) mathematically via epsilon padding
        epsilon = 0.0001
        expected_percents = np.where(expected_percents == 0, epsilon, expected_percents)
        actual_percents = np.where(actual_percents == 0, epsilon, actual_percents)
        
        # Iterative PSI formulation
        psi_sum = np.sum((actual_percents - expected_percents) * np.log(actual_percents / expected_percents))
        
        return float(psi_sum)


# ---------------------------------------------------------------------------
# 3. OMNI ENGINE CLASS
# ---------------------------------------------------------------------------

class OmniNannyMlEngine:
    """
    Production Engine mapping Data Drift & Performance Estimation mathematics.
    """
    VERSION = "1.0.0"
    ENGINE_ID = "omni-nannyml"

    def __init__(self) -> None:
        self._drift_calculations = 0

    def evaluate_model_drift(self, reference_data: List[float], production_data: List[float],
                             psi_threshold: float = 0.2, bins: int = 10) -> Result:
        """Process distributions returning theoretical Drift Alerts via PSI index."""
        if not reference_data or not production_data:
            return Err("Data payloads cannot be empty.")
            
        if bins <= 0:
            return Err("Evaluation bins must be strictly positive.")

        try:
            ref_arr = np.array(reference_data, dtype=np.float64)
            prod_arr = np.array(production_data, dtype=np.float64)
            
            psi_score = MathematicalDriftTracker.calculate_psi(ref_arr, prod_arr, bins=bins)
            
            # Rule of thumb for PSI:
            # < 0.1: No significant drift
            # 0.1 - 0.2: Moderate drift
            # >= 0.2: Significant drift (alerts)
            drift_detected = psi_score >= psi_threshold
            
            self._drift_calculations += 1
            
            return Ok({
                "psi_score": psi_score,
                "drift_detected": drift_detected,
                "threshold_applied": psi_threshold,
                "status": "critical_drift" if drift_detected else "stable"
            })
            
        except Exception as exc:
            return Err(f"Mathematical drift assessment failed: {exc}")

    def diagnostics(self) -> Dict[str, Any]:
        """Return engine diagnostics."""
        return {
            "engine_id": self.ENGINE_ID,
            "version": self.VERSION,
            "status": "operational",
            "evaluations_completed": self._drift_calculations,
            "features": [
                "population_stability_index_psi",
                "distribution_histogram_drift_tracking",
                "epsilon_padded_mathematical_validation",
            ]
        }
