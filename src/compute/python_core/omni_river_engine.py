"""
OMNI River Engine — Production Hard-Code

Executes real River online/streaming ML pipelines using native
river.tree.HoeffdingTreeClassifier, river.preprocessing.StandardScaler,
river.compose.Pipeline, and river.metrics to incrementally learn from
data streams one sample at a time.

References:
    - https://github.com/online-ml/river
    - river.tree.HoeffdingTreeClassifier
    - river.compose.Pipeline
    - river.datasets.Phishing
"""

import asyncio
import logging
import time
import uuid
from typing import Any, Dict, Optional

import numpy as np
from river import compose, datasets, metrics, preprocessing, tree



ENGINE_VERSION = "1.0.0-omni"
from src.compute.python_core.omni_base_engine import Result, Ok, Err

class OmniRiverEngine:
    """
    Omni River Engine (Production Hard-Code).

    Constructs actual River streaming ML pipelines and trains them
    incrementally using learn_one / predict_one on real data streams.
    No batch loading — strictly one-sample-at-a-time online learning.

    Attributes:
        config: Engine configuration dictionary.
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None) -> None:
        """
        Initializes the River streaming engine.

        Args:
            config: Optional configuration overrides.
        """
        self.config = config or {}
        self.logger = logging.getLogger(self.__class__.__name__)
        self._is_active: bool = False
        self._engine_id: str = str(uuid.uuid4())
        self._start_time: float = 0.0

    async def initialize(self) -> Dict[str, Any]:
        """
        Monadic initialization — smoke-tests a River pipeline.

        Returns:
            Dict with status, engine_id, and message.
        """
        try:
            self.logger.info(
                f"[{self.__class__.__name__}] Constructing native River pipeline..."
            )

            # Smoke-test: build a real pipeline and learn from one sample
            pipeline = compose.Pipeline(
                preprocessing.StandardScaler(),
                tree.HoeffdingTreeClassifier(),
            )
            pipeline.learn_one({"a": 1.0, "b": 2.0}, 1)
            pred = pipeline.predict_one({"a": 1.0, "b": 2.0})
            assert pred is not None, "River smoke-test prediction was None"

            self._is_active = True
            self._start_time = time.time()
            return {
                "status": "success",
                "engine_id": self._engine_id,
                "message": "River online-ML engine initialized natively.",
            }
        except Exception as e:
            self.logger.error(f"Initialization failure: {e}")
            return {"status": "error", "engine_id": self._engine_id, "error": str(e)}

    async def _execute_online_training(
        self, num_samples: int, num_features: int
    ) -> Dict[str, Any]:
        """
        Builds a real River pipeline and streams synthetic data through it.

        Args:
            num_samples: Number of streaming observations.
            num_features: Dimensionality of each observation.

        Returns:
            Dict with training results and final metric values.

        Raises:
            RuntimeError: If execution fails.
        """
        st = time.time()

        try:
            # Build native pipeline
            model = compose.Pipeline(
                preprocessing.StandardScaler(),
                tree.HoeffdingTreeClassifier(),
            )

            accuracy = metrics.Accuracy()
            f1 = metrics.F1()

            np.random.seed(42)

            correct_count = 0
            for i in range(num_samples):
                # Generate one sample at a time (true streaming)
                x = {f"f_{j}": float(np.random.randn()) for j in range(num_features)}
                # Simple binary target based on sum of features
                y = 1 if sum(x.values()) > 0 else 0

                y_pred = model.predict_one(x)
                if y_pred is not None:
                    accuracy.update(y, y_pred)
                    f1.update(y, y_pred)
                    if y_pred == y:
                        correct_count += 1

                model.learn_one(x, y)

            calc_time_ms = (time.time() - st) * 1000.0

            return {
                "num_samples_streamed": num_samples,
                "num_features": num_features,
                "pipeline_components": [
                    step.__class__.__name__
                    for step in [
                        preprocessing.StandardScaler(),
                        tree.HoeffdingTreeClassifier(),
                    ]
                ],
                "final_accuracy": round(float(accuracy.get()), 4),
                "final_f1": round(float(f1.get()), 4),
                "correct_predictions": correct_count,
                "execution_time_ms": round(calc_time_ms, 2),
            }
        except Exception as e:
            raise RuntimeError(f"River online training failed: {e}")

    async def _execute_builtin_dataset(self) -> Dict[str, Any]:
        """
        Trains on the real River Phishing dataset (built-in, no download).

        Returns:
            Dict with training results on the Phishing dataset.

        Raises:
            RuntimeError: If execution fails.
        """
        st = time.time()

        try:
            model = compose.Pipeline(
                preprocessing.StandardScaler(),
                tree.HoeffdingTreeClassifier(),
            )
            accuracy = metrics.Accuracy()
            count = 0

            for x, y in datasets.Phishing():
                y_pred = model.predict_one(x)
                if y_pred is not None:
                    accuracy.update(y, y_pred)
                model.learn_one(x, y)
                count += 1

            calc_time_ms = (time.time() - st) * 1000.0

            return {
                "dataset": "Phishing (river built-in)",
                "samples_processed": count,
                "final_accuracy": round(float(accuracy.get()), 4),
                "execution_time_ms": round(calc_time_ms, 2),
            }
        except Exception as e:
            raise RuntimeError(f"River Phishing dataset execution failed: {e}")

    async def process(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Receives parameters and executes online learning pipelines.

        Args:
            data: Contains 'num_samples', 'num_features', or 'use_builtin_dataset'.

        Returns:
            Monadic result dict.
        """
        if not self._is_active:
            return {
                "status": "error",
                "engine_id": self._engine_id,
                "error": "Engine inactive.",
            }

        try:
            use_builtin = data.get("use_builtin_dataset", False)

            if use_builtin:
                result = await self._execute_builtin_dataset()
            else:
                num_samples = data.get("num_samples", 1000)
                num_features = data.get("num_features", 10)
                if num_samples <= 0 or num_features <= 0:
                    raise ValueError("num_samples and num_features must be positive.")
                result = await self._execute_online_training(num_samples, num_features)

            return {"status": "success", "data": {"river_streaming_result": result}}
        except Exception as e:
            self.logger.error(f"River execution error: {e}")
            return {"status": "error", "engine_id": self._engine_id, "error": str(e)}

    def diagnostics(self) -> Dict[str, Any]:
        """
        Returns engine health diagnostics.

        Returns:
            Dict with engine status and uptime.
        """
        return {
            "engine": self.__class__.__name__,
            "engine_id": self._engine_id,
            "status": "active" if self._is_active else "inactive",
            "uptime_seconds": (
                round(time.time() - self._start_time, 2) if self._is_active else 0.0
            ),
            "river_version": "0.21.2",
        }
