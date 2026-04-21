"""
OmniChainerEngine — Native Define-by-Run Deep Learning Framework.

Studied from: chainer/chainer (5.9k★)
Implements: Dynamic computational graph with autograd (Variable with
operator overloading), loss functions (softmax, MSE, cross-entropy),
linear layers, and a training loop with configurable TrainingConfig.

OMNI Domain: compute/ (Python)
CODE RULE 001-005 compliant. Zero external ML dependencies.
"""

from __future__ import annotations

import math
import random
from dataclasses import dataclass, field
from typing import Callable, Dict, List, Optional, Tuple, Any


ENGINE_VERSION: str = "1.1.0-omni"
ENGINE_NAME: str = "OmniChainerEngine"

Vector = List[float]


# ---------------------------------------------------------------------------
# Autograd — Variable with operator overloading
# ---------------------------------------------------------------------------

class Variable:
    """Dynamic variable with automatic differentiation.

    Supports scalar and vector values. Operator overloading enables
    natural mathematical expressions that build the computation graph
    implicitly (Define-by-Run paradigm).

    Args:
        data: Scalar float or list of floats.
        name: Optional identifier for debugging.
    """

    def __init__(self, data, name: str = "v") -> None:
        """Initialize Variable."""
        if isinstance(data, (int, float)):
            self.data: float = float(data)
            self._is_scalar: bool = True
        elif isinstance(data, list):
            self.data = data[:]
            self._is_scalar = False
        else:
            self.data = data
            self._is_scalar = isinstance(data, float)
        self.grad: float = 0.0 if self._is_scalar else ([0.0 for _ in range(len(data))] if isinstance(data, list) else 0.0)
        self.name: str = name
        self._backward: Optional[Callable] = None
        self._children: List[Variable] = []

    def backward(self) -> None:
        """Reverse-mode automatic differentiation.

        Performs topological sort of the graph and propagates gradients
        from this variable back to all ancestors.
        """
        # Seed
        if self._is_scalar:
            self.grad = 1.0
        else:
            self.grad = [1.0] * len(self.data) if isinstance(self.data, list) else 1.0

        # Topological sort (Kahn's algorithm)
        topo: List[Variable] = []
        visited = set()

        def _build(v: Variable) -> None:
            if id(v) not in visited:
                visited.add(id(v))
                for c in v._children:
                    _build(c)
                topo.append(v)

        _build(self)

        for v in reversed(topo):
            if v._backward is not None:
                v._backward()

    # -- Operator overloads --------------------------------------------------

    def __add__(self, other: Variable) -> Variable:
        other = other if isinstance(other, Variable) else Variable(other)
        if self._is_scalar and other._is_scalar:
            out = Variable(self.data + other.data, f"({self.name}+{other.name})")
        else:
            raise TypeError("Vector addition uses engine.dynamic_add")

        def _backward() -> None:
            if isinstance(self.grad, (int, float)):
                self.grad += out.grad
                other.grad += out.grad
            else:
                for i in range(len(self.grad)):
                    self.grad[i] += out.grad[i]
                    other.grad[i] += out.grad[i]

        out._backward = _backward
        out._children = [self, other]
        return out

    def __mul__(self, other: Variable) -> Variable:
        other = other if isinstance(other, Variable) else Variable(other)
        if self._is_scalar and other._is_scalar:
            out = Variable(self.data * other.data, f"({self.name}*{other.name})")
        else:
            raise TypeError("Vector multiplication uses engine methods")

        def _backward() -> None:
            self.grad += other.data * out.grad
            other.grad += self.data * out.grad

        out._backward = _backward
        out._children = [self, other]
        return out

    def __repr__(self) -> str:
        return f"Variable({self.data}, grad={self.grad}, name='{self.name}')"


# ---------------------------------------------------------------------------
# Loss functions
# ---------------------------------------------------------------------------

class LossFunctions:
    """Collection of loss and activation functions."""

    @staticmethod
    def softmax(logits: Vector) -> Vector:
        """Numerically stable softmax.

        Args:
            logits: Raw scores.

        Returns:
            Probability distribution.
        """
        max_val = max(logits)
        exps = [math.exp(x - max_val) for x in logits]
        total = sum(exps)
        return [e / total for e in exps]

    @staticmethod
    def mse(predictions: Vector, targets: Vector) -> float:
        """Mean Squared Error loss.

        Args:
            predictions: Model outputs.
            targets: Ground truth values.

        Returns:
            MSE scalar.
        """
        n = len(predictions)
        return sum((p - t) ** 2 for p, t in zip(predictions, targets)) / n

    @staticmethod
    def cross_entropy(predictions: Vector, targets: Vector) -> float:
        """Cross-entropy loss (expects probabilities, not logits).

        Args:
            predictions: Predicted probabilities.
            targets: One-hot or soft targets.

        Returns:
            Cross-entropy scalar.
        """
        return -sum(
            t * math.log(max(p, 1e-12)) for p, t in zip(predictions, targets)
        )


# ---------------------------------------------------------------------------
# Linear layer
# ---------------------------------------------------------------------------

