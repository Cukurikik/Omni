"""OmniLightRAGEngine.

Optimized dual-level retrieval (local entity + global relationship)
fast routing for the LightRAG architecture.
"""
import sys
import os
from typing import Dict, Any, List
from __future__ import annotations

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..')))
from src.compute.python_core.omni_base_engine import Result, Ok, Err

class OmniLightRAGEngine:
    """Zero-mock engine for LightRAG dual retrieval routing."""

    @staticmethod
    def diagnostics() -> dict:
        return {
            "engine": "OmniLightRAGEngine",
            "version": "1.0.0",
            "primitive": "dual_level_retriever",
            "monadic_enforcement": True,
        }

    @staticmethod
    def balance_retrieval_query(query_complexity: float, max_tokens: int = 4096) -> Result:
        """
        LightRAG dynamically balances tokens spent on local entity details
        vs global graph relationship summaries based on query complexity.
        """
        if max_tokens <= 0:
            return Err(ValueError("Max tokens must be positive"))
            
        # Complexity between 0.0 (very specific fact) to 1.0 (broad summary)
        clamped_complexity = max(0.0, min(1.0, query_complexity))
        
        # High complexity = more global context. Low complexity = more local context.
        global_ratio = 0.2 + (0.6 * clamped_complexity)
        local_ratio = 1.0 - global_ratio
        
        global_tokens = int(max_tokens * global_ratio)
        local_tokens = max_tokens - global_tokens
        
        return Ok({
            "query_complexity": clamped_complexity,
            "global_relationship_tokens": global_tokens,
            "local_entity_tokens": local_tokens,
            "strategy": "broad_summary" if clamped_complexity > 0.6 else "specific_fact"
        })
