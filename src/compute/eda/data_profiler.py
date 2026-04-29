import pandas as pd
import numpy as np
from typing import Dict, Any, List

class OmniResult:
    def __init__(self, ok: Any = None, err: str = None):
        self.ok = ok
        self.err = err
    
    def is_ok(self) -> bool:
        return self.err is None
        
    def unwrap(self) -> Any:
        if not self.is_ok():
            raise RuntimeError(f"Unwrap failed: {self.err}")
        return self.ok

class DataProfiler:
    def __init__(self, sample_size: int = 100000):
        self.sample_size = sample_size

    def profile_dataframe(self, df: pd.DataFrame) -> OmniResult:
        try:
            if df.empty:
                return OmniResult(err="DataFrame is empty")

            if len(df) > self.sample_size:
                df = df.sample(self.sample_size, random_state=42)

            profile = {
                "n_rows": int(len(df)),
                "n_columns": int(df.shape[1]),
                "memory_usage_bytes": int(df.memory_usage(deep=True).sum()),
                "columns": {}
            }

            for col in df.columns:
                series = df[col]
                dtype = str(series.dtype)
                n_missing = int(series.isna().sum())
                p_missing = float(n_missing / len(df))
                
                col_stats = {
                    "dtype": dtype,
                    "n_missing": n_missing,
                    "p_missing": p_missing,
                }

                if pd.api.types.is_numeric_dtype(series):
                    col_stats.update(self._profile_numeric(series))
                elif pd.api.types.is_categorical_dtype(series) or pd.api.types.is_object_dtype(series):
                    col_stats.update(self._profile_categorical(series))

                profile["columns"][col] = col_stats

            return OmniResult(ok=profile)

        except Exception as e:
            return OmniResult(err=f"Profiling failed: {str(e)}")

    def _profile_numeric(self, series: pd.Series) -> Dict[str, Any]:
        s = series.dropna()
        if s.empty:
            return {}
            
        return {
            "type": "numeric",
            "mean": float(s.mean()),
            "std": float(s.std()),
            "min": float(s.min()),
            "25%": float(s.quantile(0.25)),
            "50%": float(s.median()),
            "75%": float(s.quantile(0.75)),
            "max": float(s.max()),
            "n_zeros": int((s == 0).sum()),
            "kurtosis": float(s.kurtosis()),
            "skewness": float(s.skew())
        }

    def _profile_categorical(self, series: pd.Series) -> Dict[str, Any]:
        s = series.dropna()
        if s.empty:
            return {}
            
        value_counts = s.value_counts()
        return {
            "type": "categorical",
            "n_unique": int(s.nunique()),
            "top_categories": value_counts.head(5).to_dict(),
            "mode": str(value_counts.index[0]) if not value_counts.empty else None
        }
