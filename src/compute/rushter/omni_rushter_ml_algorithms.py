# OMNI MOTHER - DIVINE MEMORY INTEGRATION
# Rushter ML Algorithms (OMNI Zero-Mock Implementation)
# Implements K-Means centroid reassignment step mathematically.

from dataclasses import dataclass
from typing import List, Tuple, Optional
import math

@dataclass
class Result:
    value: Optional[List[List[float]]] # The New Centroids
    error: Optional[str]
    is_ok: bool

    @staticmethod
    def ok(val: List[List[float]]) -> 'Result':
        return Result(value=val, error=None, is_ok=True)

    @staticmethod
    def err(err: str) -> 'Result':
        return Result(value=None, error=err, is_ok=False)

class KMeansCore:
    def _euclidean(self, a: List[float], b: List[float]) -> float:
        return sum((x - y) ** 2 for x, y in zip(a, b))

    def update_centroids(self, X: List[List[float]], centroids: List[List[float]]) -> Result:
        if not X or not centroids:
            return Result.err("Data or centroids array is empty.")
            
        k = len(centroids)
        dims = len(X[0])
        
        if len(centroids[0]) != dims:
            return Result.err("Centroid and Data dimensional mismatch.")
            
        new_centroids = [[0.0] * dims for _ in range(k)]
        counts = [0] * k
        
        for point in X:
            # Find nearest centroid
            best_idx = 0
            best_dist = float('inf')
            
            for i in range(k):
                 dist = self._euclidean(point, centroids[i])
                 if dist < best_dist:
                     best_dist = dist
                     best_idx = i
                     
            counts[best_idx] += 1
            for d in range(dims):
                 new_centroids[best_idx][d] += point[d]
                 
        for i in range(k):
             if counts[i] == 0:
                 return Result.err(f"Centroid {i} collapsed (no points assigned).")
             for d in range(dims):
                 new_centroids[i][d] /= counts[i]
                 
        return Result.ok(new_centroids)
