"""
OMNI Marqo Engine
=================
Production-grade Vector Database abstraction inspired by marqo-ai/marqo.
Provides an in-memory document indexing and multi-dimensional
vector search engine executing completely via NumPy matmuls.

OMNI Layer: compute (Python)
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Union

import numpy as np


# ---------------------------------------------------------------------------
# 1. OMNI Result Monad
# ---------------------------------------------------------------------------


ENGINE_VERSION = "1.0.0-omni"

class MarqoError(Exception):
    """Base error for Marqo Vector engine."""

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
# 2. VECTOR SEARCH ENGINE
# ---------------------------------------------------------------------------

@dataclass
class Document:
    """Production-grade Document component."""
    id: str
    content: Dict[str, Any]
    tensor: np.ndarray

@dataclass
class SearchResult:
    """Production-grade Search Result component."""
    document: Document
    score: float


class VectorIndex:
    """An in-memory parallel index supporting Cosine & L2 distance."""
    
    def __init__(self, dimension: int):
        """Initialize VectorIndex."""
        self.dimension = dimension
        self.documents: Dict[str, Document] = {}
        # Precomputed matrix for fast retrieval
        self._matrix: Optional[np.ndarray] = None
        self._id_map: List[str] = []
        
    def add_document(self, doc_id: str, content: Dict[str, Any], tensor: np.ndarray) -> Result:
        """Add document to VectorIndex."""
        if not isinstance(tensor, np.ndarray):
            return Err("Tensor must be a numpy array.")
            
        tensor = tensor.flatten()
        if tensor.shape[0] != self.dimension:
            return Err(f"Tensor dimension mismatch. Expected {self.dimension}, got {tensor.shape[0]}.")
            
        # Normalize tensor for fast cosine similarity via dot product
        norm = np.linalg.norm(tensor)
        normalized_tensor = tensor if norm == 0 else tensor / norm
            
        doc = Document(id=doc_id, content=content, tensor=normalized_tensor)
        self.documents[doc_id] = doc
        
        # Invalidate cache
        self._matrix = None
        self._id_map = []
        
        return Ok(True)
        
    def _rebuild_index(self):
        if len(self.documents) == 0:
            self._matrix = np.empty((0, self.dimension))
            self._id_map = []
            return
            
        ids = list(self.documents.keys())
        matrix = np.vstack([self.documents[doc_id].tensor for doc_id in ids])
        
        self._id_map = ids
        self._matrix = matrix
        
    def search(self, query_tensor: np.ndarray, top_k: int = 5, method: str = "cosine") -> Result:
        """Execute search operation for VectorIndex."""
        if len(self.documents) == 0:
            return Ok([])
            
        if self._matrix is None:
            self._rebuild_index()
            
        if query_tensor.flatten().shape[0] != self.dimension:
            return Err(f"Query tensor dimension mismatch. Expected {self.dimension}, got {query_tensor.flatten().shape[0]}.")
            
        q = query_tensor.flatten()
        q_norm = np.linalg.norm(q)
        q_normalized = q if q_norm == 0 else q / q_norm
        
        if method == "cosine":
            # Since both the index and query are normalized, Cosine Similarity == Dot Product
            # matrix is (N, D), q is (D,). scores is (N,)
            scores = self._matrix.dot(q_normalized) # type: ignore
            # Sort descending
            best_indices = np.argsort(scores)[-top_k:][::-1]
            
        elif method == "l2":
            # L2 distance
            diff = self._matrix - q_normalized # type: ignore
            distances = np.linalg.norm(diff, axis=1)
            # We want minimum distance, so score = -distance to sort descending
            scores = -distances
            best_indices = np.argsort(scores)[-top_k:][::-1]
            # Convert negative distance back to distance for the final payload score
            scores = distances
        else:
            return Err(f"Unknown search method: {method}")
            
        results = []
        for idx in best_indices:
            doc_id = self._id_map[idx]
            doc = self.documents[doc_id]
            score = float(scores[idx])
            results.append(SearchResult(document=doc, score=score))
            
        return Ok(results)


# ---------------------------------------------------------------------------
# 3. OMNI ENGINE CLASS
# ---------------------------------------------------------------------------

class OmniMarqoEngine:
    """
    Production Engine for Multi-Modal Vector Search.
    """
    VERSION = "1.0.0"
    ENGINE_ID = "omni-marqo"

    def __init__(self):
        """Initialize OmniMarqoEngine."""
        self.indices: Dict[str, VectorIndex] = {}

    def create_index(self, index_name: str, dimension: int) -> Result:
        """Performs create index operation for OmniMarqoEngine."""
        if index_name in self.indices:
            return Err(f"Index '{index_name}' already exists.")
        
        self.indices[index_name] = VectorIndex(dimension)
        return Ok(True)

    def get_index(self, index_name: str) -> Result:
        """Performs get index operation for OmniMarqoEngine."""
        if index_name not in self.indices:
            return Err(f"Index '{index_name}' not found.")
        return Ok(self.indices[index_name])

    def diagnostics(self) -> Dict[str, Any]:
        """Performs diagnostics operation for OmniMarqoEngine."""
        index_stats = {name: len(idx.documents) for name, idx in self.indices.items()}
        return {
            "engine_id": self.ENGINE_ID,
            "version": self.VERSION,
            "indices_count": len(self.indices),
            "index_stats": index_stats,
            "status": "operational",
        }
