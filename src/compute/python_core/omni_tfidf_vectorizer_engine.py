"""OmniTfIdfVectorizerEngine — Production-grade TF-IDF text vectorizer.

Implements Term Frequency-Inverse Document Frequency from scratch with
configurable normalization and document similarity computation.
"""
import math
from typing import Any, Dict, List, Tuple
from src.compute.python_core.omni_base_engine import Result, Ok, Err


class OmniTfIdfVectorizerEngine:
    """Production engine for TF-IDF text vectorization."""

    ENGINE_VERSION = "1.0.0"

    @staticmethod
    def _tokenize(text: str) -> List[str]:
        return [w.lower().strip(".,!?;:'\"()") for w in text.split() if w.strip(".,!?;:'\"()")]

    def fit_transform(self, documents: List[str]) -> Result:
        """
        Compute TF-IDF matrix for a corpus of documents.

        Args:
            documents: List of text documents.

        Returns:
            Result with TF-IDF matrix, vocabulary, and IDF values.
        """
        try:
            if not documents:
                return Err(ValueError("Documents must be non-empty."))

            tokenized = [self._tokenize(doc) for doc in documents]
            vocab = sorted(set(w for tokens in tokenized for w in tokens))
            vocab_idx = {w: i for i, w in enumerate(vocab)}
            n_docs = len(documents)
            n_terms = len(vocab)

            # Document frequency
            df = {}
            for tokens in tokenized:
                seen = set(tokens)
                for w in seen:
                    df[w] = df.get(w, 0) + 1

            # IDF: log(N / df(t)) + 1 (smooth)
            idf = {w: math.log(n_docs / df.get(w, 1)) + 1.0 for w in vocab}

            # TF-IDF matrix
            matrix = []
            for tokens in tokenized:
                tf = {}
                for w in tokens:
                    tf[w] = tf.get(w, 0) + 1
                row = [0.0] * n_terms
                for w, count in tf.items():
                    if w in vocab_idx:
                        row[vocab_idx[w]] = (count / max(len(tokens), 1)) * idf[w]
                # L2 normalize
                norm = math.sqrt(sum(v ** 2 for v in row))
                if norm > 0:
                    row = [v / norm for v in row]
                matrix.append([round(v, 8) for v in row])

            return Ok({"tfidf_matrix": matrix, "vocabulary": vocab,
                        "idf": {w: round(v, 6) for w, v in idf.items()},
                        "n_documents": n_docs, "n_terms": n_terms})
        except Exception as e:
            return Err(e)

    def cosine_similarity(self, vec_a: List[float], vec_b: List[float]) -> Result:
        """Compute cosine similarity between two TF-IDF vectors."""
        try:
            if len(vec_a) != len(vec_b):
                return Err(ValueError("Vectors must have equal length."))
            dot = sum(a * b for a, b in zip(vec_a, vec_b))
            na = math.sqrt(sum(a ** 2 for a in vec_a))
            nb = math.sqrt(sum(b ** 2 for b in vec_b))
            sim = dot / (na * nb) if (na > 0 and nb > 0) else 0.0
            return Ok({"similarity": round(sim, 8)})
        except Exception as e:
            return Err(e)

    def diagnostics(self) -> Dict[str, Any]:
        return {"engine": "OmniTfIdfVectorizerEngine", "version": self.ENGINE_VERSION,
                "status": "operational", "complexity": "O(N*V) TF-IDF with L2 normalization"}
