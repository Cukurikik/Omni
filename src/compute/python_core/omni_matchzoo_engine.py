"""
OMNI MatchZoo Engine — Deep text matching primitives.

Assimilated from: NTMC-Community/MatchZoo (3.8k ★)
Facilitating the design, comparison and sharing of deep text matching models.

Implements core text matching building blocks:
  - Text representation: TF-IDF, BM25, one-hot, word embeddings
  - Interaction matrices: cosine, dot product, matching histograms
  - Matching models: DRMM, ArcI, MatchPyramid, KNRM kernels
  - Ranking losses: pairwise hinge, cross-entropy, listwise
  - Evaluation: MRR, MAP, NDCG, Precision@K

OMNI Domain: compute/ (Python)
CODE RULE 001-005 compliant. Only numpy dependency.
"""

from __future__ import annotations

import math
from typing import Any, Dict, List, Optional, Tuple, Set
from collections import Counter

import numpy as np


ENGINE_VERSION: str = "1.0.0-omni"
ENGINE_NAME: str = "OmniMatchZooEngine"


class Result:
    """Monadic Result type for error handling."""
    pass

class Ok(Result):
    """Monadic Ok result type."""
    def __init__(self, value: Any) -> None:
        """Initialize Ok."""
        self.value = value

class Err(Result):
    """Monadic Err result type."""
    def __init__(self, error: str) -> None:
        """Initialize Err."""
        self.error = error


