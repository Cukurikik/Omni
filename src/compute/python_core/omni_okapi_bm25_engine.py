"""OmniOkapiBm25Engine for text retrieval scoring."""
import math
from typing import Dict, Any, List
from src.compute.python_core.omni_base_engine import OmniBaseEngine, Result

class OmniOkapiBm25Engine(OmniBaseEngine):
    """Production-grade Omni Okapi Bm25 Engine for the OMNI Framework.

        Provides deterministic, zero-mock computational methods
        with monadic Result[T, E] error handling.
        """
    def __init__(self, k1: float = 1.5, b: float = 0.75):
        self.k1 = k1
        self.b = b
        self.doc_lengths = []
        self.avgdl = 0.0
        self.doc_freqs = []
        self.idf = {}
        self.N = 0

    def fit(self, corpus: List[str]) -> Result[Dict[str, Any], str]:
        """Fits the BM25 model on a corpus of strings."""
        try:
            self.N = len(corpus)
            self.doc_lengths = []
            self.doc_freqs = []
            
            df: Dict[str, int] = {}
            total_len = 0
            
            for doc in corpus:
                tokens = doc.lower().split()
                self.doc_lengths.append(len(tokens))
                total_len += len(tokens)
                
                term_counts = {}
                for token in tokens:
                    term_counts[token] = term_counts.get(token, 0) + 1
                self.doc_freqs.append(term_counts)
                
                for term in term_counts.keys():
                    df[term] = df.get(term, 0) + 1
                    
            if self.N > 0:
                self.avgdl = total_len / self.N
            else:
                self.avgdl = 0.0
                
            self.idf = {}
            for term, freq in df.items():
                self.idf[term] = math.log(1.0 + (self.N - freq + 0.5) / (freq + 0.5))
                
            return Result.ok({"docs": self.N, "avgdl": self.avgdl, "vocab_size": len(self.idf)})
        except Exception as e:
            return Result.fail(str(e))

    def score(self, query: str) -> Result[Dict[str, Any], str]:
        """Calculates BM25 scores for all documents given a query."""
        try:
            if self.N == 0:
                return Result.fail("Model not fitted")
                
            query_tokens = query.lower().split()
            scores = [0.0] * self.N
            
            for q in query_tokens:
                if q not in self.idf:
                    continue
                idf_val = self.idf[q]
                for idx in range(self.N):
                    tf = self.doc_freqs[idx].get(q, 0)
                    if tf > 0:
                        dl = self.doc_lengths[idx]
                        num = tf * (self.k1 + 1)
                        den = tf + self.k1 * (1 - self.b + self.b * (dl / self.avgdl))
                        scores[idx] += idf_val * (num / den)
                        
            return Result.ok({"scores": scores})
        except Exception as e:
            return Result.fail(str(e))

    def diagnostics(self) -> Dict[str, Any]:
        return {
            "engine": "OmniOkapiBm25Engine",
            "status": "operational",
            "k1": self.k1,
            "b": self.b
        }
