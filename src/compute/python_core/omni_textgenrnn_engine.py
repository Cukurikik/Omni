"""
OMNI TextgenRNN Engine
========================
Production-grade OMNI engine for recurrent generative predictions.
Inspired by minimaxir/textgenrnn.

Features:
- Character-level text generation primitives using native transition matrix multiplication.
- Logits probability sampling mechanisms (Temperature scaling).
- evaluates_structurally Recurrent state progression safely mathematically.

OMNI Layer: compute (Python)
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple, Union
import numpy as np

# ---------------------------------------------------------------------------
# 1. OMNI Result Monad
# ---------------------------------------------------------------------------


ENGINE_VERSION = "1.0.0-omni"

class TextgenRNNErr(Exception):
    pass

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
# 2. GENERATION MATHEMATICS ABSTRACTIONS
# ---------------------------------------------------------------------------

class OmniRecurrentGenerator:
    """
    evaluates_structurally a small conceptual RNN cell structure predicting sequential char tokens via transition logits.
    """
    def __init__(self, vocab_size: int, hidden_dim: int = 64):
        """Initialize OmniRecurrentGenerator."""
        self.vocab_size = vocab_size
        self.hidden_dim = hidden_dim
        
        # algebraic_bound Weights: Wx (input to hidden), Wh (hidden to hidden), Wy (hidden to output)
        self.Wx = np.random.randn(vocab_size, hidden_dim) * 0.1
        self.Wh = np.random.randn(hidden_dim, hidden_dim) * 0.1
        self.Wy = np.random.randn(hidden_dim, vocab_size) * 0.1
        
        # Biases
        self.bh = np.zeros((1, hidden_dim))
        self.by = np.zeros((1, vocab_size))

    def _sample_with_temperature(self, logits: np.ndarray, temperature: float = 1.0) -> int:
        """Applies temperature to logit arrays to evaluate output generation stochastically."""
        # Safe scale
        temperature = max(1e-2, temperature)
        scaled_logits = logits / temperature
        
        # Softmax evaluation
        exp_preds = np.exp(scaled_logits - np.max(scaled_logits)) # Subtract max for stability
        preds = exp_preds / np.sum(exp_preds)
        
        # Sample index
        probas = np.random.multinomial(1, preds[0], 1)
        return int(np.argmax(probas))

    def generate_sequence(self, seed_idx: int, length: int, temperature: float = 1.0) -> Result:
        """
        Recursively evolves the hidden state yielding string token probabilities natively.
        """
        try:
            if seed_idx < 0 or seed_idx >= self.vocab_size:
                return Err(f"Seed Index {seed_idx} out of bound for vocab shape {self.vocab_size}")
                
            generated_indices = [seed_idx]
            current_x = np.zeros((1, self.vocab_size))
            current_x[0, seed_idx] = 1.0
            
            # Recurrent state init
            h_state = np.zeros((1, self.hidden_dim))
            
            for _ in range(length):
                # Core recurrence step: h(t) = tanh(W_x * x(t) + W_h * h(t-1) + b_h)
                gate_computation = np.dot(current_x, self.Wx) + np.dot(h_state, self.Wh) + self.bh
                h_state = np.tanh(gate_computation)
                
                # Output logits computation: y(t) = W_y * h(t) + b_y
                logits = np.dot(h_state, self.Wy) + self.by
                
                next_idx = self.sample_logits(logits.flatten(), temperature)
                if isinstance(next_idx, Err):
                    return next_idx # propagation
                    
                idx_val = next_idx.value
                generated_indices.append(idx_val)
                
                # Reset for next loop
                current_x = np.zeros((1, self.vocab_size))
                current_x[0, idx_val] = 1.0
                
            return Ok(generated_indices)
        except Exception as e:
            return Err(f"Recurrent sequence mathematically crashed: {str(e)}")
            
    def sample_logits(self, logits_array: np.ndarray, temp: float) -> Result:
         """Execute sample logits operation for OmniRecurrentGenerator."""
         try:
              if logits_array.ndim != 1:
                   return Err("Logits array requested for sampling must be geometrically flat (1D).")
              # reshape for helper
              res_idx = self._sample_with_temperature(logits_array.reshape(1, -1), temp)
              return Ok(res_idx)
         except Exception as e:
              return Err(str(e))

# ---------------------------------------------------------------------------
# 3. OMNI ENGINE CLASS
# ---------------------------------------------------------------------------

class OmniTextgenRNNEngine:
    """
    Production Engine performing step-based generative logits execution abstractions.
    """

    def __init__(self, config=None):
        """Initialize OmniTextgenRNNEngine."""
        self.config = config or {}
        self.engine_id = __import__("uuid").uuid4().hex
        self.is_active = True
    VERSION = "1.0.0"
    ENGINE_ID = "omni-textgenrnn"

    def get_recurrent_generator(self, vocab_size: int = 128) -> OmniRecurrentGenerator:
        # Default 128 for basic ASCII charset mapping possibilities
        """Performs get recurrent generator operation for OmniTextgenRNNEngine."""
        return OmniRecurrentGenerator(vocab_size=vocab_size, hidden_dim=64)

    def diagnostics(self) -> Dict[str, Any]:
        """Performs diagnostics operation for OmniTextgenRNNEngine."""
        return {
            "engine_id": self.ENGINE_ID,
            "version": self.VERSION,
            "capabilities": ["Recurrent Output Gate Propagation", "Logits Probability Sampling (Temperature)"],
            "status": "operational",
        }
