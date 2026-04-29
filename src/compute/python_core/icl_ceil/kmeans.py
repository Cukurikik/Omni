import numpy as np

class KMeansUpdater:
    def update_centroids(self, data: np.ndarray, labels: np.ndarray, k: int) -> np.ndarray:
        if len(data) == 0:
            raise ValueError("Empty data array")
        new_centroids = np.zeros((k, data.shape[1]))
        for i in range(k):
            cluster_points = data[labels == i]
            if len(cluster_points) > 0:
                new_centroids[i] = np.mean(cluster_points, axis=0)
        return new_centroids
