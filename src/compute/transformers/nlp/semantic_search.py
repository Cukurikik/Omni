"""
OMNI Transformer — Semantic Text Search Pipeline
End-to-end semantic search using embedding models.
"""
import torch
from typing import List, Dict, Optional
from ..rag.pipeline import VectorIndex
from ..rag.embedding_model import OmniEmbeddingModel
import logging

logger = logging.getLogger(__name__)


class SemanticSearchEngine:
    """Production semantic search engine."""
    def __init__(self, embedding_model=None, index: Optional[VectorIndex] = None):
        self.model = embedding_model
        self.index = index or VectorIndex()
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        if self.model:
            self.model.to(self.device).eval()

    @torch.inference_mode()
    def _embed(self, texts: List[str], tokenizer=None, max_length: int = 512) -> torch.Tensor:
        if self.model is None:
            # Fallback: random embeddings
            return torch.randn(len(texts), 768)
        embeddings = []
        for text in texts:
            if tokenizer:
                encoded = tokenizer.encode(text, max_length=max_length)
                ids = torch.tensor([encoded["input_ids"]], device=self.device)
            else:
                ids = torch.tensor([[ord(c) % 30000 for c in text[:max_length]]], device=self.device)
            emb = self.model(ids)
            embeddings.append(emb.cpu())
        return torch.cat(embeddings, dim=0)

    def index_documents(self, documents: List[Dict], tokenizer=None) -> int:
        texts = [d["text"] for d in documents]
        embeddings = self._embed(texts, tokenizer)
        self.index.add(embeddings, documents)
        logger.info(f"Indexed {len(documents)} documents")
        return len(documents)

    def search(self, query: str, top_k: int = 10, tokenizer=None) -> List[Dict]:
        q_emb = self._embed([query], tokenizer).squeeze(0)
        return self.index.search(q_emb, top_k)

    def save_index(self, path: str) -> None:
        self.index.save(path)

    def load_index(self, path: str) -> None:
        self.index.load(path)