class Linear:
    """Fully connected (dense) layer.

    Attributes:
        in_features: Input dimension.
        out_features: Output dimension.
        weights: Weight matrix [in_features × out_features].
        bias: Bias vector [out_features].
    """

    def __init__(self, in_features: int, out_features: int) -> None:
        """Initialize Linear."""
        self.in_features = in_features
        self.out_features = out_features

        # Xavier init
        limit = math.sqrt(6.0 / (in_features + out_features))
        self.weights: List[Vector] = [
            [random.uniform(-limit, limit) for _ in range(out_features)]
            for _ in range(in_features)
        ]
        self.bias: Vector = [0.0 for _ in range(out_features)]

    def forward(self, x: Vector) -> Vector:
        """Forward pass: y = Wx + b.

        Args:
            x: Input vector of length in_features.

        Returns:
            Output vector of length out_features.
        """
        out = self.bias[:]
        for j in range(self.out_features):
            for i in range(self.in_features):
                out[j] += x[i] * self.weights[i][j]
        return out

    def parameters(self) -> List[Vector]:
        """Return all trainable parameters.

        Returns:
            List containing weight rows and bias.
        """
        return self.weights + [self.bias]


# ---------------------------------------------------------------------------
# Training loop
# ---------------------------------------------------------------------------

@dataclass
class TrainingConfig:
    """Configuration for the training loop.

    Attributes:
        epochs: Number of training epochs.
        batch_size: Mini-batch size.
        learning_rate: SGD learning rate.
    """
    epochs: int = 10
    batch_size: int = 32
    learning_rate: float = 0.01


@dataclass
class EpochLog:
    """Log entry for a single training epoch.

    Attributes:
        epoch: Epoch number (1-indexed).
        avg_loss: Average loss over the epoch.
        samples_processed: Total samples processed.
    """
    epoch: int
    avg_loss: float
    samples_processed: int


class Trainer:
    """Simple SGD training loop for Linear layers.

    Args:
        config: TrainingConfig instance.
    """

    def __init__(self, config: TrainingConfig) -> None:
        """Initialize Trainer."""
        self.config = config

    def train(
        self, model: Linear, data: List[Vector], targets: List[Vector]
    ) -> List[EpochLog]:
        """Train the model using mini-batch SGD.

        Args:
            model: Linear layer to train.
            data: List of input vectors.
            targets: List of target vectors.

        Returns:
            List of EpochLog entries, one per epoch.
        """
        logs: List[EpochLog] = []
        n = len(data)
        lr = self.config.learning_rate

        for epoch in range(1, self.config.epochs + 1):
            # Shuffle indices
            indices = list(range(n))
            random.shuffle(indices)

            total_loss = 0.0
            processed = 0

            for start in range(0, n, self.config.batch_size):
                batch_idx = indices[start : start + self.config.batch_size]
                batch_loss = 0.0

                # Accumulate gradients
                grad_w = [
                    [0.0 for _ in range(model)].out_features for _ in range(model.in_features)
                ]
                grad_b = [0.0 for _ in range(model)].out_features

                for idx in batch_idx:
                    x_i = data[idx]
                    t_i = targets[idx]
                    y_i = model.forward(x_i)

                    # MSE loss per sample
                    loss_i = sum((y - t) ** 2 for y, t in zip(y_i, t_i)) / len(t_i)
                    batch_loss += loss_i

                    # Gradient of MSE w.r.t output: 2*(y - t) / out_features
                    d_out = [2 * (y - t) / len(t_i) for y, t in zip(y_i, t_i)]

                    # Accumulate w and b gradients
                    for j in range(model.out_features):
                        grad_b[j] += d_out[j]
                        for i in range(model.in_features):
                            grad_w[i][j] += x_i[i] * d_out[j]

                bs = len(batch_idx)
                # Update parameters
                for i in range(model.in_features):
                    for j in range(model.out_features):
                        model.weights[i][j] -= lr * grad_w[i][j] / bs

                for j in range(model.out_features):
                    model.bias[j] -= lr * grad_b[j] / bs

                total_loss += batch_loss
                processed += bs

            avg = total_loss / max(processed, 1)
            logs.append(EpochLog(epoch=epoch, avg_loss=avg, samples_processed=processed))

        return logs


# ---------------------------------------------------------------------------
# Core Engine
# ---------------------------------------------------------------------------

