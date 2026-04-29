import numpy as np
from typing import Tuple, List, Optional

# OMNI DATA SCIENCE: k-Means Clustering
# Pure NumPy implementation without scikit-learn.
# Source: CodeCutTech/Data-science

class KMeansError(Exception):
    pass

class KMeans:
    def __init__(self, n_clusters: int, max_iters: int = 100, tol: float = 1e-4):
        self.n_clusters = n_clusters
        self.max_iters = max_iters
        self.tol = tol
        self.centroids = None

    def fit(self, X: np.ndarray) -> Tuple[Optional[np.ndarray], Optional[KMeansError]]:
        try:
            if not isinstance(X, np.ndarray):
                return None, KMeansError("Input must be a numpy array.")
            if len(X) < self.n_clusters:
                return None, KMeansError("Number of samples must be >= n_clusters.")

            n_samples, n_features = X.shape
            
            # 1. Initialize centroids randomly (Forgy method)
            random_indices = np.random.choice(n_samples, self.n_clusters, replace=False)
            self.centroids = X[random_indices]

            for i in range(self.max_iters):
                # 2. Assign clusters
                # Calculate distances: ||X - C||^2
                # X: (n, d), C: (k, d) -> (n, k, d)
                distances = np.linalg.norm(X[:, np.newaxis] - self.centroids, axis=2)
                labels = np.argmin(distances, axis=1)

                # 3. Update centroids
                new_centroids = np.zeros((self.n_clusters, n_features))
                for k in range(self.n_clusters):
                    cluster_points = X[labels == k]
                    if len(cluster_points) > 0:
                        new_centroids[k] = np.mean(cluster_points, axis=0)
                    else:
                        # Handle empty cluster by re-initializing it to a random point
                        new_centroids[k] = X[np.random.choice(n_samples)]

                # 4. Check convergence
                if np.linalg.norm(new_centroids - self.centroids) < self.tol:
                    self.centroids = new_centroids
                    break
                    
                self.centroids = new_centroids

            return labels, None

        except Exception as e:
            return None, KMeansError(f"K-Means fit failed: {str(e)}")

    def predict(self, X: np.ndarray) -> Tuple[Optional[np.ndarray], Optional[KMeansError]]:
        try:
            if self.centroids is None:
                return None, KMeansError("Model must be fitted before prediction.")
            distances = np.linalg.norm(X[:, np.newaxis] - self.centroids, axis=2)
            return np.argmin(distances, axis=1), None
        except Exception as e:
            return None, KMeansError(f"K-Means predict failed: {str(e)}")
