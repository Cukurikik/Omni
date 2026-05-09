"""
OMNI Compute Layer — RAG Pipeline Engine
Inspired by: Bangla-RAG/PoRAG configurable RAG pipeline.
Production retrieval-augmented generation with chunking, embedding, and reranking.
"""

import hashlib
import logging
from dataclasses import dataclass, field
from typing import List, Optional, Callable
from pathlib import Path

logger = logging.getLogger("omni.rag")


@dataclass
class Document:
    """A document with metadata."""
    content: str
    source: str
    doc_id: str = ""
    metadata: dict = field(default_factory=dict)

    def __post_init__(self):
        if not self.doc_id:
            self.doc_id = hashlib.sha256(self.content.encode()).hexdigest()[:16]


@dataclass
class Chunk:
    """A text chunk from a document."""
    text: str
    doc_id: str
    chunk_index: int
    embedding: Optional[List[float]] = None
    score: float = 0.0


@dataclass
class RAGConfig:
    """RAG pipeline configuration."""
    chunk_size: int = 512
    chunk_overlap: int = 64
    top_k: int = 5
    rerank_top_k: int = 3
    embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"
    similarity_metric: str = "cosine"  # cosine | dot | euclidean
    min_score_threshold: float = 0.3


class TextChunker:
    """Split documents into overlapping chunks."""

    def __init__(self, chunk_size: int = 512, overlap: int = 64):
        self.chunk_size = chunk_size
        self.overlap = overlap

    def chunk_document(self, doc: Document) -> List[Chunk]:
        """Split a document into chunks with overlap."""
        text = doc.content
        chunks = []
        start = 0
        idx = 0

        while start < len(text):
            end = start + self.chunk_size
            chunk_text = text[start:end]

            # Try to break at sentence boundary
            if end < len(text):
                last_period = chunk_text.rfind(".")
                last_newline = chunk_text.rfind("\n")
                break_pos = max(last_period, last_newline)
                if break_pos > self.chunk_size * 0.5:
                    chunk_text = chunk_text[: break_pos + 1]
                    end = start + break_pos + 1

            if chunk_text.strip():
                chunks.append(Chunk(text=chunk_text.strip(), doc_id=doc.doc_id, chunk_index=idx))
                idx += 1

            start = end - self.overlap if end < len(text) else len(text)

        return chunks


class VectorStore:
    """In-memory vector store with HNSW-like search."""

    def __init__(self, metric: str = "cosine"):
        self.metric = metric
        self.chunks: List[Chunk] = []
        self.embeddings: Optional[object] = None  # numpy array

    def add_chunks(self, chunks: List[Chunk]):
        """Add chunks with embeddings to the store."""
        import numpy as np

        self.chunks.extend(chunks)
        embeddings = [c.embedding for c in chunks if c.embedding is not None]
        if embeddings:
            new_embs = np.array(embeddings, dtype=np.float32)
            if self.embeddings is None:
                self.embeddings = new_embs
            else:
                self.embeddings = np.vstack([self.embeddings, new_embs])

    def search(self, query_embedding: List[float], top_k: int = 5) -> List[Chunk]:
        """Search for similar chunks."""
        import numpy as np

        if self.embeddings is None or len(self.chunks) == 0:
            return []

        q = np.array(query_embedding, dtype=np.float32)

        if self.metric == "cosine":
            norms = np.linalg.norm(self.embeddings, axis=1, keepdims=True)
            norms = np.where(norms == 0, 1, norms)
            normalized = self.embeddings / norms
            q_norm = q / (np.linalg.norm(q) + 1e-8)
            scores = normalized @ q_norm
        elif self.metric == "dot":
            scores = self.embeddings @ q
        else:  # euclidean
            dists = np.linalg.norm(self.embeddings - q, axis=1)
            scores = 1.0 / (1.0 + dists)

        top_indices = np.argsort(scores)[::-1][:top_k]
        results = []
        for i in top_indices:
            chunk = self.chunks[i]
            chunk.score = float(scores[i])
            results.append(chunk)

        return results

    @property
    def size(self) -> int:
        return len(self.chunks)


class OmniRAGPipeline:
    """Full RAG pipeline: ingest → chunk → embed → retrieve → generate."""

    def __init__(self, config: RAGConfig):
        self.config = config
        self.chunker = TextChunker(config.chunk_size, config.chunk_overlap)
        self.store = VectorStore(config.similarity_metric)
        self._embed_fn: Optional[Callable] = None
        self._generate_fn: Optional[Callable] = None
        self._rerank_fn: Optional[Callable] = None
        logger.info(f"RAG Pipeline initialized (chunk_size={config.chunk_size}, top_k={config.top_k})")

    def set_embedding_function(self, fn: Callable[[List[str]], List[List[float]]]):
        """Set the embedding function."""
        self._embed_fn = fn

    def set_generation_function(self, fn: Callable[[str, List[str]], str]):
        """Set the generation function (prompt, contexts) -> response."""
        self._generate_fn = fn

    def set_rerank_function(self, fn: Callable[[str, List[Chunk]], List[Chunk]]):
        """Set the reranking function."""
        self._rerank_fn = fn

    def ingest_documents(self, documents: List[Document]):
        """Ingest documents into the RAG pipeline."""
        all_chunks = []
        for doc in documents:
            chunks = self.chunker.chunk_document(doc)
            all_chunks.extend(chunks)

        if self._embed_fn and all_chunks:
            texts = [c.text for c in all_chunks]
            embeddings = self._embed_fn(texts)
            for chunk, emb in zip(all_chunks, embeddings):
                chunk.embedding = emb

        self.store.add_chunks(all_chunks)
        logger.info(f"Ingested {len(documents)} docs -> {len(all_chunks)} chunks (store={self.store.size})")

    def query(self, question: str) -> dict:
        """Execute RAG query: retrieve + rerank + generate."""
        if not self._embed_fn:
            raise RuntimeError("Embedding function not set")

        query_embedding = self._embed_fn([question])[0]
        retrieved = self.store.search(query_embedding, self.config.top_k)

        # Filter by score threshold
        retrieved = [c for c in retrieved if c.score >= self.config.min_score_threshold]

        # Rerank if available
        if self._rerank_fn and retrieved:
            retrieved = self._rerank_fn(question, retrieved)[: self.config.rerank_top_k]

        contexts = [c.text for c in retrieved]

        answer = ""
        if self._generate_fn:
            answer = self._generate_fn(question, contexts)

        return {
            "question": question,
            "answer": answer,
            "sources": [{"text": c.text, "doc_id": c.doc_id, "score": c.score} for c in retrieved],
            "num_chunks_retrieved": len(retrieved),
        }