class OmniChainerEngine:
    """Production-grade Define-by-Run deep learning engine.

    Capabilities:
        - Dynamic computational graph via Variable with operator overloading
        - Reverse-mode autograd with topological sort
        - Loss functions (softmax, MSE, cross-entropy)
        - Linear layers with Xavier initialization
        - Training loop with configurable epochs/batch/lr
    """

    def __init__(self) -> None:
        """Initialize OmniChainerEngine."""
        self.loss = LossFunctions()
        self._version: str = ENGINE_VERSION
        self._name: str = ENGINE_NAME

    def linear(self, in_features: int, out_features: int) -> Linear:
        """Factory method for Linear layers.

        Args:
            in_features: Input dimension.
            out_features: Output dimension.

        Returns:
            Linear instance.
        """
        return Linear(in_features, out_features)

    def trainer(self, config: TrainingConfig) -> Trainer:
        """Factory method for Trainer.

        Args:
            config: TrainingConfig instance.

        Returns:
            Trainer instance.
        """
        return Trainer(config)

    # -- Legacy API (Batch 10 backward compatibility) -------------------------

    def dynamic_add(self, x0, x1):
        """Legacy dynamic addition for numpy-based Variables.

        Args:
            x0: Variable with numpy .data attribute.
            x1: Variable with numpy .data attribute.

        Returns:
            Result wrapping a Variable with the sum.
        """
        try:
            import numpy as _np
            if hasattr(x0, 'data') and hasattr(x0.data, 'shape'):
                if x0.data.shape != x1.data.shape:
                    return Result(error="Shape mismatch across dynamic bounds tracking.")
                y_data = x0.data + x1.data
                y = Variable(list(y_data) if hasattr(y_data, '__iter__') else y_data, name="add_out")
                y.data = y_data  # keep numpy
                y.grad = _np.zeros_like(y_data)

                class _Op:
                    """Production-grade _ Op component."""
                    def __init__(self, inputs, outputs):
                        """Initialize _Op."""
                        self.inputs = inputs
                        self.outputs = outputs
                    def backward_fn(self, gys):
                        """Execute backward fn operation for _Op."""
                        return [gys[0], gys[0]]

                op = _Op([x0, x1], [y])
                y.creator_op = op
                # Ensure inputs have numpy grad
                if not hasattr(x0, 'creator_op'):
                    x0.creator_op = None
                if not hasattr(x1, 'creator_op'):
                    x1.creator_op = None
                return Result(value=y)
            else:
                out = x0 + x1
                return Result(value=out)
        except Exception as e:
            return Result(error=f"Dynamic trace Add error: {str(e)}")

    def dynamic_mul(self, x0, x1):
        """Legacy dynamic multiplication for numpy-based Variables.

        Args:
            x0: Variable with numpy .data attribute.
            x1: Variable with numpy .data attribute.

        Returns:
            Result wrapping a Variable with the product.
        """
        try:
            import numpy as _np
            if hasattr(x0, 'data') and hasattr(x0.data, 'shape'):
                y_data = x0.data * x1.data
                y = Variable(list(y_data) if hasattr(y_data, '__iter__') else y_data, name="mul_out")
                y.data = y_data
                y.grad = _np.zeros_like(y_data)

                _x0_data = x0.data.copy()
                _x1_data = x1.data.copy()

                class _Op:
                    """Production-grade _ Op component."""
                    def __init__(self, inputs, outputs):
                        """Initialize _Op."""
                        self.inputs = inputs
                        self.outputs = outputs
                    def backward_fn(self, gys):
                        """Execute backward fn operation for _Op."""
                        return [gys[0] * _x1_data, gys[0] * _x0_data]

                op = _Op([x0, x1], [y])
                y.creator_op = op
                if not hasattr(x0, 'creator_op'):
                    x0.creator_op = None
                if not hasattr(x1, 'creator_op'):
                    x1.creator_op = None
                return Result(value=y)
            else:
                out = x0 * x1
                return Result(value=out)
        except Exception as e:
            return Result(error=f"Dynamic trace Mul error: {str(e)}")

    def execute_graph_propagation(self, variables, target_variable):
        """Legacy backward propagation for numpy-based Variables.

        Args:
            variables: List of input variables.
            target_variable: Output variable to backprop from.

        Returns:
            Result indicating success or failure.
        """
        try:
            import numpy as _np
            target_variable.grad = _np.ones_like(target_variable.data)

            # Topological backward walk
            funcs = []
            if hasattr(target_variable, 'creator_op') and target_variable.creator_op is not None:
                funcs.append(target_variable.creator_op)

            while funcs:
                f = funcs.pop(0)
                gys = [y.grad for y in f.outputs]
                gxs = f.backward_fn(gys)

                for x, gx in zip(f.inputs, gxs):
                    x.grad = x.grad + gx
                    if hasattr(x, 'creator_op') and x.creator_op is not None and x.creator_op not in funcs:
                        funcs.append(x.creator_op)

            return Result(value={"status": "Graph evaluation complete natively."})
        except Exception as e:
            return Result(error=f"Dynamic propagation error: {str(e)}")

    def health(self) -> Dict[str, Any]:
        """Return engine health diagnostics.

        Returns:
            Dictionary with engine status information.
        """
        return {
            "engine": self._name,
            "version": self._version,
            "status": "operational",
            "paradigm": "define-by-run",
            "autograd": True,
            "capabilities": [
                "variable_autograd", "operator_overloading",
                "softmax", "mse", "cross_entropy",
                "linear_layer", "training_loop",
            ],
        }

    # Legacy alias for diagnostics
    def diagnostics(self) -> Dict[str, Any]:
        """Performs diagnostics operation for OmniChainerEngine."""
        return self.health()


# ---------------------------------------------------------------------------
# Legacy Result class (backward-compatible with Batch 10 tests)
# ---------------------------------------------------------------------------

class Result:
    """Monadic result pattern for legacy compatibility."""
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
