"""
@omni-domain Compute Layer (Data Preparation)
@omni-source various/data-prep
@omni-description Data Prep Cleaner mimicking ETL pipeline with validation.
@omni-requirement zero-mock, monadic-error
"""
import math
from typing import Any, Optional, List, Dict

class OmniResult:
    def __init__(self, data=None, error=None):
        self.data = data
        self.error = error
    def is_ok(self): return self.error is None

class DataPrepError(Exception): pass

class DataPrepCleaner:
    def __init__(self, null_threshold=0.5, outlier_sigma=3.0):
        self.null_threshold = null_threshold
        self.outlier_sigma = outlier_sigma

    def remove_null_columns(self, dataset: List[Dict]) -> OmniResult:
        try:
            if not dataset:
                return OmniResult(error=DataPrepError("Dataset is empty."))
            all_keys = set()
            for row in dataset:
                all_keys.update(row.keys())
            null_ratios = {}
            for key in all_keys:
                null_count = sum(1 for row in dataset if row.get(key) is None)
                null_ratios[key] = null_count / len(dataset)
            keep_keys = [k for k, v in null_ratios.items() if v < self.null_threshold]
            cleaned = [{k: row.get(k) for k in keep_keys} for row in dataset]
            removed = [k for k in all_keys if k not in keep_keys]
            return OmniResult(data={"cleaned": cleaned, "removed_columns": removed})
        except Exception as e:
            return OmniResult(error=DataPrepError(f"Null column removal failed: {e}"))

    def remove_outliers(self, values: List[float]) -> OmniResult:
        try:
            if not values:
                return OmniResult(error=DataPrepError("Values list is empty."))
            n = len(values)
            mean = sum(values) / n
            variance = sum((x - mean) ** 2 for x in values) / n
            std = math.sqrt(variance) if variance > 0 else 0
            if std == 0:
                return OmniResult(data={"cleaned": values, "removed_count": 0})
            lower = mean - self.outlier_sigma * std
            upper = mean + self.outlier_sigma * std
            cleaned = [x for x in values if lower <= x <= upper]
            return OmniResult(data={"cleaned": cleaned, "removed_count": n - len(cleaned)})
        except Exception as e:
            return OmniResult(error=DataPrepError(f"Outlier removal failed: {e}"))

    def normalize_minmax(self, values: List[float]) -> OmniResult:
        try:
            if not values:
                return OmniResult(error=DataPrepError("Values list is empty."))
            min_val = min(values)
            max_val = max(values)
            if max_val == min_val:
                return OmniResult(data={"normalized": [0.5] * len(values)})
            normalized = [(v - min_val) / (max_val - min_val) for v in values]
            return OmniResult(data={"normalized": normalized})
        except Exception as e:
            return OmniResult(error=DataPrepError(f"Normalization failed: {e}"))
