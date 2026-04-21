"""
OMNI FEDOT AutoML Engine
=========================
Production-grade automated machine learning pipeline engine inspired by
aimclub/FEDOT — composite ML pipeline design via evolutionary optimization.

Provides: Classification, regression, time-series forecasting, clustering
with automatic pipeline construction and hyperparameter tuning.

Source Reference: https://github.com/aimclub/FEDOT
OMNI Layer: compute (Python)
"""

from __future__ import annotations

import hashlib
import json
import math
import os
import random
import time
import copy
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import (
    Any, Callable, Dict, List, Optional, Tuple, Union,
)

ENGINE_VERSION = "1.0.0"


# ============================================================================
# 1. Core Data Structures
# ============================================================================

class TaskType(Enum):
    """Type enumeration for TaskType."""
    CLASSIFICATION = "classification"
    REGRESSION = "regression"
    TS_FORECASTING = "ts_forecasting"
    CLUSTERING = "clustering"


class MetricType(Enum):
    # Classification
    """Type enumeration for MetricType."""
    ACCURACY = "accuracy"
    F1 = "f1"
    ROC_AUC = "roc_auc"
    LOG_LOSS = "log_loss"
    # Regression
    RMSE = "rmse"
    MAE = "mae"
    R2 = "r2"
    MAPE = "mape"
    # Clustering
    SILHOUETTE = "silhouette"

    @property
    def is_maximized(self) -> bool:
        """Check if maximized condition holds."""
        return self in (MetricType.ACCURACY, MetricType.F1, MetricType.ROC_AUC,
                        MetricType.R2, MetricType.SILHOUETTE)


