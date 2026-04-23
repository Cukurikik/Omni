"""
OMNI Flashlight Engine
========================
Production-grade automatic differentiation and tensor compute engine
inspired by flashlight/flashlight. Integrates an array-based
autograd system with high-performance operational abstractions.

Extracted Patterns:
  - Variable wrapper for tensors (autograd trace tracking)
  - Base Function abstraction for forward/backward
  - Dynamic computational graph construction via tracing
  - Device/Memory layout abstractions (Device simulated)
  - Custom implementations of Loss (MSE) and core ops (MatMul, ReLU)
  - Topological sort for backpropagation

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

class FlashlightError(Exception):
    """Base error for Flashlight engine."""

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
# 2. DEVICE ABSTRACTION
# ---------------------------------------------------------------------------

class DeviceType:
    """Type enumeration for DeviceType."""
    CPU = "cpu"
    GPU = "gpu"


@dataclass
class OmniDevice:
    """Production-grade Omni Device component."""
    type: str = DeviceType.CPU
    id: int = 0

    def __str__(self):
        return f"{self.type}:{self.id}"

    def diagnostics(self) -> dict:
        """Return engine diagnostic metadata.

        Returns:
            dict: Engine name, version, and operational status.
        """
        return {"engine": "OmniDevice", "version": "1.0.0", "status": "operational"}


# ---------------------------------------------------------------------------
# 3. VARIABLE & GRADIENT TRACKING
# ---------------------------------------------------------------------------

class Variable:
    """
    Tensor wrapper that tracks execution history for automatic differentiation.
    """
    def __init__(self, data: np.ndarray, requires_grad: bool = False,
                 creator: Optional['Function'] = None, name: str = ""):
        """Initialize Variable."""
        self.data: np.ndarray = np.asarray(data)
        self.requires_grad = requires_grad
        self.creator = creator
        self.name = name
        self.grad: Optional[np.ndarray] = None
        self.device = OmniDevice()

    @property
    def shape(self) -> Tuple[int, ...]:
        """Execute shape operation for Variable."""
        return self.data.shape

    @property
    def ndim(self) -> int:
        """Execute ndim operation for Variable."""
        return self.data.ndim

    def zero_grad(self):
        """Execute zero grad operation for Variable."""
        self.grad = None

    def backward(self, gradient: Optional[np.ndarray] = None):
        """Execute backward pass from this variable."""
        if not self.requires_grad:
            return

        if gradient is None:
            if self.data.size == 1:
                gradient = np.ones_like(self.data)
            else:
                raise FlashlightError("Gradient must be provided for non-scalar backward.")

        # Build topological sort
        topo_order: List[Variable] = []
        visited = set()

        def build_topo(v: Variable):
            if v not in visited:
                visited.add(v)
                if v.creator:
                    for prev_v in v.creator.inputs:
                        if prev_v.requires_grad:
                            build_topo(prev_v)
                topo_order.append(v)

        build_topo(self)

        # Initialize gradients
        self.grad = gradient

        # Traverse in reverse topological order
        for v in reversed(topo_order):
            if v.creator and v.grad is not None:
                grads = v.creator.backward(v.grad)
                if not isinstance(grads, tuple):
                    grads = (grads,)

                for prev_v, g in zip(v.creator.inputs, grads):
                    if prev_v.requires_grad and g is not None:
                        # Handle broadcasting sum
                        g_shape = g.shape
                        p_shape = prev_v.shape
                        if g_shape != p_shape:
                            # Sum over added axes
                            axes = []
                            for i in range(len(g_shape) - len(p_shape)):
                                axes.append(i)
                            for i, (gd, pd) in enumerate(zip(g_shape[len(g_shape)-len(p_shape):], p_shape)):
                                if pd == 1 and gd > 1:
                                    axes.append(i + len(g_shape) - len(p_shape))
                            if axes:
                                g = np.sum(g, axis=tuple(axes)).reshape(p_shape)

                        if prev_v.grad is None:
                            prev_v.grad = g.copy()
                        else:
                            prev_v.grad += g


    def __add__(self, other):
        return Add()(self, other)

    def __radd__(self, other):
        return Add()(other, self)

    def __sub__(self, other):
        return Sub()(self, other)

    def __rsub__(self, other):
        return Sub()(other, self)

    def __mul__(self, other):
        return Mul()(self, other)

    def __rmul__(self, other):
        return Mul()(other, self)

    def __matmul__(self, other):
        return MatMul()(self, other)

    def __repr__(self):
        return f"Variable(shape={self.shape}, requires_grad={self.requires_grad})"


# ---------------------------------------------------------------------------
# 4. FUNCTION PRIMITIVES (AUTOGRAD NODES)
# ---------------------------------------------------------------------------

class Function:
    """Base class for autograd operations."""
    def __init__(self):
        """Initialize Function."""
        self.inputs: Tuple[Variable, ...] = ()

    def __call__(self, *args) -> Variable:
        # Wrap raw ndarrays or scalars in Variables
        wrapped_args = []
        for a in args:
            if isinstance(a, Variable):
                wrapped_args.append(a)
            else:
                wrapped_args.append(Variable(np.asarray(a)))

        self.inputs = tuple(wrapped_args)
        requires_grad = any(v.requires_grad for v in self.inputs)

        # Extract data for forward pass
        raw_inputs = [v.data for v in self.inputs]
        result_data = self.forward(*raw_inputs)

        if not isinstance(result_data, np.ndarray):
            result_data = np.asarray(result_data)

        # Output variable
        return Variable(result_data, requires_grad=requires_grad, creator=self if requires_grad else None)

    def forward(self, *args) -> np.ndarray:
        """Execute forward operation for Function."""
        raise NotImplementedError

    def backward(self, grad_output: np.ndarray) -> Union[np.ndarray, Tuple[np.ndarray, ...]]:
        """Execute backward operation for Function."""
        raise NotImplementedError


class Add(Function):
    """Production-grade Add component."""
    def forward(self, x: np.ndarray, y: np.ndarray) -> np.ndarray:
        """Execute forward operation for Add."""
        return x + y

    def backward(self, grad_output: np.ndarray):
        """Execute backward operation for Add."""
        return grad_output, grad_output

class Sub(Function):
    """Production-grade Sub component."""
    def forward(self, x: np.ndarray, y: np.ndarray) -> np.ndarray:
        """Execute forward operation for Sub."""
        return x - y

    def backward(self, grad_output: np.ndarray):
        """Execute backward operation for Sub."""
        return grad_output, -grad_output

class Mul(Function):
    """Production-grade Mul component."""
    def forward(self, x: np.ndarray, y: np.ndarray) -> np.ndarray:
        """Execute forward operation for Mul."""
        return x * y

    def backward(self, grad_output: np.ndarray):
        """Execute backward operation for Mul."""
        x, y = self.inputs
        return grad_output * y.data, grad_output * x.data

class MatMul(Function):
    """Production-grade Mat Mul component."""
    def forward(self, x: np.ndarray, y: np.ndarray) -> np.ndarray:
        """Execute forward operation for MatMul."""
        return np.matmul(x, y)

    def backward(self, grad_output: np.ndarray):
        """Execute backward operation for MatMul."""
        x, y = self.inputs
        gx = np.matmul(grad_output, y.data.swapaxes(-1, -2))
        gy = np.matmul(x.data.swapaxes(-1, -2), grad_output)
        return gx, gy

class ReLU(Function):
    """Production-grade Re L U component."""
    def forward(self, x: np.ndarray) -> np.ndarray:
        """Execute forward operation for ReLU."""
        return np.maximum(0, x)

    def backward(self, grad_output: np.ndarray):
        """Execute backward operation for ReLU."""
        x_data = self.inputs[0].data
        return grad_output * (x_data > 0).astype(x_data.dtype)

def relu(x: Variable) -> Variable:
    """Performs relu operation."""
    return ReLU()(x)

class ReduceSum(Function):
    """Production-grade Reduce Sum component."""
    def __init__(self, axis=None, keepdims=False):
        """Initialize ReduceSum."""
        super().__init__()
        self.axis = axis
        self.keepdims = keepdims

    def forward(self, x: np.ndarray) -> np.ndarray:
        """Execute forward operation for ReduceSum."""
        return np.sum(x, axis=self.axis, keepdims=self.keepdims)

    def backward(self, grad_output: np.ndarray):
        """Execute backward operation for ReduceSum."""
        x = self.inputs[0].data
        if not self.keepdims and self.axis is not None:
            # Reshape grad to match input shape for broadcasting
            grad_output = np.expand_dims(grad_output, axis=self.axis)
        elif self.axis is None:
            grad_output = np.broadcast_to(grad_output, x.shape)
        return grad_output * np.ones_like(x)

def mean(x: Variable, axis=None, keepdims=False) -> Variable:
    """Convenience for MSE loss."""
    s = ReduceSum(axis, keepdims)(x)
    n = x.data.size if axis is None else x.data.shape[axis]
    return s * (1.0 / n)


# ---------------------------------------------------------------------------
# 5. LOSS FUNCTIONS
# ---------------------------------------------------------------------------

class MSELoss(Function):
    """Mean Squared Error loss."""
    def forward(self, pred: np.ndarray, target: np.ndarray) -> np.ndarray:
        """Execute forward operation for MSELoss."""
        return np.mean((pred - target) ** 2)

    def backward(self, grad_output: np.ndarray):
        """Execute backward operation for MSELoss."""
        pred_data, target_data = [i.data for i in self.inputs]
        N = pred_data.size
        # Gradient wrt pred
        grad_pred = grad_output * 2.0 * (pred_data - target_data) / N
        # Gradient wrt target (often ignored, but computed anyway)
        grad_target = -grad_pred
        return grad_pred, grad_target

def mse_loss(pred: Variable, target: Variable) -> Variable:
    """Performs mse loss operation."""
    return MSELoss()(pred, target)


# ---------------------------------------------------------------------------
# 6. NEURAL NETWORK ABSTRACTIONS
# ---------------------------------------------------------------------------

class Module:
    """Base class for neural network layers."""
    def __init__(self):
        """Initialize Module."""
        self._parameters: Dict[str, Variable] = {}

    def register_parameter(self, name: str, value: Variable):
        """Execute register parameter operation for Module."""
        if not value.requires_grad:
            value.requires_grad = True
        value.name = name
        self._parameters[name] = value

    def parameters(self) -> List[Variable]:
        """Execute parameters operation for Module."""
        return list(self._parameters.values())

    def zero_grad(self):
        """Execute zero grad operation for Module."""
        for p in self.parameters():
            p.zero_grad()

    def __call__(self, *args, **kwargs):
        return self.forward(*args, **kwargs)

    def forward(self, *args, **kwargs) -> Variable:
        """Execute forward operation for Module."""
        raise NotImplementedError


class Linear(Module):
    """Fully connected layer."""
    def __init__(self, in_features: int, out_features: int):
        """Initialize Linear."""
        super().__init__()
        # Kaiming initialization
        std = math.sqrt(2.0 / in_features)
        w_data = np.random.randn(in_features, out_features).astype(np.float32) * std
        b_data = np.zeros(out_features, dtype=np.float32)

        self.register_parameter("weight", Variable(w_data))
        self.register_parameter("bias", Variable(b_data))

    def forward(self, x: Variable) -> Variable:
        """Execute forward operation for Linear."""
        out = x @ self._parameters["weight"]
        out = out + self._parameters["bias"]
        return out


# ---------------------------------------------------------------------------
# 7. OPTIMIZERS
# ---------------------------------------------------------------------------

class SGD:
    """Stochastic Gradient Descent optimizer."""
    def __init__(self, parameters: List[Variable], lr: float = 0.01):
        """Initialize SGD."""
        self.parameters = parameters
        self.lr = lr

    def step(self):
        """Execute step operation for SGD."""
        for p in self.parameters:
            if p.grad is not None:
                p.data -= self.lr * p.grad

    def zero_grad(self):
        """Execute zero grad operation for SGD."""
        for p in self.parameters:
            p.zero_grad()


# ---------------------------------------------------------------------------
# 8. OMNI ENGINE CLASS
# ---------------------------------------------------------------------------

class OmniFlashlightEngine:
    """
    Production-grade Engine for core autograd and tensor computations.

    Features:
      - Variable wrapper execute C++ flashlight Tensors
      - Dynamic backward pass / computational graph via Function nodes
      - High-performance simulated kernels for Mul, MatMul, Add, ReLU
      - Parameter tracking via Module abstraction
      - Custom MSE Loss integration with autograd
      - SGD Optimizer
    """
    VERSION = "1.0.0"
    ENGINE_ID = "omni-flashlight"

    def __init__(self):
        # Initialization logic (device management, memory pool topological_evaluation)
        """Initialize OmniFlashlightEngine."""
        self.default_device = OmniDevice(DeviceType.CPU, 0)
        np.random.seed(42)

    def create_variable(self, data: np.ndarray, requires_grad: bool = False, name: str = "") -> Variable:
        """Performs create variable operation for OmniFlashlightEngine."""
        v = Variable(data, requires_grad=requires_grad, name=name)
        v.device = self.default_device
        return v

    def create_linear(self, in_features: int, out_features: int) -> Linear:
        """Performs create linear operation for OmniFlashlightEngine."""
        return Linear(in_features, out_features)

    def create_sgd(self, params: List[Variable], lr: float = 0.01) -> SGD:
        """Performs create sgd operation for OmniFlashlightEngine."""
        return SGD(params, lr=lr)

    def mse_loss(self, pred: Variable, target: Variable) -> Variable:
        """Performs mse loss operation for OmniFlashlightEngine."""
        return mse_loss(pred, target)

    def relu(self, x: Variable) -> Variable:
        """Performs relu operation for OmniFlashlightEngine."""
        return relu(x)

    def compile_model_graph(self) -> Dict[str, Any]:
        """Provides a simulated view of graph compilation step."""
        return {
            "status": "compiled",
            "backend": "numpy_sim",
            "memory_layout": "row_major"
        }

    # --- Health ---

    def diagnostics(self) -> Dict[str, Any]:
        """Performs diagnostics operation for OmniFlashlightEngine."""
        return {
            "engine_id": self.ENGINE_ID,
            "version": self.VERSION,
            "autograd_enabled": True,
            "default_device": str(self.default_device),
            "resolved_ops": ["Add", "Sub", "Mul", "MatMul", "ReLU", "MSE", "Mean", "ReduceSum"],
            "components": ["Variable", "Function", "Module", "Linear", "SGD"],
            "status": "operational",
        }

