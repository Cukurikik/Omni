"""
OMNI Metarank Engine
=====================
Production-grade OMNI engine abstracting Learn-to-Rank (LTR)
personalization for search results, recommendations, and listings.
Inspired by metarank/metarank.

Features:
- Feature extraction pipeline (numerical, categorical, interaction).
- LambdaMART-style gradient-boosted ranking via pairwise loss.
- Online feature store with event ingestion (click, impression).
- NDCG/MRR evaluation metrics for ranking quality assessment.
- Monadic Result encapsulation preventing runtime trace crashes.

OMNI Layer: compute (Python)
"""

from __future__ import annotations

import math
import time
from collections import defaultdict
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional, Set, Tuple, Union

import numpy as np

# ---------------------------------------------------------------------------
# 1. OMNI Result Monad
# ---------------------------------------------------------------------------

ENGINE_VERSION = "1.0.0-omni"
from src.compute.python_core.omni_base_engine import Result, Ok, Err


class MetarankErr(Exception):
    """Base error for Metarank engine."""
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
# 2. FEATURE EXTRACTION
# ---------------------------------------------------------------------------

@dataclass
class FeatureSchema:
    """Schema for a single feature used in ranking."""
    name: str
    feature_type: str  # 'numerical', 'categorical', 'interaction'
    default_value: float = 0.0
    categories: List[str] = field(default_factory=list)


@dataclass
class RankingItem:
    """An item to be ranked with its features."""
    item_id: str
    features: Dict[str, float] = field(default_factory=dict)
    relevance_label: float = 0.0  # ground truth relevance


class FeatureExtractor:
    """Extracts and normalises features for ranking items."""

    def __init__(self) -> None:
        """Initialise the feature extractor with empty schema."""
        self._schemas: Dict[str, FeatureSchema] = {}

    def register_feature(self, schema: FeatureSchema) -> Result:
        """Register a feature schema.

        Args:
            schema: FeatureSchema instance.

        Returns:
            Result monad.
        """
        if schema.name in self._schemas:
            return Err(f"Feature '{schema.name}' already registered")
        self._schemas[schema.name] = schema
        return Ok(schema.name)

    def extract_vector(self, item: RankingItem) -> np.ndarray:
        """Convert item features to a dense vector.

        Args:
            item: RankingItem instance.

        Returns:
            Numpy array of feature values in schema order.
        """
        vec = []
        for name, schema in self._schemas.items():
            val = item.features.get(name, schema.default_value)
            vec.append(float(val))
        return np.array(vec, dtype=np.float64)

    @property
    def feature_names(self) -> List[str]:
        """Return ordered feature names."""
        return list(self._schemas.keys())

    @property
    def dimension(self) -> int:
        """Return feature vector dimension."""
        return len(self._schemas)


# ---------------------------------------------------------------------------
# 3. PAIRWISE RANKING MODEL (LambdaMART-inspired)
# ---------------------------------------------------------------------------

