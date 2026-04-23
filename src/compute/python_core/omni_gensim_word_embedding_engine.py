"""OmniGensimWordEmbeddingEngine — Production-grade word embedding engine.

Computes word vector operations: cosine similarity, analogy resolution,
TF-IDF weighting, and vocabulary statistics. Operates on pre-computed
embedding dictionaries (word → vector) without external NLP libraries.
"""
import math
from typing import Any, Dict, List, Optional, Tuple
from src.compute.python_core.omni_base_engine import Result, Ok, Err


class OmniGensimWordEmbeddingEngine:
    """Production engine for word embedding operations and vector similarity."""

    ENGINE_VERSION = "1.0.0"

    def __init__(self, embedding_dim: int = 128, max_vocab_size: int = 500000):
        """
        Initialize word embedding engine.

        Args:
            embedding_dim: Expected dimensionality of embedding vectors.
            max_vocab_size: Maximum vocabulary size.
        """
        if embedding_dim <= 0:
            raise ValueError("embedding_dim must be positive.")
        self.embedding_dim = embedding_dim
        self.max_vocab_size = max_vocab_size

    @staticmethod
    def _dot(a: List[float], b: List[float]) -> float:
        """Compute dot product of two vectors."""
        return sum(x * y for x, y in zip(a, b))

    @staticmethod
    def _norm(v: List[float]) -> float:
        """Compute L2 norm of a vector."""
        return math.sqrt(sum(x * x for x in v))

    @staticmethod
    def _vec_add(a: List[float], b: List[float]) -> List[float]:
        """Element-wise vector addition."""
        return [x + y for x, y in zip(a, b)]

    @staticmethod
    def _vec_sub(a: List[float], b: List[float]) -> List[float]:
        """Element-wise vector subtraction."""
        return [x - y for x, y in zip(a, b)]

    def cosine_similarity(self, vec_a: List[float], vec_b: List[float]) -> Result:
        """
        Compute cosine similarity between two word vectors.

        cos(θ) = (A · B) / (‖A‖ × ‖B‖)

        Args:
            vec_a: First word vector.
            vec_b: Second word vector.

        Returns:
            Result with similarity score in [-1, 1].
        """
        try:
            if len(vec_a) != len(vec_b):
                return Err(ValueError(f"Vector dimensions must match: {len(vec_a)} != {len(vec_b)}"))
            if not vec_a:
                return Err(ValueError("Vectors must be non-empty."))

            dot = self._dot(vec_a, vec_b)
            norm_a = self._norm(vec_a)
            norm_b = self._norm(vec_b)

            if norm_a < 1e-15 or norm_b < 1e-15:
                return Err(ValueError("Cannot compute similarity for zero-magnitude vectors."))

            similarity = dot / (norm_a * norm_b)
            # Clamp to [-1, 1] due to floating-point precision
            similarity = max(-1.0, min(1.0, similarity))

            return Ok({
                "cosine_similarity": round(similarity, 10),
                "dot_product": round(dot, 10),
                "norm_a": round(norm_a, 10),
                "norm_b": round(norm_b, 10),
                "dimensions": len(vec_a),
            })

        except Exception as e:
            return Err(e)

    def find_most_similar(
        self, target_vector: List[float], vocabulary: Dict[str, List[float]], top_k: int = 5
    ) -> Result:
        """
        Find the top-K most similar words to a target vector.

        Args:
            target_vector: Query vector to find neighbors for.
            vocabulary: Dict mapping word strings to their embedding vectors.
            top_k: Number of nearest neighbors to return.

        Returns:
            Result with ranked list of (word, similarity) pairs.
        """
        try:
            if not vocabulary:
                return Err(ValueError("Vocabulary must be non-empty."))
            if not target_vector:
                return Err(ValueError("Target vector must be non-empty."))
            if top_k < 1:
                return Err(ValueError("top_k must be at least 1."))

            norm_target = self._norm(target_vector)
            if norm_target < 1e-15:
                return Err(ValueError("Target vector has zero magnitude."))

            similarities = []
            for word, vec in vocabulary.items():
                if len(vec) != len(target_vector):
                    continue
                norm_v = self._norm(vec)
                if norm_v < 1e-15:
                    continue
                sim = self._dot(target_vector, vec) / (norm_target * norm_v)
                similarities.append((word, round(sim, 10)))

            similarities.sort(key=lambda x: -x[1])
            top_results = similarities[:top_k]

            return Ok({
                "most_similar": [{"word": w, "similarity": s} for w, s in top_results],
                "vocab_size": len(vocabulary),
                "top_k": top_k,
                "query_dimensions": len(target_vector),
            })

        except Exception as e:
            return Err(e)

    def compute_word_analogy(
        self,
        word_a: List[float],
        word_b: List[float],
        word_c: List[float],
        vocabulary: Dict[str, List[float]],
    ) -> Result:
        """
        Solve word analogy: A is to B as C is to ? → D = B - A + C.

        The classic Word2Vec analogy operation. Finds the word whose vector
        is closest to (B - A + C).

        Args:
            word_a: Vector of word A.
            word_b: Vector of word B.
            word_c: Vector of word C.
            vocabulary: Full vocabulary dict.

        Returns:
            Result with the analogy result word.
        """
        try:
            if not (word_a and word_b and word_c):
                return Err(ValueError("All input word vectors must be non-empty."))

            # D = B - A + C
            target = self._vec_add(self._vec_sub(word_b, word_a), word_c)
            result = self.find_most_similar(target, vocabulary, top_k=1)

            if not result.is_ok():
                return result

            return Ok({
                "analogy_vector": [round(v, 8) for v in target],
                "best_match": result.value["most_similar"][0] if result.value["most_similar"] else None,
                "operation": "B - A + C",
            })

        except Exception as e:
            return Err(e)

    def compute_tfidf_weights(self, documents: List[List[str]]) -> Result:
        """
        Compute TF-IDF weights for a corpus of tokenized documents.

        TF(t,d) = count(t in d) / |d|
        IDF(t) = log(N / df(t))
        TF-IDF(t,d) = TF(t,d) × IDF(t)

        Args:
            documents: List of documents, each as a list of word tokens.

        Returns:
            Result with TF-IDF weight matrix per document.
        """
        try:
            if not documents:
                return Err(ValueError("Documents list must be non-empty."))

            N = len(documents)

            # Document frequency: how many docs contain each term
            df: Dict[str, int] = {}
            for doc in documents:
                seen = set(doc)
                for word in seen:
                    df[word] = df.get(word, 0) + 1

            # IDF
            idf = {word: math.log(N / count) for word, count in df.items()}

            # TF-IDF per document
            tfidf_matrix = []
            for doc in documents:
                doc_len = len(doc)
                if doc_len == 0:
                    tfidf_matrix.append({})
                    continue
                tf: Dict[str, int] = {}
                for word in doc:
                    tf[word] = tf.get(word, 0) + 1
                weights = {
                    word: round((count / doc_len) * idf.get(word, 0), 8)
                    for word, count in tf.items()
                }
                tfidf_matrix.append(weights)

            return Ok({
                "tfidf_matrix": tfidf_matrix,
                "vocabulary_size": len(df),
                "n_documents": N,
                "idf_scores": {w: round(v, 8) for w, v in sorted(idf.items(), key=lambda x: -x[1])[:50]},
            })

        except Exception as e:
            return Err(e)

    def diagnostics(self) -> Dict[str, Any]:
        """Provides engine operational status and metadata."""
        return {
            "engine": "OmniGensimWordEmbeddingEngine",
            "version": self.ENGINE_VERSION,
            "status": "operational",
            "embedding_dim": self.embedding_dim,
            "max_vocab_size": self.max_vocab_size,
            "complexity": "O(V × D) cosine similarity + O(N × V) TF-IDF",
        }
