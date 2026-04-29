# OMNI MOTHER - DIVINE MEMORY INTEGRATION
# Gensim Topic Modeler (OMNI Zero-Mock Implementation)
# Implements Term Frequency - Inverse Document Frequency (TF-IDF) extraction vectorizer.

from dataclasses import dataclass
from typing import List, Dict, Tuple, Optional
import math

@dataclass
class Result:
    value: Optional[List[List[Tuple[int, float]]]] # Document ID -> List of (WordID, tfidf)
    error: Optional[str]
    is_ok: bool

    @staticmethod
    def ok(val: List[List[Tuple[int, float]]]) -> 'Result':
        return Result(value=val, error=None, is_ok=True)

    @staticmethod
    def err(err: str) -> 'Result':
        return Result(value=None, error=err, is_ok=False)

class GensimTfIdfCore:
    def build_matrix(self, tokenized_docs: List[List[int]], vocab_size: int) -> Result:
        if not tokenized_docs:
            return Result.err("Corpus is empty.")
        if vocab_size <= 0:
            return Result.err("Vocabulary size must be positive.")

        doc_count = len(tokenized_docs)
        doc_frequencies = [0] * vocab_size
        
        # Calculate Term Frequencies (TF) per document
        # And Document Frequencies (DF)
        tf_matrices = []
        for doc in tokenized_docs:
            tf = {}
            for token_id in doc:
                if token_id >= vocab_size:
                    return Result.err(f"Token ID {token_id} exceeds vocabulary limit.")
                tf[token_id] = tf.get(token_id, 0) + 1
                
            tf_matrices.append(tf)
            
            for token_id in tf.keys():
                doc_frequencies[token_id] += 1

        # Calculate TF-IDF vectors iteratively
        tfidf_vectors = []
        for tf in tf_matrices:
            vector = []
            doc_len = sum(tf.values())
            for token_id, count in tf.items():
                term_freq = count / doc_len
                # IDF calculation: log( N / df_t )
                idf = math.log10(doc_count / (1.0 + doc_frequencies[token_id]))
                vector.append((token_id, term_freq * idf))
                
            # L2 Normalization (Gensim standard)
            norm = math.sqrt(sum(val * val for _, val in vector))
            if norm > 0:
                vector = [(tid, val / norm) for tid, val in vector]
                
            tfidf_vectors.append(vector)

        return Result.ok(tfidf_vectors)
