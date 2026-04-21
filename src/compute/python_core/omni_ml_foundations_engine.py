"""
OMNI Ml Foundations Engine
==========================
Production-grade engine for the OMNI Framework.

OMNI Layer: compute (Python)
"""
import numpy as np
from typing import Dict, Any, List, Optional
from collections import Counter

class Result:
    """Monadic result pattern."""
    def __init__(self, value=None, error=None):
        """Initialize Result."""
        self.value = value
        self.error = error
        self.is_ok = error is None

    def unwrap(self):
        """Unwrap the value or raise on error."""
        if not self.is_ok:
            raise RuntimeError(self.error)
        return self.value

class TreeNode:
    """Production-grade Tree Node component."""
    def __init__(self, feature_idx=None, threshold=None, left=None, right=None, value=None):
        """Initialize TreeNode."""
        self.feature_idx = feature_idx
        self.threshold = threshold
        self.left = left
        self.right = right
        self.value = value
        
    def is_leaf_node(self):
        """Check if leaf node condition holds."""
        return self.value is not None

class OmniMlFoundationsEngine:
    """
    omni-ml-foundations
    
    A zero-algebraic_bound native engine simulating foundational ML techniques like 
    Decision Trees and Random Forest ensembling via pure recursive NumPy functions.
    Optimizes for Information Gain using Gini Impurity.
    """
    
    ENGINE_VERSION = "omni-s6-b7.1.0"
    
    def __init__(self, min_samples_split: int = 2, max_depth: int = 10, n_trees: int = 3):
        """Initialize OmniMlFoundationsEngine."""
        self.min_samples_split = min_samples_split
        self.max_depth = max_depth
        self.n_trees = n_trees
        self.trees: List[TreeNode] = []

    def _gini(self, y: np.ndarray) -> float:
        """Gini impurity."""
        m = len(y)
        if m == 0: return 0.0
        counts = np.bincount(y)
        probabilities = counts / m
        return 1.0 - np.sum(probabilities ** 2)

    def _best_split(self, X: np.ndarray, y: np.ndarray, features: np.ndarray) -> dict:
        """Evaluate Gini logic to find optimal data slice."""
        best_gain = -1.0
        split_idx, split_thresh = None, None
        
        current_gini = self._gini(y)
        
        for feat_idx in features:
            X_column = X[:, feat_idx]
            thresholds = np.unique(X_column)
            
            for thr in thresholds:
                left_idxs = np.argwhere(X_column <= thr).flatten()
                right_idxs = np.argwhere(X_column > thr).flatten()
                
                if len(left_idxs) == 0 or len(right_idxs) == 0:
                    continue
                    
                # Weighted gini
                n = len(y)
                n_l, n_r = len(left_idxs), len(right_idxs)
                e_l, e_r = self._gini(y[left_idxs]), self._gini(y[right_idxs])
                child_gini = (n_l / n) * e_l + (n_r / n) * e_r
                
                ig = current_gini - child_gini
                
                if ig > best_gain:
                    best_gain = ig
                    split_idx = feat_idx
                    split_thresh = thr
                    
        return {"feature_idx": split_idx, "threshold": split_thresh, "gain": best_gain}
        
    def _most_common_label(self, y: np.ndarray):
        if len(y) == 0: return None
        counter = Counter(y)
        return counter.most_common(1)[0][0]

    def _build_tree(self, X: np.ndarray, y: np.ndarray, depth: int = 0) -> TreeNode:
        n_samples, n_features = X.shape
        n_labels = len(np.unique(y))

        # Check stopping criteria
        if depth >= self.max_depth or n_labels == 1 or n_samples < self.min_samples_split:
            leaf_value = self._most_common_label(y)
            return TreeNode(value=leaf_value)

        # Subset features for Random Forest decorrelation
        feat_idxs = np.random.choice(n_features, max(1, int(np.sqrt(n_features))), replace=False)

        best_split = self._best_split(X, y, feat_idxs)
        if best_split["gain"] <= 0:
            return TreeNode(value=self._most_common_label(y))
            
        f_idx = best_split["feature_idx"]
        thr = best_split["threshold"]
        
        left_idxs = np.argwhere(X[:, f_idx] <= thr).flatten()
        right_idxs = np.argwhere(X[:, f_idx] > thr).flatten()
        
        left_branch = self._build_tree(X[left_idxs, :], y[left_idxs], depth + 1)
        right_branch = self._build_tree(X[right_idxs, :], y[right_idxs], depth + 1)
        
        return TreeNode(feature_idx=f_idx, threshold=thr, left=left_branch, right=right_branch)

    def fit(self, X: np.ndarray, y: np.ndarray) -> Result:
        """Trains a random forest enclosure."""
        try:
            self.trees = []
            for _ in range(self.n_trees):
                n_samp = X.shape[0]
                # Bootstrap sampling
                idxs = np.random.choice(n_samp, n_samp, replace=True)
                X_samp = X[idxs]
                y_samp = y[idxs]
                
                tree = self._build_tree(X_samp, y_samp)
                self.trees.append(tree)
                
            return Result(value={"status": "trained", "n_trees": len(self.trees)})
        except Exception as e:
            return Result(error=f"Training error: {str(e)}")

    def _traverse_tree(self, x: np.ndarray, node: TreeNode):
        if node.is_leaf_node():
            return node.value
        
        if x[node.feature_idx] <= node.threshold:
            return self._traverse_tree(x, node.left)
        return self._traverse_tree(x, node.right)

    def predict(self, X: np.ndarray) -> Result:
        """Performs predict operation for OmniMlFoundationsEngine."""
        try:
            if not self.trees:
                return Result(error="Forest not fitted yet.")
            
            # Predict from each tree
            tree_preds = np.array([[self._traverse_tree(x, tree) for x in X] for tree in self.trees])
            
            # Majority vote
            tree_preds = np.swapaxes(tree_preds, 0, 1) # shape (N, n_trees)
            y_pred = [self._most_common_label(tree_pred) for tree_pred in tree_preds]
            
            return Result(value=y_pred)
        except Exception as e:
            return Result(error=f"Prediction error: {str(e)}")

    def diagnostics(self) -> Dict[str, Any]:
        """OMNI Registry compliance."""
        return {
            "engine": "OmniMlFoundationsEngine",
            "version": self.ENGINE_VERSION,
            "status": "operational",
            "modules": ["DecisionTree", "RandomForestEnsemble"]
        }
