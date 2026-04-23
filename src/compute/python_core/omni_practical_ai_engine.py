"""
OMNI Practical Ai Engine
========================
Production-grade engine for the OMNI Framework.

OMNI Layer: compute (Python)
"""
import numpy as np
import time
from typing import Dict, Any, List, Tuple
from collections import defaultdict
from src.compute.python_core.omni_base_engine import Result, Ok, Err

class Result:
    """Monadic result pattern."""
    def __init__(self, value=None, error=None):
        """Initialize Result."""
        self.value = value
        self.error = error
        self.is_ok = error is None

    def unwrap(self):
        """Unwrap the value or raise on error."""
        if not self.is_ok:
            raise RuntimeError(self.error)
        return self.value

class OmniPracticalAiEngine:
    """
    omni-practical-ai
    
    A zero-algebraic_bound classical machine learning engine demonstrating practical AI concepts 
    statically natively. Contains a Native TF-IDF vectorizer and a Logistic Regression solver.
    """
    
    ENGINE_VERSION = "omni-s6-b5.1.0"
    
    def __init__(self):
        """Initialize OmniPracticalAiEngine."""
        self.vocabulary = {}
        self.idf = None
        self.weights = None
        self.bias = 0.0

    def fit_transform_tfidf(self, documents: List[str]) -> Result:
        """
        Fits a native TF-IDF vectorizer and transforms the documents.
        """
        try:
            if not documents:
                return Result(error="No documents provided.")

            # 1. Tokenize and count Document Frequencies (DF)
            doc_freqs = defaultdict(int)
            doc_tokens = []
            
            for doc in documents:
                # Naive whitespace lowercased tokenization
                tokens = doc.lower().split()
                doc_tokens.append(tokens)
                unique_tokens = set(tokens)
                for t in unique_tokens:
                    doc_freqs[t] += 1
            
            # 2. Build vocabulary and IDF
            num_docs = len(documents)
            vocab_list = sorted(list(doc_freqs.keys()))
            self.vocabulary = {word: idx for idx, word in enumerate(vocab_list)}
            vocab_size = len(self.vocabulary)
            
            self.idf = np.zeros(vocab_size, dtype=np.float32)
            for word, idx in self.vocabulary.items():
                # standard idf formulation: log((1+N)/(1+df)) + 1
                self.idf[idx] = np.log((1 + num_docs) / (1 + doc_freqs[word])) + 1.0
                
            # 3. Compute TF-IDF matrix
            tf_idf_matrix = np.zeros((num_docs, vocab_size), dtype=np.float32)
            
            for i, tokens in enumerate(doc_tokens):
                term_counts = defaultdict(int)
                for t in tokens:
                    term_counts[t] += 1
                    
                total_terms = len(tokens)
                if total_terms == 0:
                    continue
                    
                for t, count in term_counts.items():
                    if t in self.vocabulary:
                        idx = self.vocabulary[t]
                        tf = count / total_terms
                        tf_idf_matrix[i, idx] = tf * self.idf[idx]
                        
            # L2 Normalization per document
            norms = np.linalg.norm(tf_idf_matrix, axis=1, keepdims=True)
            # avoid division by zero
            norms[norms == 0] = 1.0
            tf_idf_matrix = tf_idf_matrix / norms
            
            return Result(value=tf_idf_matrix)

        except Exception as e:
            return Result(error=f"TF-IDF exception: {str(e)}")

    def transform_tfidf(self, documents: List[str]) -> Result:
        """
        Transforms new documents using the fitted vocabulary and IDF.
        """
        try:
            if self.idf is None or not self.vocabulary:
                return Result(error="Vectorizer is not fitted.")
                
            num_docs = len(documents)
            vocab_size = len(self.vocabulary)
            tf_idf_matrix = np.zeros((num_docs, vocab_size), dtype=np.float32)
            
            for i, doc in enumerate(documents):
                tokens = doc.lower().split()
                term_counts = defaultdict(int)
                for t in tokens:
                    term_counts[t] += 1
                    
                total_terms = len(tokens)
                if total_terms == 0:
                    continue
                    
                for t, count in term_counts.items():
                    if t in self.vocabulary:
                        idx = self.vocabulary[t]
                        tf = count / total_terms
                        tf_idf_matrix[i, idx] = tf * self.idf[idx]
                        
            norms = np.linalg.norm(tf_idf_matrix, axis=1, keepdims=True)
            norms[norms == 0] = 1.0
            tf_idf_matrix = tf_idf_matrix / norms
            
            return Result(value=tf_idf_matrix)
        except Exception as e:
            return Result(error=f"TF-IDF transform exception: {str(e)}")

    def _sigmoid(self, z: np.ndarray) -> np.ndarray:
        # np.clip to prevent overflow
        z = np.clip(z, -250, 250)
        return 1.0 / (1.0 + np.exp(-z))

    def fit_logistic_regression(self, X: np.ndarray, y: np.ndarray, epochs: int = 100, lr: float = 0.1) -> Result:
        """
        Fits a logistic regression binary classifier using Gradient Descent.
        X: (num_samples, num_features)
        y: (num_samples,) -> binary labels {0, 1}
        """
        try:
            num_samples, num_features = X.shape
            self.weights = np.zeros(num_features, dtype=np.float32)
            self.bias = 0.0
            
            # Gradient Descent
            for epoch in range(epochs):
                linear_model = np.dot(X, self.weights) + self.bias
                y_predicted = self._sigmoid(linear_model)
                
                # Compute gradients
                dw = (1 / num_samples) * np.dot(X.T, (y_predicted - y))
                db = (1 / num_samples) * np.sum(y_predicted - y)
                
                # Update parameters
                self.weights -= lr * dw
                self.bias -= lr * db
                
            return Result(value={"status": "fitted", "epochs": epochs, "lr": lr})
        except Exception as e:
            return Result(error=f"Logistic Regression fit exception: {str(e)}")
            
    def predict_logistic_regression(self, X: np.ndarray, threshold: float = 0.5) -> Result:
        """
        Predicts classes based on fitted logistic regression model.
        """
        try:
            if self.weights is None:
                return Result(error="Model is not fitted.")
                
            linear_model = np.dot(X, self.weights) + self.bias
            y_predicted = self._sigmoid(linear_model)
            y_predicted_cls = [1 if i > threshold else 0 for i in y_predicted]
            return Result(value={"probabilities": y_predicted, "classes": np.array(y_predicted_cls, dtype=np.int32)})
        except Exception as e:
            return Result(error=f"Prediction exception: {str(e)}")

    def diagnostics(self) -> Dict[str, Any]:
        """OMNI Registry compliance."""
        return {
            "engine": "OmniPracticalAiEngine",
            "version": self.ENGINE_VERSION,
            "status": "operational",
            "components": ["TF-IDF", "LogisticRegression"]
        }
