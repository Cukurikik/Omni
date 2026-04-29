"""OmniHybridRAGDenseSparseEngine.

Computes Reciprocal Rank Fusion (RRF) to optimally merge
results from dense (vector) and sparse (BM25) retrieval systems.
"""
import sys
import os
from typing import Dict, Any, List
from __future__ import annotations

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..')))
from src.compute.python_core.omni_base_engine import Result, Ok, Err

class OmniHybridRAGDenseSparseEngine:
    """Production mathematical engine for RRF hybrid search fusion."""

    @staticmethod
    def diagnostics() -> dict:
        return {
            "engine": "OmniHybridRAGDenseSparseEngine",
            "version": "1.0.0",
            "primitive": "reciprocal_rank_fusion",
            "monadic_enforcement": True,
        }

    @staticmethod
    def fuse_rankings(dense_ranks: List[str], sparse_ranks: List[str], k: int = 60) -> Result:
        """
        Calculates RRF score: 1 / (k + rank) for each document across both lists.
        k is a smoothing constant, usually 60.
        """
        if not dense_ranks and not sparse_ranks:
            return Err(ValueError("Both ranking lists are empty"))
            
        scores = {}
        
        # Process dense
        for idx, doc_id in enumerate(dense_ranks):
            rank = idx + 1
            scores[doc_id] = scores.get(doc_id, 0.0) + (1.0 / (k + rank))
            
        # Process sparse
        for idx, doc_id in enumerate(sparse_ranks):
            rank = idx + 1
            scores[doc_id] = scores.get(doc_id, 0.0) + (1.0 / (k + rank))
            
        # Sort by RRF score descending
        fused_list = sorted(scores.items(), key=lambda item: item[1], reverse=True)
        
        return Ok({
            "fused_rankings": [{"doc_id": doc_id, "rrf_score": score} for doc_id, score in fused_list],
            "total_unique_docs": len(scores),
            "k_constant": k
        })
