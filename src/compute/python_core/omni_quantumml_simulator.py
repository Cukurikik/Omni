# Omni QuantumML Simulator Engine
import math
from typing import List, Tuple

def simulate_qubit_rotation(state_vector: Tuple[float, float], theta: float) -> Tuple[float, float]:
    """Simulate a single qubit Ry rotation gate."""
    alpha, beta = state_vector
    cos_t = math.cos(theta / 2.0)
    sin_t = math.sin(theta / 2.0)
    
    new_alpha = alpha * cos_t - beta * sin_t
    new_beta = alpha * sin_t + beta * cos_t
    return (round(new_alpha, 6), round(new_beta, 6))

def compute_quantum_fidelity(state_a: Tuple[float, float], state_b: Tuple[float, float]) -> float:
    """Compute fidelity between two single-qubit pure states."""
    # Fidelity |<a|b>|^2
    dot_product = state_a[0]*state_b[0] + state_a[1]*state_b[1]
    return round(dot_product ** 2, 6)

def quantum_loss_function(pred_state: Tuple[float, float], target_state: Tuple[float, float]) -> float:
    fidelity = compute_quantum_fidelity(pred_state, target_state)
    return round(1.0 - fidelity, 6)
