"""
OMNI Cognita Engine
===================
Production-grade abstraction inspired by truefoundry/cognita.
Implements a strict Numpy-based RAG Retrieval Vector Store via Term-Frequency
Inverse Document Frequency (TF-IDF) avoiding bulky Transformer embeddings.

OMNI Layer: compute (Python)
"""

from __future__ import annotations

import collections
import math
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple, Union

import numpy as np


# ---------------------------------------------------------------------------
# 1. OMNI Result Monad
# ---------------------------------------------------------------------------


ENGINE_VERSION = "1.0.0-omni"
from src.compute.python_core.omni_base_engine import Result, Ok, Err

class CognitaError(Exception):
    """Base error for Cognita RAG abstraction."""

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
# 2. RAG RETRIEVER & VECTOR STORE
# ---------------------------------------------------------------------------

class TFIDFVectorizer:
    """Computes TF-IDF metrics from scratch."""
    def __init__(self):
        """Initialize TFIDFVectorizer."""
        self.vocabulary: Dict[str, int] = {}
        self.idf: np.ndarray = np.array([])
        
    def _tokenize(self, text: str) -> List[str]:
        return text.lower().replace('.', '').replace(',', '').split()

    def fit(self, documents: List[str]) -> Result:
        """Fit TFIDFVectorizer to data."""
        try:
            doc_counts = collections.Counter()
            for doc in documents:
                words = set(self._tokenize(doc))
                for w in words:
                    doc_counts[w] += 1
            
            # Map words to indices
            self.vocabulary = {w: i for i, w in enumerate(doc_counts.keys())}
            
            N = len(documents)
            # IDF = log(N / (df + 1)) + 1
            idf_vals = []
            for w in self.vocabulary:
                idf_vals.append(math.log(N / (doc_counts[w] + 1)) + 1.0)
            
            self.idf = np.array(idf_vals)
            return Ok(True)
        except Exception as e:
            return Err(f"Text tokenization and fitting failed: {e}")

    def transform(self, documents: List[str]) -> Result:
        """Transform transform."""
        if not self.vocabulary:
            return Err("Vectorizer is entirely unfitted.")
            
        try:
            vocab_size = len(self.vocabulary)
            matrix = np.zeros((len(documents), vocab_size))
            
            for i, doc in enumerate(documents):
                tokens = self._tokenize(doc)
                counter = collections.Counter(tokens)
                doc_len = max(len(tokens), 1)
                
                for word, count in counter.items():
                    if word in self.vocabulary:
                        idx = self.vocabulary[word]
                        tf = count / doc_len
                        matrix[i, idx] = tf * self.idf[idx]
            
            return Ok(matrix)
        except Exception as e:
            return Err(f"Transformation matrix extraction failed: {e}")


class SemanticRetriever:
    """Executes Dot-Product Cosine Similarity over the TF-IDF space."""
    
    def __init__(self):
        """Initialize SemanticRetriever."""
        self.vectorizer = TFIDFVectorizer()
        self.store: np.ndarray = np.array([])
        self.documents: List[str] = []
        
    def ingest(self, corpus: List[str]) -> Result:
        """Execute ingest operation for SemanticRetriever."""
        if not corpus:
            return Err("Empty corpus cannot be registered.")
            
        self.documents = corpus
        fit_res = self.vectorizer.fit(corpus)
        if hasattr(fit_res, "error"):
            return fit_res
            
        trans_res = self.vectorizer.transform(corpus)
        if hasattr(trans_res, "error"):
            return trans_res
            
        self.store = trans_res.value
        
        # normalize store vectors
        norms = np.linalg.norm(self.store, axis=1, keepdims=True)
        norms[norms == 0] = 1e-10
        self.store = self.store / norms
        
        return Ok(True)

    def search(self, query: str, top_k: int = 3) -> Result:
        """Execute search operation for SemanticRetriever."""
        if self.store.size == 0:
            return Err("Store is completely isolated from context. Please ingest first.")
            
        try:
            q_res = self.vectorizer.transform([query])
            if hasattr(q_res, "error"):
                return q_res
                
            q_vec = q_res.value[0]
            q_norm = np.linalg.norm(q_vec)
            if q_norm == 0:
                q_norm = 1e-10
            q_vec = q_vec / q_norm
            
            # Cosine similarity
            similarities = np.dot(self.store, q_vec)
            
            best_indices = np.argsort(similarities)[::-1][:top_k]
            
            results = [
                {"document": self.documents[idx], "score": float(similarities[idx])}
                for idx in best_indices
            ]
            return Ok(results)
            
        except Exception as e:
            return Err(f"Search retrieval process crashed: {e}")


# ---------------------------------------------------------------------------
# 3. OMNI ENGINE CLASS
# ---------------------------------------------------------------------------

class OmniCognitaEngine:
    """
    Production Engine for RAG Semantic TF-IDF Resolution.
    """

    def __init__(self, config=None):
        """Initialize OmniCognitaEngine."""
        self.config = config or {}
        self.engine_id = __import__("uuid").uuid4().hex
        self.is_active = True
    VERSION = "1.0.0"
    ENGINE_ID = "omni-cognita"

    def get_retriever(self) -> SemanticRetriever:
        """Performs get retriever operation for OmniCognitaEngine."""
        return SemanticRetriever()

    def diagnostics(self) -> Dict[str, Any]:
        """Performs diagnostics operation for OmniCognitaEngine."""
        return {
            "engine_id": self.ENGINE_ID,
            "version": self.VERSION,
            "architecture": "Statistical TF-IDF Cosine Embedding Map",
            "status": "operational",
        }
