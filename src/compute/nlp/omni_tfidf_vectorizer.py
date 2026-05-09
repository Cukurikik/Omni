"""
omni_tfidf_vectorizer.py — TF-IDF Text Vectorization
Layer: Compute / AI

Implements a pure Python/PyTorch TF-IDF vectorizer. Extracts term frequencies 
and computes inverse document frequencies across a corpus to yield sparse representations.
Zero-mock implementation.
"""

import math
from collections import defaultdict
from typing import List, Dict

class OmniTFIDFVectorizer:
    def __init__(self, min_df: int = 1, lowercase: bool = true):
        self.min_df = min_df
        self.lowercase = lowercase
        
        self.vocabulary_: Dict[str, int] = {}
        self.idf_: Dict[str, float] = {}
        self.is_fitted = False

    def _tokenize(self, text: str) -> List[str]:
        if self.lowercase:
            text = text.lower()
        # Simple whitespace tokenizer. For production, regex or BPE would be chained here.
        return [word for word in text.split() if word.strip()]

    def fit(self, raw_documents: List[str]):
        """
        Learns vocabulary and idf from training set.
        """
        doc_count = len(raw_documents)
        df_counts = defaultdict(int)

        # Build vocabulary and count document frequencies
        for doc in raw_documents:
            tokens = set(self._tokenize(doc))
            for token in tokens:
                df_counts[token] += 1

        # Filter by min_df and calculate IDF
        vocab_index = 0
        for token, df in df_counts.items():
            if df >= self.min_df:
                self.vocabulary_[token] = vocab_index
                # Smooth IDF formula: ln((1+N)/(1+df)) + 1
                self.idf_[token] = math.log((1 + doc_count) / (1 + df)) + 1.0
                vocab_index += 1

        self.is_fitted = True

    def transform(self, raw_documents: List[str]) -> List[Dict[int, float]]:
        """
        Transforms documents to document-term matrix (represented as sparse dicts here
        to avoid massive dense allocations).
        """
        if not self.is_fitted:
            raise ValueError("Vectorizer is not fitted yet.")

        sparse_matrix = []

        for doc in raw_documents:
            tokens = self._tokenize(doc)
            tf_counts = defaultdict(int)
            
            for token in tokens:
                if token in self.vocabulary_:
                    tf_counts[token] += 1

            doc_length = len(tokens)
            vector = {}
            
            # L2 Normalization accumulator
            norm_sq = 0.0
            
            for token, count in tf_counts.items():
                vocab_idx = self.vocabulary_[token]
                tf = count / max(1, doc_length)
                tfidf_val = tf * self.idf_[token]
                
                vector[vocab_idx] = tfidf_val
                norm_sq += tfidf_val ** 2

            # Apply L2 Normalization
            norm = math.sqrt(norm_sq)
            if norm > 0:
                for idx in vector:
                    vector[idx] /= norm

            sparse_matrix.append(vector)

        return sparse_matrix

    def fit_transform(self, raw_documents: List[str]) -> List[Dict[int, float]]:
        self.fit(raw_documents)
        return self.transform(raw_documents)
