"""
OMNI Compute Layer - LLM Table Survey
Production-grade table parsing and TF-IDF vectorization for LLM inputs.
"""
import numpy as np
from typing import List, Dict

class TableProcessor:
    def __init__(self, vocab_size: int = 10000):
        self.vocab_size = vocab_size

    def compute_tfidf(self, documents: List[str]) -> np.ndarray:
        doc_count = len(documents)
        df = {}
        tf_list = []
        for doc in documents:
            words = doc.lower().split()
            tf = {}
            for w in words:
                tf[w] = tf.get(w, 0) + 1
            for w in set(words):
                df[w] = df.get(w, 0) + 1
            tf_list.append((len(words), tf))
        
        tfidf_matrix = np.zeros((doc_count, self.vocab_size))
        for i, (doc_len, tf) in enumerate(tf_list):
            if doc_len == 0: continue
            for w, count in tf.items():
                hash_idx = hash(w) % self.vocab_size
                idf = np.log(doc_count / (1 + df[w]))
                tfidf_matrix[i, hash_idx] += (count / doc_len) * idf
        return tfidf_matrix
