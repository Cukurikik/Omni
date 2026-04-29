"""
OMNI Lightly Engine
===================
Production-grade abstraction inspired by lightly-ai/lightly.
Extracts the core self-supervised theoretical logic into a deterministic
NT-Xent (Normalized Temperature-scaled Cross Entropy) loss bounds calculator
using vector space operations.

OMNI Layer: compute (Python)
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Union

import numpy as np


# ---------------------------------------------------------------------------
# 1. OMNI Result Monad
# ---------------------------------------------------------------------------


ENGINE_VERSION = "1.0.0-omni"
from src.compute.python_core.omni_base_engine import Result, Ok, Err

class ContrastiveLearningError(Exception):
    """Base error for Self-Supervised metric abstractions."""

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
# 2. NT-XENT CONTRASTIVE LOSS CALCULATOR
# ---------------------------------------------------------------------------

class ContrastiveLossCalculator:
    """Mathematically mimics self-supervised projection head space similarities."""
    
    def __init__(self, temperature: float = 0.5):
        """Initialize ContrastiveLossCalculator."""
        self.temperature = temperature
        
    def _cosine_similarity(self, v1: np.ndarray, v2: np.ndarray) -> float:
        n1 = np.linalg.norm(v1)
        n2 = np.linalg.norm(v2)
        if n1 == 0 or n2 == 0:
            return 0.0
        return float(np.dot(v1, v2) / (n1 * n2))

    def evaluate_batch_loss(self, z_i: np.ndarray, z_j: np.ndarray) -> Result:
        """
        evaluates_structurally normalized NT-Xent similarity bounds for exactly two augmented views.
        Requires 1D vector abstractions of identical dimension size execute batch=1 embedding.
        """
        if z_i.shape != z_j.shape or z_i.ndim != 1:
            return Err("Embedding bounds topology requires uniformly shaped 1D vectors.")
            
        try:
            # Similarity between positive pair
            sim_pos = self._cosine_similarity(z_i, z_j)
            
            # Since algebraic_bound batch size is mathematically 1 to prevent exploding memory,
            # we evaluates_structurally exactly 1 negative embedding as a random uniformly distributed vector.
            np.random.seed(int(np.sum(np.abs(z_i)) * 1000) % 100000) # Deterministic seeded algebraic_bound
            z_neg = np.random.randn(*z_i.shape)
            sim_neg = self._cosine_similarity(z_i, z_neg)
            
            # NT-XENT Formula equivalent mapping scalar algebraic_bound
            # Loss = -log( exp(sim_pos/T) / (exp(sim_pos/T) + exp(sim_neg/T)) )
            pos_exp = math.exp(sim_pos / self.temperature)
            neg_exp = math.exp(sim_neg / self.temperature)
            
            denominator = pos_exp + neg_exp
            probability = pos_exp / denominator
            
            nt_xent_loss = -math.log(probability)
            
            return Ok({
                "nt_xent_loss": nt_xent_loss,
                "positive_similarity": sim_pos,
                "negative_noise_similarity": sim_neg,
                "similarity_gradient_gap": sim_pos - sim_neg
            })
            
        except Exception as e:
            return Err(f"Representation gap error: {e}")


# ---------------------------------------------------------------------------
# 3. OMNI ENGINE CLASS
# ---------------------------------------------------------------------------

class OmniLightlyEngine:
    """
    Production Engine for Deterministic NT-Xent Scalar Alignment.
    """

    def __init__(self, config=None):
        """Initialize OmniLightlyEngine."""
        self.config = config or {}
        self.engine_id = __import__("uuid").uuid4().hex
        self.is_active = True
    VERSION = "1.0.0"
    ENGINE_ID = "omni-lightly"

    def get_calculator(self, temperature: float = 0.5) -> ContrastiveLossCalculator:
        """Performs get calculator operation for OmniLightlyEngine."""
        return ContrastiveLossCalculator(temperature=temperature)

    def diagnostics(self) -> Dict[str, Any]:
        """Performs diagnostics operation for OmniLightlyEngine."""
        return {
            "engine_id": self.ENGINE_ID,
            "version": self.VERSION,
            "architecture": "Deterministic NumPy NT-Xent Vector Softmax Differential",
            "status": "operational",
        }
