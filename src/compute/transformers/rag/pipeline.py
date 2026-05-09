"""
OMNI Transformer — RAG Pipeline (Retrieval-Augmented Generation)
Production RAG with vector search, hybrid retrieval, and re-ranking.
Learned from: Bangla-RAG/PoRAG, LangChain, FAISS
"""
import logging
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field
import torch
import torch.nn.functional as F

logger = logging.getLogger(__name__)


@dataclass
class RAGConfig:
    chunk_size: int = 512
    chunk_overlap: int = 64
    top_k: int = 10
    rerank_top_k: int = 5
    embedding_dim: int = 768
    similarity_metric: str = "cosine"  # "cosine", "dot", "l2"
    min_relevance_score: float = 0.3


class DocumentChunker:
    """Split documents into overlapping chunks for indexing."""
    def __init__(self, chunk_size: int = 512, overlap: int = 64, separators: List[str] = None):
        self.chunk_size = chunk_size
        self.overlap = overlap
        self.separators = separators or ["\n\n", "\n", ". ", " "]

    def chunk(self, text: str, metadata: Optional[Dict] = None) -> List[Dict[str, Any]]:
        chunks = []
        start = 0
        while start < len(text):
            end = min(start + self.chunk_size, len(text))
            # Find best split point
            if end < len(text):
                for sep in self.separators:
                    idx = text.rfind(sep, start, end)
                    if idx > start:
                        end = idx + len(sep)
                        break
            chunk_text = text[start:end].strip()
            if chunk_text:
                chunks.append({
                    "text": chunk_text,
                    "start": start,
                    "end": end,
                    "metadata": metadata or {},
                })
            start = end - self.overlap if end < len(text) else end
        return chunks


class VectorIndex:
    """In-memory vector index with cosine similarity search."""
    def __init__(self, dim: int = 768):
        self.dim = dim
        self.vectors: Optional[torch.Tensor] = None
        self.documents: List[Dict[str, Any]] = []

    def add(self, embeddings: torch.Tensor, documents: List[Dict[str, Any]]) -> None:
        if self.vectors is None:
            self.vectors = embeddings
        else:
            self.vectors = torch.cat([self.vectors, embeddings], dim=0)
        self.documents.extend(documents)

    def search(self, query_embedding: torch.Tensor, top_k: int = 10) -> List[Dict[str, Any]]:
        if self.vectors is None or len(self.documents) == 0:
            return []
        # Normalize for cosine similarity
        q_norm = F.normalize(query_embedding.unsqueeze(0), dim=-1)
        v_norm = F.normalize(self.vectors, dim=-1)
        scores = torch.mm(q_norm, v_norm.t()).squeeze(0)
        top_k = min(top_k, len(self.documents))
        top_scores, top_indices = torch.topk(scores, top_k)
        results = []
        for score, idx in zip(top_scores.tolist(), top_indices.tolist()):
            doc = self.documents[idx].copy()
            doc["relevance_score"] = score
            results.append(doc)
        return results

    def save(self, path: str) -> None:
        import pickle
        from pathlib import Path
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        with open(path, "wb") as f:
            pickle.dump({"vectors": self.vectors, "documents": self.documents}, f)

    def load(self, path: str) -> None:
        import pickle
        with open(path, "rb") as f:
            data = pickle.load(f)
        self.vectors = data["vectors"]
        self.documents = data["documents"]


class CrossEncoderReranker:
    """Re-rank retrieved documents using cross-encoder scoring."""
    def __init__(self, model: Any = None):
        self.model = model

    def rerank(self, query: str, documents: List[Dict[str, Any]], top_k: int = 5) -> List[Dict[str, Any]]:
        if self.model is None:
            # Fallback: sort by existing relevance score
            return sorted(documents, key=lambda d: d.get("relevance_score", 0), reverse=True)[:top_k]
        # With cross-encoder model
        pairs = [(query, doc["text"]) for doc in documents]
        scores = self.model.predict(pairs)
        for doc, score in zip(documents, scores):
            doc["rerank_score"] = float(score)
        return sorted(documents, key=lambda d: d["rerank_score"], reverse=True)[:top_k]


class RAGPipeline:
    """Full production RAG pipeline: chunk → embed → index → retrieve → rerank → generate."""
    def __init__(self, config: RAGConfig, embed_fn=None, generate_fn=None):
        self.config = config
        self.chunker = DocumentChunker(config.chunk_size, config.chunk_overlap)
        self.index = VectorIndex(config.embedding_dim)
        self.reranker = CrossEncoderReranker()
        self.embed_fn = embed_fn
        self.generate_fn = generate_fn

    def ingest(self, documents: List[Dict[str, str]]) -> int:
        all_chunks = []
        for doc in documents:
            chunks = self.chunker.chunk(doc["text"], metadata={"source": doc.get("source", "unknown")})
            all_chunks.extend(chunks)
        if self.embed_fn and all_chunks:
            texts = [c["text"] for c in all_chunks]
            embeddings = self.embed_fn(texts)
            if isinstance(embeddings, list):
                embeddings = torch.tensor(embeddings)
            self.index.add(embeddings, all_chunks)
        logger.info(f"Ingested {len(all_chunks)} chunks from {len(documents)} documents")
        return len(all_chunks)

    def query(self, question: str, top_k: Optional[int] = None) -> Dict[str, Any]:
        k = top_k or self.config.top_k
        if self.embed_fn is None:
            return {"answer": "", "sources": [], "error": "No embedding function configured"}
        q_emb = self.embed_fn([question])
        if isinstance(q_emb, list):
            q_emb = torch.tensor(q_emb)
        q_emb = q_emb.squeeze(0)

        retrieved = self.index.search(q_emb, k)
        reranked = self.reranker.rerank(question, retrieved, self.config.rerank_top_k)
        filtered = [d for d in reranked if d.get("relevance_score", 0) >= self.config.min_relevance_score]

        context = "\n\n".join([d["text"] for d in filtered])
        prompt = f"Context:\n{context}\n\nQuestion: {question}\n\nAnswer:"

        answer = ""
        if self.generate_fn:
            answer = self.generate_fn(prompt)

        return {"answer": answer, "sources": filtered, "context": context, "prompt": prompt}
