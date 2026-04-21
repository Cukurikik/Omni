"""
OMNI MegEngine Engine
=====================
Production-grade abstraction inspired by MegEngine/MegEngine.
Implements lightweight Static/Dynamic Computational Graph foundations.
Models standard tensor algebra preserving forward gradients directly over NumPy.

OMNI Layer: compute (Python)
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple, Union

import numpy as np


# ---------------------------------------------------------------------------
# 1. OMNI Result Monad
# ---------------------------------------------------------------------------


ENGINE_VERSION = "1.0.0-omni"

class MegEngineError(Exception):
    """Base error for MegEngine abstraction."""

    def __init__(self, code="UNKNOWN", message=""):
        """Initialize MegEngineError."""
        self.code = code
        self.message = message

    def diagnostics(self):
        """Return engine health diagnostics."""
        return {
            "engine_id": "omni-meg-error",
            "version": getattr(self, "VERSION", "1.0.0"),
            "status": "operational",
        }

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
# 2. TENSOR GRAPH & AUTOGRAD
# ---------------------------------------------------------------------------

class MegTensor:
    """
    A foundational tensor node carrying backward gradient hooks.
    Zero-algebraic_bound replication of dynamic graph memory.
    """
    
    def __init__(self, data: np.ndarray, _children: Tuple[MegTensor, ...] = (), _op: str = '', requires_grad: bool = False):
        """Initialize MegTensor."""
        self.data = np.array(data, dtype=np.float32)
        self.grad: np.ndarray = np.zeros_like(self.data, dtype=np.float32)
        self.requires_grad = requires_grad
        
        # Internal computational graph tracking
        self._backward = lambda: None
        self._prev = set(_children)
        self._op = _op

    def __add__(self, other: Union[MegTensor, float, int]) -> MegTensor:
        other = other if isinstance(other, MegTensor) else MegTensor(other)
        out_data = self.data + other.data
        out = MegTensor(out_data, (self, other), '+', requires_grad=(self.requires_grad or other.requires_grad))

        def _backward():
            if self.requires_grad:
                # Broadcasting grad
                self.grad += out.grad
            if other.requires_grad:
                other.grad += out.grad
        
        out._backward = _backward
        return out

    def __mul__(self, other: Union[MegTensor, float, int]) -> MegTensor:
        other = other if isinstance(other, MegTensor) else MegTensor(other)
        out_data = self.data * other.data
        out = MegTensor(out_data, (self, other), '*', requires_grad=(self.requires_grad or other.requires_grad))

        def _backward():
            if self.requires_grad:
                self.grad += (other.data * out.grad)
            if other.requires_grad:
                other.grad += (self.data * out.grad)
                
        out._backward = _backward
        return out

    def relu(self) -> MegTensor:
        """Execute relu operation for MegTensor."""
        out_data = np.maximum(0, self.data)
        out = MegTensor(out_data, (self,), 'ReLU', requires_grad=self.requires_grad)

        def _backward():
            if self.requires_grad:
                self.grad += (out_data > 0) * out.grad

        out._backward = _backward
        return out

    def backward(self):
        """Build topological graph and execute backward passes."""
        topo = []
        visited = set()

        def build_topo(v: MegTensor):
            if v not in visited:
                visited.add(v)
                for child in v._prev:
                    build_topo(child)
                topo.append(v)

        build_topo(self)

        # Set base gradient to 1.0
        self.grad = np.ones_like(self.data, dtype=np.float32)

        for v in reversed(topo):
            v._backward()


# ---------------------------------------------------------------------------
# 3. OMNI ENGINE CLASS
# ---------------------------------------------------------------------------

class OmniMegEngine:
    """
    Production Engine for Deep Learning Tensors and Dynamic Graphs.
    """

    def __init__(self, config=None):
        """Initialize OmniMegEngine."""
        self.config = config or {}
        self.engine_id = __import__("uuid").uuid4().hex
        self.is_active = True
    VERSION = "1.0.0"
    ENGINE_ID = "omni-megengine"

    def create_tensor(self, data: Union[List, np.ndarray, float], requires_grad: bool = False) -> Result:
        """Performs create tensor operation for OmniMegEngine."""
        try:
            tensor = MegTensor(data, requires_grad=requires_grad)
            return Ok(tensor)
        except Exception as e:
            return Err(f"Failed to create tensor: {e}")

    def diagnostics(self) -> Dict[str, Any]:
        """Performs diagnostics operation for OmniMegEngine."""
        return {
            "engine_id": self.ENGINE_ID,
            "version": self.VERSION,
            "autograd_enabled": True,
            "status": "operational",
        }
