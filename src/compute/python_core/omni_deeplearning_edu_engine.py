"""
OMNI DeepLearning Edu Engine
==============================
Production-grade abstraction of core Deep Learning concepts,
inspired by mbadry1/DeepLearning.ai-Summary.
This engine distills deep learning theory into executable,
highly optimized NumPy primitives for educational and production use.

Extracted Patterns:
  - Weight Initialization (Xavier, He)
  - Regularization (Dropout, L2 Simulation)
  - Normalization (Batch Normalization)
  - Advanced Optimizers (Adam, RMSprop, Momentum)
  - Clear, mathematical formulation of forward and backward passes

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

class DLEduError(Exception):
    """Base error for DL Edu engine."""

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
# 2. WEIGHT INITIALIZATION
# ---------------------------------------------------------------------------

class Initializer:
    """Production-grade Initializer component."""

    @staticmethod
    def he_normal(shape: Tuple[int, ...], seed: int = 42) -> np.ndarray:
        """He/Kaiming Normal Initialization. Best for ReLU."""
        rs = np.random.RandomState(seed)
        fan_in = shape[0]
        std = np.sqrt(2.0 / fan_in)
        return rs.randn(*shape).astype(np.float32) * std

    @staticmethod
    def xavier_normal(shape: Tuple[int, ...], seed: int = 42) -> np.ndarray:
        """Xavier/Glorot Normal Initialization. Best for Tanh/Sigmoid."""
        rs = np.random.RandomState(seed)
        fan_in = shape[0]
        fan_out = shape[1] if len(shape) > 1 else shape[0]
        std = np.sqrt(2.0 / (fan_in + fan_out))
        return rs.randn(*shape).astype(np.float32) * std

    @staticmethod
    def zeros(shape: Tuple[int, ...]) -> np.ndarray:
        """Execute zeros operation for Initializer."""
        return np.zeros(shape, dtype=np.float32)


# ---------------------------------------------------------------------------
# 3. REGULARIZATION: DROPOUT
# ---------------------------------------------------------------------------

class Dropout:
    """Inverted Dropout implementation."""
    def __init__(self, keep_prob: float = 0.5, seed: int = 42):
        """Initialize Dropout."""
        self.keep_prob = keep_prob
        self.rs = np.random.RandomState(seed)
        self.mask: Optional[np.ndarray] = None

    def forward(self, x: np.ndarray, is_training: bool = True) -> np.ndarray:
        """Execute forward operation for Dropout."""
        if not is_training or self.keep_prob >= 1.0:
            return x

        # Create dropout mask D[l] = np.random.rand(...) < keep_prob
        self.mask = (self.rs.rand(*x.shape) < self.keep_prob).astype(np.float32)
        
        # Apply mask and scale (Inverted Dropout technique)
        return (x * self.mask) / self.keep_prob

    def backward(self, grad_output: np.ndarray) -> np.ndarray:
        """Execute backward operation for Dropout."""
        if self.mask is None:
            return grad_output
        return (grad_output * self.mask) / self.keep_prob


# ---------------------------------------------------------------------------
# 4. NORMALIZATION: BATCH NORM
# ---------------------------------------------------------------------------

class BatchNorm:
    """
    Batch Normalization layer.
    Normalizes the input over the batch dimension, then scales and shifts.
    """
    def __init__(self, num_features: int, epsilon: float = 1e-5, momentum: float = 0.9):
        """Initialize BatchNorm."""
        self.epsilon = epsilon
        self.momentum = momentum
        
        # Learnable parameters
        self.gamma = np.ones((1, num_features), dtype=np.float32)
        self.beta = np.zeros((1, num_features), dtype=np.float32)
        
        # Running statistics (Exponential Moving Average)
        self.running_mean = np.zeros((1, num_features), dtype=np.float32)
        self.running_var = np.ones((1, num_features), dtype=np.float32)

        # Cache for backward pass
        self.cache: Dict[str, np.ndarray] = {}

    def forward(self, x: np.ndarray, is_training: bool = True) -> np.ndarray:
        """x has shape (batch_size, num_features)"""
        if is_training:
            mu = np.mean(x, axis=0, keepdims=True)
            var = np.var(x, axis=0, keepdims=True)
            
            # Update running stats
            self.running_mean = self.momentum * self.running_mean + (1 - self.momentum) * mu
            self.running_var = self.momentum * self.running_var + (1 - self.momentum) * var
        else:
            mu = self.running_mean
            var = self.running_var

        # Normalize
        x_norm = (x - mu) / np.sqrt(var + self.epsilon)
        
        # Scale and shift
        out = self.gamma * x_norm + self.beta

        if is_training:
            self.cache = {'x': x, 'x_norm': x_norm, 'mu': mu, 'var': var}

        return out

    def backward(self, grad_output: np.ndarray) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """
        Returns dx, dgamma, dbeta.
        """
        if not self.cache:
            return grad_output, np.zeros_like(self.gamma), np.zeros_like(self.beta)

        x, x_norm, mu, var = self.cache['x'], self.cache['x_norm'], self.cache['mu'], self.cache['var']
        N = grad_output.shape[0]

        dgamma = np.sum(grad_output * x_norm, axis=0, keepdims=True)
        dbeta = np.sum(grad_output, axis=0, keepdims=True)

        # Gradient wrt x
        dx_norm = grad_output * self.gamma
        dvar = np.sum(dx_norm * (x - mu) * -0.5 * np.power(var + self.epsilon, -1.5), axis=0, keepdims=True)
        dmu = np.sum(dx_norm * -1.0 / np.sqrt(var + self.epsilon), axis=0, keepdims=True) + dvar * np.mean(-2.0 * (x - mu), axis=0, keepdims=True)
        
        dx = (dx_norm / np.sqrt(var + self.epsilon)) + (dvar * 2.0 * (x - mu) / N) + (dmu / N)

        return dx, dgamma, dbeta


# ---------------------------------------------------------------------------
# 5. ADVANCED OPTIMIZERS
# ---------------------------------------------------------------------------

class Optimizer:
    """Production-grade Optimizer component."""
    def update(self, params: Dict[str, np.ndarray], grads: Dict[str, np.ndarray]):
        """Execute update operation for Optimizer."""
        raise NotImplementedError


class Momentum(Optimizer):
    """SGD with Momentum."""
    def __init__(self, lr: float = 0.01, beta: float = 0.9):
        """Initialize Momentum."""
        self.lr = lr
        self.beta = beta
        self.v: Dict[str, np.ndarray] = {}

    def update(self, params: Dict[str, np.ndarray], grads: Dict[str, np.ndarray]):
        """Execute update operation for Momentum."""
        for key in params.keys():
            if key not in self.v:
                self.v[key] = np.zeros_like(params[key])
            
            # v = beta * v + (1 - beta) * dW
            self.v[key] = self.beta * self.v[key] + (1 - self.beta) * grads[key]
            params[key] -= self.lr * self.v[key]


class RMSprop(Optimizer):
    """RMSprop optimizer."""
    def __init__(self, lr: float = 0.01, beta: float = 0.999, epsilon: float = 1e-8):
        """Initialize RMSprop."""
        self.lr = lr
        self.beta = beta
        self.epsilon = epsilon
        self.s: Dict[str, np.ndarray] = {}

    def update(self, params: Dict[str, np.ndarray], grads: Dict[str, np.ndarray]):
        """Execute update operation for RMSprop."""
        for key in params.keys():
            if key not in self.s:
                self.s[key] = np.zeros_like(params[key])
            
            # s = beta * s + (1 - beta) * dW^2
            self.s[key] = self.beta * self.s[key] + (1 - self.beta) * np.square(grads[key])
            
            # W = W - lr * dW / sqrt(s + eps)
            params[key] -= self.lr * grads[key] / (np.sqrt(self.s[key]) + self.epsilon)


class Adam(Optimizer):
    """Adam Optimizer (Adaptive Moment Estimation)."""
    def __init__(self, lr: float = 0.001, beta1: float = 0.9, beta2: float = 0.999, epsilon: float = 1e-8):
        """Initialize Adam."""
        self.lr = lr
        self.beta1 = beta1
        self.beta2 = beta2
        self.epsilon = epsilon
        self.t = 0
        self.v: Dict[str, np.ndarray] = {}
        self.s: Dict[str, np.ndarray] = {}

    def update(self, params: Dict[str, np.ndarray], grads: Dict[str, np.ndarray]):
        """Execute update operation for Adam."""
        self.t += 1
        for key in params.keys():
            if key not in self.v:
                self.v[key] = np.zeros_like(params[key])
                self.s[key] = np.zeros_like(params[key])

            # Momentum
            self.v[key] = self.beta1 * self.v[key] + (1 - self.beta1) * grads[key]
            # RMS
            self.s[key] = self.beta2 * self.s[key] + (1 - self.beta2) * np.square(grads[key])
            
            # Bias correction
            v_corrected = self.v[key] / (1 - self.beta1**self.t)
            s_corrected = self.s[key] / (1 - self.beta2**self.t)

            # Update
            params[key] -= self.lr * v_corrected / (np.sqrt(s_corrected) + self.epsilon)


# ---------------------------------------------------------------------------
# 6. OMNI ENGINE CLASS
# ---------------------------------------------------------------------------

class OmniDeepLearningEduEngine:
    """
    Production-grade Educational Engine mapping deep learning concepts to code.

    Provides:
      - Weight Initialization approaches (He, Xavier)
      - Layers providing regularization / normalization (Dropout, BatchNorm)
      - Suite of optimized parameter update strategies (Momentum, RMSprop, Adam)
    """
    VERSION = "1.0.0"
    ENGINE_ID = "omni-dl-edu"

    def __init__(self):
        """Initialize OmniDeepLearningEduEngine."""
        self.initializer = Initializer()

    def get_initializer(self) -> Initializer:
        """Performs get initializer operation for OmniDeepLearningEduEngine."""
        return self.initializer

    def create_dropout(self, keep_prob: float = 0.5) -> Dropout:
        """Performs create dropout operation for OmniDeepLearningEduEngine."""
        return Dropout(keep_prob=keep_prob)

    def create_batch_norm(self, num_features: int) -> BatchNorm:
        """Performs create batch norm operation for OmniDeepLearningEduEngine."""
        return BatchNorm(num_features=num_features)

    def create_adam(self, lr: float = 0.001) -> Adam:
        """Performs create adam operation for OmniDeepLearningEduEngine."""
        return Adam(lr=lr)

    def create_rmsprop(self, lr: float = 0.01) -> RMSprop:
        """Performs create rmsprop operation for OmniDeepLearningEduEngine."""
        return RMSprop(lr=lr)

    def create_momentum(self, lr: float = 0.01) -> Momentum:
        """Performs create momentum operation for OmniDeepLearningEduEngine."""
        return Momentum(lr=lr)

    # --- Health ---

    def diagnostics(self) -> Dict[str, Any]:
        """Performs diagnostics operation for OmniDeepLearningEduEngine."""
        return {
            "engine_id": self.ENGINE_ID,
            "version": self.VERSION,
            "initializers": ["he_normal", "xavier_normal", "zeros"],
            "layers": ["Dropout", "BatchNorm"],
            "optimizers": ["Momentum", "RMSprop", "Adam"],
            "status": "operational",
        }
