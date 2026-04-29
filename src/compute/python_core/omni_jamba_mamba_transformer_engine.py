"""OmniJambaMambaTransformerEngine.

Calculates layer routing and state space model (SSM) memory bounds
for Hybrid Mamba-Transformer architectures like Jamba.
"""
import sys
import os
from typing import Dict, Any, List
from __future__ import annotations

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..')))
from src.compute.python_core.omni_base_engine import Result, Ok, Err

class OmniJambaMambaTransformerEngine:
    """Production mathematical engine for hybrid architecture constraints."""

    @staticmethod
    def diagnostics() -> dict:
        return {
            "engine": "OmniJambaMambaTransformerEngine",
            "version": "1.0.0",
            "primitive": "hybrid_mamba_transformer_allocator",
            "monadic_enforcement": True,
        }

    @staticmethod
    def calculate_layer_distribution(total_layers: int, mamba_ratio: int = 7) -> Result:
        """
        Calculates the pattern of Mamba vs Transformer layers.
        """
        if total_layers <= 0:
            return Err(ValueError("Total layers must be positive"))
            
        layer_types = []
        for i in range(total_layers):
            if i % (mamba_ratio + 1) == 0:
                layer_types.append("ATTENTION")
            else:
                layer_types.append("MAMBA_SSM")
                
        return Ok(layer_types)

    @staticmethod
    def calculate_memory_footprint(seq_len: int, d_model: int, total_layers: int) -> Result:
        """
        Calculates memory bounds for inference context.
        """
        if seq_len <= 0 or d_model <= 0:
            return Err(ValueError("Sequence length and d_model must be positive"))
            
        dist_res = OmniJambaMambaTransformerEngine.calculate_layer_distribution(total_layers)
        if dist_res.is_err():
            return dist_res
            
        layers = dist_res.unwrap()
        attn_count = layers.count("ATTENTION")
        mamba_count = layers.count("MAMBA_SSM")
        
        attn_mem = attn_count * (seq_len * seq_len * 2) 
        mamba_mem = mamba_count * (seq_len * d_model * 2)
        
        return Ok({
            "attention_memory_bytes": attn_mem,
            "mamba_memory_bytes": mamba_mem,
            "total_activation_memory_bytes": attn_mem + mamba_mem,
            "attention_layers": attn_count,
            "mamba_layers": mamba_count
        })
