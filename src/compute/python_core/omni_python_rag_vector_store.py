# OMNI MOTHER — SEMESTER 14 BATCH 36
# Python — Computational & Data Layer (OMNI Zero-Mock Implementation)
# Implements production-grade embedding vector index with cosine similarity search.
# Absorbs patterns from: github.com/infiniflow/ragflow, langchain vectorstores

"""
OMNI Embedding Vector Store Engine

Production-grade vector similarity search using exact brute-force cosine similarity.
Implements the core retrieval component of RAG (Retrieval-Augmented Generation).

Features:
- Cosine similarity with L2-normalized vectors
- Top-K nearest neighbor search
- Metadata filtering
- Monadic Result[T, E] pattern
"""

from __future__ import annotations
import math
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional


@dataclass
class VectorResult:
    """Monadic result container for vector operations."""
    value: Any = None
    is_ok: bool = True
    error: str = ""

    @staticmethod
    def ok(value: Any) -> VectorResult:
        return VectorResult(value=value, is_ok=True, error="")

    @staticmethod
    def err(error: str) -> VectorResult:
        return VectorResult(value=None, is_ok=False, error=error)


@dataclass
class VectorDocument:
    """A document with its embedding vector and metadata."""
    doc_id: str
    content: str
    embedding: List[float]
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class SearchHit:
    """A search result with computed similarity score."""
    doc_id: str
    content: str
    score: float
    metadata: Dict[str, Any]


def _l2_norm(vec: List[float]) -> float:
    """Computes L2 (Euclidean) norm of a vector."""
    return math.sqrt(sum(x * x for x in vec))


def _cosine_similarity(a: List[float], b: List[float]) -> float:
    """
    Computes cosine similarity between two vectors.

    cos(a, b) = dot(a, b) / (||a|| * ||b||)

    Args:
        a: First vector
        b: Second vector (must be same dimension as a)

    Returns:
        Similarity score in [-1.0, 1.0]

    Raises:
        ValueError: If vectors have different dimensions or zero norm
    """
    if len(a) != len(b):
        raise ValueError(f"Dimension mismatch: {len(a)} vs {len(b)}")

    dot_product = sum(ai * bi for ai, bi in zip(a, b))
    norm_a = _l2_norm(a)
    norm_b = _l2_norm(b)

    if norm_a == 0.0 or norm_b == 0.0:
        raise ValueError("Cannot compute cosine similarity with zero-norm vector")

    return dot_product / (norm_a * norm_b)


class OmniVectorStoreEngine:
    """
    Production-grade in-memory vector store for RAG retrieval.

    Supports:
    - Document ingestion with embedding vectors
    - Top-K cosine similarity search
    - Metadata-based filtering
    - Diagnostics and health monitoring

    Example:
        >>> store = OmniVectorStoreEngine(dimension=384)
        >>> store.ingest([VectorDocument("d1", "hello world", [0.1]*384)])
        >>> results = store.search([0.1]*384, top_k=5)
    """

    def __init__(self, dimension: int) -> None:
        """
        Initialize vector store with fixed embedding dimension.

        Args:
            dimension: Embedding vector dimension (e.g., 384 for MiniLM, 1536 for OpenAI)
        """
        if dimension <= 0:
            raise ValueError("Vector dimension must be > 0")
        self._dimension = dimension
        self._documents: Dict[str, VectorDocument] = {}

    def ingest(self, documents: List[VectorDocument]) -> VectorResult:
        """
        Ingest documents into the vector store.

        Args:
            documents: List of VectorDocument with embeddings

        Returns:
            VectorResult with count of ingested documents
        """
        if not documents:
            return VectorResult.err("Cannot ingest empty document list")

        ingested = 0
        for doc in documents:
            if len(doc.embedding) != self._dimension:
                return VectorResult.err(
                    f"Document '{doc.doc_id}' embedding dim {len(doc.embedding)} != store dim {self._dimension}"
                )
            if not doc.doc_id:
                return VectorResult.err("Document ID must be non-empty")
            if not doc.content:
                return VectorResult.err("Document content must be non-empty")

            self._documents[doc.doc_id] = doc
            ingested += 1

        return VectorResult.ok({"ingested": ingested, "total": len(self._documents)})

    def search(
        self,
        query_embedding: List[float],
        top_k: int = 10,
        metadata_filter: Optional[Dict[str, Any]] = None,
        score_threshold: float = 0.0,
    ) -> VectorResult:
        """
        Search for documents most similar to the query embedding.

        Args:
            query_embedding: Query vector (same dimension as stored documents)
            top_k: Maximum number of results to return
            metadata_filter: Optional key-value pairs that documents must match
            score_threshold: Minimum similarity score to include in results

        Returns:
            VectorResult with list of SearchHit sorted by score descending
        """
        if len(query_embedding) != self._dimension:
            return VectorResult.err(
                f"Query dim {len(query_embedding)} != store dim {self._dimension}"
            )
        if top_k <= 0:
            return VectorResult.err("top_k must be > 0")
        if not self._documents:
            return VectorResult.err("Vector store is empty — no documents to search")

        hits: List[SearchHit] = []

        for doc in self._documents.values():
            # Apply metadata filter
            if metadata_filter:
                skip = False
                for key, val in metadata_filter.items():
                    if doc.metadata.get(key) != val:
                        skip = True
                        break
                if skip:
                    continue

            try:
                score = _cosine_similarity(query_embedding, doc.embedding)
            except ValueError as e:
                return VectorResult.err(f"Similarity computation failed: {e}")

            if score >= score_threshold:
                hits.append(SearchHit(
                    doc_id=doc.doc_id,
                    content=doc.content,
                    score=score,
                    metadata=doc.metadata,
                ))

        # Sort by score descending (exact, deterministic sort)
        hits.sort(key=lambda h: h.score, reverse=True)

        return VectorResult.ok(hits[:top_k])

    def delete(self, doc_id: str) -> VectorResult:
        """Remove a document from the store by ID."""
        if doc_id not in self._documents:
            return VectorResult.err(f"Document '{doc_id}' not found")
        del self._documents[doc_id]
        return VectorResult.ok({"deleted": doc_id, "remaining": len(self._documents)})

    def diagnostics(self) -> Dict[str, Any]:
        """Returns engine diagnostics and health status."""
        return {
            "engine": "OmniVectorStoreEngine",
            "layer": "compute/python",
            "dimension": self._dimension,
            "document_count": len(self._documents),
            "status": "operational",
            "learned_from": "infiniflow/ragflow, langchain vectorstores",
        }
