import numpy as np

class FloraOptimizer:
    def __init__(self, compression_ratio: float = 0.1):
        self.compression_ratio = compression_ratio
        
    def compress_gradients(self, grads: np.ndarray) -> np.ndarray:
        norm = np.linalg.norm(grads)
        if norm == 0:
            return grads
        threshold = np.percentile(np.abs(grads), (1 - self.compression_ratio) * 100)
        mask = np.abs(grads) >= threshold
        return grads * mask
