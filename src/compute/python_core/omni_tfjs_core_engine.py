"""
OMNI TFJS-Core Engine
=====================
Production-grade, zero-algebraic_bound tensor math and auto-differentiation engine 
inspired by `tensorflow/tfjs-core`. Implements reverse-mode auto-differentiation
using a dynamically constructed computational graph (Gradient Tape), 
pure mathematical operations, and pure NumPy memory management.

Extracted Patterns:
  - Reverse-mode auto-differentiation (GradientTape)
  - Directed Acyclic Graph (DAG) construction during forward pass
  - Mathematical core ops: add, sub, mul, div, matmul, relu, sigmoid
  - Topological sorting for backpropagation
  - Variable scoping and parameter gradient updates

OMNI Layer: compute (Python)
"""

from __future__ import annotations
import numpy as np
import uuid
from typing import Any, Callable, Dict, List, Optional, Tuple, Union

# ---------------------------------------------------------------------------
# 1. OMNI Result Monad
# ---------------------------------------------------------------------------


ENGINE_VERSION = "1.0.0-omni"
from src.compute.python_core.omni_base_engine import Result, Ok, Err

class AutoGradError(Exception):
    """Base error for TFJS-Core engine operations."""

# ---------------------------------------------------------------------------
# 2. COMPUTATIONAL GRAPH ABSTRACTION
# ---------------------------------------------------------------------------

class OmniTensor:
    """
    Core tensor structure acting as a node in the computational graph.
    Holds pure numerical data and its respective gradients, alongside 
    references to the operation that produced it for backpropagation.
    """
    def __init__(self, data: Union[float, list, np.ndarray], requires_grad: bool = False, _children: tuple = (), _op: str = '', name: str = ''):
        """Initialize OmniTensor."""
        self.data = np.array(data, dtype=np.float32) if not isinstance(data, np.ndarray) else data.astype(np.float32)
        self.requires_grad = requires_grad or any(getattr(c, 'requires_grad', False) for c in _children)
        self.grad = np.zeros_like(self.data, dtype=np.float32)
        
        # Auto-diff internal graph constructs
        self._backward: Callable[[], None] = lambda: None
        self._prev = set(_children)
        self._op = _op
        self.id = uuid.uuid4().hex
        self.name = name or self.id[:8]

    @property
    def shape(self) -> Tuple[int, ...]:
        """Execute shape operation for OmniTensor."""
        return self.data.shape

    @property
    def ndim(self) -> int:
        """Execute ndim operation for OmniTensor."""
        return self.data.ndim

    def zero_grad(self) -> None:
        """Reset gradients to zero."""
        self.grad = np.zeros_like(self.data, dtype=np.float32)

    def backward(self) -> None:
        """
        Execute reverse-mode differentiation.
        Topologically sorts the graph and applies the chain rule backward.
        """
        topo = []
        visited = set()
        
        def build_topo(v: OmniTensor):
            if v not in visited:
                visited.add(v)
                for child in v._prev:
                    build_topo(child)
                topo.append(v)
                
        build_topo(self)
        
        # Base case derivative
        self.grad = np.ones_like(self.data, dtype=np.float32)
        
        # Traverse the list in reverse and apply backward ops
        for node in reversed(topo):
            node._backward()

    # --- Overloaded operators for magic mathematical constructs ---
    
    def __add__(self, other: Union[OmniTensor, float, int]) -> 'OmniTensor':
        other = other if isinstance(other, OmniTensor) else OmniTensor(other)
        out = OmniTensor(self.data + other.data, _children=(self, other), _op='+')
        
        def _backward():
            if self.requires_grad:
                # Handle broadcasting summation
                grad_self = out.grad
                while grad_self.ndim > self.ndim: grad_self = grad_self.sum(axis=0)
                for i, dim in enumerate(self.shape):
                    if dim == 1: grad_self = grad_self.sum(axis=i, keepdims=True)
                self.grad += grad_self
                
            if other.requires_grad:
                grad_other = out.grad
                while grad_other.ndim > other.ndim: grad_other = grad_other.sum(axis=0)
                for i, dim in enumerate(other.shape):
                    if dim == 1: grad_other = grad_other.sum(axis=i, keepdims=True)
                other.grad += grad_other
        out._backward = _backward
        return out

    def __mul__(self, other: Union[OmniTensor, float, int]) -> 'OmniTensor':
        other = other if isinstance(other, OmniTensor) else OmniTensor(other)
        out = OmniTensor(self.data * other.data, _children=(self, other), _op='*')
        
        def _backward():
            if self.requires_grad:
                grad_self = out.grad * other.data
                while grad_self.ndim > self.ndim: grad_self = grad_self.sum(axis=0)
                for i, dim in enumerate(self.shape):
                    if dim == 1: grad_self = grad_self.sum(axis=i, keepdims=True)
                self.grad += grad_self
                
            if other.requires_grad:
                grad_other = out.grad * self.data
                while grad_other.ndim > other.ndim: grad_other = grad_other.sum(axis=0)
                for i, dim in enumerate(other.shape):
                    if dim == 1: grad_other = grad_other.sum(axis=i, keepdims=True)
                other.grad += grad_other
        out._backward = _backward
        return out
        
    def __neg__(self) -> 'OmniTensor':
        return self * -1
        
    def __sub__(self, other: Union[OmniTensor, float, int]) -> 'OmniTensor':
        return self + (-other)
        
    def __pow__(self, other: Union[int, float]) -> 'OmniTensor':
        assert isinstance(other, (int, float)), "only supporting int/float powers for now"
        out = OmniTensor(self.data ** other, _children=(self,), _op=f'**{other}')
        
        def _backward():
            if self.requires_grad:
                self.grad += out.grad * (other * (self.data ** (other - 1)))
        out._backward = _backward
        return out

    def __truediv__(self, other: Union[OmniTensor, float, int]) -> 'OmniTensor':
        return self * (other ** -1)

    def relu(self) -> 'OmniTensor':
        """Execute relu operation for OmniTensor."""
        out = OmniTensor(np.maximum(0, self.data), _children=(self,), _op='ReLU')
        def _backward():
            if self.requires_grad:
                self.grad += out.grad * (out.data > 0).astype(np.float32)
        out._backward = _backward
        return out

    def matmul(self, other: 'OmniTensor') -> 'OmniTensor':
        """Execute matmul operation for OmniTensor."""
        assert isinstance(other, OmniTensor)
        out = OmniTensor(self.data @ other.data, _children=(self, other), _op='@')
        def _backward():
            if self.requires_grad:
                self.grad += out.grad @ other.data.T
            if other.requires_grad:
                other.grad += self.data.T @ out.grad
        out._backward = _backward
        return out

    def sigmoid(self) -> 'OmniTensor':
        """Execute sigmoid operation for OmniTensor."""
        s = 1.0 / (1.0 + np.exp(-np.clip(self.data, -20, 20)))
        out = OmniTensor(s, _children=(self,), _op='Sigmoid')
        def _backward():
            if self.requires_grad:
                self.grad += out.grad * (s * (1.0 - s))
        out._backward = _backward
        return out
        
    def sum(self) -> 'OmniTensor':
        """Execute sum operation for OmniTensor."""
        out = OmniTensor(self.data.sum(), _children=(self,), _op='SUM')
        def _backward():
            if self.requires_grad:
                self.grad += np.ones_like(self.data) * out.grad
        out._backward = _backward
        return out

    def diagnostics(self) -> dict:
        """Return engine diagnostic metadata.

        Returns:
            dict: Engine name, version, and operational status.
        """
        return {"engine": "OmniTensor", "version": "1.0.0", "status": "operational"}

