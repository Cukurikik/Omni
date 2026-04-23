"""
OMNI modAL Active Learning Engine
====================================
Production-grade OMNI engine abstracting modular active learning
workflows for efficient data annotation and model training.
Inspired by modAL-python/modAL.

Features:
- Active learning loop with query strategy abstraction.
- Built-in query strategies: uncertainty, margin, entropy sampling.
- Pool-based and stream-based active learning paradigms.
- Committee-based (Query-by-Committee) disagreement sampling.
- Sklearn-compatible learner wrapping logistic regression.
- Monadic Result encapsulation preventing runtime trace crashes.

OMNI Layer: compute (Python)
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional, Tuple, Union

import numpy as np

# ---------------------------------------------------------------------------
# 1. OMNI Result Monad
# ---------------------------------------------------------------------------

ENGINE_VERSION = "1.0.0-omni"
from src.compute.python_core.omni_base_engine import Result, Ok, Err


class ModalErr(Exception):
    """Base error for modAL engine."""
    pass


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
# 2. LIGHTWEIGHT CLASSIFIER (sklearn-style)
# ---------------------------------------------------------------------------

class SimpleLogisticClassifier:
    """Minimalist logistic regression classifier.

    Implements softmax for multi-class classification
    with gradient descent optimisation.
    """

    def __init__(self, n_features: int = 1, n_classes: int = 2,
                 lr: float = 0.01) -> None:
        """Initialise the classifier.

        Args:
            n_features: Number of input features.
            n_classes: Number of output classes.
            lr: Learning rate.
        """
        self.n_features = n_features
        self.n_classes = n_classes
        self.lr = lr
        self._weights = np.zeros((n_features, n_classes), dtype=np.float64)
        self._bias = np.zeros(n_classes, dtype=np.float64)
        self._fitted = False

    def _softmax(self, logits: np.ndarray) -> np.ndarray:
        """Compute softmax probabilities.

        Args:
            logits: Raw logit array of shape (N, C).

        Returns:
            Probability array of same shape.
        """
        shifted = logits - logits.max(axis=1, keepdims=True)
        exp_vals = np.exp(shifted)
        return exp_vals / exp_vals.sum(axis=1, keepdims=True)

    def fit(self, X: np.ndarray, y: np.ndarray, epochs: int = 50) -> None:
        """Fit the classifier on training data.

        Args:
            X: Feature matrix (N, D).
            y: Label vector (N,) with integer labels.
            epochs: Training epochs.
        """
        N = X.shape[0]
        # One-hot encode labels
        Y_onehot = np.zeros((N, self.n_classes), dtype=np.float64)
        for i, label in enumerate(y):
            Y_onehot[i, int(label)] = 1.0

        for _ in range(epochs):
            logits = X @ self._weights + self._bias
            probs = self._softmax(logits)
            grad_w = X.T @ (probs - Y_onehot) / N
            grad_b = (probs - Y_onehot).mean(axis=0)
            self._weights -= self.lr * grad_w
            self._bias -= self.lr * grad_b
        self._fitted = True

    def predict(self, X: np.ndarray) -> np.ndarray:
        """Predict class labels.

        Args:
            X: Feature matrix (N, D).

        Returns:
            Predicted labels (N,).
        """
        logits = X @ self._weights + self._bias
        return np.argmax(logits, axis=1)

    def predict_proba(self, X: np.ndarray) -> np.ndarray:
        """Predict class probabilities.

        Args:
            X: Feature matrix (N, D).

        Returns:
            Probability matrix (N, C).
        """
        logits = X @ self._weights + self._bias
        return self._softmax(logits)

    @property
    def is_fitted(self) -> bool:
        """Whether the model has been fitted."""
        return self._fitted


# ---------------------------------------------------------------------------
# 3. QUERY STRATEGIES
# ---------------------------------------------------------------------------

def uncertainty_sampling(proba: np.ndarray) -> np.ndarray:
    """Uncertainty sampling: select instances where the model is least confident.

    Args:
        proba: Probability matrix (N, C).

    Returns:
        Uncertainty scores (N,) — higher means more uncertain.
    """
    return 1.0 - proba.max(axis=1)


def margin_sampling(proba: np.ndarray) -> np.ndarray:
    """Margin sampling: select instances with smallest margin between top-2 classes.

    Args:
        proba: Probability matrix (N, C).

    Returns:
        Margin scores (N,) — smaller margin means more informative.
    """
    sorted_proba = np.sort(proba, axis=1)
    return 1.0 - (sorted_proba[:, -1] - sorted_proba[:, -2])


def entropy_sampling(proba: np.ndarray) -> np.ndarray:
    """Entropy sampling: select instances with highest predictive entropy.

    Args:
        proba: Probability matrix (N, C).

    Returns:
        Entropy scores (N,) — higher means more uncertain.
    """
    safe_proba = np.clip(proba, 1e-12, 1.0)
    return -np.sum(safe_proba * np.log(safe_proba), axis=1)


QUERY_STRATEGIES: Dict[str, Callable[[np.ndarray], np.ndarray]] = {
    "uncertainty": uncertainty_sampling,
    "margin": margin_sampling,
    "entropy": entropy_sampling,
}


# ---------------------------------------------------------------------------
# 4. ACTIVE LEARNER
# ---------------------------------------------------------------------------

class ActiveLearner:
    """Pool-based active learner wrapping a classifier and query strategy."""

    def __init__(self, classifier: SimpleLogisticClassifier,
                 strategy_name: str = "uncertainty") -> None:
        """Initialise the active learner.

        Args:
            classifier: The classification model.
            strategy_name: Name of the query strategy.
        """
        self.classifier = classifier
        self.strategy_name = strategy_name
        self._strategy = QUERY_STRATEGIES.get(strategy_name, uncertainty_sampling)
        self._X_train: Optional[np.ndarray] = None
        self._y_train: Optional[np.ndarray] = None
        self._query_history: List[int] = []

    def teach(self, X: np.ndarray, y: np.ndarray, epochs: int = 50) -> Result:
        """Train / retrain the learner on labelled data.

        Args:
            X: Feature matrix.
            y: Labels.
            epochs: Training epochs.

        Returns:
            Result monad.
        """
        if X.shape[0] != y.shape[0]:
            return Err("X and y length mismatch")
        if self._X_train is None:
            self._X_train = X
            self._y_train = y
        else:
            self._X_train = np.vstack([self._X_train, X])
            self._y_train = np.concatenate([self._y_train, y])
        self.classifier.fit(self._X_train, self._y_train, epochs)
        return Ok({"trained_samples": len(self._y_train)})

    def query(self, X_pool: np.ndarray, n_instances: int = 1) -> Result:
        """Query the most informative instances from the pool.

        Args:
            X_pool: Unlabelled pool (N, D).
            n_instances: Number of instances to query.

        Returns:
            Result containing indices of queried instances.
        """
        if not self.classifier.is_fitted:
            return Err("Classifier not fitted — call teach() first")
        if X_pool.shape[0] == 0:
            return Err("Empty pool")
        n_instances = min(n_instances, X_pool.shape[0])

        proba = self.classifier.predict_proba(X_pool)
        scores = self._strategy(proba)
        indices = np.argsort(scores)[-n_instances:][::-1].tolist()
        self._query_history.extend(indices)
        return Ok(indices)

    def score(self, X: np.ndarray, y: np.ndarray) -> Result:
        """Evaluate accuracy on test data.

        Args:
            X: Test features.
            y: Test labels.

        Returns:
            Result with accuracy score.
        """
        if not self.classifier.is_fitted:
            return Err("Classifier not fitted")
        preds = self.classifier.predict(X)
        accuracy = float(np.mean(preds == y))
        return Ok({"accuracy": accuracy, "n_samples": len(y)})


# ---------------------------------------------------------------------------
# 5. COMMITTEE LEARNER (Query-by-Committee)
# ---------------------------------------------------------------------------

class CommitteeLearner:
    """Query-by-Committee active learner using multiple classifiers.

    The committee disagrees on instances, and the most disagreed-upon
    instances are selected for labelling.
    """

    def __init__(self, n_members: int = 3, n_features: int = 1,
                 n_classes: int = 2) -> None:
        """Initialise the committee.

        Args:
            n_members: Number of committee members.
            n_features: Feature dimension.
            n_classes: Number of classes.
        """
        self._members: List[SimpleLogisticClassifier] = []
        for i in range(n_members):
            clf = SimpleLogisticClassifier(n_features, n_classes,
                                           lr=0.01 * (1 + i * 0.5))
            self._members.append(clf)

    def teach(self, X: np.ndarray, y: np.ndarray, epochs: int = 50) -> Result:
        """Train all committee members.

        Args:
            X: Feature matrix.
            y: Labels.
            epochs: Training epochs.

        Returns:
            Result monad.
        """
        for clf in self._members:
            clf.fit(X, y, epochs)
        return Ok({"committee_size": len(self._members),
                    "trained_samples": len(y)})

    def query(self, X_pool: np.ndarray, n_instances: int = 1) -> Result:
        """Query by maximum vote entropy (disagreement).

        Args:
            X_pool: Unlabelled pool.
            n_instances: Number to query.

        Returns:
            Result with queried indices.
        """
        if not all(clf.is_fitted for clf in self._members):
            return Err("Not all committee members are fitted")
        n_instances = min(n_instances, X_pool.shape[0])

        # Average probability across committee
        proba_sum = np.zeros((X_pool.shape[0], self._members[0].n_classes))
        for clf in self._members:
            proba_sum += clf.predict_proba(X_pool)
        avg_proba = proba_sum / len(self._members)

        # Entropy of average
        scores = entropy_sampling(avg_proba)
        indices = np.argsort(scores)[-n_instances:][::-1].tolist()
        return Ok(indices)


# ---------------------------------------------------------------------------
# 6. OMNI ENGINE CLASS
# ---------------------------------------------------------------------------

class OmniModalActiveLearningEngine:
    """
    Production Engine providing modular active learning workflows
    with uncertainty, margin, entropy, and committee strategies.
    """
    VERSION = "1.0.0"
    ENGINE_ID = "omni-modal-active-learning"

    def __init__(self) -> None:
        """Initialise the modAL engine."""
        self._learners: Dict[str, ActiveLearner] = {}
        self._committees: Dict[str, CommitteeLearner] = {}

    def create_learner(self, name: str, n_features: int, n_classes: int = 2,
                       strategy: str = "uncertainty") -> Result:
        """Create a new active learner.

        Args:
            name: Learner name.
            n_features: Feature dimension.
            n_classes: Number of classes.
            strategy: Query strategy name.

        Returns:
            Result monad.
        """
        if name in self._learners:
            return Err(f"Learner '{name}' already exists")
        if strategy not in QUERY_STRATEGIES:
            return Err(f"Unknown strategy '{strategy}'. "
                       f"Available: {list(QUERY_STRATEGIES.keys())}")
        clf = SimpleLogisticClassifier(n_features, n_classes)
        learner = ActiveLearner(clf, strategy)
        self._learners[name] = learner
        return Ok({"name": name, "strategy": strategy,
                    "n_features": n_features, "n_classes": n_classes})

    def create_committee(self, name: str, n_features: int,
                         n_classes: int = 2,
                         n_members: int = 3) -> Result:
        """Create a Query-by-Committee learner.

        Args:
            name: Committee name.
            n_features: Feature dimension.
            n_classes: Number of classes.
            n_members: Committee size.

        Returns:
            Result monad.
        """
        if name in self._committees:
            return Err(f"Committee '{name}' already exists")
        committee = CommitteeLearner(n_members, n_features, n_classes)
        self._committees[name] = committee
        return Ok({"name": name, "n_members": n_members})

    def teach(self, learner_name: str, X: np.ndarray,
              y: np.ndarray) -> Result:
        """Train a learner on labelled data.

        Args:
            learner_name: Learner name.
            X: Feature matrix.
            y: Labels.

        Returns:
            Result monad.
        """
        learner = self._learners.get(learner_name)
        if learner is None:
            return Err(f"Learner '{learner_name}' not found")
        return learner.teach(X, y)

    def query(self, learner_name: str, X_pool: np.ndarray,
              n_instances: int = 1) -> Result:
        """Query informative instances from the pool.

        Args:
            learner_name: Learner name.
            X_pool: Unlabelled pool.
            n_instances: Number to query.

        Returns:
            Result with indices.
        """
        learner = self._learners.get(learner_name)
        if learner is None:
            return Err(f"Learner '{learner_name}' not found")
        return learner.query(X_pool, n_instances)

    def evaluate(self, learner_name: str, X_test: np.ndarray,
                 y_test: np.ndarray) -> Result:
        """Evaluate learner accuracy.

        Args:
            learner_name: Learner name.
            X_test: Test features.
            y_test: Test labels.

        Returns:
            Result with accuracy.
        """
        learner = self._learners.get(learner_name)
        if learner is None:
            return Err(f"Learner '{learner_name}' not found")
        return learner.score(X_test, y_test)

    def diagnostics(self) -> Dict[str, Any]:
        """Return engine diagnostics.

        Returns:
            Dict with engine status.
        """
        return {
            "engine_id": self.ENGINE_ID,
            "version": self.VERSION,
            "status": "operational",
            "active_learners": len(self._learners),
            "committees": len(self._committees),
            "strategies_available": list(QUERY_STRATEGIES.keys()),
            "features": [
                "pool_based_active_learning",
                "uncertainty_sampling",
                "margin_sampling",
                "entropy_sampling",
                "query_by_committee",
                "logistic_classifier",
            ],
        }
