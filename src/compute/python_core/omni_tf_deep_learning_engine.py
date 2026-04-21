"""
OmniTfDeepLearningEngine — Native Keras-Style Sequential Deep Learning Engine.

Studied from: mrdbourke/tensorflow-deep-learning (5.5k★)
Implements: Sequential model builder, Dense/BatchNormalization/Dropout/Flatten
layers, optimizers (Adam, SGD, RMSprop), loss functions (MSE, MAE,
categorical/binary cross-entropy), learning rate schedulers (CosineAnnealing,
WarmupCosine, StepDecay), EarlyStopping callback, data utilities, and full
training/evaluation loop with history tracking.

OMNI Domain: compute/ (Python)
CODE RULE 001-005 compliant. Only numpy dependency.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Tuple

import numpy as np


ENGINE_VERSION: str = "1.1.0-omni"
ENGINE_NAME: str = "OmniTfDeepLearningEngine"


# ---------------------------------------------------------------------------
# Monadic Result Types
# ---------------------------------------------------------------------------

class Ok:
    """Success result wrapper.

    Attributes:
        value: The wrapped success value.
    """
    def __init__(self, value: Any = None) -> None:
        """Initialize Ok."""
        self.value = value

    def __repr__(self) -> str:
        return f"Ok({self.value!r})"


class Err:
    """Error result wrapper.

    Attributes:
        error: The error message or object.
    """
    def __init__(self, error: Any) -> None:
        """Initialize Err."""
        self.error = error

    def __repr__(self) -> str:
        return f"Err({self.error!r})"


# ---------------------------------------------------------------------------
# Activation functions
# ---------------------------------------------------------------------------

def _relu(x: np.ndarray) -> np.ndarray:
    return np.maximum(0, x)

def _sigmoid(x: np.ndarray) -> np.ndarray:
    x = np.clip(x, -500, 500)
    return 1.0 / (1.0 + np.exp(-x))

def _tanh(x: np.ndarray) -> np.ndarray:
    return np.tanh(x)

def _softmax(x: np.ndarray) -> np.ndarray:
    e = np.exp(x - np.max(x, axis=-1, keepdims=True))
    return e / np.sum(e, axis=-1, keepdims=True)

def _leaky_relu(x: np.ndarray, alpha: float = 0.01) -> np.ndarray:
    return np.where(x > 0, x, alpha * x)

def _linear(x: np.ndarray) -> np.ndarray:
    return x

def _swish(x: np.ndarray) -> np.ndarray:
    return x * _sigmoid(x)

_ACTIVATIONS: Dict[str, Callable] = {
    "relu": _relu, "sigmoid": _sigmoid, "tanh": _tanh,
    "softmax": _softmax, "leaky_relu": _leaky_relu,
    "linear": _linear, "swish": _swish,
}


# ---------------------------------------------------------------------------
# Loss functions
# ---------------------------------------------------------------------------

def _mse_loss(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    return float(np.mean((y_true - y_pred) ** 2))

def _mae_loss(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    return float(np.mean(np.abs(y_true - y_pred)))

def _categorical_crossentropy(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    y_pred = np.clip(y_pred, 1e-12, 1 - 1e-12)
    return float(-np.mean(np.sum(y_true * np.log(y_pred), axis=-1)))

def _binary_crossentropy(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    y_pred = np.clip(y_pred, 1e-12, 1 - 1e-12)
    return float(-np.mean(y_true * np.log(y_pred) + (1 - y_true) * np.log(1 - y_pred)))

_LOSSES: Dict[str, Callable] = {
    "mse": _mse_loss, "mae": _mae_loss,
    "categorical_crossentropy": _categorical_crossentropy,
    "binary_crossentropy": _binary_crossentropy,
}

# ---------------------------------------------------------------------------
# Metric functions
# ---------------------------------------------------------------------------

def _accuracy(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    if y_true.ndim > 1:
        return float(np.mean(np.argmax(y_true, axis=-1) == np.argmax(y_pred, axis=-1)))
    return float(np.mean((y_pred > 0.5).astype(int) == y_true.astype(int)))

def _mae_metric(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    return _mae_loss(y_true, y_pred)

_METRICS: Dict[str, Callable] = {
    "accuracy": _accuracy, "mae": _mae_metric,
}


# ---------------------------------------------------------------------------
# Layers
# ---------------------------------------------------------------------------

class Dense:
    """Fully connected layer with activation.

    Args:
        units: Output dimensionality.
        activation: Activation function name.
    """
    def __init__(self, units: int, activation: str = "linear") -> None:
        """Initialize Dense."""
        self.units = units
        self.activation_name = activation
        self._act_fn = _ACTIVATIONS.get(activation, _linear)
        self.W: Optional[np.ndarray] = None
        self.b: Optional[np.ndarray] = None
        self.input_dim: Optional[int] = None

    def build(self, input_dim: int) -> None:
        """Initialize weights using Glorot uniform.

        Args:
            input_dim: Dimension of input features.
        """
        self.input_dim = input_dim
        limit = np.sqrt(6.0 / (input_dim + self.units))
        self.W = np.random.uniform(-limit, limit, (input_dim, self.units)).astype(np.float32)
        self.b = np.zeros(self.units, dtype=np.float32)

    def forward(self, x: np.ndarray) -> np.ndarray:
        """Forward pass.

        Args:
            x: Input array of shape (..., input_dim).

        Returns:
            Output array of shape (..., units).
        """
        return self._act_fn(x @ self.W + self.b)

    @property
    def param_count(self) -> int:
        """Execute param count operation for Dense."""
        if self.W is not None:
            return int(self.W.size + self.b.size)
        return 0


class BatchNormalization:
    """Batch normalization layer.

    Args:
        eps: Small float for numerical stability.
        momentum: Running statistics momentum.
    """
    def __init__(self, eps: float = 1e-5, momentum: float = 0.1) -> None:
        """Initialize BatchNormalization."""
        self.eps = eps
        self.momentum = momentum
        self.gamma: Optional[np.ndarray] = None
        self.beta: Optional[np.ndarray] = None
        self.running_mean: Optional[np.ndarray] = None
        self.running_var: Optional[np.ndarray] = None
        self.units: Optional[int] = None

    def build(self, input_dim: int) -> None:
        """Execute build operation for BatchNormalization."""
        self.units = input_dim
        self.gamma = np.ones(input_dim, dtype=np.float32)
        self.beta = np.zeros(input_dim, dtype=np.float32)
        self.running_mean = np.zeros(input_dim, dtype=np.float32)
        self.running_var = np.ones(input_dim, dtype=np.float32)

    def forward(self, x: np.ndarray, training: bool = True) -> np.ndarray:
        """Execute forward operation for BatchNormalization."""
        if training:
            mean = np.mean(x, axis=0)
            var = np.var(x, axis=0)
            self.running_mean = (1 - self.momentum) * self.running_mean + self.momentum * mean
            self.running_var = (1 - self.momentum) * self.running_var + self.momentum * var
        else:
            mean = self.running_mean
            var = self.running_var
        return self.gamma * (x - mean) / np.sqrt(var + self.eps) + self.beta

    @property
    def param_count(self) -> int:
        """Execute param count operation for BatchNormalization."""
        return int(self.gamma.size + self.beta.size) if self.gamma is not None else 0


class Dropout:
    """Dropout regularization layer.

    Args:
        rate: Fraction of inputs to drop during training.
    """
    def __init__(self, rate: float = 0.5) -> None:
        """Initialize Dropout."""
        self.rate = rate
        self.units: Optional[int] = None

    def build(self, input_dim: int) -> None:
        """Execute build operation for Dropout."""
        self.units = input_dim

    def forward(self, x: np.ndarray, training: bool = True) -> np.ndarray:
        """Execute forward operation for Dropout."""
        if training and self.rate > 0:
            mask = (np.random.rand(*x.shape) > self.rate).astype(np.float32)
            return x * mask / (1 - self.rate)
        return x

    @property
    def param_count(self) -> int:
        """Execute param count operation for Dropout."""
        return 0


class Flatten:
    """Flatten layer — reshapes input to (batch, -1).

    Passthrough for 2D inputs.
    """
    def __init__(self) -> None:
        """Initialize Flatten."""
        self.units: Optional[int] = None

    def build(self, input_dim: int) -> None:
        """Execute build operation for Flatten."""
        self.units = input_dim

    def forward(self, x: np.ndarray, training: bool = True) -> np.ndarray:
        """Execute forward operation for Flatten."""
        if x.ndim > 2:
            return x.reshape(x.shape[0], -1)
        return x

    @property
    def param_count(self) -> int:
        """Execute param count operation for Flatten."""
        return 0


# ---------------------------------------------------------------------------
# Optimizers
# ---------------------------------------------------------------------------

class Adam:
    """Adam optimizer (Kingma & Ba, 2014).

    Args:
        lr: Learning rate.
        beta1: Exponential decay rate for first moment.
        beta2: Exponential decay rate for second moment.
        eps: Numerical stability constant.
    """
    def __init__(self, lr: float = 0.001, beta1: float = 0.9, beta2: float = 0.999, eps: float = 1e-8) -> None:
        """Initialize Adam."""
        self.lr = lr
        self.beta1 = beta1
        self.beta2 = beta2
        self.eps = eps
        self.t = 0
        self._m: Dict[int, np.ndarray] = {}
        self._v: Dict[int, np.ndarray] = {}

    def update(self, param_id: int, param: np.ndarray, grad: np.ndarray) -> np.ndarray:
        """Execute update operation for Adam."""
        self.t += 1
        if param_id not in self._m:
            self._m[param_id] = np.zeros_like(param)
            self._v[param_id] = np.zeros_like(param)
        self._m[param_id] = self.beta1 * self._m[param_id] + (1 - self.beta1) * grad
        self._v[param_id] = self.beta2 * self._v[param_id] + (1 - self.beta2) * grad ** 2
        m_hat = self._m[param_id] / (1 - self.beta1 ** self.t)
        v_hat = self._v[param_id] / (1 - self.beta2 ** self.t)
        return param - self.lr * m_hat / (np.sqrt(v_hat) + self.eps)


class SGD:
    """Stochastic Gradient Descent optimizer.

    Args:
        lr: Learning rate.
        momentum: Momentum coefficient.
    """
    def __init__(self, lr: float = 0.01, momentum: float = 0.0) -> None:
        """Initialize SGD."""
        self.lr = lr
        self.momentum = momentum
        self._v: Dict[int, np.ndarray] = {}

    def update(self, param_id: int, param: np.ndarray, grad: np.ndarray) -> np.ndarray:
        """Execute update operation for SGD."""
        if param_id not in self._v:
            self._v[param_id] = np.zeros_like(param)
        self._v[param_id] = self.momentum * self._v[param_id] - self.lr * grad
        return param + self._v[param_id]


class RMSprop:
    """RMSprop optimizer.

    Args:
        lr: Learning rate.
        rho: Decay rate.
        eps: Numerical stability constant.
    """
    def __init__(self, lr: float = 0.001, rho: float = 0.9, eps: float = 1e-8) -> None:
        """Initialize RMSprop."""
        self.lr = lr
        self.rho = rho
        self.eps = eps
        self._s: Dict[int, np.ndarray] = {}

    def update(self, param_id: int, param: np.ndarray, grad: np.ndarray) -> np.ndarray:
        """Execute update operation for RMSprop."""
        if param_id not in self._s:
            self._s[param_id] = np.zeros_like(param)
        self._s[param_id] = self.rho * self._s[param_id] + (1 - self.rho) * grad ** 2
        return param - self.lr * grad / (np.sqrt(self._s[param_id]) + self.eps)


_OPTIMIZERS: Dict[str, type] = {"adam": Adam, "sgd": SGD, "rmsprop": RMSprop}


# ---------------------------------------------------------------------------
# Learning Rate Schedulers
# ---------------------------------------------------------------------------

class CosineAnnealing:
    """Cosine annealing learning rate scheduler.

    Args:
        initial_lr: Starting learning rate.
        T_max: Maximum number of iterations.
    """
    def __init__(self, initial_lr: float = 0.01, T_max: int = 100) -> None:
        """Initialize CosineAnnealing."""
        self.initial_lr = initial_lr
        self.T_max = T_max

    def get_lr(self, epoch: int, current_lr: float) -> float:
        """Retrieve lr from CosineAnnealing."""
        return self.initial_lr * (1 + math.cos(math.pi * epoch / self.T_max)) / 2


class WarmupCosine:
    """Cosine schedule with linear warmup.

    Args:
        initial_lr: Peak learning rate.
        warmup_epochs: Number of warmup epochs.
        T_max: Total epochs.
    """
    def __init__(self, initial_lr: float = 0.01, warmup_epochs: int = 5, T_max: int = 100) -> None:
        """Initialize WarmupCosine."""
        self.initial_lr = initial_lr
        self.warmup_epochs = warmup_epochs
        self.T_max = T_max

    def get_lr(self, epoch: int, current_lr: float) -> float:
        """Retrieve lr from WarmupCosine."""
        if epoch < self.warmup_epochs:
            return self.initial_lr * (epoch + 1) / self.warmup_epochs
        progress = (epoch - self.warmup_epochs) / max(1, self.T_max - self.warmup_epochs)
        return self.initial_lr * (1 + math.cos(math.pi * progress)) / 2


class StepDecay:
    """Step decay learning rate scheduler.

    Args:
        initial_lr: Starting learning rate.
        drop_rate: Multiplicative factor.
        step_size: Epochs between drops.
    """
    def __init__(self, initial_lr: float = 0.01, drop_rate: float = 0.5, step_size: int = 10) -> None:
        """Initialize StepDecay."""
        self.initial_lr = initial_lr
        self.drop_rate = drop_rate
        self.step_size = step_size

    def get_lr(self, epoch: int, current_lr: float) -> float:
        """Retrieve lr from StepDecay."""
        return self.initial_lr * (self.drop_rate ** (epoch // self.step_size))


# ---------------------------------------------------------------------------
# EarlyStopping callback
# ---------------------------------------------------------------------------

class EarlyStopping:
    """Early stopping callback to terminate training when validation loss plateaus.

    Args:
        patience: Number of epochs with no improvement before stopping.
        min_delta: Minimum change to qualify as improvement.
    """
    def __init__(self, patience: int = 5, min_delta: float = 0.0) -> None:
        """Initialize EarlyStopping."""
        self.patience = patience
        self.min_delta = min_delta
        self._best: Optional[float] = None
        self._wait: int = 0

    def check(self, val_loss: float) -> bool:
        """Check whether training should stop.

        Args:
            val_loss: Current validation loss.

        Returns:
            True if training should stop.
        """
        if self._best is None or val_loss < self._best - self.min_delta:
            self._best = val_loss
            self._wait = 0
            return False
        self._wait += 1
        return self._wait >= self.patience


# ---------------------------------------------------------------------------
# Training History
# ---------------------------------------------------------------------------

@dataclass
class TrainingHistory:
    """Record of training metrics per epoch.

    Attributes:
        loss: List of training loss per epoch.
        val_loss: List of validation loss per epoch.
        metrics: Dict of metric name -> list of values per epoch.
    """
    loss: List[float] = field(default_factory=list)
    val_loss: List[float] = field(default_factory=list)
    metrics: Dict[str, List[float]] = field(default_factory=dict)


# ---------------------------------------------------------------------------
# Sequential Model
# ---------------------------------------------------------------------------

class Sequential:
    """Keras-style sequential model container.

    Layers are stacked linearly. Supports compile, fit, evaluate, predict,
    and summary.
    """

    def __init__(self, layers: Optional[List] = None) -> None:
        """Initialize Sequential."""
        self.layers: List = layers if layers else []
        self._compiled = False
        self._optimizer = None
        self._loss_fn = None
        self._loss_name: str = ""
        self._metric_fns: Dict[str, Callable] = {}
        self._lr: float = 0.001

    def add(self, layer) -> None:
        """Append a layer.

        Args:
            layer: Layer instance (Dense, BatchNormalization, Dropout, Flatten).
        """
        self.layers.append(layer)

    def compile(
        self, optimizer: str = "adam", loss: str = "mse",
        metrics: Optional[List[str]] = None, lr: float = 0.001,
    ) -> Ok | Err:
        """Configure the model for training.

        Args:
            optimizer: Optimizer name ("adam", "sgd", "rmsprop").
            loss: Loss function name.
            metrics: List of metric names to track.
            lr: Learning rate.

        Returns:
            Ok on success, Err on failure.
        """
        if optimizer not in _OPTIMIZERS:
            return Err(f"Unknown optimizer: {optimizer}")
        if loss not in _LOSSES:
            return Err(f"Unknown loss: {loss}")

        self._lr = lr
        opt_cls = _OPTIMIZERS[optimizer]
        self._optimizer = opt_cls(lr=lr)
        self._loss_fn = _LOSSES[loss]
        self._loss_name = loss

        if metrics:
            for m in metrics:
                if m in _METRICS:
                    self._metric_fns[m] = _METRICS[m]

        self._compiled = True
        return Ok("compiled")

    def _build(self, input_dim: int) -> None:
        """Build all layers by propagating dimensions.

        Args:
            input_dim: Dimension of input features.
        """
        dim = input_dim
        for layer in self.layers:
            layer.build(dim)
            if hasattr(layer, "units") and layer.units is not None:
                dim = layer.units

    def _forward(self, x: np.ndarray, training: bool = True) -> np.ndarray:
        """Forward pass through all layers.

        Args:
            x: Input batch.
            training: Whether in training mode.

        Returns:
            Output predictions.
        """
        out = x
        for layer in self.layers:
            if isinstance(layer, (Dropout, BatchNormalization)):
                out = layer.forward(out, training=training)
            else:
                out = layer.forward(out)
        return out

    def fit(
        self, X: np.ndarray, y: np.ndarray, epochs: int = 10,
        batch_size: int = 32, validation_data: Optional[Tuple] = None,
        verbose: bool = True,
    ) -> Ok | Err:
        """Train the model.

        Args:
            X: Training features.
            y: Training targets.
            epochs: Number of epochs.
            batch_size: Mini-batch size.
            validation_data: Optional (X_val, y_val) tuple.
            verbose: Print progress.

        Returns:
            Ok(TrainingHistory) on success, Err on failure.
        """
        if not self._compiled:
            return Err("Model not compiled")

        # Build layers on first call
        if self.layers[0].W is None if isinstance(self.layers[0], Dense) else (not hasattr(self.layers[0], '_built')):
            self._build(X.shape[-1])

        history = TrainingHistory()
        n = X.shape[0]

        for epoch in range(epochs):
            # Shuffle
            perm = np.random.permutation(n)
            X_shuf = X[perm]
            y_shuf = y[perm]

            epoch_loss = 0.0
            batches = 0

            for start in range(0, n, batch_size):
                xb = X_shuf[start:start + batch_size].astype(np.float32)
                yb = y_shuf[start:start + batch_size].astype(np.float32)

                # Forward
                pred = self._forward(xb, training=True)
                loss = self._loss_fn(yb, pred)
                epoch_loss += loss
                batches += 1

                # Numerical gradient-based parameter update
                pid = 0
                for layer in self.layers:
                    if isinstance(layer, Dense) and layer.W is not None:
                        # Weight gradient (numerical approximation for production correctness)
                        grad_W = np.zeros_like(layer.W)
                        h = 1e-4
                        for i in range(min(layer.W.shape[0], layer.W.shape[0])):
                            for j in range(layer.W.shape[1]):
                                layer.W[i, j] += h
                                loss_plus = self._loss_fn(yb, self._forward(xb, False))
                                layer.W[i, j] -= 2 * h
                                loss_minus = self._loss_fn(yb, self._forward(xb, False))
                                layer.W[i, j] += h
                                grad_W[i, j] = (loss_plus - loss_minus) / (2 * h)

                        layer.W = self._optimizer.update(pid, layer.W, grad_W)
                        pid += 1

                        # Bias gradient
                        grad_b = np.zeros_like(layer.b)
                        for j in range(layer.b.size):
                            layer.b[j] += h
                            loss_plus = self._loss_fn(yb, self._forward(xb, False))
                            layer.b[j] -= 2 * h
                            loss_minus = self._loss_fn(yb, self._forward(xb, False))
                            layer.b[j] += h
                            grad_b[j] = (loss_plus - loss_minus) / (2 * h)

                        layer.b = self._optimizer.update(pid, layer.b, grad_b)
                        pid += 1

            avg_loss = epoch_loss / max(batches, 1)
            history.loss.append(avg_loss)

            # Validation
            if validation_data is not None:
                xv, yv = validation_data
                val_pred = self._forward(xv.astype(np.float32), training=False)
                vl = self._loss_fn(yv.astype(np.float32), val_pred)
                history.val_loss.append(vl)

            if verbose:
                msg = f"Epoch {epoch+1}/{epochs} - loss: {avg_loss:.4f}"
                if history.val_loss:
                    msg += f" - val_loss: {history.val_loss[-1]:.4f}"
                print(msg)

        return Ok(history)

    def evaluate(self, X: np.ndarray, y: np.ndarray) -> Dict[str, float]:
        """Evaluate the model on test data.

        Args:
            X: Test features.
            y: Test targets.

        Returns:
            Dict with loss and metric values.
        """
        pred = self._forward(X.astype(np.float32), training=False)
        result = {"loss": self._loss_fn(y.astype(np.float32), pred)}
        for name, fn in self._metric_fns.items():
            result[name] = fn(y, pred)
        return result

    def predict(self, X: np.ndarray) -> np.ndarray:
        """Generate predictions.

        Args:
            X: Input features.

        Returns:
            Model predictions.
        """
        return self._forward(X.astype(np.float32), training=False)

    def summary(self) -> str:
        """Generate a human-readable model summary.

        Returns:
            Multi-line string describing the architecture.
        """
        lines = ["=" * 50, "Model Summary", "=" * 50]
        total = 0
        for i, layer in enumerate(self.layers):
            name = type(layer).__name__
            units = getattr(layer, 'units', '?')
            act = getattr(layer, 'activation_name', '-')
            params = getattr(layer, 'param_count', 0)
            if callable(params):
                params = params()
            total += params
            lines.append(f"  [{i}] {name:20s} units={units!s:6s} act={act:10s} params={params}")
        lines.append("-" * 50)
        lines.append(f"  Total params: {total}")
        lines.append("=" * 50)
        return "\n".join(lines)


# ---------------------------------------------------------------------------
# Core Engine
# ---------------------------------------------------------------------------

class OmniTfDeepLearningEngine:
    """Production-grade Keras-style deep learning engine.

    Capabilities:
        - Sequential model with Dense, BN, Dropout, Flatten layers
        - Adam/SGD/RMSprop optimizers
        - MSE/MAE/CrossEntropy losses
        - CosineAnnealing/WarmupCosine/StepDecay schedulers
        - EarlyStopping callback
        - Data utilities (train_test_split, one_hot, normalize)
    """

    def __init__(self) -> None:
        """Initialize OmniTfDeepLearningEngine."""
        self._version: str = ENGINE_VERSION
        self._name: str = ENGINE_NAME

    def build_classifier(
        self, input_dim: int, hidden_units: List[int],
        num_classes: int, dropout_rate: float = 0.0,
    ) -> Sequential:
        """Build a classifier Sequential model.

        Args:
            input_dim: Input feature dimension.
            hidden_units: List of hidden layer sizes.
            num_classes: Number of output classes.
            dropout_rate: Dropout rate between layers.

        Returns:
            Sequential model (not yet compiled).
        """
        model = Sequential()
        for units in hidden_units:
            model.add(Dense(units, activation="relu"))
            if dropout_rate > 0:
                model.add(Dropout(rate=dropout_rate))
        model.add(Dense(num_classes, activation="softmax"))
        model._build(input_dim)
        return model

    def build_regressor(
        self, input_dim: int, hidden_units: List[int],
        output_dim: int = 1,
    ) -> Sequential:
        """Build a regressor Sequential model.

        Args:
            input_dim: Input feature dimension.
            hidden_units: List of hidden layer sizes.
            output_dim: Output dimension.

        Returns:
            Sequential model (not yet compiled).
        """
        model = Sequential()
        for units in hidden_units:
            model.add(Dense(units, activation="relu"))
        model.add(Dense(output_dim, activation="linear"))
        model._build(input_dim)
        return model

    # -- Data Utilities ------------------------------------------------------

    @staticmethod
    def train_test_split(
        X: np.ndarray, y: np.ndarray, test_size: float = 0.2,
        random_state: Optional[int] = None,
    ) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
        """Split data into train and test sets.

        Args:
            X: Features array.
            y: Labels array.
            test_size: Fraction for test set.
            random_state: Random seed for reproducibility.

        Returns:
            (X_train, X_test, y_train, y_test).
        """
        rng = np.random.RandomState(random_state)
        n = X.shape[0]
        perm = rng.permutation(n)
        split = int(n * (1 - test_size))
        return X[perm[:split]], X[perm[split:]], y[perm[:split]], y[perm[split:]]

    @staticmethod
    def one_hot_encode(labels: np.ndarray, num_classes: int) -> np.ndarray:
        """One-hot encode integer labels.

        Args:
            labels: Integer label array.
            num_classes: Total number of classes.

        Returns:
            One-hot encoded array of shape (N, num_classes).
        """
        n = labels.shape[0]
        oh = np.zeros((n, num_classes), dtype=np.float32)
        for i in range(n):
            oh[i, int(labels[i])] = 1.0
        return oh

    @staticmethod
    def normalize(X: np.ndarray) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """Z-score normalization.

        Args:
            X: Feature array.

        Returns:
            (normalized_X, mean, std).
        """
        mean = np.mean(X, axis=0)
        std = np.std(X, axis=0) + 1e-8
        return (X - mean) / std, mean, std

    # -- Introspection -------------------------------------------------------

    @staticmethod
    def available_optimizers() -> List[str]:
        """Performs available optimizers operation for OmniTfDeepLearningEngine."""
        return list(_OPTIMIZERS.keys())

    @staticmethod
    def available_losses() -> List[str]:
        """Performs available losses operation for OmniTfDeepLearningEngine."""
        return list(_LOSSES.keys())

    @staticmethod
    def available_activations() -> List[str]:
        """Performs available activations operation for OmniTfDeepLearningEngine."""
        return list(_ACTIVATIONS.keys())

    def diagnostics(self) -> Dict[str, Any]:
        """Return engine health diagnostics.

        Returns:
            Dictionary with engine status information.
        """
        return {
            "engine": self._name,
            "version": self._version,
            "status": "operational",
            "optimizers": self.available_optimizers(),
            "losses": self.available_losses(),
            "activations": self.available_activations(),
        }

    # -- Legacy API (Batch 10 backward compatibility) -------------------------

    def add(self, layer) -> None:
        """Legacy add method — creates an internal Sequential model and adds layers."""
        if not hasattr(self, '_legacy_model') or self._legacy_model is None:
            self._legacy_model = Sequential()
        self._legacy_model.add(layer)

    def compile_model(self, input_shape: int):
        """Legacy compile — build layers using the old API signature."""
        if not hasattr(self, '_legacy_model') or self._legacy_model is None:
            return Result(error="No layers added")
        self._legacy_input_shape = input_shape
        self._legacy_model._build(input_shape)
        self._legacy_compiled = True
        return Result(value={"status": "Compiled structurally."})

    def predict(self, x: np.ndarray):
        """Legacy predict — forward through sequentially added layers."""
        if not hasattr(self, '_legacy_compiled') or not self._legacy_compiled:
            return Result(error="Sequential model is not compiled algebraically.")
        if x.shape[-1] != self._legacy_input_shape:
            return Result(error=f"Dimensionality map violation. Expected {self._legacy_input_shape}, received {x.shape[-1]}")
        predictions = self._legacy_model._forward(x.astype(np.float32), training=False)
        return Result(value={"predictions": predictions})


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


# Legacy alias
NativeDenseLayer = Dense
