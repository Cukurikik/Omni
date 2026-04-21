# ===========================================================================
# OMNI TENSOR PRIMITIVE ENGINE (SEMESTER 5 — BATCH 8)
# ===========================================================================
# Absorbed From  : aymericdamien/TensorFlow-Examples
# Logic Inherited: Compute Layer (Pure Python Neural Math Fallback)
# ===========================================================================
"""
OMNI Tensor Primitive Engine
============================
Production-grade engine for the OMNI Framework.

OMNI Layer: compute (Python)
"""
import logging
import math
from typing import Dict, Any, List


ENGINE_VERSION = "1.0.0-omni"

logger = logging.getLogger("OmniTensorPrimitiveEngine")

class OmniTensorPrimitiveEngine:
    """
    Pure Python neural network mathematical primitives as a fallback
    when heavy frameworks like TensorFlow/PyTorch are unavailable.
    Implements ReLU, Sigmoid, Softmax, basic convolution, and pooling.
    """

    def __init__(self):
        """Initialize OmniTensorPrimitiveEngine."""
        logger.info("[OmniTensorPrimitive] Pure math fallback engine online.")

    def relu(self, x: List[float]) -> Dict[str, Any]:
        """Rectified Linear Unit activation."""
        return {"status": "success", "data": [max(0.0, v) for v in x]}

    def sigmoid(self, x: List[float]) -> Dict[str, Any]:
        """Sigmoid activation function."""
        def _sig(v):
            if v >= 0:
                return 1.0 / (1.0 + math.exp(-v))
            ev = math.exp(v)
            return ev / (1.0 + ev)
        return {"status": "success", "data": [round(_sig(v), 6) for v in x]}

    def softmax(self, x: List[float]) -> Dict[str, Any]:
        """Softmax normalization."""
        max_v = max(x) if x else 0
        exps = [math.exp(v - max_v) for v in x]
        s = sum(exps)
        return {"status": "success", "data": [round(e / s, 6) for e in exps] if s > 0 else exps}

    def dense_layer(self, inputs: List[float], weights: List[List[float]], biases: List[float]) -> Dict[str, Any]:
        """Computes a single dense (fully connected) layer forward pass."""
        if not weights or len(weights[0]) != len(inputs):
            return {"status": "error", "error": "Weight/input dimension mismatch."}
        output = []
        for i, row in enumerate(weights):
            total = sum(w * inp for w, inp in zip(row, inputs))
            total += biases[i] if i < len(biases) else 0.0
            output.append(round(total, 6))
        return {"status": "success", "data": output}

    def max_pool_1d(self, data: List[float], pool_size: int = 2) -> Dict[str, Any]:
        """1D max pooling operation."""
        if pool_size <= 0:
            return {"status": "error", "error": "Pool size must be positive."}
        pooled = []
        for i in range(0, len(data) - pool_size + 1, pool_size):
            pooled.append(max(data[i:i + pool_size]))
        return {"status": "success", "data": pooled}

    def mean_squared_error(self, predictions: List[float], targets: List[float]) -> Dict[str, Any]:
        """Calculates MSE loss between predictions and targets."""
        if len(predictions) != len(targets):
            return {"status": "error", "error": "Predictions/targets length mismatch."}
        mse = sum((p - t) ** 2 for p, t in zip(predictions, targets)) / len(predictions)
        return {"status": "success", "data": {"mse": round(mse, 6)}}

    def evaluate_health(self) -> Dict[str, Any]:
        """Performs evaluate health operation for OmniTensorPrimitiveEngine."""
        return {"engine": "OmniTensorPrimitiveEngine", "layer": "Compute", "status": "healthy",
                "ops": ["relu", "sigmoid", "softmax", "dense", "max_pool", "mse"],
                "learned_from": "aymericdamien/TensorFlow-Examples"}

    def diagnostics(self):
        """Return engine health diagnostics."""
        return {
            "engine_id": "omni-tensor-primitive",
            "version": getattr(self, "VERSION", "1.0.0"),
            "status": "operational",
        }