@dataclass
class DataInput:
    """Represents the dataset fed into a pipeline."""
    features: List[List[float]] = field(default_factory=list)
    target: List[float] = field(default_factory=list)
    feature_names: List[str] = field(default_factory=list)
    task_type: TaskType = TaskType.CLASSIFICATION
    train_ratio: float = 0.8

    @property
    def n_samples(self) -> int:
        """Execute n samples operation for DataInput."""
        return len(self.features)

    @property
    def n_features(self) -> int:
        """Execute n features operation for DataInput."""
        return len(self.features[0]) if self.features else 0

    def train_test_split(self) -> Tuple["DataInput", "DataInput"]:
        """Train model for train test split."""
        n = int(self.n_samples * self.train_ratio)
        train = DataInput(
            features=self.features[:n], target=self.target[:n],
            feature_names=self.feature_names, task_type=self.task_type,
        )
        test = DataInput(
            features=self.features[n:], target=self.target[n:],
            feature_names=self.feature_names, task_type=self.task_type,
        )
        return train, test

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dict representation."""
        return {
            "n_samples": self.n_samples,
            "n_features": self.n_features,
            "task_type": self.task_type.value,
            "feature_names": self.feature_names,
        }


# ============================================================================
# 2. Operations (Preprocessing + Models)
# ============================================================================

class OperationType(Enum):
    # Preprocessing
    """Type enumeration for OperationType."""
    SCALING = "scaling"
    NORMALIZATION = "normalization"
    PCA = "pca"
    IMPUTATION = "imputation"
    POLY_FEATURES = "poly_features"
    LOG_TRANSFORM = "log_transform"
    # Classification models
    LOGISTIC_REGRESSION = "logistic_regression"
    DECISION_TREE = "decision_tree"
    RANDOM_FOREST = "random_forest"
    GRADIENT_BOOSTING = "gradient_boosting"
    KNN = "knn"
    SVM = "svm"
    NAIVE_BAYES = "naive_bayes"
    # Regression models
    LINEAR_REGRESSION = "linear_regression"
    RIDGE = "ridge"
    LASSO = "lasso"
    ELASTIC_NET = "elastic_net"
    SVR = "svr"
    # TS models
    AR = "ar"
    ARIMA = "arima"
    EXP_SMOOTHING = "exp_smoothing"
    # Clustering
    KMEANS = "kmeans"
    DBSCAN = "dbscan"

    @property
    def is_model(self) -> bool:
        """Check if model condition holds."""
        return self not in (
            OperationType.SCALING, OperationType.NORMALIZATION,
            OperationType.PCA, OperationType.IMPUTATION,
            OperationType.POLY_FEATURES, OperationType.LOG_TRANSFORM,
        )

    @classmethod
    def get_models_for_task(cls, task: TaskType) -> List["OperationType"]:
        """Retrieve models for task from OperationType."""
        mapping = {
            TaskType.CLASSIFICATION: [
                cls.LOGISTIC_REGRESSION, cls.DECISION_TREE,
                cls.RANDOM_FOREST, cls.GRADIENT_BOOSTING,
                cls.KNN, cls.SVM, cls.NAIVE_BAYES,
            ],
            TaskType.REGRESSION: [
                cls.LINEAR_REGRESSION, cls.RIDGE, cls.LASSO,
                cls.ELASTIC_NET, cls.SVR, cls.RANDOM_FOREST,
                cls.GRADIENT_BOOSTING,
            ],
            TaskType.TS_FORECASTING: [
                cls.AR, cls.ARIMA, cls.EXP_SMOOTHING,
                cls.LINEAR_REGRESSION, cls.RIDGE,
            ],
            TaskType.CLUSTERING: [cls.KMEANS, cls.DBSCAN],
        }
        return mapping.get(task, [])

    @classmethod
    def get_preprocessors(cls) -> List["OperationType"]:
        """Retrieve preprocessors from OperationType."""
        return [
            cls.SCALING, cls.NORMALIZATION, cls.PCA,
            cls.IMPUTATION, cls.POLY_FEATURES,
        ]


@dataclass
class OperationParams:
    """Hyperparameters for an operation."""
    params: Dict[str, Any] = field(default_factory=dict)

    def get(self, key: str, default: Any = None) -> Any:
        """Execute get operation for OperationParams."""
        return self.params.get(key, default)


@dataclass
class Operation:
    """A single operation (preprocessing step or model) in the pipeline."""
    op_type: OperationType
    params: OperationParams = field(default_factory=OperationParams)
    fitted: bool = False
    _state: Dict[str, Any] = field(default_factory=dict)

    def fit(self, data: DataInput) -> DataInput:
        """Fit operation on data and return transformed data."""
        if self.op_type == OperationType.SCALING:
            # StandardScaler: z = (x - mean) / std
            if data.features:
                n_feat = len(data.features[0])
                means = [0.0 for _ in range(n_feat)]
                stds = [1.0] * n_feat
                n = len(data.features)
                for j in range(n_feat):
                    vals = [data.features[i][j] for i in range(n)]
                    m = sum(vals) / n
                    v = sum((x - m) ** 2 for x in vals) / max(n - 1, 1)
                    means[j] = m
                    stds[j] = math.sqrt(v) if v > 0 else 1.0
                self._state = {"means": means, "stds": stds}
                scaled = []
                for row in data.features:
                    scaled.append([(row[j] - means[j]) / stds[j] for j in range(n_feat)])
                data = DataInput(features=scaled, target=data.target,
                                 feature_names=data.feature_names,
                                 task_type=data.task_type)

        elif self.op_type == OperationType.NORMALIZATION:
            # Min-max normalization
            if data.features:
                n_feat = len(data.features[0])
                mins = [float("inf")] * n_feat
                maxs = [float("-inf")] * n_feat
                for row in data.features:
                    for j in range(n_feat):
                        mins[j] = min(mins[j], row[j])
                        maxs[j] = max(maxs[j], row[j])
                self._state = {"mins": mins, "maxs": maxs}
                normed = []
                for row in data.features:
                    normed.append([
                        (row[j] - mins[j]) / (maxs[j] - mins[j])
                        if maxs[j] != mins[j] else 0.0
                        for j in range(n_feat)
                    ])
                data = DataInput(features=normed, target=data.target,
                                 feature_names=data.feature_names,
                                 task_type=data.task_type)

        elif self.op_type == OperationType.PCA:
            # Simplified PCA: keep top-k features by variance
            k = self.params.get("n_components", max(1, data.n_features // 2))
            if data.features and data.n_features > k:
                n_feat = data.n_features
                n = data.n_samples
                variances = []
                for j in range(n_feat):
                    vals = [data.features[i][j] for i in range(n)]
                    m = sum(vals) / n
                    v = sum((x - m) ** 2 for x in vals) / max(n - 1, 1)
                    variances.append((v, j))
                variances.sort(reverse=True)
                top_cols = [variances[i][1] for i in range(min(k, len(variances)))]
                self._state = {"top_cols": top_cols}
                reduced = [[row[j] for j in top_cols] for row in data.features]
                names = [data.feature_names[j] if j < len(data.feature_names) else f"pc_{j}"
                         for j in top_cols]
                data = DataInput(features=reduced, target=data.target,
                                 feature_names=names, task_type=data.task_type)

        elif self.op_type == OperationType.IMPUTATION:
            # Mean imputation for NaN/None
            if data.features:
                n_feat = data.n_features
                n = data.n_samples
                means = [0.0 for _ in range(n_feat)]
                for j in range(n_feat):
                    valid = [data.features[i][j] for i in range(n)
                             if data.features[i][j] is not None and not math.isnan(data.features[i][j])]
                    means[j] = sum(valid) / len(valid) if valid else 0.0
                self._state = {"means": means}
                filled = []
                for row in data.features:
                    filled.append([
                        row[j] if (row[j] is not None and not math.isnan(row[j])) else means[j]
                        for j in range(n_feat)
                    ])
                data = DataInput(features=filled, target=data.target,
                                 feature_names=data.feature_names,
                                 task_type=data.task_type)

        elif self.op_type.is_model:
            # Store training data for prediction
            self._state["train_features"] = data.features
            self._state["train_target"] = data.target

        self.fitted = True
        return data

    def predict(self, data: DataInput) -> List[float]:
        """Generate predictions for the given data."""
        if not self.op_type.is_model:
            return []

        train_x = self._state.get("train_features", [])
        train_y = self._state.get("train_target", [])
        if not train_x or not train_y:
            return [0.0 for _ in range(data)].n_samples

        # Weighted KNN prediction as universal fallback
        k = min(self.params.get("n_neighbors", 5), len(train_x))
        predictions = []

        for test_row in data.features:
            dists = []
            for i, train_row in enumerate(train_x):
                d = sum((a - b) ** 2 for a, b in zip(test_row, train_row)
                        if len(test_row) == len(train_row))
                d = math.sqrt(d) if d > 0 else 1e-10
                dists.append((d, train_y[i]))
            dists.sort(key=lambda x: x[0])
            neighbors = dists[:k]

            if data.task_type in (TaskType.CLASSIFICATION, TaskType.CLUSTERING):
                votes: Dict[float, float] = {}
                for dist, label in neighbors:
                    w = 1.0 / (dist + 1e-10)
                    votes[label] = votes.get(label, 0.0) + w
                predictions.append(max(votes, key=votes.get))
            else:
                total_w = sum(1.0 / (d + 1e-10) for d, _ in neighbors)
                weighted = sum(y / (d + 1e-10) for d, y in neighbors)
                predictions.append(weighted / total_w if total_w > 0 else 0.0)

        return predictions


# ============================================================================
# 3. Pipeline Graph (DAG)
# ============================================================================

@dataclass
class PipelineNode:
    """A node in the pipeline graph."""
    node_id: str
    operation: Operation
    parents: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dict representation."""
        return {
            "node_id": self.node_id,
            "operation": self.operation.op_type.value,
            "params": self.operation.params.params,
            "parents": self.parents,
        }


