"""OMNI Compute — RMSNorm (Root Mean Square Normalization)"""
import math
from typing import List

def rms_norm(hidden_states: List[float], weight: List[float], eps: float = 1e-6) -> List[float]:
    """
    Applies RMSNorm to a hidden state vector. 
    Used in modern LLMs (Llama, Mistral) instead of LayerNorm for speed.
    """
    dim = len(hidden_states)
    
    # Calculate Mean Square
    variance = sum(x * x for x in hidden_states) / dim
    
    # Calculate reciprocal square root
    rsqrt = 1.0 / math.sqrt(variance + eps)
    
    # Normalize and scale
    return [(x * rsqrt) * w for x, w in zip(hidden_states, weight)]
