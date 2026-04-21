"""
OMNI Start Machine Learning Engine
====================================
Production-grade OMNI engine abstracting fundamental Machine Learning algorithms.
Inspired by louisfb01/start-machine-learning.

Features:
- Principal Component Analysis (PCA)
- K-Means Clustering
- Multivariate Linear Regression

All operations are zero-mock and execute purely via NumPy with robust mathematics.

OMNI Layer: compute (Python)
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple, Union

import numpy as np

# ---------------------------------------------------------------------------
# 1. OMNI Result Monad
# ---------------------------------------------------------------------------


ENGINE_VERSION = "1.0.0-omni"

class StartMLError(Exception):
    """Base error for Start ML engine."""

@dataclass(frozen=True)
class Ok:
    """Monadic Ok result type."""
    value: Any

@dataclass(frozen=True)
class Err:
    """Monadic Err result type."""
    error: str

Result = Union[Ok, Err]


# ---------------------------------------------------------------------------
# 2. FOUNDATIONAL ALGORITHMS
# ---------------------------------------------------------------------------

class LinearRegression:
    """Multivariate Linear Regression via Normal Equation."""
    
    def __init__(self):
        """Initialize LinearRegression."""
        self.weights: Optional[np.ndarray] = None
        self.bias: Optional[float] = None
        
    def fit(self, X: np.ndarray, y: np.ndarray) -> Result:
        """Fit LinearRegression to data."""
        if X.ndim != 2 or y.ndim != 1:
            return Err("X must be 2D and y must be 1D.")
        if X.shape[0] != y.shape[0]:
            return Err("Number of samples in X and y must match.")
            
        try:
            # Add ones column for bias
            X_b = np.c_[np.ones((X.shape[0], 1)), X]
            
            # Normal equation: theta = (X^T * X)^-1 * X^T * y
            theta_best = np.linalg.inv(X_b.T.dot(X_b)).dot(X_b.T).dot(y)
            
            self.bias = float(theta_best[0])
            self.weights = theta_best[1:]
            return Ok(True)
        except np.linalg.LinAlgError:
            return Err("Matrix is singular and cannot be inverted. Use gradient descent instead.")
        except Exception as e:
            return Err(str(e))

    def predict(self, X: np.ndarray) -> Result:
        """Generate prediction for predict."""
        if self.weights is None or self.bias is None:
            return Err("Model is not fitted. Cannot predict.")
        if X.ndim != 2:
            return Err("X must be 2D.")
        
        preds = X.dot(self.weights) + self.bias
        return Ok(preds)


class PCA:
    """Principal Component Analysis using SVD abstraction."""
    
    def __init__(self, n_components: int):
        """Initialize PCA."""
        self.n_components = n_components
        self.components: Optional[np.ndarray] = None
        self.mean: Optional[np.ndarray] = None
        
    def fit_transform(self, X: np.ndarray) -> Result:
        """Execute fit transform operation for PCA."""
        if X.ndim != 2:
            return Err("X must be 2D.")
        if self.n_components > X.shape[1]:
            return Err("n_components cannot be greater than the number of features.")
            
        # 1. Center the data
        self.mean = np.mean(X, axis=0)
        X_centered = X - self.mean
        
        # 2. Compute covariance matrix
        # Cov = X^T * X / (n - 1)
        cov_matrix = np.cov(X_centered, rowvar=False)
        
        # 3. Eigen decomposition
        eigenvalues, eigenvectors = np.linalg.eigh(cov_matrix)
        
        # 4. Sort eigenvectors by eigenvalues in descending order
        sorted_idx = np.argsort(eigenvalues)[::-1]
        eigenvectors = eigenvectors[:, sorted_idx]
        
        # 5. Take the first n_components
        self.components = eigenvectors[:, :self.n_components]
        
        # 6. Project the data
        X_projected = X_centered.dot(self.components)
        return Ok(X_projected)


class KMeans:
    """K-Means Clustering via standard Lloyd's algorithm."""
    
    def __init__(self, k: int, max_iters: int = 100, seed: int = 42):
        """Initialize KMeans."""
        self.k = k
        self.max_iters = max_iters
        self.seed = seed
        self.centroids: Optional[np.ndarray] = None
        self.inertia: float = 0.0

    def fit(self, X: np.ndarray) -> Result:
        """Fit KMeans to data."""
        if X.ndim != 2:
            return Err("X must be 2D.")
        if X.shape[0] < self.k:
            return Err("Number of samples must be >= k.")
            
        rs = np.random.RandomState(self.seed)
        # Randomly initialize centroids by picking k random points from X
        idx = rs.choice(X.shape[0], self.k, replace=False)
        self.centroids = X[idx].astype(np.float32)
        
        for _ in range(self.max_iters):
            # Assign clusters
            clusters = self._get_clusters(X)
            
            # Compute new centroids
            new_centroids = self._compute_centroids(X, clusters)
            
            # Check convergence
            if np.allclose(self.centroids, new_centroids):
                break
                
            self.centroids = new_centroids
            
        # Calculate inertia (within cluster sum of squares)
        self._calculate_inertia(X)
        return Ok(self.centroids)

    def predict(self, X: np.ndarray) -> Result:
        """Generate prediction for predict."""
        if self.centroids is None:
            return Err("KMeans model is not fitted.")
        clusters = self._get_clusters(X)
        return Ok(clusters)

    def _get_clusters(self, X: np.ndarray) -> np.ndarray:
        # Distance between each point and each centroid
        distances = np.linalg.norm(X[:, np.newaxis] - self.centroids, axis=2)
        return np.argmin(distances, axis=1)

    def _compute_centroids(self, X: np.ndarray, clusters: np.ndarray) -> np.ndarray:
        new_centroids = np.zeros((self.k, X.shape[1]), dtype=np.float32)
        for i in range(self.k):
            cluster_points = X[clusters == i]
            if len(cluster_points) > 0:
                new_centroids[i] = np.mean(cluster_points, axis=0)
            else:
                new_centroids[i] = self.centroids[i] # type: ignore
        return new_centroids
        
    def _calculate_inertia(self, X: np.ndarray):
        clusters = self._get_clusters(X)
        self.inertia = 0.0
        for i in range(self.k):
            cluster_points = X[clusters == i]
            if len(cluster_points) > 0:
                self.inertia += np.sum((cluster_points - self.centroids[i])**2) # type: ignore


# ---------------------------------------------------------------------------
# 3. OMNI ENGINE CLASS
# ---------------------------------------------------------------------------

class OmniStartMLEngine:
    """
    Production Engine for fundamental ML operations.
    """

    def __init__(self, config=None):
        """Initialize OmniStartMLEngine."""
        self.config = config or {}
        self.engine_id = __import__("uuid").uuid4().hex
        self.is_active = True
    VERSION = "1.0.0"
    ENGINE_ID = "omni-start-ml"

    def create_linear_regression(self) -> LinearRegression:
        """Performs create linear regression operation for OmniStartMLEngine."""
        return LinearRegression()

    def create_pca(self, n_components: int) -> PCA:
        """Performs create pca operation for OmniStartMLEngine."""
        return PCA(n_components=n_components)

    def create_kmeans(self, k: int) -> KMeans:
        """Performs create kmeans operation for OmniStartMLEngine."""
        return KMeans(k=k)

    def diagnostics(self) -> Dict[str, Any]:
        """Performs diagnostics operation for OmniStartMLEngine."""
        return {
            "engine_id": self.ENGINE_ID,
            "version": self.VERSION,
            "models_supported": ["LinearRegression", "PCA", "KMeans"],
            "status": "operational",
        }
