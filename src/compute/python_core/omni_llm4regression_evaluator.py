# Omni LLM4Regression Evaluator (Python)
# Compute Layer: In-context regression evaluation for LLMs on synthetic tasks.
# Ref: robertvacareanu/llm4regression — LLMs for regression without parameter updates.

from typing import List, Tuple
import math

def compute_mse(predictions: List[float], targets: List[float]) -> float:
    if len(predictions) != len(targets) or not predictions:
        return float('inf')
    total = sum((p - t) ** 2 for p, t in zip(predictions, targets))
    return round(total / len(predictions), 10)

def compute_r_squared(predictions: List[float], targets: List[float]) -> float:
    if len(predictions) != len(targets) or len(targets) < 2:
        return 0.0
    mean_y = sum(targets) / len(targets)
    ss_res = sum((t - p) ** 2 for p, t in zip(predictions, targets))
    ss_tot = sum((t - mean_y) ** 2 for t in targets)
    if ss_tot == 0.0:
        return 1.0 if ss_res == 0.0 else 0.0
    return round(1.0 - ss_res / ss_tot, 8)

def linear_regression_closed_form(x: List[float], y: List[float]) -> Tuple[float, float]:
    n = len(x)
    if n != len(y) or n < 2:
        return (0.0, 0.0)
    sum_x = sum(x)
    sum_y = sum(y)
    sum_xy = sum(xi * yi for xi, yi in zip(x, y))
    sum_x2 = sum(xi ** 2 for xi in x)
    denom = n * sum_x2 - sum_x ** 2
    if abs(denom) < 1e-15:
        return (0.0, sum_y / n)
    slope = (n * sum_xy - sum_x * sum_y) / denom
    intercept = (sum_y - slope * sum_x) / n
    return (round(slope, 10), round(intercept, 10))
