"""
OMNI Compute Layer: MLxtend Ensemble Voting Classifier
Combines multiple estimators for robust predictions.
"""
import numpy as np
from typing import List, Tuple, Optional

Result = Tuple[Optional[np.ndarray], Optional[Exception]]

class MajorityVoteClassifier:
    def __init__(self, weights: Optional[List[float]] = None):
        self.weights = weights
        self._fitted_classifiers = []

    def fit(self, classifiers: List[any], X: np.ndarray, y: np.ndarray) -> Result:
        try:
            if self.weights and len(self.weights) != len(classifiers):
                return None, ValueError("Number of classifiers and weights must be equal")

            self._fitted_classifiers = []
            for clf in classifiers:
                # Assuming duck-typing for standard 'fit' interface
                clf.fit(X, y)
                self._fitted_classifiers.append(clf)
            
            return np.array([True]), None
        except Exception as e:
            return None, e

    def predict(self, X: np.ndarray) -> Result:
        try:
            if not self._fitted_classifiers:
                return None, RuntimeError("Classifiers not fitted")

            # Collect predictions from all classifiers: shape (n_classifiers, n_samples)
            predictions = np.asarray([clf.predict(X)[0] for clf in self._fitted_classifiers])
            
            # Apply weighted majority voting
            if self.weights:
                maj = np.apply_along_axis(
                    lambda x: np.argmax(np.bincount(x, weights=self.weights)),
                    axis=0,
                    arr=predictions
                )
            else:
                maj = np.apply_along_axis(
                    lambda x: np.argmax(np.bincount(x)),
                    axis=0,
                    arr=predictions
                )
            return maj, None
        except Exception as e:
            return None, e
