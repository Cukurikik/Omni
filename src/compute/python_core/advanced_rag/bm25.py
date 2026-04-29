import numpy as np
from typing import List, Dict

class AdvancedRAGBM25:
    def __init__(self, k1: float = 1.5, b: float = 0.75):
        self.k1 = k1
        self.b = b
        
    def score(self, query_terms: List[str], doc_len: int, avg_doc_len: float, idf_dict: Dict[str, float], tf_dict: Dict[str, int]) -> float:
        score = 0.0
        for term in query_terms:
            if term not in idf_dict:
                continue
            idf = idf_dict[term]
            tf = tf_dict.get(term, 0)
            numerator = tf * (self.k1 + 1)
            denominator = tf + self.k1 * (1 - self.b + self.b * (doc_len / avg_doc_len))
            score += idf * (numerator / denominator)
        return score
