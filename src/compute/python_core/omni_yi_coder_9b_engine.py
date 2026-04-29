"""OmniYiCoder9BEngine.

Handles long-context repository-level code embedding logic and
chunking strategies optimized for the Yi-Coder 9B 128k context model.
"""
import sys
import os
import math
from typing import Dict, Any, List
from __future__ import annotations

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..')))
from src.compute.python_core.omni_base_engine import Result, Ok, Err

class OmniYiCoder9BEngine:
    """Zero-mock engine for repository-level long context chunking."""

    @staticmethod
    def diagnostics() -> dict:
        return {
            "engine": "OmniYiCoder9BEngine",
            "version": "1.0.0",
            "primitive": "repo_level_context_chunker",
            "monadic_enforcement": True,
        }

    @staticmethod
    def calculate_repo_chunking(total_repo_tokens: int, max_context: int = 128000, overlap: int = 1000) -> Result:
        """
        Calculates optimal chunks to feed an entire repository into 
        the Yi-Coder 9B model without losing structural context.
        """
        if total_repo_tokens <= 0 or max_context <= 0 or overlap < 0:
            return Err(ValueError("Invalid parameters for chunking"))
            
        if overlap >= max_context:
            return Err(ValueError("Overlap cannot be greater than or equal to max context"))
            
        if total_repo_tokens <= max_context:
            return Ok({
                "num_chunks": 1,
                "chunk_size": total_repo_tokens,
                "overlap": 0,
                "requires_chunking": False
            })
            
        effective_chunk_size = max_context - overlap
        num_chunks = math.ceil((total_repo_tokens - overlap) / effective_chunk_size)
        
        return Ok({
            "num_chunks": num_chunks,
            "chunk_size": max_context,
            "overlap": overlap,
            "requires_chunking": True,
            "total_processed_tokens": (num_chunks * effective_chunk_size) + overlap
        })
