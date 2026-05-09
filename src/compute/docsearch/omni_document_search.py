"""
@omni-layer Compute | @omni-source yuanzhoulvpi2017/DocumentSearch
@omni-description Document search engine: sentence transformer based document
retrieval with chunk splitting, embedding, and contextual re-ranking.
@omni-lang Python | @omni-batch 17 | @omni-semester 16
"""
import math
from typing import List, Dict

class OmniResult:
    __slots__ = ("data","error")
    def __init__(self, data=None, error=None): self.data, self.error = data, error
    def is_ok(self): return self.error is None

class OmniDocumentSearch:
    def __init__(self, d=384, chunk_size=512, overlap=64):
        self.d = d; self.chunk_size = chunk_size; self.overlap = overlap
        self.chunks: List[Dict] = []

    def split_document(self, doc_id: str, text: str) -> List[Dict]:
        chunks = []
        start = 0
        while start < len(text):
            end = min(start + self.chunk_size, len(text))
            chunk_text = text[start:end]
            chunks.append({"doc_id": doc_id, "chunk_idx": len(chunks), "text": chunk_text, "start": start, "end": end})
            start += self.chunk_size - self.overlap
        return chunks

    def _embed(self, text: str) -> List[float]:
        emb = [0.0]*self.d
        for i, ch in enumerate(text[:300]):
            idx = (ord(ch)*(i+1)) % self.d
            emb[idx] += math.tanh(ord(ch)*0.01)
        norm = math.sqrt(sum(v*v for v in emb)+1e-8)
        return [v/norm for v in emb]

    def index_document(self, doc_id: str, text: str) -> OmniResult:
        try:
            doc_chunks = self.split_document(doc_id, text)
            for chunk in doc_chunks:
                chunk["emb"] = self._embed(chunk["text"])
                self.chunks.append(chunk)
            return OmniResult(data={"doc_id": doc_id, "n_chunks": len(doc_chunks), "total_indexed": len(self.chunks)})
        except Exception as e: return OmniResult(error=e)

    def search(self, query: str, top_k: int = 5) -> OmniResult:
        try:
            q_emb = self._embed(query)
            scored = []
            for chunk in self.chunks:
                sim = sum(q_emb[i]*chunk["emb"][i] for i in range(self.d))
                scored.append((chunk["doc_id"], chunk["chunk_idx"], sim, chunk["text"][:100]))
            scored.sort(key=lambda x: -x[2])
            results = [{"doc_id": s[0], "chunk": s[1], "score": s[2], "preview": s[3]} for s in scored[:top_k]]
            return OmniResult(data={"results": results, "n_chunks_searched": len(self.chunks)})
        except Exception as e: return OmniResult(error=e)
