"""OmniDBRXFineGrainedMoEEngine.

Implements fine-grained Mixture of Experts (MoE) routing calculations
as used in the DBRX architecture (e.g., 16 experts, top 4 routing).
"""
import sys
import os
import math
from typing import Dict, Any, List, Tuple
from __future__ import annotations

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..')))
from src.compute.python_core.omni_base_engine import Result, Ok, Err

class OmniDBRXFineGrainedMoEEngine:
    """Production logic for fine-grained MoE token routing."""

    @staticmethod
    def diagnostics() -> dict:
        return {
            "engine": "OmniDBRXFineGrainedMoEEngine",
            "version": "1.0.0",
            "primitive": "fine_grained_moe_router",
            "monadic_enforcement": True,
        }

    @staticmethod
    def route_tokens(gate_logits: List[List[float]], top_k: int = 4) -> Result:
        """
        Routes tokens to the top-k experts based on gate logits.
        """
        if not gate_logits or not gate_logits[0]:
            return Err(ValueError("Invalid gate logits provided"))
            
        num_experts = len(gate_logits[0])
        if top_k > num_experts:
            return Err(ValueError(f"top_k ({top_k}) cannot exceed num_experts ({num_experts})"))
            
        routing_decisions = []
        for token_logits in gate_logits:
            if len(token_logits) != num_experts:
                return Err(ValueError("Inconsistent number of experts across tokens"))
                
            # Softmax calculation
            max_logit = max(token_logits)
            exp_logits = [math.exp(l - max_logit) for l in token_logits]
            sum_exp = sum(exp_logits)
            probs = [e / sum_exp for e in exp_logits]
            
            # Select top-k
            indexed_probs = list(enumerate(probs))
            indexed_probs.sort(key=lambda x: x[1], reverse=True)
            
            top_k_indices = [idx for idx, _ in indexed_probs[:top_k]]
            top_k_weights = [weight for _, weight in indexed_probs[:top_k]]
            
            # Re-normalize weights among top-k
            sum_top_k = sum(top_k_weights)
            normalized_weights = [w / sum_top_k for w in top_k_weights] if sum_top_k > 0 else [0.0]*top_k
            
            routing_decisions.append({
                "experts": top_k_indices,
                "weights": normalized_weights
            })
            
        return Ok(routing_decisions)
