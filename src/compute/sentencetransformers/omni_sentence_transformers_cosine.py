# OMNI MOTHER - DIVINE MEMORY INTEGRATION
# Sentence Transformers (OMNI Zero-Mock Implementation)
# Implements dot-product cosine similarity evaluation strictly mathematically.

from dataclasses import dataclass
from typing import List, Optional
import math

@dataclass
class Result:
    value: Optional[float]
    error: Optional[str]
    is_ok: bool

    @staticmethod
    def ok(val: float) -> 'Result':
        return Result(value=val, error=None, is_ok=True)

    @staticmethod
    def err(err: str) -> 'Result':
        return Result(value=None, error=err, is_ok=False)

class SentenceTransformerMetrics:
    def calculate_cosine_similarity(self, vector_a: List[float], vector_b: List[float]) -> Result:
        """
        Computes cosine similarity mathematically robust to zero-vectors.
        """
        if not vector_a or not vector_b:
             return Result.err("Input sentence vectors cannot be empty.")
             
        if len(vector_a) != len(vector_b):
             return Result.err("Sentence dimension mismatch.")
             
        dot_product = 0.0
        norm_a = 0.0
        norm_b = 0.0
        
        for a, b in zip(vector_a, vector_b):
             dot_product += a * b
             norm_a += a * a
             norm_b += b * b
             
        if norm_a == 0.0 or norm_b == 0.0:
             return Result.err("Cannot calculate cosine similarity for zero-magnitude vector.")
             
        magnitude = math.sqrt(norm_a) * math.sqrt(norm_b)
        cosine_sim = dot_product / magnitude
        
        # Clamp to bounds to fix mathematical IEEE floating point precision drift
        cosine_sim = max(-1.0, min(1.0, cosine_sim))
        
        return Result.ok(cosine_sim)
