# Omni BuildYourOwnX ML Trainer (Python)
# Compute: Foundational ML building blocks from scratch.
# Ref: amitshekhariitbhu/build-your-own-x-machine-learning
import math
from typing import List, Tuple

def linear_regression_gradient(X: List[List[float]], y: List[float], weights: List[float], lr: float) -> List[float]:
    n = len(X)
    if n == 0: return weights
    d = len(weights)
    grad = [0.0] * d
    for i in range(n):
        pred = sum(X[i][j] * weights[j] for j in range(d))
        error = pred - y[i]
        for j in range(d):
            grad[j] += (2.0 / n) * error * X[i][j]
    return [weights[j] - lr * grad[j] for j in range(d)]

def sigmoid(x: float) -> float:
    return 1.0 / (1.0 + math.exp(-max(-500, min(500, x))))

def binary_cross_entropy(y_true: List[float], y_pred: List[float]) -> float:
    n = len(y_true)
    if n == 0: return 0.0
    eps = 1e-15
    return -sum(y * math.log(max(p, eps)) + (1-y) * math.log(max(1-p, eps)) for y, p in zip(y_true, y_pred)) / n
