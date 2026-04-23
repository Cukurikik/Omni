"""OmniNumpyBroadcastingTensorEngine — Production-grade tensor broadcasting and operations.

Implements NumPy-style broadcasting rules for arbitrary-dimensional tensors
represented as nested Python lists. Supports element-wise add, multiply,
subtract, and dot product with full shape compatibility validation.
"""
import math
from typing import Any, Dict, List, Tuple, Union
from src.compute.python_core.omni_base_engine import Result, Ok, Err

# Type alias for nested-list tensors
Tensor = Union[float, int, List]


class OmniNumpyBroadcastingTensorEngine:
    """Production engine for tensor broadcasting and element-wise operations."""

    ENGINE_VERSION = "1.0.0"

    def __init__(self, max_dimensions: int = 8):
        """
        Initialize broadcasting engine.

        Args:
            max_dimensions: Maximum tensor dimensionality allowed.
        """
        if max_dimensions <= 0:
            raise ValueError("max_dimensions must be positive.")
        self.max_dimensions = max_dimensions

    @staticmethod
    def _infer_shape(tensor: Tensor) -> Tuple[int, ...]:
        """Infer shape of a nested-list tensor recursively."""
        shape = []
        current = tensor
        while isinstance(current, list):
            shape.append(len(current))
            if len(current) == 0:
                break
            current = current[0]
        return tuple(shape)

    @staticmethod
    def _broadcast_shapes(shape_a: Tuple[int, ...], shape_b: Tuple[int, ...]) -> Tuple[int, ...]:
        """
        Compute the broadcast-compatible result shape following NumPy rules:
        align from the right, each dimension must be equal or one of them is 1.

        Raises ValueError if shapes are not broadcast-compatible.
        """
        ndim = max(len(shape_a), len(shape_b))
        # Pad shorter shape with 1s on the left
        sa = (1,) * (ndim - len(shape_a)) + shape_a
        sb = (1,) * (ndim - len(shape_b)) + shape_b

        result = []
        for da, db in zip(sa, sb):
            if da == db:
                result.append(da)
            elif da == 1:
                result.append(db)
            elif db == 1:
                result.append(da)
            else:
                raise ValueError(f"Shapes {shape_a} and {shape_b} are not broadcast-compatible.")
        return tuple(result)

    def _get_element(self, tensor: Tensor, shape: Tuple[int, ...], indices: Tuple[int, ...]) -> float:
        """Get element from tensor with broadcasting index clamping."""
        current = tensor
        ndim_diff = len(indices) - len(shape)
        for i, idx in enumerate(indices):
            dim_idx = i - ndim_diff
            if dim_idx < 0 or shape[dim_idx] == 1:
                current = current[0] if isinstance(current, list) else current
            else:
                current = current[idx]
        return float(current)

    def elementwise_operation(
        self, tensor_a: Tensor, tensor_b: Tensor, operation: str = "add"
    ) -> Result:
        """
        Perform element-wise operation on two tensors with broadcasting.

        Implements NumPy broadcasting rules: shapes are aligned from the right,
        dimensions of size 1 are stretched to match.

        Args:
            tensor_a: First tensor (nested list of numbers).
            tensor_b: Second tensor (nested list of numbers).
            operation: One of "add", "subtract", "multiply", "divide".

        Returns:
            Result with the resulting tensor and shape metadata.
        """
        try:
            ops = {
                "add": lambda a, b: a + b,
                "subtract": lambda a, b: a - b,
                "multiply": lambda a, b: a * b,
                "divide": lambda a, b: a / b if b != 0 else math.inf,
            }
            if operation not in ops:
                return Err(ValueError(f"Unknown operation '{operation}'. Valid: {set(ops.keys())}"))

            shape_a = self._infer_shape(tensor_a)
            shape_b = self._infer_shape(tensor_b)

            if len(shape_a) > self.max_dimensions or len(shape_b) > self.max_dimensions:
                return Err(ValueError(f"Tensor dimensionality exceeds max_dimensions={self.max_dimensions}."))

            result_shape = self._broadcast_shapes(shape_a, shape_b)
            op_fn = ops[operation]

            def build_result(depth: int, indices: Tuple[int, ...]) -> Tensor:
                if depth == len(result_shape):
                    a = self._get_element(tensor_a, shape_a, indices)
                    b = self._get_element(tensor_b, shape_b, indices)
                    return round(op_fn(a, b), 10)
                return [build_result(depth + 1, indices + (i,)) for i in range(result_shape[depth])]

            result_tensor = build_result(0, ())

            return Ok({
                "result_tensor": result_tensor,
                "shape_a": list(shape_a),
                "shape_b": list(shape_b),
                "result_shape": list(result_shape),
                "operation": operation,
                "broadcast_applied": shape_a != shape_b,
            })

        except ValueError as ve:
            return Err(ve)
        except Exception as e:
            return Err(e)

    def dot_product(self, vector_a: List[float], vector_b: List[float]) -> Result:
        """
        Compute dot product of two 1-D vectors.

        Args:
            vector_a: First vector.
            vector_b: Second vector.

        Returns:
            Result with scalar dot product value.
        """
        try:
            if len(vector_a) != len(vector_b):
                return Err(ValueError(f"Vector lengths must match: {len(vector_a)} != {len(vector_b)}"))
            if not vector_a:
                return Err(ValueError("Vectors must be non-empty."))

            dot = sum(a * b for a, b in zip(vector_a, vector_b))
            return Ok({
                "dot_product": round(dot, 10),
                "vector_length": len(vector_a),
            })
        except Exception as e:
            return Err(e)

    def diagnostics(self) -> Dict[str, Any]:
        """Provides engine operational status and metadata."""
        return {
            "engine": "OmniNumpyBroadcastingTensorEngine",
            "version": self.ENGINE_VERSION,
            "status": "operational",
            "max_dimensions": self.max_dimensions,
            "complexity": "O(∏ result_shape) element-wise broadcast operations",
        }
