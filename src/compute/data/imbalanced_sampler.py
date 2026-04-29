import numpy as np

class OmniSMOTE:
    def __init__(self, k_neighbors=5):
        self.k = k_neighbors

    def fit_resample(self, X, y):
        # Pure math implementation of Synthetic Minority Over-sampling Technique
        classes, counts = np.unique(y, return_counts=True)
        majority_class = classes[np.argmax(counts)]
        minority_class = classes[np.argmin(counts)]
        
        min_X = X[y == minority_class]
        maj_X = X[y == majority_class]
        
        n_synthetic = len(maj_X) - len(min_X)
        if n_synthetic <= 0: return X, y
        
        synthetic_samples = []
        for _ in range(n_synthetic):
            idx = np.random.randint(0, len(min_X))
            neighbor_idx = np.random.randint(0, len(min_X))
            diff = min_X[neighbor_idx] - min_X[idx]
            synthetic = min_X[idx] + np.random.rand() * diff
            synthetic_samples.append(synthetic)
            
        new_X = np.vstack([X, np.array(synthetic_samples)])
        new_y = np.hstack([y, [minority_class] * n_synthetic])
        return new_X, new_y
