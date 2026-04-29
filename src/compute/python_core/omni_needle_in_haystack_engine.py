"""OmniNeedleInHaystackEngine.

Calculates loss decay functions over extreme context lengths
based on the Needle In A Haystack (NIAH) structural test.
"""
import sys
import os
import math
from typing import Dict, Any, List
from __future__ import annotations

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..')))
from src.compute.python_core.omni_base_engine import Result, Ok, Err

class OmniNeedleInHaystackEngine:
    """Production zero-mock engine for NIAH structural decay constraints."""

    @staticmethod
    def diagnostics() -> dict:
        return {
            "engine": "OmniNeedleInHaystackEngine",
            "version": "1.0.0",
            "primitive": "niah_decay_function",
            "monadic_enforcement": True,
        }

    @staticmethod
    def compute_attention_decay(context_length: int, depth: float, base_attention: float = 1.0) -> Result:
        """
        Theoretical model for how attention degrades for a specific fact
        based on context length and depth.
        Usually models struggle most in the "middle" of the context.
        """
        if context_length <= 0:
            return Err(ValueError("Context length must be positive"))
            
        if depth < 0.0 or depth > 1.0:
            return Err(ValueError("Depth must be between 0.0 and 1.0"))
            
        # Parabolic decay function (worst in the middle, depth=0.5)
        # Decay scales with context length (e.g. degrades more at 128k than 4k)
        length_penalty = math.log10(max(10, context_length)) / 5.0 # Normalizer
        
        # Parabola: 4 * (d - 0.5)^2 gives 1 at edges, 0 in middle
        # We invert it: 1 - (4 * (d - 0.5)^2) gives 1 in middle, 0 at edges
        middle_weakness = 1.0 - (4.0 * ((depth - 0.5) ** 2))
        
        decay_factor = middle_weakness * length_penalty * 0.5
        
        final_attention = max(0.0, base_attention - decay_factor)
        
        return Ok({
            "context_length": context_length,
            "depth": depth,
            "theoretical_retrieval_probability": final_attention,
            "is_lost_in_middle_risk": final_attention < 0.5
        })
