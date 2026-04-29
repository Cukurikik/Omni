import numpy as np

class BipartiteMatcher:
    def compute_matching_score(self, weights: np.ndarray) -> float:
        if weights.size == 0:
            return 0.0
        # Simple greedy approximation for matching score
        score = 0.0
        w = weights.copy()
        for _ in range(min(w.shape)):
            if np.max(w) <= 0:
                break
            idx = np.unravel_index(np.argmax(w), w.shape)
            score += w[idx]
            w[idx[0], :] = 0
            w[:, idx[1]] = 0
        return float(score)
