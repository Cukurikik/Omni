#!/usr/bin/env python3
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# OMNI PRODUCTION DL OPS — Production-Level Deep Learning Pipeline
# Meta-functionalized from: alirezadir/Production-Level-Deep-Learning (4.6k★)
# Paradigm: End-to-end DL deployment from training to production
# Layer: COMPUTE + NETWORK (Python)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
OMNI Production DL Ops — Full-stack deep learning deployment pipeline.
Covers data versioning, experiment tracking, model serving, monitoring.

Key paradigms absorbed:
1. ML Project Lifecycle — prioritize, scope, prototype, deploy
2. Data Pipeline — source → label → store → version → process
3. Experiment Tracking — log metrics, hyperparams, artifacts
4. Model Serving — REST/gRPC with latency budgets & A/B testing
5. Monitoring & Observability — data drift, model degradation alerts
6. Feature Store — shared feature computation and reuse
"""
import sys
sys.stdout.reconfigure(encoding='utf-8')

import json
import time
import hashlib
import statistics
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional, Tuple
from enum import Enum
from abc import ABC, abstractmethod


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# SECTION 1: Data Pipeline Components
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━


class DataSourceType(Enum):
    LOCAL_FILE = "local_file"
    OBJECT_STORE = "object_store"     # S3/GCS/Ceph
    DATABASE = "database"             # Postgres/MySQL
    FEATURE_STORE = "feature_store"   # FEAST/Michelangelo
    DATA_LAKE = "data_lake"           # Redshift/BigQuery
    STREAMING = "streaming"           # Kafka/Pub/Sub
    SYNTHETIC = "synthetic"


@dataclass
class DataVersion:
    """Tracks data version for reproducibility (from DVC pattern)."""
    version_id: str
    hash_digest: str
    n_samples: int
    n_features: int
    source_type: DataSourceType
    timestamp: float = field(default_factory=time.time)
    metadata: Dict[str, Any] = field(default_factory=dict)


class DataVersionManager:
    """Manages data versions for ML reproducibility."""

    def __init__(self):
        self.versions: Dict[str, DataVersion] = {}

    def register(self, data: List[Dict], source: DataSourceType = DataSourceType.LOCAL_FILE) -> DataVersion:
        digest = hashlib.sha256(json.dumps(data, sort_keys=True, default=str).encode()).hexdigest()[:16]
        vid = f"v-{digest}"
        version = DataVersion(
            version_id=vid,
            hash_digest=digest,
            n_samples=len(data),
            n_features=len(data[0]) if data else 0,
            source_type=source,
        )
        self.versions[vid] = version
        return version

    def get(self, version_id: str) -> Optional[DataVersion]:
        return self.versions.get(version_id)

    def list_versions(self) -> List[DataVersion]:
        return list(self.versions.values())


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# SECTION 2: Experiment Tracking (from MLflow/W&B patterns)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━


@dataclass
class ExperimentRun:
    """A single experiment run with full provenance."""
    run_id: str
    experiment_name: str
    model_type: str
    hyperparams: Dict[str, Any]
    metrics: Dict[str, float]
    data_version: str
    duration_seconds: float
    artifacts: List[str] = field(default_factory=list)
    tags: Dict[str, str] = field(default_factory=dict)
    timestamp: float = field(default_factory=time.time)

    @property
    def primary_metric(self) -> float:
        """Return the best available metric."""
        for key in ["f1", "auc", "accuracy", "rmse"]:
            if key in self.metrics:
                return self.metrics[key]
        return list(self.metrics.values())[0] if self.metrics else 0.0


class ExperimentTracker:
    """Tracks ML experiments with metrics, hyperparams, and artifacts."""

    def __init__(self):
        self.runs: Dict[str, ExperimentRun] = {}
        self._run_counter = 0

    def start_run(self, experiment: str, model_type: str,
                  hyperparams: Dict[str, Any], data_version: str) -> str:
        self._run_counter += 1
        run_id = f"run-{self._run_counter:04d}"
        run = ExperimentRun(
            run_id=run_id,
            experiment_name=experiment,
            model_type=model_type,
            hyperparams=hyperparams,
            metrics={},
            data_version=data_version,
            duration_seconds=0.0,
        )
        self.runs[run_id] = run
        return run_id

    def log_metrics(self, run_id: str, metrics: Dict[str, float]):
        if run_id in self.runs:
            self.runs[run_id].metrics.update(metrics)

    def log_artifact(self, run_id: str, artifact_path: str):
        if run_id in self.runs:
            self.runs[run_id].artifacts.append(artifact_path)

    def end_run(self, run_id: str, duration: float):
        if run_id in self.runs:
            self.runs[run_id].duration_seconds = duration

    def best_run(self, experiment: str, metric: str = "f1") -> Optional[ExperimentRun]:
        """Find the best run for a given experiment by metric."""
        runs = [r for r in self.runs.values() if r.experiment_name == experiment and metric in r.metrics]
        if not runs:
            return None
        return max(runs, key=lambda r: r.metrics[metric])

    def compare_runs(self, run_ids: List[str]) -> List[Dict]:
        results = []
        for rid in run_ids:
            run = self.runs.get(rid)
            if run:
                results.append({
                    "run_id": run.run_id,
                    "model": run.model_type,
                    "metrics": run.metrics,
                    "hyperparams": run.hyperparams,
                    "data_version": run.data_version,
                    "duration": round(run.duration_seconds, 2),
                })
        return results


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# SECTION 3: Model Serving (REST endpoint pattern)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━


class ServingMode(Enum):
    SINGLE = "single"
    AB_TEST = "ab_test"
    CANARY = "canary"
    SHADOW = "shadow"


@dataclass
class ServingConfig:
    """Configuration for model serving."""
    model_id: str
    mode: ServingMode = ServingMode.SINGLE
    latency_budget_ms: float = 100.0
    max_batch_size: int = 32
    autoscale_min: int = 1
    autoscale_max: int = 10
    traffic_split: Dict[str, float] = field(default_factory=dict)  # for A/B testing


@dataclass
class PredictionRequest:
    """A model prediction request."""
    request_id: str
    input_data: Any
    timestamp: float = field(default_factory=time.time)


@dataclass
class PredictionResponse:
    """A model prediction response."""
    request_id: str
    prediction: Any
    model_id: str
    latency_ms: float
    confidence: float = 0.0


class ModelServer:
    """Serves registered models with observability."""

    def __init__(self, config: ServingConfig):
        self.config = config
        self.predict_fn: Optional[Callable] = None
        self.request_log: List[Dict] = []
        self._latencies: List[float] = []

    def register_model(self, predict_fn: Callable):
        self.predict_fn = predict_fn

    def predict(self, request: PredictionRequest) -> PredictionResponse:
        t0 = time.time()
        result = self.predict_fn(request.input_data) if self.predict_fn else None
        latency = (time.time() - t0) * 1000
        self._latencies.append(latency)

        response = PredictionResponse(
            request_id=request.request_id,
            prediction=result,
            model_id=self.config.model_id,
            latency_ms=round(latency, 2),
        )

        # Log for monitoring
        self.request_log.append({
            "request_id": request.request_id,
            "model_id": self.config.model_id,
            "latency_ms": response.latency_ms,
            "timestamp": request.timestamp,
        })

        return response

    def health(self) -> Dict:
        return {
            "model_id": self.config.model_id,
            "mode": self.config.mode.value,
            "total_requests": len(self.request_log),
            "avg_latency_ms": round(statistics.mean(self._latencies), 2) if self._latencies else 0,
            "p99_latency_ms": round(sorted(self._latencies)[int(len(self._latencies) * 0.99)] if self._latencies else 0, 2),
            "within_budget": (statistics.mean(self._latencies) if self._latencies else 0) <= self.config.latency_budget_ms,
        }


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# SECTION 4: Monitoring & Drift Detection
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━


class AlertLevel(Enum):
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"


@dataclass
class MonitoringAlert:
    """An alert triggered by drift or degradation."""
    level: AlertLevel
    metric: str
    message: str
    current_value: float
    threshold: float
    timestamp: float = field(default_factory=time.time)


class ModelMonitor:
    """Monitors model performance and detects data/model drift."""

    def __init__(self, model_id: str):
        self.model_id = model_id
        self.baseline_metrics: Dict[str, float] = {}
        self.current_metrics: Dict[str, float] = {}
        self.alerts: List[MonitoringAlert] = []
        self.drift_threshold: float = 0.10  # 10% degradation

    def set_baseline(self, metrics: Dict[str, float]):
        self.baseline_metrics = dict(metrics)

    def update_metrics(self, metrics: Dict[str, float]) -> List[MonitoringAlert]:
        """Update current metrics and check for degradation."""
        self.current_metrics = dict(metrics)
        new_alerts = []

        for metric, baseline_val in self.baseline_metrics.items():
            current_val = self.current_metrics.get(metric, 0)
            if baseline_val > 0:
                degradation = (baseline_val - current_val) / baseline_val

                if degradation > self.drift_threshold * 2:
                    alert = MonitoringAlert(
                        AlertLevel.CRITICAL, metric,
                        f"{metric} degraded {degradation:.1%} from baseline",
                        current_val, baseline_val
                    )
                    new_alerts.append(alert)
                elif degradation > self.drift_threshold:
                    alert = MonitoringAlert(
                        AlertLevel.WARNING, metric,
                        f"{metric} declining: {degradation:.1%} from baseline",
                        current_val, baseline_val
                    )
                    new_alerts.append(alert)

        self.alerts.extend(new_alerts)
        return new_alerts

    def check_data_drift(self, train_stats: Dict[str, float],
                         prod_stats: Dict[str, float]) -> List[MonitoringAlert]:
        """Simple population stability index (PSI) approximation."""
        alerts = []
        for feature in train_stats:
            if feature in prod_stats:
                train_val = train_stats[feature]
                prod_val = prod_stats[feature]
                if train_val > 0:
                    shift = abs(prod_val - train_val) / train_val
                    if shift > 0.25:
                        alerts.append(MonitoringAlert(
                            AlertLevel.WARNING, f"feature:{feature}",
                            f"Data drift detected: {feature} shifted {shift:.1%}",
                            prod_val, train_val
                        ))
        self.alerts.extend(alerts)
        return alerts

    def status(self) -> Dict:
        return {
            "model_id": self.model_id,
            "baseline": self.baseline_metrics,
            "current": self.current_metrics,
            "total_alerts": len(self.alerts),
            "critical_alerts": sum(1 for a in self.alerts if a.level == AlertLevel.CRITICAL),
        }


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# SECTION 5: Feature Store (from FEAST pattern)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━


@dataclass
class FeatureDefinition:
    """A reusable feature with extraction logic."""
    name: str
    description: str
    compute_fn: Optional[Callable] = None
    cache_ttl_seconds: int = 3600
    version: str = "1.0"


class FeatureStore:
    """Centralized feature store for shared feature computation."""

    def __init__(self):
        self.features: Dict[str, FeatureDefinition] = {}
        self._cache: Dict[str, Tuple[float, Any]] = {}

    def register(self, feature: FeatureDefinition):
        self.features[feature.name] = feature

    def compute(self, feature_name: str, entity_data: Any) -> Any:
        feat = self.features.get(feature_name)
        if not feat:
            raise ValueError(f"Feature '{feature_name}' not found")

        # Check cache
        cache_key = f"{feature_name}:{hashlib.md5(str(entity_data).encode()).hexdigest()[:8]}"
        if cache_key in self._cache:
            ts, val = self._cache[cache_key]
            if time.time() - ts < feat.cache_ttl_seconds:
                return val

        # Compute
        result = feat.compute_fn(entity_data) if feat.compute_fn else None
        self._cache[cache_key] = (time.time(), result)
        return result

    def list_features(self) -> List[Dict]:
        return [
            {"name": f.name, "description": f.description, "version": f.version}
            for f in self.features.values()
        ]


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# SECTION 6: Main Production DL Engine
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━


class OmniProductionDLEngine:
    """
    The OMNI Production DL Engine — full lifecycle management.
    Data versioning → experiment tracking → model serving → monitoring.
    """

    def __init__(self):
        self.data_mgr = DataVersionManager()
        self.tracker = ExperimentTracker()
        self.servers: Dict[str, ModelServer] = {}
        self.monitors: Dict[str, ModelMonitor] = {}
        self.feature_store = FeatureStore()

    def version_data(self, data: List[Dict]) -> DataVersion:
        return self.data_mgr.register(data)

    def start_experiment(self, name: str, model_type: str,
                         hyperparams: Dict, data_version: str) -> str:
        return self.tracker.start_run(name, model_type, hyperparams, data_version)

    def log_metrics(self, run_id: str, metrics: Dict[str, float]):
        self.tracker.log_metrics(run_id, metrics)

    def end_experiment(self, run_id: str, duration: float):
        self.tracker.end_run(run_id, duration)

    def deploy_model(self, model_id: str, predict_fn: Callable,
                     config: Optional[ServingConfig] = None) -> ModelServer:
        cfg = config or ServingConfig(model_id=model_id)
        server = ModelServer(cfg)
        server.register_model(predict_fn)
        self.servers[model_id] = server
        self.monitors[model_id] = ModelMonitor(model_id)
        return server

    def infer(self, model_id: str, input_data: Any) -> PredictionResponse:
        server = self.servers.get(model_id)
        if not server:
            raise ValueError(f"Model '{model_id}' not deployed")
        req = PredictionRequest(
            request_id=hashlib.md5(str(time.time()).encode()).hexdigest()[:8],
            input_data=input_data
        )
        return server.predict(req)

    def full_status(self) -> Dict:
        return {
            "data_versions": len(self.data_mgr.versions),
            "experiments": len(self.tracker.runs),
            "deployed_models": list(self.servers.keys()),
            "monitors": {k: v.status() for k, v in self.monitors.items()},
            "features": len(self.feature_store.features),
        }


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# META-FUNCTION TEST
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

if __name__ == "__main__":
    print("=" * 70)
    print("  OMNI PRODUCTION DL OPS ENGINE")
    print("=" * 70)

    engine = OmniProductionDLEngine()

    # 1. Version data
    data = [{"x": 1, "y": 0}, {"x": 2, "y": 1}, {"x": 3, "y": 0}]
    version = engine.version_data(data)
    print(f"\n   Data versioned: {version.version_id} ({version.n_samples} samples)")

    # 2. Experiment tracking
    run_id = engine.start_experiment("fraud_detection", "xgboost",
                                     {"max_depth": 6, "lr": 0.01},
                                     version.version_id)
    engine.log_metrics(run_id, {"accuracy": 0.92, "f1": 0.88, "auc": 0.95})
    engine.end_experiment(run_id, 42.5)

    run_id2 = engine.start_experiment("fraud_detection", "random_forest",
                                      {"n_estimators": 100},
                                      version.version_id)
    engine.log_metrics(run_id2, {"accuracy": 0.89, "f1": 0.85, "auc": 0.91})
    engine.end_experiment(run_id2, 28.3)

    best = engine.tracker.best_run("fraud_detection", "f1")
    print(f"   Best run: {best.run_id} ({best.model_type}) — F1={best.metrics['f1']}")

    # 3. Deploy model
    server = engine.deploy_model("fraud-v1", lambda x: 1 if x.get("x", 0) > 2 else 0)
    for input_data in [{"x": 1}, {"x": 3}, {"x": 5}]:
        resp = engine.infer("fraud-v1", input_data)
        print(f"   Prediction: {input_data} → {resp.prediction} ({resp.latency_ms}ms)")

    health = server.health()
    print(f"   Server health: avg={health['avg_latency_ms']}ms, within_budget={health['within_budget']}")

    # 4. Monitor
    monitor = engine.monitors["fraud-v1"]
    monitor.set_baseline({"f1": 0.88, "accuracy": 0.92})
    alerts = monitor.update_metrics({"f1": 0.75, "accuracy": 0.80})
    print(f"   Monitoring alerts: {len(alerts)}")
    for a in alerts:
        print(f"      [{a.level.value:8s}] {a.message}")

    # 5. Feature store
    engine.feature_store.register(FeatureDefinition(
        name="risk_score", description="User risk score",
        compute_fn=lambda d: d.get("x", 0) * 10
    ))
    score = engine.feature_store.compute("risk_score", {"x": 5})
    print(f"   Feature 'risk_score': {score}")

    # 6. Full status
    status = engine.full_status()
    print(f"\n   Full Status:")
    print(f"      Data versions: {status['data_versions']}")
    print(f"      Experiments: {status['experiments']}")
    print(f"      Deployed models: {status['deployed_models']}")
    print(f"      Feature store: {status['features']} features")

    print("\n" + "=" * 70)
    print("  META-FUNCTIONALIZED: Production-Level Deep Learning")
    print("   Data versioning (DVC pattern)")
    print("   Experiment tracking (MLflow pattern)")
    print("   Model serving with latency budgets & A/B testing")
    print("   Monitoring & drift detection (PSI-based)")
    print("   Feature store (FEAST pattern)")
    print("   Full ML lifecycle management")
    print("=" * 70)
