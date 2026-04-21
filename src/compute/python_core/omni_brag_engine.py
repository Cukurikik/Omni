"""
OMNI bRAG Engine
================
Production-grade abstraction inspired by bragai/bRAG-langchain.
Implements the Retrieval (R) part in RAG absolutely zero-mocked without 
the bloated Langchain network via deterministic BM25 Algorithm in Numpy.

OMNI Layer: compute (Python)
"""

from __future__ import annotations

import math
from collections import Counter
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Union

import numpy as np


# ---------------------------------------------------------------------------
# 1. OMNI Result Monad
# ---------------------------------------------------------------------------


ENGINE_VERSION = "1.0.0-omni"

class bRAGError(Exception):
    """Base error for RAG integration abstractions."""

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
# 2. BM25 SPARSE VECTOR RETRIEVAL MODULE
# ---------------------------------------------------------------------------

class BM25Generator:
    """Okapi BM25 formulation executing completely locally."""
    
    def __init__(self, k1: float = 1.5, b: float = 0.75):
        """Initialize BM25Generator."""
        self.k1 = k1
        self.b = b
        self.doc_counts: List[Dict[str, int]] = []
        self.doc_len: List[int] = []
        self.avgdl: float = 0.0
        self.N: int = 0
        self.df: Dict[str, int] = Counter()
        self.idf: Dict[str, float] = {}
        self.corpus: List[str] = []
        
    def _tokenize(self, text: str) -> List[str]:
        return text.lower().replace('.', ' ').replace(',', ' ').split()
        
    def add_corpus(self, docs: List[str]) -> Result:
        """Add corpus to BM25Generator."""
        try:
            self.corpus = docs
            self.N = len(docs)
            self.doc_len = []
            
            for doc in docs:
                tokens = self._tokenize(doc)
                self.doc_len.append(len(tokens))
                cnt = Counter(tokens)
                self.doc_counts.append(cnt)
                
                # Document frequency increment
                for t in cnt.keys():
                    self.df[t] += 1
                    
            if self.N > 0:
                self.avgdl = sum(self.doc_len) / self.N
                
            # Calculate IDF
            # IDF(qi) = ln( (N - n(qi) + 0.5) / (n(qi) + 0.5) + 1 )
            for term, freq in self.df.items():
                self.idf[term] = math.log(((self.N - freq + 0.5) / (freq + 0.5)) + 1.0)
                
            return Ok(True)
        except Exception as e:
            return Err(f"Lexical document corpus breakdown failed: {e}")

    def query_rank(self, query: str, top_k: int = 3) -> Result:
        """Determines best ranking matches without invoking LLM models."""
        if self.N == 0:
            return Err("Zero corpus memory registered.")
            
        try:
            q_tokens = self._tokenize(query)
            scores = np.zeros(self.N, dtype=np.float64)
            
            for i in range(self.N):
                doc_score = 0.0
                doc_dict = self.doc_counts[i]
                dl = self.doc_len[i]
                
                for t in q_tokens:
                    if t not in doc_dict:
                        continue
                    
                    term_idf = self.idf.get(t, 0.0)
                    f_d = doc_dict[t]
                    
                    # BM25 function
                    numerator = f_d * (self.k1 + 1)
                    denominator = f_d + self.k1 * (1 - self.b + self.b * (dl / self.avgdl))
                    
                    doc_score += term_idf * (numerator / denominator)
                    
                scores[i] = doc_score
                
            # Numpy argsort retrieves the indices of ascending arrays
            best_idx = np.argsort(scores)[::-1][:top_k]
            
            results = []
            for idx in best_idx:
                results.append({
                    "id": int(idx),
                    "score": float(scores[idx]),
                    "document": self.corpus[idx]
                })
                
            return Ok(results)
            
        except Exception as e:
            return Err(f"Syntagmatic logic projection defect: {e}")


# ---------------------------------------------------------------------------
# 3. OMNI ENGINE CLASS
# ---------------------------------------------------------------------------

class OmniBRAGEngine:
    """
    Production Engine for Generative Retrieval Architecture.
    """

    def __init__(self, config=None):
        """Initialize OmniBRAGEngine."""
        self.config = config or {}
        self.engine_id = __import__("uuid").uuid4().hex
        self.is_active = True
    VERSION = "1.0.0"
    ENGINE_ID = "omni-brag"

    def get_bm25_system(self) -> BM25Generator:
        """Performs get bm25 system operation for OmniBRAGEngine."""
        return BM25Generator()

    def diagnostics(self) -> Dict[str, Any]:
        """Performs diagnostics operation for OmniBRAGEngine."""
        return {
            "engine_id": self.ENGINE_ID,
            "version": self.VERSION,
            "architecture": "Deterministic BM25 Logic (Zero-Dependency RAG)",
            "status": "operational",
        }