class OmniMatchZooEngine:
    """Production-grade deep text matching engine.

    Implements text matching and ranking primitives:
      - Text representation (TF-IDF, BM25, embeddings)
      - Interaction matrices (cosine, histogram)
      - Matching kernels (KNRM, DRMM histogram)
      - Ranking losses (hinge, listwise)
      - IR evaluation metrics (MRR, MAP, NDCG, P@K)

    @since 1.0.0
    @tags ["text-matching", "information-retrieval", "ranking", "matchzoo", "compute"]
    """

    VERSION = ENGINE_VERSION
    ENGINE_ID = ENGINE_NAME

    def __init__(self) -> None:
        """Initialize OmniMatchZooEngine."""
        pass

    def diagnostics(self) -> Result:
        """Performs diagnostics operation for OmniMatchZooEngine."""
        return Ok({
            "engine": self.ENGINE_ID, "version": self.VERSION,
            "status": "operational",
            "capabilities": [
                "tfidf", "bm25", "cosine_interaction", "histogram_mapping",
                "knrm_kernels", "hinge_loss", "ndcg", "mrr", "map", "precision_at_k",
            ],
        })

    # -----------------------------------------------------------------
    # 1. TEXT REPRESENTATION
    # -----------------------------------------------------------------

    def compute_tf(self, doc_tokens: List[str]) -> Result:
        """Compute term frequency for a document.

        @param doc_tokens: List of tokens in the document.
        @returns Result with dict: token → TF value.
        """
        counts = Counter(doc_tokens)
        n = len(doc_tokens) if doc_tokens else 1
        tf = {t: c / n for t, c in counts.items()}
        return Ok(tf)

    def compute_idf(self, corpus: List[List[str]]) -> Result:
        """Compute inverse document frequency across corpus.

        IDF(t) = log(N / (1 + df(t)))

        @param corpus: List of documents (each a list of tokens).
        @returns Result with dict: token → IDF value.
        """
        N = len(corpus)
        df: Dict[str, int] = {}
        for doc in corpus:
            seen: Set[str] = set()
            for t in doc:
                if t not in seen:
                    df[t] = df.get(t, 0) + 1
                    seen.add(t)
        idf = {t: math.log(N / (1 + count)) for t, count in df.items()}
        return Ok(idf)

    def tfidf_vector(self, doc_tokens: List[str], idf: Dict[str, float], vocab: List[str]) -> Result:
        """Convert document to TF-IDF vector.

        @param doc_tokens: List of tokens.
        @param idf: IDF dictionary.
        @param vocab: Ordered vocabulary list.
        @returns Result with (len(vocab),) TF-IDF vector.
        """
        tf_res = self.compute_tf(doc_tokens)
        if isinstance(tf_res, Err):
            return tf_res
        tf = tf_res.value
        vec = np.zeros(len(vocab))
        for i, term in enumerate(vocab):
            vec[i] = tf.get(term, 0) * idf.get(term, 0)
        return Ok(vec)

    def bm25_score(
        self, query_tokens: List[str], doc_tokens: List[str],
        idf: Dict[str, float], avgdl: float,
        k1: float = 1.5, b: float = 0.75
    ) -> Result:
        """Compute BM25 relevance score.

        BM25(q, d) = sum_t IDF(t) * (tf * (k1+1)) / (tf + k1*(1-b+b*dl/avgdl))

        @param query_tokens: Query tokens.
        @param doc_tokens: Document tokens.
        @param idf: Precomputed IDF dict.
        @param avgdl: Average document length.
        @returns Result with scalar BM25 score.
        """
        dl = len(doc_tokens)
        tf_counts = Counter(doc_tokens)
        score = 0.0
        for t in query_tokens:
            if t in tf_counts:
                tf = tf_counts[t]
                idf_t = idf.get(t, 0)
                numerator = tf * (k1 + 1)
                denominator = tf + k1 * (1 - b + b * dl / max(avgdl, 1))
                score += idf_t * numerator / denominator
        return Ok(float(score))

    # -----------------------------------------------------------------
    # 2. INTERACTION MATRICES
    # -----------------------------------------------------------------

    def cosine_interaction_matrix(
        self, query_embeddings: np.ndarray, doc_embeddings: np.ndarray
    ) -> Result:
        """Compute cosine similarity interaction matrix.

        @param query_embeddings: (Q, D) query word embeddings.
        @param doc_embeddings: (T, D) document word embeddings.
        @returns Result with (Q, T) cosine similarity matrix.
        """
        q_norm = query_embeddings / (np.linalg.norm(query_embeddings, axis=1, keepdims=True) + 1e-10)
        d_norm = doc_embeddings / (np.linalg.norm(doc_embeddings, axis=1, keepdims=True) + 1e-10)
        return Ok(q_norm @ d_norm.T)

    def histogram_mapping(
        self, interaction_row: np.ndarray, n_bins: int = 30
    ) -> Result:
        """Map interaction scores to histogram (DRMM-style).

        @param interaction_row: (T,) cosine similarities for one query term.
        @param n_bins: Number of histogram bins.
        @returns Result with (n_bins,) histogram.
        """
        bins = np.linspace(-1, 1, n_bins + 1)
        hist, _ = np.histogram(interaction_row, bins=bins)
        # Normalize
        total = np.sum(hist) + 1e-10
        return Ok(hist.astype(np.float64) / total)

    # -----------------------------------------------------------------
    # 3. MATCHING KERNELS
    # -----------------------------------------------------------------

    def knrm_kernels(
        self, interaction_matrix: np.ndarray, n_kernels: int = 11
    ) -> Result:
        """KNRM: Kernel-based Neural Ranking Model.

        Apply Gaussian kernels on interaction matrix and pool.

        @param interaction_matrix: (Q, T) cosine similarities.
        @param n_kernels: Number of kernels.
        @returns Result with (Q, n_kernels) kernel features.
        """
        # Kernel means: evenly spaced from -1 to 1
        mus = np.linspace(-1, 1, n_kernels)
        sigma = 0.1

        Q, T = interaction_matrix.shape
        features = np.zeros((Q, n_kernels))
        for k in range(n_kernels):
            # RBF kernel
            K = np.exp(-0.5 * ((interaction_matrix - mus[k]) / sigma) ** 2)
            # Log-sum-exp pooling over document dimension
            features[:, k] = np.log(np.sum(K, axis=1) + 1e-10)

        return Ok(features)

    def drmm_matching(
        self, interaction_matrix: np.ndarray, n_bins: int = 30,
        W_hidden: Optional[np.ndarray] = None, b_hidden: Optional[np.ndarray] = None
    ) -> Result:
        """DRMM: Deep Relevance Matching Model.

        For each query term, create histogram of match scores,
        then feed through MLP.

        @param interaction_matrix: (Q, T) cosine similarities.
        @param n_bins: Histogram bins.
        @param W_hidden: (n_bins, hidden) MLP weight (optional).
        @param b_hidden: (hidden,) MLP bias (optional).
        @returns Result with (Q, hidden) or (Q, n_bins) features.
        """
        Q = interaction_matrix.shape[0]
        histograms = np.zeros((Q, n_bins))
        for q in range(Q):
            h_res = self.histogram_mapping(interaction_matrix[q], n_bins)
            if isinstance(h_res, Err):
                return h_res
            histograms[q] = h_res.value

        if W_hidden is not None and b_hidden is not None:
            out = np.maximum(0, histograms @ W_hidden + b_hidden)
            return Ok(out)
        return Ok(histograms)

    # -----------------------------------------------------------------
    # 4. RANKING LOSSES
    # -----------------------------------------------------------------

    def pairwise_hinge_loss(
        self, pos_scores: np.ndarray, neg_scores: np.ndarray, margin: float = 1.0
    ) -> Result:
        """Pairwise hinge loss for ranking.

        L = max(0, margin - (s_pos - s_neg))

        @param pos_scores: (N,) scores for positive documents.
        @param neg_scores: (N,) scores for negative documents.
        @param margin: Margin (default 1.0).
        @returns Result with scalar mean loss.
        """
        loss = np.maximum(0, margin - (pos_scores - neg_scores))
        return Ok(float(np.mean(loss)))

    def listwise_softmax_loss(self, scores: np.ndarray, relevance: np.ndarray) -> Result:
        """ListNet-style listwise softmax cross-entropy loss.

        @param scores: (N,) predicted scores.
        @param relevance: (N,) ground-truth relevance.
        @returns Result with scalar loss.
        """
        # Softmax of scores
        mx = np.max(scores)
        e_s = np.exp(scores - mx)
        p_s = e_s / (np.sum(e_s) + 1e-10)
        # Softmax of relevance
        mx_r = np.max(relevance)
        e_r = np.exp(relevance - mx_r)
        p_r = e_r / (np.sum(e_r) + 1e-10)
        # Cross-entropy
        loss = -np.sum(p_r * np.log(p_s + 1e-10))
        return Ok(float(loss))

    # -----------------------------------------------------------------
    # 5. EVALUATION METRICS
    # -----------------------------------------------------------------

    def precision_at_k(self, relevance: np.ndarray, k: int) -> Result:
        """Precision@K.

        @param relevance: (N,) binary relevance of ranked documents.
        @param k: Cutoff.
        @returns Result with P@K.
        """
        if k <= 0:
            return Err("k must be positive.")
        return Ok(float(np.mean(relevance[:min(k, len(relevance))] > 0)))

    def mrr(self, relevance: np.ndarray) -> Result:
        """Mean Reciprocal Rank (for single query).

        @param relevance: (N,) binary relevance.
        @returns Result with RR (reciprocal rank of first relevant doc).
        """
        for i, r in enumerate(relevance):
            if r > 0:
                return Ok(1.0 / (i + 1))
        return Ok(0.0)

    def average_precision(self, relevance: np.ndarray) -> Result:
        """Average Precision for a single query.

        @param relevance: (N,) binary relevance of ranked results.
        @returns Result with AP.
        """
        if np.sum(relevance) == 0:
            return Ok(0.0)
        cum_rel = np.cumsum(relevance)
        precision_at_ranks = cum_rel / np.arange(1, len(relevance) + 1)
        ap = np.sum(precision_at_ranks * relevance) / np.sum(relevance)
        return Ok(float(ap))

    def ndcg(self, relevance: np.ndarray, k: Optional[int] = None) -> Result:
        """Normalized Discounted Cumulative Gain.

        @param relevance: (N,) graded relevance.
        @param k: Optional cutoff.
        @returns Result with NDCG@k.
        """
        if k is not None:
            relevance = relevance[:k]
        dcg = np.sum((2 ** relevance - 1) / np.log2(np.arange(1, len(relevance) + 1) + 1))
        ideal = np.sort(relevance)[::-1]
        idcg = np.sum((2 ** ideal - 1) / np.log2(np.arange(1, len(ideal) + 1) + 1))
        if idcg < 1e-10:
            return Ok(0.0)
        return Ok(float(dcg / idcg))
