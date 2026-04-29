"""
OMNI Compute Layer - AlphaRec
Language Representations for Recommenders using Pearson Correlation.
"""
import numpy as np

class AlphaRecPearson:
    def compute_correlation(self, x: np.ndarray, y: np.ndarray) -> float:
        if len(x) != len(y) or len(x) == 0:
            raise ValueError("Arrays must be of same non-zero length")
        x_mean, y_mean = np.mean(x), np.mean(y)
        num = np.sum((x - x_mean) * (y - y_mean))
        den = np.sqrt(np.sum((x - x_mean)**2) * np.sum((y - y_mean)**2))
        return num / den if den != 0 else 0.0
