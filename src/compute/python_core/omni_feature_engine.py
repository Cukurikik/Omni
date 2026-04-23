"""
OMNI Feature Engine
===================
Production-grade OMNI engine abstracting data matrix transformations.
Inspired by feature-engine/feature_engine.

Features:
- Pure numeric imputation algorithms (Mean, Median, Zero).
- Pure numeric Discretization (Equal width binning).
- Matrix-level array transformations ensuring pure computational state.
- Monadic Result encapsulation preventing runtime trace crashes.

OMNI Layer: compute (Python)
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Any, Dict, List, Union

import numpy as np

# ---------------------------------------------------------------------------
# 1. OMNI Result Monad
# ---------------------------------------------------------------------------

ENGINE_VERSION = "1.0.0-omni"
from src.compute.python_core.omni_base_engine import Result, Ok, Err


class FeatureEngineErr(Exception):
    """OMNI Engine class: FeatureEngineErr."""

    def __init__(self, code="UNKNOWN", message=""):
        """Initialize FeatureEngineErr."""
        self.code = code
        self.message = message

    def diagnostics(self):
        """Return error class diagnostics."""
        return {
            "engine": "FeatureEngineErr",
            "status": "error-type",
            "version": "1.0.0",
        }
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
# 2. TRANSFORMERS (PURE FUNCTIONS)
# ---------------------------------------------------------------------------

class MatrixTransformers:
    """OMNI Zero-Prod Production Implementation for MatrixTransformers."""
    
    @staticmethod
    def impute_missing(data: np.ndarray, strategy: str = "mean") -> np.ndarray:
        """Replace np.nan in a 1D array based on strategy."""
        arr = np.copy(data)
        mask = np.isnan(arr)
        
        if not np.any(mask):
            return arr
            
        valid_data = arr[~mask]
        
        if strategy == "mean":
            val = np.mean(valid_data) if len(valid_data) > 0 else 0.0
        elif strategy == "median":
            val = np.median(valid_data) if len(valid_data) > 0 else 0.0
        elif strategy == "zero":
            val = 0.0
        else:
            val = 0.0 # Fallback
            
        arr[mask] = val
        return arr

    @staticmethod
    def equal_width_discretizer(data: np.ndarray, bins: int = 10) -> np.ndarray:
        """Categorize continuous data into discrete integer buckets."""
        arr = np.copy(data)
        if bins < 2:
            return arr # Cannot discretize into 1 bin
            
        min_val, max_val = np.min(arr), np.max(arr)
        if min_val == max_val:
            return np.zeros_like(arr, dtype=np.int32)
            
        step = (max_val - min_val) / bins
        
        # Calculate bin indices: floor((x - min) / step)
        discretized = np.floor((arr - min_val) / step)
        
        # Max value edge case will push it out of bounds explicitly
        discretized[discretized == bins] = bins - 1
        
        return discretized.astype(np.int32)


# ---------------------------------------------------------------------------
# 3. OMNI ENGINE CLASS
# ---------------------------------------------------------------------------

class OmniFeatureEngine:
    """
    Production Engine providing Data Engineering Transformations.
    """
    VERSION = "1.0.0"
    ENGINE_ID = "omni-feature-engine"

    def __init__(self) -> None:
        self._transformation_count = 0

    def fit_transform_imputation(self, data: List[float], strategy: str) -> Result:
        """Apply functional missing value imputation."""
        # Convert Python list representing Nones to float nan
        safe_data = [float('nan') if x is None else x for x in data]
            
        arr = np.array(safe_data, dtype=np.float64)
        if len(arr) == 0:
            return Err("Input data array cannot be empty.")
            
        if strategy not in ["mean", "median", "zero"]:
            return Err("Invalid strategy. Allowed: 'mean', 'median', 'zero'.")
            
        try:
            transformed = MatrixTransformers.impute_missing(arr, strategy)
            self._transformation_count += 1
            return Ok(transformed.tolist())
        except Exception as exc:
            return Err(f"Imputation mapping failed: {exc}")

    def fit_transform_discretizer(self, data: List[float], bins: int) -> Result:
        """Apply equal width scaling onto the array."""
        safe_data = [float('nan') if x is None else x for x in data]
        arr = np.array(safe_data, dtype=np.float64)
        
        if len(arr) == 0:
            return Err("Input data array cannot be empty.")
            
        if np.any(np.isnan(arr)):
            return Err("Data contains NaNs. Cannot discretize without imputation first.")
            
        if bins < 2:
            return Err(f"Bins must be greater than or equal to 2, got {bins}")
            
        try:
            transformed = MatrixTransformers.equal_width_discretizer(arr, bins)
            self._transformation_count += 1
            return Ok(transformed.tolist())
        except Exception as exc:
            return Err(f"Discretization mapping failed: {exc}")

    def diagnostics(self) -> Dict[str, Any]:
        """Return engine diagnostics."""
        return {
            "engine_id": self.ENGINE_ID,
            "version": self.VERSION,
            "status": "operational",
            "total_computations": self._transformation_count,
            "features": [
                "missing_value_imputation",
                "equal_width_discretization",
                "pure_array_mathematical_transformations",
            ]
        }
