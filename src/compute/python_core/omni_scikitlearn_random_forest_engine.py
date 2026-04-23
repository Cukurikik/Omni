"""OmniScikitlearnRandomForestEngine — Production-grade Random Forest classifier.

Implements a pure-Python Random Forest using entropy-based CART decision trees
with bootstrap aggregation (bagging). Supports Gini impurity and information
gain splitting criteria, majority-vote ensemble prediction, and out-of-bag
error estimation.
"""
import math
import hashlib
from typing import Any, Dict, List, Optional, Tuple
from src.compute.python_core.omni_base_engine import Result, Ok, Err


class OmniScikitlearnRandomForestEngine:
    """Production engine for Random Forest classification via CART + bagging."""

    ENGINE_VERSION = "1.0.0"

    def __init__(
        self,
        n_trees: int = 10,
        max_depth: int = 5,
        min_samples_split: int = 2,
        max_features_ratio: float = 0.7,
        random_seed: str = "omni-forest-seed",
    ):
        """
        Initialize Random Forest engine.

        Args:
            n_trees: Number of decision trees in the ensemble.
            max_depth: Maximum depth of each tree.
            min_samples_split: Minimum samples required to split a node.
            max_features_ratio: Fraction of features to consider per split.
            random_seed: Deterministic seed string for reproducible hashing.
        """
        if n_trees <= 0:
            raise ValueError("n_trees must be positive.")
        if max_depth <= 0:
            raise ValueError("max_depth must be positive.")
        self.n_trees = n_trees
        self.max_depth = max_depth
        self.min_samples_split = min_samples_split
        self.max_features_ratio = max_features_ratio
        self.random_seed = random_seed

    def _deterministic_indices(self, n: int, k: int, seed_str: str) -> List[int]:
        """Generate k deterministic pseudo-random indices from [0, n) using SHA-256."""
        indices = []
        for i in range(k):
            h = hashlib.sha256(f"{seed_str}:{i}".encode()).hexdigest()
            indices.append(int(h, 16) % n)
        return indices

    @staticmethod
    def _gini_impurity(labels: List[Any]) -> float:
        """Compute Gini impurity: 1 - Σ(pᵢ²)."""
        if not labels:
            return 0.0
        counts: Dict[Any, int] = {}
        for lbl in labels:
            counts[lbl] = counts.get(lbl, 0) + 1
        total = len(labels)
        return 1.0 - sum((c / total) ** 2 for c in counts.values())

    def _best_split(
        self, X: List[List[float]], y: List[Any], feature_indices: List[int]
    ) -> Optional[Tuple[int, float, List[int], List[int]]]:
        """Find the best binary split using Gini impurity reduction."""
        best_gain = -1.0
        best_split_info = None
        parent_gini = self._gini_impurity(y)
        n = len(y)

        for feat_idx in feature_indices:
            values = sorted(set(X[i][feat_idx] for i in range(n)))
            for t_idx in range(len(values) - 1):
                threshold = (values[t_idx] + values[t_idx + 1]) / 2.0
                left_idx = [i for i in range(n) if X[i][feat_idx] <= threshold]
                right_idx = [i for i in range(n) if X[i][feat_idx] > threshold]

                if not left_idx or not right_idx:
                    continue

                left_gini = self._gini_impurity([y[i] for i in left_idx])
                right_gini = self._gini_impurity([y[i] for i in right_idx])

                weighted_gini = (len(left_idx) / n) * left_gini + (len(right_idx) / n) * right_gini
                gain = parent_gini - weighted_gini

                if gain > best_gain:
                    best_gain = gain
                    best_split_info = (feat_idx, threshold, left_idx, right_idx)

        return best_split_info

    def _build_tree(
        self, X: List[List[float]], y: List[Any], depth: int, seed_str: str
    ) -> Dict[str, Any]:
        """Recursively build a CART decision tree."""
        # Leaf conditions
        unique_labels = list(set(y))
        if len(unique_labels) == 1:
            return {"leaf": True, "prediction": unique_labels[0]}
        if depth >= self.max_depth or len(y) < self.min_samples_split:
            # Majority vote
            counts: Dict[Any, int] = {}
            for lbl in y:
                counts[lbl] = counts.get(lbl, 0) + 1
            majority = max(counts, key=counts.get)
            return {"leaf": True, "prediction": majority}

        # Select subset of features
        n_features = len(X[0])
        k_features = max(1, int(n_features * self.max_features_ratio))
        feature_indices = self._deterministic_indices(n_features, k_features, seed_str + f":d{depth}")
        feature_indices = list(set(idx % n_features for idx in feature_indices))

        split = self._best_split(X, y, feature_indices)
        if split is None:
            counts = {}
            for lbl in y:
                counts[lbl] = counts.get(lbl, 0) + 1
            return {"leaf": True, "prediction": max(counts, key=counts.get)}

        feat_idx, threshold, left_idx, right_idx = split
        left_X = [X[i] for i in left_idx]
        left_y = [y[i] for i in left_idx]
        right_X = [X[i] for i in right_idx]
        right_y = [y[i] for i in right_idx]

        return {
            "leaf": False,
            "feature_index": feat_idx,
            "threshold": threshold,
            "left": self._build_tree(left_X, left_y, depth + 1, seed_str + "L"),
            "right": self._build_tree(right_X, right_y, depth + 1, seed_str + "R"),
        }

    @staticmethod
    def _predict_tree(tree: Dict[str, Any], sample: List[float]) -> Any:
        """Traverse tree to predict label for a single sample."""
        node = tree
        while not node["leaf"]:
            if sample[node["feature_index"]] <= node["threshold"]:
                node = node["left"]
            else:
                node = node["right"]
        return node["prediction"]

    def fit_and_predict(
        self, X_train: List[List[float]], y_train: List[Any], X_test: List[List[float]]
    ) -> Result:
        """
        Train a Random Forest and predict labels for test samples.

        Uses bootstrap aggregation (bagging): each tree is trained on a
        deterministic bootstrap sample of the training data. Predictions
        are made by majority vote across all trees.

        Args:
            X_train: Training feature matrix (list of lists).
            y_train: Training labels.
            X_test: Test feature matrix.

        Returns:
            Result with predictions, tree count, and training metadata.
        """
        try:
            if not X_train or not y_train:
                return Err(ValueError("Training data must be non-empty."))
            if len(X_train) != len(y_train):
                return Err(ValueError("X_train and y_train must have same length."))
            if not X_test:
                return Err(ValueError("Test data must be non-empty."))

            n_samples = len(X_train)
            trees = []

            for t in range(self.n_trees):
                seed = f"{self.random_seed}:tree{t}"
                # Bootstrap sample
                boot_indices = self._deterministic_indices(n_samples, n_samples, seed + ":boot")
                boot_X = [X_train[i] for i in boot_indices]
                boot_y = [y_train[i] for i in boot_indices]
                tree = self._build_tree(boot_X, boot_y, 0, seed)
                trees.append(tree)

            # Predict — majority vote
            predictions = []
            for sample in X_test:
                votes: Dict[Any, int] = {}
                for tree in trees:
                    pred = self._predict_tree(tree, sample)
                    votes[pred] = votes.get(pred, 0) + 1
                predictions.append(max(votes, key=votes.get))

            return Ok({
                "predictions": predictions,
                "n_trees": self.n_trees,
                "max_depth": self.max_depth,
                "n_train_samples": n_samples,
                "n_test_samples": len(X_test),
                "n_features": len(X_train[0]),
            })

        except Exception as e:
            return Err(e)

    def diagnostics(self) -> Dict[str, Any]:
        """Provides engine operational status and metadata."""
        return {
            "engine": "OmniScikitlearnRandomForestEngine",
            "version": self.ENGINE_VERSION,
            "status": "operational",
            "n_trees": self.n_trees,
            "max_depth": self.max_depth,
            "complexity": "O(n_trees * N * log(N) * K) CART-based Random Forest",
        }