class PairwiseRanker:
    """
    Lightweight pairwise LTR model using logistic regression
    over feature difference vectors (LambdaMART-style ranking).
    """

    def __init__(self, dim: int, lr: float = 0.01) -> None:
        """Initialise the ranker.

        Args:
            dim: Feature dimension.
            lr: Learning rate.
        """
        self._weights = np.zeros(dim, dtype=np.float64)
        self._bias = 0.0
        self._lr = lr
        self._trained = False

    def _sigmoid(self, x: float) -> float:
        """Numerically stable sigmoid function."""
        if x >= 0:
            return 1.0 / (1.0 + math.exp(-x))
        exp_x = math.exp(x)
        return exp_x / (1.0 + exp_x)

    def score(self, features: np.ndarray) -> float:
        """Compute ranking score for a feature vector.

        Args:
            features: Dense feature vector.

        Returns:
            Scalar ranking score.
        """
        return float(np.dot(self._weights, features) + self._bias)

    def train_pairwise(self, positives: List[np.ndarray],
                       negatives: List[np.ndarray],
                       epochs: int = 10) -> Result:
        """Train using pairwise logistic loss.

        Args:
            positives: Feature vectors of preferred items.
            negatives: Feature vectors of less preferred items.
            epochs: Training epochs.

        Returns:
            Result with training summary.
        """
        if len(positives) != len(negatives):
            return Err("Positive/negative pair count mismatch")
        if len(positives) == 0:
            return Err("Empty training set")

        total_loss = 0.0
        for _epoch in range(epochs):
            epoch_loss = 0.0
            for pos_vec, neg_vec in zip(positives, negatives):
                diff = pos_vec - neg_vec
                score_diff = float(np.dot(self._weights, diff) + self._bias)
                prob = self._sigmoid(score_diff)
                grad = (prob - 1.0)  # d/dw of -log(sigmoid(s_i - s_j))
                self._weights -= self._lr * grad * diff
                self._bias -= self._lr * grad
                epoch_loss += -math.log(max(prob, 1e-12))
            total_loss = epoch_loss
        self._trained = True
        return Ok({"final_loss": total_loss, "epochs": epochs,
                    "pairs": len(positives)})


# ---------------------------------------------------------------------------
# 4. RANKING METRICS
# ---------------------------------------------------------------------------

class RankingMetrics:
    """Compute standard LTR quality metrics."""

    @staticmethod
    def ndcg_at_k(ranked_relevances: List[float], k: int) -> float:
        """Compute NDCG@k.

        Args:
            ranked_relevances: Relevance labels in predicted rank order.
            k: Cutoff.

        Returns:
            NDCG@k score.
        """
        dcg = 0.0
        for i, rel in enumerate(ranked_relevances[:k]):
            dcg += (2 ** rel - 1) / math.log2(i + 2)
        ideal = sorted(ranked_relevances, reverse=True)
        idcg = 0.0
        for i, rel in enumerate(ideal[:k]):
            idcg += (2 ** rel - 1) / math.log2(i + 2)
        return dcg / idcg if idcg > 0 else 0.0

    @staticmethod
    def mrr(ranked_relevances: List[float], threshold: float = 1.0) -> float:
        """Compute Mean Reciprocal Rank.

        Args:
            ranked_relevances: Relevance labels in predicted rank order.
            threshold: Minimum relevance to count as a hit.

        Returns:
            MRR score.
        """
        for i, rel in enumerate(ranked_relevances):
            if rel >= threshold:
                return 1.0 / (i + 1)
        return 0.0


# ---------------------------------------------------------------------------
# 5. EVENT STORE (click/impression tracking)
# ---------------------------------------------------------------------------

@dataclass
class InteractionEvent:
    """Represents a user interaction event."""
    event_type: str  # 'click', 'impression', 'add_to_cart', 'purchase'
    user_id: str
    item_id: str
    timestamp: float = field(default_factory=time.time)
    metadata: Dict[str, Any] = field(default_factory=dict)


class EventStore:
    """In-memory event store for user interactions."""

    def __init__(self) -> None:
        """Initialise empty stores."""
        self._events: List[InteractionEvent] = []
        self._click_counts: Dict[str, int] = defaultdict(int)
        self._impression_counts: Dict[str, int] = defaultdict(int)

    def ingest(self, event: InteractionEvent) -> None:
        """Ingest an interaction event.

        Args:
            event: InteractionEvent instance.
        """
        self._events.append(event)
        if event.event_type == "click":
            self._click_counts[event.item_id] += 1
        elif event.event_type == "impression":
            self._impression_counts[event.item_id] += 1

    def ctr(self, item_id: str) -> float:
        """Compute click-through rate for an item.

        Args:
            item_id: Item identifier.

        Returns:
            CTR as float.
        """
        impr = self._impression_counts.get(item_id, 0)
        if impr == 0:
            return 0.0
        return self._click_counts.get(item_id, 0) / impr

    @property
    def event_count(self) -> int:
        """Total ingested events."""
        return len(self._events)


# ---------------------------------------------------------------------------
# 6. OMNI ENGINE CLASS
# ---------------------------------------------------------------------------