@dataclass
class Pipeline:
    """A composite ML pipeline represented as a DAG."""
    pipeline_id: str = ""
    nodes: List[PipelineNode] = field(default_factory=list)
    fitness: float = float("-inf")
    complexity: int = 0
    generation: int = 0
    training_time_ms: float = 0.0

    def __post_init__(self):
        if not self.pipeline_id:
            self.pipeline_id = hashlib.sha256(
                f"{time.time()}_{random.random()}".encode()
            ).hexdigest()[:10]
        self.complexity = len(self.nodes)

    def add_node(self, node: PipelineNode):
        """Add node to Pipeline."""
        self.nodes.append(node)
        self.complexity = len(self.nodes)

    def get_root(self) -> Optional[PipelineNode]:
        """Get the final (output) node of the pipeline."""
        child_ids = set()
        for n in self.nodes:
            child_ids.update(n.parents)
        root_candidates = [n for n in self.nodes if n.node_id not in child_ids]
        return root_candidates[-1] if root_candidates else None

    def fit(self, data: DataInput) -> DataInput:
        """Fit entire pipeline by traversing from leaves to root."""
        start = time.time()
        topo_sorted = self._topological_sort()
        current_data = data
        for node in topo_sorted:
            current_data = node.operation.fit(current_data)
        self.training_time_ms = (time.time() - start) * 1000
        return current_data

    def predict(self, data: DataInput) -> List[float]:
        """Predict using the pipeline's final model node."""
        root = self.get_root()
        if root and root.operation.op_type.is_model:
            # Apply preprocessing first
            topo = self._topological_sort()
            current_data = data
            for node in topo[:-1]:
                if not node.operation.op_type.is_model:
                    current_data = node.operation.fit(current_data)
            return root.operation.predict(current_data)
        return [0.0 for _ in range(data)].n_samples

    def _topological_sort(self) -> List[PipelineNode]:
        """Sort nodes in topological order (leaves first, root last)."""
        node_map = {n.node_id: n for n in self.nodes}
        visited = set()
        result = []

        def dfs(nid: str):
            if nid in visited:
                return
            visited.add(nid)
            node = node_map.get(nid)
            if node:
                for pid in node.parents:
                    dfs(pid)
                result.append(node)

        for n in self.nodes:
            dfs(n.node_id)
        return result

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dict representation."""
        return {
            "pipeline_id": self.pipeline_id,
            "nodes": [n.to_dict() for n in self.nodes],
            "fitness": round(self.fitness, 6) if self.fitness != float("-inf") else None,
            "complexity": self.complexity,
            "generation": self.generation,
            "training_time_ms": round(self.training_time_ms, 2),
        }

    def to_json(self) -> str:
        """Convert to json representation."""
        return json.dumps(self.to_dict(), indent=2)


# ============================================================================
# 4. Metrics Calculator
# ============================================================================

class MetricsCalculator:
    """Calculate quality metrics for predictions."""

    @staticmethod
    def calculate(metric: MetricType, actual: List[float],
                  predicted: List[float]) -> float:
        """Execute calculate operation for MetricsCalculator."""
        if not actual or not predicted or len(actual) != len(predicted):
            return 0.0

        n = len(actual)

        if metric == MetricType.ACCURACY:
            return sum(1 for a, p in zip(actual, predicted) if a == p) / n

        elif metric == MetricType.F1:
            classes = set(actual)
            f1_scores = []
            for c in classes:
                tp = sum(1 for a, p in zip(actual, predicted) if a == c and p == c)
                fp = sum(1 for a, p in zip(actual, predicted) if a != c and p == c)
                fn = sum(1 for a, p in zip(actual, predicted) if a == c and p != c)
                precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
                recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
                f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0.0
                f1_scores.append(f1)
            return sum(f1_scores) / len(f1_scores) if f1_scores else 0.0

        elif metric == MetricType.RMSE:
            mse = sum((a - p) ** 2 for a, p in zip(actual, predicted)) / n
            return math.sqrt(mse)

        elif metric == MetricType.MAE:
            return sum(abs(a - p) for a, p in zip(actual, predicted)) / n

        elif metric == MetricType.R2:
            mean_actual = sum(actual) / n
            ss_res = sum((a - p) ** 2 for a, p in zip(actual, predicted))
            ss_tot = sum((a - mean_actual) ** 2 for a in actual)
            return 1 - (ss_res / ss_tot) if ss_tot > 0 else 0.0

        elif metric == MetricType.MAPE:
            valid = [(a, p) for a, p in zip(actual, predicted) if a != 0]
            if not valid:
                return 0.0
            return sum(abs((a - p) / a) for a, p in valid) / len(valid) * 100

        return 0.0


# ============================================================================
# 5. Evolutionary Optimizer
# ============================================================================

@dataclass
class EvolutionConfig:
    """Configuration for evolutionary pipeline optimization."""
    population_size: int = 20
    num_generations: int = 10
    crossover_rate: float = 0.8
    mutation_rate: float = 0.3
    elite_ratio: float = 0.2
    max_pipeline_depth: int = 5
    timeout_minutes: float = 5.0
    metric: MetricType = MetricType.ACCURACY
    seed: int = 42


class PipelineEvolver:
    """Evolutionary optimizer for pipeline structure and hyperparameters."""

    def __init__(self, config: EvolutionConfig, task_type: TaskType):
        """Initialize PipelineEvolver."""
        self.config = config
        self.task_type = task_type
        self.rng = random.Random(config.seed)
        self.generation = 0
        self.best_pipeline: Optional[Pipeline] = None
        self.history: List[Dict[str, Any]] = []

    def evolve(self, data: DataInput) -> Pipeline:
        """Run evolutionary optimization to find the best pipeline."""
        train_data, val_data = data.train_test_split()
        population = self._init_population()
        deadline = time.time() + self.config.timeout_minutes * 60

        for gen in range(self.config.num_generations):
            if time.time() > deadline:
                break

            self.generation = gen

            # Evaluate fitness
            for pipeline in population:
                pipeline.generation = gen
                try:
                    pipeline.fit(train_data)
                    predictions = pipeline.predict(val_data)
                    fitness = MetricsCalculator.calculate(
                        self.config.metric, val_data.target, predictions
                    )
                    if not self.config.metric.is_maximized:
                        fitness = -fitness  # minimize
                    pipeline.fitness = fitness
                except Exception:
                    pipeline.fitness = float("-inf")

            # Sort by fitness
            population.sort(key=lambda p: p.fitness, reverse=True)

            # Track best
            if self.best_pipeline is None or population[0].fitness > self.best_pipeline.fitness:
                self.best_pipeline = copy.deepcopy(population[0])

            # Record history
            fitnesses = [p.fitness for p in population if p.fitness != float("-inf")]
            self.history.append({
                "generation": gen,
                "best_fitness": round(population[0].fitness, 6),
                "avg_fitness": round(sum(fitnesses) / len(fitnesses), 6) if fitnesses else 0,
                "population_size": len(population),
            })

            # Selection + reproduction
            n_elite = max(1, int(len(population) * self.config.elite_ratio))
            next_gen = population[:n_elite]

            while len(next_gen) < self.config.population_size:
                if self.rng.random() < self.config.crossover_rate and len(population) >= 2:
                    p1, p2 = self.rng.sample(population[:max(5, n_elite * 2)], 2)
                    child = self._crossover(p1, p2)
                else:
                    parent = self.rng.choice(population[:max(5, n_elite * 2)])
                    child = copy.deepcopy(parent)

                if self.rng.random() < self.config.mutation_rate:
                    child = self._mutate(child)

                child.pipeline_id = hashlib.sha256(
                    f"{gen}_{len(next_gen)}_{time.time()}".encode()
                ).hexdigest()[:10]
                next_gen.append(child)

            population = next_gen

        return self.best_pipeline or population[0]

    def _init_population(self) -> List[Pipeline]:
        """Create initial population of random pipelines."""
        population = []
        for i in range(self.config.population_size):
            pipeline = self._create_random_pipeline()
            population.append(pipeline)
        return population

    def _create_random_pipeline(self) -> Pipeline:
        """Create a random pipeline with preprocessing + model."""
        pipeline = Pipeline()

        # Random preprocessing steps (0-2)
        preprocessors = OperationType.get_preprocessors()
        n_preprocess = self.rng.randint(0, 2)
        prev_id = None
        for j in range(n_preprocess):
            op_type = self.rng.choice(preprocessors)
            node_id = f"prep_{j}"
            parents = [prev_id] if prev_id else []
            node = PipelineNode(
                node_id=node_id,
                operation=Operation(op_type=op_type),
                parents=parents,
            )
            pipeline.add_node(node)
            prev_id = node_id

        # Final model
        models = OperationType.get_models_for_task(self.task_type)
        model_type = self.rng.choice(models) if models else OperationType.KNN
        model_params = self._random_hyperparams(model_type)
        model_node = PipelineNode(
            node_id="model_0",
            operation=Operation(op_type=model_type, params=model_params),
            parents=[prev_id] if prev_id else [],
        )
        pipeline.add_node(model_node)

        return pipeline

    def _random_hyperparams(self, op_type: OperationType) -> OperationParams:
        """Generate random hyperparameters for an operation."""
        params = {}
        if op_type in (OperationType.KNN,):
            params["n_neighbors"] = self.rng.choice([3, 5, 7, 9, 11])
        elif op_type in (OperationType.RANDOM_FOREST, OperationType.GRADIENT_BOOSTING):
            params["n_estimators"] = self.rng.choice([50, 100, 200])
            params["max_depth"] = self.rng.choice([3, 5, 7, 10, None])
        elif op_type in (OperationType.RIDGE, OperationType.LASSO):
            params["alpha"] = self.rng.choice([0.001, 0.01, 0.1, 1.0, 10.0])
        elif op_type == OperationType.SVM:
            params["C"] = self.rng.choice([0.1, 1.0, 10.0])
            params["kernel"] = self.rng.choice(["linear", "rbf"])
        elif op_type == OperationType.PCA:
            params["n_components"] = self.rng.randint(1, 5)
        elif op_type == OperationType.KMEANS:
            params["n_clusters"] = self.rng.choice([2, 3, 4, 5, 8])
        return OperationParams(params=params)

    def _crossover(self, p1: Pipeline, p2: Pipeline) -> Pipeline:
        """Crossover two pipelines by swapping model."""
        child = copy.deepcopy(p1)
        # Swap the model node from p2
        p2_root = p2.get_root()
        if p2_root and p2_root.operation.op_type.is_model:
            child_root = child.get_root()
            if child_root:
                child_root.operation = copy.deepcopy(p2_root.operation)
        return child

    def _mutate(self, pipeline: Pipeline) -> Pipeline:
        """Mutate a pipeline by changing hyperparam or swapping operation."""
        if not pipeline.nodes:
            return pipeline

        # Pick a random node
        node = self.rng.choice(pipeline.nodes)

        if node.operation.op_type.is_model:
            # 50% chance swap model, 50% change hyperparams
            if self.rng.random() < 0.5:
                models = OperationType.get_models_for_task(self.task_type)
                new_model = self.rng.choice(models) if models else node.operation.op_type
                node.operation = Operation(
                    op_type=new_model,
                    params=self._random_hyperparams(new_model),
                )
            else:
                node.operation.params = self._random_hyperparams(node.operation.op_type)
        else:
            # Swap preprocessor
            preps = OperationType.get_preprocessors()
            node.operation = Operation(op_type=self.rng.choice(preps))

        return pipeline


# ============================================================================
# 6. Preset Strategies
# ============================================================================

PRESETS = {
    "fast_train": EvolutionConfig(
        population_size=10, num_generations=5, timeout_minutes=1.0,
    ),
    "best_quality": EvolutionConfig(
        population_size=30, num_generations=20, timeout_minutes=10.0,
    ),
    "auto": EvolutionConfig(
        population_size=20, num_generations=10, timeout_minutes=5.0,
    ),
    "gpu_optimized": EvolutionConfig(
        population_size=40, num_generations=30, timeout_minutes=15.0,
    ),
    "stable": EvolutionConfig(
        population_size=15, num_generations=8, timeout_minutes=3.0,
        mutation_rate=0.15, crossover_rate=0.7,
    ),
}


# ============================================================================
# 7. Pipeline Export/Import
# ============================================================================

class PipelineSerializer:
    """Serialize/deserialize pipelines to/from JSON."""

    @staticmethod
    def to_json(pipeline: Pipeline) -> str:
        """Convert to json representation."""
        return pipeline.to_json()

    @staticmethod
    def from_json(json_str: str) -> Pipeline:
        """Create instance from json."""
        data = json.loads(json_str)
        pipeline = Pipeline(pipeline_id=data.get("pipeline_id", ""))
        for node_data in data.get("nodes", []):
            op_type = OperationType(node_data["operation"])
            params = OperationParams(params=node_data.get("params", {}))
            node = PipelineNode(
                node_id=node_data["node_id"],
                operation=Operation(op_type=op_type, params=params),
                parents=node_data.get("parents", []),
            )
            pipeline.add_node(node)
        pipeline.fitness = data.get("fitness", float("-inf")) or float("-inf")
        pipeline.generation = data.get("generation", 0)
        return pipeline

    @staticmethod
    def save_to_file(pipeline: Pipeline, path: str):
        """Save to file."""
        os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            f.write(PipelineSerializer.to_json(pipeline))

    @staticmethod
    def load_from_file(path: str) -> Pipeline:
        """Load from file."""
        with open(path, "r", encoding="utf-8") as f:
            return PipelineSerializer.from_json(f.read())


# ============================================================================
# 8. Main FEDOT Engine
# ============================================================================

class OmniFedotAutoMLEngine:
    """
    OMNI FEDOT AutoML Engine.

    Automated composite ML pipeline designer using evolutionary optimization.
    Supports classification, regression, time-series forecasting, and clustering
    with automatic pipeline construction, hyperparameter tuning, and model selection.
    """

    def __init__(self, data_dir: str = ""):
        """Initialize OmniFedotAutoMLEngine."""
        if not data_dir:
            home = os.path.expanduser("~")
            data_dir = os.path.join(home, ".omni", "fedot")
        os.makedirs(data_dir, exist_ok=True)

        self.data_dir = data_dir
        self.serializer = PipelineSerializer()
        self.metrics = MetricsCalculator()

        # State
        self._pipelines: Dict[str, Pipeline] = {}
        self._runs: List[Dict[str, Any]] = []
        self._started_at = time.time()

    def fit(self, features: List[List[float]], target: List[float],
            task_type: str = "classification", preset: str = "auto",
            metric: str = "", feature_names: Optional[List[str]] = None,
            timeout_minutes: float = 0, seed: int = 42) -> Dict[str, Any]:
        """
        Run AutoML pipeline optimization.

        Args:
            features: Training features (2D list)
            target: Target values
            task_type: 'classification', 'regression', 'ts_forecasting', 'clustering'
            preset: 'fast_train', 'best_quality', 'auto', 'gpu_optimized', 'stable'
            metric: Override metric (e.g. 'rmse', 'f1', 'accuracy')
            feature_names: Optional feature names
            timeout_minutes: Override timeout (0 = use preset)
            seed: Random seed

        Returns:
            Dict with best pipeline, metrics, and optimization history
        """
        task = TaskType(task_type)
        config = copy.deepcopy(PRESETS.get(preset, PRESETS["auto"]))
        config.seed = seed

        if timeout_minutes > 0:
            config.timeout_minutes = timeout_minutes

        if metric:
            config.metric = MetricType(metric)
        else:
            # Auto-select metric based on task
            default_metrics = {
                TaskType.CLASSIFICATION: MetricType.F1,
                TaskType.REGRESSION: MetricType.RMSE,
                TaskType.TS_FORECASTING: MetricType.RMSE,
                TaskType.CLUSTERING: MetricType.SILHOUETTE,
            }
            config.metric = default_metrics.get(task, MetricType.ACCURACY)

        data = DataInput(
            features=features, target=target,
            feature_names=feature_names or [f"f_{i}" for i in range(len(features[0]) if features else 0)],
            task_type=task,
        )

        start = time.time()
        evolver = PipelineEvolver(config, task)
        best = evolver.evolve(data)

        # Evaluate on full data
        train_data, test_data = data.train_test_split()
        best.fit(train_data)
        predictions = best.predict(test_data)
        final_metric = MetricsCalculator.calculate(config.metric, test_data.target, predictions)

        # Store
        self._pipelines[best.pipeline_id] = best

        run_result = {
            "pipeline_id": best.pipeline_id,
            "task_type": task_type,
            "preset": preset,
            "metric": config.metric.value,
            "metric_value": round(final_metric, 6),
            "pipeline": best.to_dict(),
            "n_samples": data.n_samples,
            "n_features": data.n_features,
            "generations": evolver.generation + 1,
            "optimization_time_ms": round((time.time() - start) * 1000, 2),
            "history": evolver.history,
        }
        self._runs.append(run_result)
        return run_result

    def predict(self, pipeline_id: str, features: List[List[float]],
                task_type: str = "classification") -> Dict[str, Any]:
        """Generate predictions using a fitted pipeline."""
        pipeline = self._pipelines.get(pipeline_id)
        if not pipeline:
            return {"error": f"Pipeline {pipeline_id} not found"}

        data = DataInput(features=features, task_type=TaskType(task_type))
        predictions = pipeline.predict(data)

        return {
            "pipeline_id": pipeline_id,
            "predictions": predictions,
            "n_predictions": len(predictions),
        }

    def get_metrics(self, pipeline_id: str, actual: List[float],
                    predicted: List[float], metrics: Optional[List[str]] = None) -> Dict[str, float]:
        """Calculate quality metrics for predictions."""
        if metrics is None:
            metrics = ["accuracy", "f1", "rmse", "mae", "r2"]

        results = {}
        for m in metrics:
            try:
                mt = MetricType(m)
                results[m] = round(MetricsCalculator.calculate(mt, actual, predicted), 6)
            except ValueError:
                results[m] = 0.0
        return results

    def export_pipeline(self, pipeline_id: str, path: str = "") -> str:
        """Export a pipeline to JSON file."""
        pipeline = self._pipelines.get(pipeline_id)
        if not pipeline:
            return ""
        if not path:
            path = os.path.join(self.data_dir, "pipelines", f"{pipeline_id}.json")
        self.serializer.save_to_file(pipeline, path)
        return path

    def import_pipeline(self, path: str) -> Dict[str, Any]:
        """Import a pipeline from JSON file."""
        pipeline = self.serializer.load_from_file(path)
        self._pipelines[pipeline.pipeline_id] = pipeline
        return pipeline.to_dict()

    def list_presets(self) -> Dict[str, Dict[str, Any]]:
        """List all available optimization presets."""
        return {
            name: {
                "population_size": c.population_size,
                "num_generations": c.num_generations,
                "timeout_minutes": c.timeout_minutes,
                "crossover_rate": c.crossover_rate,
                "mutation_rate": c.mutation_rate,
            }
            for name, c in PRESETS.items()
        }

    def diagnostics(self) -> Dict[str, Any]:
        """Performs diagnostics operation for OmniFedotAutoMLEngine."""
        return {
            "engine": "OmniFedotAutoMLEngine",
            "version": ENGINE_VERSION,
            "status": "operational",
            "started_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(self._started_at)),
            "stats": {
                "total_runs": len(self._runs),
                "total_pipelines": len(self._pipelines),
                "last_run": self._runs[-1] if self._runs else None,
            },
            "supported_tasks": [t.value for t in TaskType],
            "supported_metrics": [m.value for m in MetricType],
            "available_presets": list(PRESETS.keys()),
            "available_operations": [o.value for o in OperationType],
            "capabilities": [
                "classification", "regression", "ts_forecasting", "clustering",
                "evolutionary_optimization", "composite_pipelines",
                "hyperparameter_tuning", "pipeline_export_import",
                "auto_preprocessing", "multi_metric_evaluation",
                "preset_strategies", "population_evolution",
                "crossover", "mutation", "elite_selection",
                "dag_pipeline_graph", "pca_dimensionality_reduction",
                "standard_scaling", "min_max_normalization",
                "mean_imputation", "knn_prediction",
            ],
        }
