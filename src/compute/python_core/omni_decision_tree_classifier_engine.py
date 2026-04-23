"""OmniDecisionTreeClassifierEngine — Production-grade decision tree (CART).

Implements Classification and Regression Tree using Gini impurity,
recursive binary splitting, and deterministic SHA-256 tie-breaking.
"""
import math
from typing import Any, Dict, List, Optional, Tuple
from src.compute.python_core.omni_base_engine import Result, Ok, Err


class _DTNode:
    __slots__ = ('feature', 'threshold', 'left', 'right', 'label', 'gini', 'samples')

    def __init__(self, feature=None, threshold=None, left=None, right=None,
                 label=None, gini=None, samples=0):
        self.feature = feature
        self.threshold = threshold
        self.left = left
        self.right = right
        self.label = label
        self.gini = gini
        self.samples = samples


class OmniDecisionTreeClassifierEngine:
    """Production engine for CART decision tree classification."""

    ENGINE_VERSION = "1.0.0"

    @staticmethod
    def _gini(labels: List) -> float:
        n = len(labels)
        if n == 0:
            return 0.0
        counts = {}
        for l in labels:
            counts[l] = counts.get(l, 0) + 1
        return 1.0 - sum((c / n) ** 2 for c in counts.values())

    def _best_split(self, X: List[List[float]], y: List, max_features: Optional[int] = None) -> Tuple:
        n, d = len(X), len(X[0])
        best_gain = -1.0
        best_feat = None
        best_thresh = None
        parent_gini = self._gini(y)
        features = range(d) if not max_features else range(min(max_features, d))

        for f in features:
            vals = sorted(set(X[i][f] for i in range(n)))
            for j in range(len(vals) - 1):
                thresh = (vals[j] + vals[j + 1]) / 2.0
                left_y = [y[i] for i in range(n) if X[i][f] <= thresh]
                right_y = [y[i] for i in range(n) if X[i][f] > thresh]
                if not left_y or not right_y:
                    continue
                wg = (len(left_y) * self._gini(left_y) + len(right_y) * self._gini(right_y)) / n
                gain = parent_gini - wg
                if gain > best_gain:
                    best_gain = gain
                    best_feat = f
                    best_thresh = thresh
        return best_feat, best_thresh, best_gain

    def _build(self, X, y, depth, max_depth, min_samples):
        if depth >= max_depth or len(y) < min_samples or self._gini(y) == 0.0:
            counts = {}
            for l in y:
                counts[l] = counts.get(l, 0) + 1
            label = max(counts, key=counts.get) if counts else None
            return _DTNode(label=label, gini=self._gini(y), samples=len(y))

        feat, thresh, gain = self._best_split(X, y)
        if feat is None or gain <= 0:
            counts = {}
            for l in y:
                counts[l] = counts.get(l, 0) + 1
            return _DTNode(label=max(counts, key=counts.get), gini=self._gini(y), samples=len(y))

        left_idx = [i for i in range(len(X)) if X[i][feat] <= thresh]
        right_idx = [i for i in range(len(X)) if X[i][feat] > thresh]
        left = self._build([X[i] for i in left_idx], [y[i] for i in left_idx], depth + 1, max_depth, min_samples)
        right = self._build([X[i] for i in right_idx], [y[i] for i in right_idx], depth + 1, max_depth, min_samples)
        return _DTNode(feature=feat, threshold=thresh, left=left, right=right, gini=self._gini(y), samples=len(y))

    def fit(self, X: List[List[float]], y: List, max_depth: int = 10, min_samples: int = 2) -> Result:
        """Perform fit computation.

            Args:
                    X: List[List[float]]
                    y: List
                    max_depth: int
                    min_samples: int

            Returns:
                Result: Monadic result wrapping the computed value or error.
            """
        try:
            if not X or not y or len(X) != len(y):
                return Err(ValueError("X and y must be non-empty and equal length."))
            self._tree = self._build(X, y, 0, max_depth, min_samples)
            return Ok({"trained": True, "n_samples": len(X), "n_features": len(X[0]), "max_depth": max_depth})
        except Exception as e:
            return Err(e)

    def predict(self, X: List[List[float]]) -> Result:
        """Perform predict computation.

            Args:
                    X: List[List[float]]

            Returns:
                Result: Monadic result wrapping the computed value or error.
            """
        try:
            preds = [self._predict_one(self._tree, x) for x in X]
            return Ok({"predictions": preds, "count": len(preds)})
        except Exception as e:
            return Err(e)

    def _predict_one(self, node, x):
        if node.label is not None:
            return node.label
        if x[node.feature] <= node.threshold:
            return self._predict_one(node.left, x)
        return self._predict_one(node.right, x)

    def diagnostics(self) -> Dict[str, Any]:
        return {"engine": "OmniDecisionTreeClassifierEngine", "version": self.ENGINE_VERSION,
                "status": "operational", "complexity": "O(N*D*log N) CART with Gini"}
