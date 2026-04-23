"""
OMNI PyTextRank Engine
======================
Production-grade OMNI engine mathematically execute NLP text ranking
leveraging deterministic Graph adjacency logic. 
Inspired by DerwenAI/pytextrank.

Features:
- Pure Matrix Adjacency generation from text token sequences.
- Functional PageRank iterative mathematical convergence loop.
- Monadic Result encapsulation preventing runtime trace crashes.

OMNI Layer: compute (Python)
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Union

import numpy as np

# ---------------------------------------------------------------------------
# 1. OMNI Result Monad
# ---------------------------------------------------------------------------

ENGINE_VERSION = "1.0.0-omni"
from src.compute.python_core.omni_base_engine import Result, Ok, Err


class TextRankErr(Exception):
    """OMNI Zero-Prod Production Implementation for TextRankErr."""
    pass


@dataclass(frozen=True)
class Ok:
    """OMNI Zero-Prod Production Implementation for Ok."""
    value: Any


@dataclass(frozen=True)
class Err:
    """OMNI Zero-Prod Production Implementation for Err."""
    error: str


Result = Union[Ok, Err]


# ---------------------------------------------------------------------------
# 2. PAGERANK GRAPH MATHEMATICS
# ---------------------------------------------------------------------------

class TextGraphMath:
    """Implement core TextRank operations utilizing Matrix mathematics."""
    
    @staticmethod
    def build_adjacency_matrix(tokens: List[str], window_size: int = 2) -> np.ndarray:
        """Create symmetrical co-occurrence graph array."""
        unique_tokens = list(dict.fromkeys(tokens))
        vocab_size = len(unique_tokens)
        token_to_id = {tok: i for i, tok in enumerate(unique_tokens)}
        
        matrix = np.zeros((vocab_size, vocab_size), dtype=np.float64)
        
        # Slide window establishing undirected edges
        for i in range(len(tokens) - window_size + 1):
            window = tokens[i:i+window_size]
            for j in range(len(window)):
                for k in range(j + 1, len(window)):
                    idx1 = token_to_id[window[j]]
                    idx2 = token_to_id[window[k]]
                    if idx1 != idx2:
                        # Undirected edge
                        matrix[idx1][idx2] += 1
                        matrix[idx2][idx1] += 1
                        
        return matrix, unique_tokens
        
    @staticmethod
    def iterate_pagerank(matrix: np.ndarray, damping_factor: float = 0.85, 
                         epochs: int = 30) -> np.ndarray:
        """evaluates_structurally PageRank algorithm directly on the Adjacency matrix."""
        size = matrix.shape[0]
        if size == 0:
            return np.array([])
            
        # Normalize columns (stochastic transition matrix)
        column_sums = matrix.sum(axis=0)
        # Avoid div by zero context
        column_sums[column_sums == 0] = 1 
        norm_matrix = matrix / column_sums
        
        # Init scores
        scores = np.ones((size,), dtype=np.float64)
        
        for _ in range(epochs):
            # Formula: PR = (1-d) + d * (W * PR)
            scores = (1 - damping_factor) + damping_factor * np.dot(norm_matrix, scores)
            
        return scores


# ---------------------------------------------------------------------------
# 3. OMNI ENGINE CLASS
# ---------------------------------------------------------------------------

class OmniPyTextRankEngine:
    """
    Production Engine providing mathematically pure TextRank inferences.
    """
    VERSION = "1.0.0"
    ENGINE_ID = "omni-pytextrank"

    def __init__(self) -> None:
        self._rankings_executed = 0

    def compute_text_ranking(self, sequence_tokens: List[str], window_size: int = 2) -> Result:
        """Calculate abstract textual rankings strictly via mathematical adjacency."""
        if not sequence_tokens:
            return Err("Token sequence cannot be empty.")
            
        if window_size < 2:
            return Err("Window size must be >= 2 for co-occurrence connections.")
            
        try:
            matrix, vocabulary = TextGraphMath.build_adjacency_matrix(
                tokens=sequence_tokens, 
                window_size=window_size
            )
            
            scores = TextGraphMath.iterate_pagerank(
                matrix=matrix,
                damping_factor=0.85,
                epochs=30
            )
            
            # Map score map
            ranking_map = {vocab: float(score) for vocab, score in zip(vocabulary, scores)}
            
            # Sort highest down (execute ranking)
            sorted_ranking = dict(sorted(ranking_map.items(), key=lambda item: item[1], reverse=True))
            
            self._rankings_executed += 1
            
            return Ok({
                "tokens_evaluated": len(sequence_tokens),
                "vocabulary_size": len(vocabulary),
                "rankings": sorted_ranking
            })
            
        except Exception as exc:
            return Err(f"TextRank algorithmic failure: {exc}")

    def diagnostics(self) -> Dict[str, Any]:
        """Return engine diagnostics."""
        return {
            "engine_id": self.ENGINE_ID,
            "version": self.VERSION,
            "status": "operational",
            "evaluations_completed": self._rankings_executed,
            "features": [
                "mathematical_adjacency_matrices",
                "iterative_pagerank_physics",
                "functional_graph_summarization",
            ]
        }