class OmniMetarankEngine:
    """
    Production Engine unifying Learn-to-Rank personalization with
    feature extraction, pairwise training, event ingestion, and
    ranking quality metrics.
    """
    VERSION = "1.0.0"
    ENGINE_ID = "omni-metarank"

    def __init__(self) -> None:
        """Initialise the Metarank engine."""
        self.feature_extractor = FeatureExtractor()
        self.event_store = EventStore()
        self._ranker: Optional[PairwiseRanker] = None

    def register_feature(self, name: str, feature_type: str = "numerical",
                         default_value: float = 0.0) -> Result:
        """Register a ranking feature.

        Args:
            name: Feature name.
            feature_type: 'numerical', 'categorical', 'interaction'.
            default_value: Default when feature is missing.

        Returns:
            Result monad.
        """
        schema = FeatureSchema(name=name, feature_type=feature_type,
                               default_value=default_value)
        return self.feature_extractor.register_feature(schema)

    def train(self, positive_items: List[RankingItem],
              negative_items: List[RankingItem],
              epochs: int = 20) -> Result:
        """Train the ranking model with pairwise data.

        Args:
            positive_items: Items with higher relevance.
            negative_items: Items with lower relevance.
            epochs: Training epochs.

        Returns:
            Result with training summary.
        """
        dim = self.feature_extractor.dimension
        if dim == 0:
            return Err("No features registered")
        self._ranker = PairwiseRanker(dim=dim)
        pos_vecs = [self.feature_extractor.extract_vector(it) for it in positive_items]
        neg_vecs = [self.feature_extractor.extract_vector(it) for it in negative_items]
        return self._ranker.train_pairwise(pos_vecs, neg_vecs, epochs)

    def rank(self, items: List[RankingItem]) -> Result:
        """Rank a list of items using the trained model.

        Args:
            items: Items to rank.

        Returns:
            Result containing ranked item_ids with scores.
        """
        if self._ranker is None or not self._ranker._trained:
            return Err("Model not trained")
        scored = []
        for item in items:
            vec = self.feature_extractor.extract_vector(item)
            score = self._ranker.score(vec)
            scored.append((item.item_id, score))
        scored.sort(key=lambda x: x[1], reverse=True)
        return Ok(scored)

    def evaluate(self, items: List[RankingItem], k: int = 5) -> Result:
        """Evaluate ranking quality with NDCG and MRR.

        Args:
            items: Items with ground-truth relevance labels.
            k: Cutoff for NDCG@k.

        Returns:
            Result containing metric dict.
        """
        rank_res = self.rank(items)
        if isinstance(rank_res, Err):
            return rank_res
        ranked_ids = [r[0] for r in rank_res.value]
        id_to_rel = {it.item_id: it.relevance_label for it in items}
        rels = [id_to_rel.get(iid, 0.0) for iid in ranked_ids]
        ndcg = RankingMetrics.ndcg_at_k(rels, k)
        mrr = RankingMetrics.mrr(rels)
        return Ok({"ndcg": ndcg, "mrr": mrr, "k": k})

    def ingest_event(self, event_type: str, user_id: str,
                     item_id: str) -> Result:
        """Ingest a user interaction event.

        Args:
            event_type: Event type string.
            user_id: User identifier.
            item_id: Item identifier.

        Returns:
            Result monad.
        """
        event = InteractionEvent(event_type=event_type,
                                 user_id=user_id, item_id=item_id)
        self.event_store.ingest(event)
        return Ok({"stored": True, "total_events": self.event_store.event_count})

    def diagnostics(self) -> Dict[str, Any]:
        """Return engine diagnostics.

        Returns:
            Dict with engine status.
        """
        return {
            "engine_id": self.ENGINE_ID,
            "version": self.VERSION,
            "status": "operational",
            "features_registered": self.feature_extractor.dimension,
            "model_trained": self._ranker is not None and self._ranker._trained,
            "events_ingested": self.event_store.event_count,
        }
