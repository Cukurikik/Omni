"""OmniKmeansClusteringEngine — Production-grade K-Means clustering.

Implements Lloyd's algorithm with K-Means++ initialization,
Euclidean distance metric, and convergence via centroid stability.
"""
import math
import hashlib
from typing import Any, Dict, List, Tuple
from src.compute.python_core.omni_base_engine import Result, Ok, Err


class OmniKmeansClusteringEngine:
    """Production engine for K-Means clustering."""

    ENGINE_VERSION = "1.0.0"

    @staticmethod
    def _euclidean(a: List[float], b: List[float]) -> float:
        return math.sqrt(sum((ai - bi) ** 2 for ai, bi in zip(a, b)))

    def _deterministic_init(self, data: List[List[float]], k: int, seed: str = "omni") -> List[List[float]]:
        """K-Means++ style init using SHA-256 deterministic selection."""
        n = len(data)
        d = len(data[0])
        idx0 = int(hashlib.sha256(seed.encode()).hexdigest()[:8], 16) % n
        centroids = [data[idx0][:]]
        for _ in range(1, k):
            dists = []
            for pt in data:
                min_d = min(self._euclidean(pt, c) for c in centroids)
                dists.append(min_d ** 2)
            total = sum(dists)
            if total == 0:
                break
            cumulative = []
            acc = 0
            for dd in dists:
                acc += dd / total
                cumulative.append(acc)
            h = int(hashlib.sha256(f"{seed}_{len(centroids)}".encode()).hexdigest()[:8], 16) / 0xFFFFFFFF
            for i, c in enumerate(cumulative):
                if h <= c:
                    centroids.append(data[i][:])
                    break
        return centroids

    def fit(self, data: List[List[float]], k: int, max_iter: int = 100, tol: float = 1e-6) -> Result:
        """
        Run K-Means clustering on the dataset.

        Args:
            data: List of data points (each a list of floats).
            k: Number of clusters.
            max_iter: Maximum iterations.
            tol: Convergence tolerance for centroid movement.

        Returns:
            Result with centroids, labels, inertia, and iterations.
        """
        try:
            n = len(data)
            if n == 0:
                return Err(ValueError("Data must be non-empty."))
            if k <= 0 or k > n:
                return Err(ValueError(f"k must be in [1, {n}]."))
            d = len(data[0])

            centroids = self._deterministic_init(data, k)
            labels = [0] * n
            iters = 0

            for it in range(max_iter):
                iters = it + 1
                for i, pt in enumerate(data):
                    best = 0
                    best_dist = self._euclidean(pt, centroids[0])
                    for j in range(1, len(centroids)):
                        dd = self._euclidean(pt, centroids[j])
                        if dd < best_dist:
                            best_dist = dd
                            best = j
                    labels[i] = best

                new_centroids = [[0.0] * d for _ in range(len(centroids))]
                counts = [0] * len(centroids)
                for i, pt in enumerate(data):
                    cl = labels[i]
                    counts[cl] += 1
                    for dim in range(d):
                        new_centroids[cl][dim] += pt[dim]
                for j in range(len(centroids)):
                    if counts[j] > 0:
                        for dim in range(d):
                            new_centroids[j][dim] /= counts[j]
                    else:
                        new_centroids[j] = centroids[j][:]

                shift = max(self._euclidean(centroids[j], new_centroids[j]) for j in range(len(centroids)))
                centroids = new_centroids
                if shift < tol:
                    break

            inertia = sum(self._euclidean(data[i], centroids[labels[i]]) ** 2 for i in range(n))

            return Ok({"centroids": [[round(v, 8) for v in c] for c in centroids],
                        "labels": labels, "inertia": round(inertia, 8), "iterations": iters,
                        "k": len(centroids), "n_samples": n, "converged": iters < max_iter})
        except Exception as e:
            return Err(e)

    def diagnostics(self) -> Dict[str, Any]:
        return {"engine": "OmniKmeansClusteringEngine", "version": self.ENGINE_VERSION,
                "status": "operational", "complexity": "O(N * K * D * I) Lloyd's algorithm"}
