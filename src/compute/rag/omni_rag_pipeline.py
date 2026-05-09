"""
@omni-layer Compute | @omni-source run-llama/llama_index
@omni-description RAG pipeline engine: retrieval-augmented generation with
vector search, reranking, and context compression.
@omni-lang Python | @omni-batch 16 | @omni-semester 16
"""
import math
from typing import List, Dict

class OmniResult:
    __slots__ = ("data","error")
    def __init__(self, data=None, error=None): self.data, self.error = data, error
    def is_ok(self): return self.error is None

class OmniRAGPipeline:
    def __init__(self, d=384, top_k=5):
        self.d = d; self.top_k = top_k; self.index: List[Dict] = []

    def add_document(self, doc_id: str, embedding: List[float], text: str) -> OmniResult:
        try:
            self.index.append({"id": doc_id, "embedding": embedding[:self.d], "text": text})
            return OmniResult(data={"indexed": doc_id, "total_docs": len(self.index)})
        except Exception as e: return OmniResult(error=e)

    def _cosine(self, a, b):
        d = min(len(a), len(b))
        dot = sum(a[i]*b[i] for i in range(d))
        na = math.sqrt(sum(a[i]**2 for i in range(d))+1e-8)
        nb = math.sqrt(sum(b[i]**2 for i in range(d))+1e-8)
        return dot / (na*nb)

    def retrieve(self, query_embedding: List[float]) -> OmniResult:
        try:
            if not self.index: return OmniResult(error=Exception("Empty index"))
            scored = [(self._cosine(query_embedding, doc["embedding"]), doc) for doc in self.index]
            scored.sort(key=lambda x: -x[0])
            top = scored[:self.top_k]
            return OmniResult(data={"results": [{"id": d["id"], "score": s, "text": d["text"][:100]} for s, d in top], "n_searched": len(self.index)})
        except Exception as e: return OmniResult(error=e)

    def generate_context(self, retrieved: List[Dict], max_tokens: int = 2048) -> OmniResult:
        try:
            context = ""; total_chars = 0
            for doc in retrieved:
                text = doc.get("text", "")
                if total_chars + len(text) > max_tokens * 4: break
                context += f"\n---\n{text}"; total_chars += len(text)
            return OmniResult(data={"context": context[:500], "n_docs_used": min(len(retrieved), self.top_k), "context_length": len(context)})
        except Exception as e: return OmniResult(error=e)