# ---------------------------------------------------------------------------
# 3. GRADIENT TAPE (Autograd Manager)
# ---------------------------------------------------------------------------

class GradientTape:
    """
    Records operations for automatic differentiation.
    In standard mode, all variables require gradient while inside tape context.
    """
    def __init__(self, persistent: bool = False):
        """Initialize GradientTape."""
        self.persistent = persistent
        self._active = False
        self._watched: List[OmniTensor] = []

    def __enter__(self):
        self._active = True
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._active = False

    def watch(self, tensor: OmniTensor) -> None:
        """Explicitly watch a tensor"""
        if self._active:
            tensor.requires_grad = True
            self._watched.append(tensor)

    def gradient(self, target: OmniTensor, sources: List[OmniTensor]) -> List[np.ndarray]:
        """
        Compute gradients of `target` with respect to `sources`.
        """
        target.backward()
        grads = [src.grad.copy() for src in sources]
        if not self.persistent:
            # Clean up graph after call unless persistent
            for src in sources:
                src.zero_grad()
        return grads

# ---------------------------------------------------------------------------
# 4. OPTIMIZERS
# ---------------------------------------------------------------------------

class SGDOptimizer:
    """Production-grade S G D Optimizer component."""
    def __init__(self, learning_rate: float = 0.01):
        """Initialize SGDOptimizer."""
        self.lr = learning_rate

    def apply_gradients(self, parameters: List[OmniTensor], gradients: List[np.ndarray]) -> None:
        """Apply simple stochastic gradient descent updates."""
        for param, grad in zip(parameters, gradients):
            param.data -= self.lr * grad

# ---------------------------------------------------------------------------
# 5. OMNI ENGINE EXPORT CLASS
# ---------------------------------------------------------------------------

class OmniTfjsCoreEngine:
    """
    Production-grade tensor math and reverse-mode AD engine.
    """

    def __init__(self, config=None):
        """Initialize OmniTfjsCoreEngine."""
        self.config = config or {}
        self.engine_id = __import__("uuid").uuid4().hex
        self.is_active = True
    VERSION = "1.0.0"
    ENGINE_ID = "omni-tfjs-core"

    def tensor(self, data: Union[float, list, np.ndarray], requires_grad: bool = False) -> OmniTensor:
        """Performs tensor operation for OmniTfjsCoreEngine."""
        return OmniTensor(data, requires_grad)

    def tape(self, persistent: bool = False) -> GradientTape:
        """Performs tape operation for OmniTfjsCoreEngine."""
        return GradientTape(persistent)
        
    def sgd(self, lr: float = 0.01) -> SGDOptimizer:
        """Performs sgd operation for OmniTfjsCoreEngine."""
        return SGDOptimizer(learning_rate=lr)

    def relu(self, tensor: OmniTensor) -> OmniTensor:
        """Performs relu operation for OmniTfjsCoreEngine."""
        return tensor.relu()

    def sigmoid(self, tensor: OmniTensor) -> OmniTensor:
        """Performs sigmoid operation for OmniTfjsCoreEngine."""
        return tensor.sigmoid()

    def matmul(self, a: OmniTensor, b: OmniTensor) -> OmniTensor:
        """Performs matmul operation for OmniTfjsCoreEngine."""
        return a.matmul(b)

    def diagnostics(self) -> Dict[str, Any]:
        """Performs diagnostics operation for OmniTfjsCoreEngine."""
        return {
            "engine_id": self.ENGINE_ID,
            "version": self.VERSION,
            "components": ["OmniTensor", "GradientTape", "SGDOptimizer"],
            "autograd": "reverse-mode",
            "status": "operational"
        }
