"""
OMNI RecBole Engine — Recommendation system primitives via collaborative filtering.
Assimilated from: RUCAIBox/RecBole + wzhe06/Ad-papers + janhuenermann/neurojs
Provides: User-item matrices, cosine similarity, matrix factorization, top-K ranking.
"""
import numpy as np
from typing import List, Tuple



ENGINE_VERSION = "1.0.0-omni"
from src.compute.python_core.omni_base_engine import Result, Ok, Err

class Result:
    """Monadic Result base."""
    pass


class Ok(Result):
    """Success variant."""
    def __init__(self, value):
        """Initialize Ok."""
        self.value = value


class Err(Result):
    """Error variant."""
    def __init__(self, error: str):
        """Initialize Err."""
        self.error = error


class OmniRecBoleEngine:
    """
    Pure NumPy recommendation engine implementing collaborative filtering,
    cosine-similarity ranking, and truncated SVD-based matrix factorization.

    Absorbs patterns from RecBole (PyTorch recommender toolkit),
    Ad-papers (advertising ML), and neurojs (JS neural nets).

    @since 1.0.0
    @tags ["recommendation", "collaborative-filtering", "ranking", "compute"]
    """

    def __init__(self) -> None:
        """Initialize OmniRecBoleEngine."""
        self._omni_version: str = "3.0.0-OMNI-NEXUS"

    def diagnostics(self) -> Result:
        """Returns engine health status."""
        return Ok({"status": "active", "engine": "RecBole", "capability": "CollaborativeFilteringRanking"})

    def cosine_similarity_matrix(self, matrix: np.ndarray) -> Result:
        """
        Computes pairwise cosine similarity between rows of the input matrix.

        sim(u, v) = (u · v) / (||u|| * ||v||)

        @param matrix: 2D array of shape (N, D) where N is users/items and D is features.
        @returns Result containing (N, N) similarity matrix.
        """
        if matrix.ndim != 2:
            return Err("Input must be a 2D matrix (N, D).")

        norms = np.linalg.norm(matrix, axis=1, keepdims=True)
        norms = np.where(norms == 0, 1e-12, norms)  # prevent division by zero
        normalized = matrix / norms
        similarity = normalized @ normalized.T

        return Ok(similarity)

    def top_k_items(self, user_scores: np.ndarray, k: int, exclude_indices: np.ndarray = None) -> Result:
        """
        Returns the top-K item indices sorted by descending score for a single user.

        @param user_scores: 1D array of predicted scores for all items.
        @param k: Number of top items to return.
        @param exclude_indices: Optional array of item indices to exclude (already consumed).
        @returns Result containing 1D array of top-K item indices.
        """
        if user_scores.ndim != 1:
            return Err("user_scores must be a 1D array.")
        if k <= 0:
            return Err("k must be a positive integer.")

        scores = user_scores.copy()
        if exclude_indices is not None:
            scores[exclude_indices] = -np.inf

        if k > len(scores):
            k = len(scores)

        top_indices = np.argpartition(scores, -k)[-k:]
        top_indices = top_indices[np.argsort(scores[top_indices])[::-1]]

        return Ok(top_indices)

    def matrix_factorize_svd(self, interaction_matrix: np.ndarray, n_factors: int) -> Result:
        """
        Performs truncated SVD on a user-item interaction matrix for latent factor extraction.

        R ≈ U_k * Sigma_k * V_k^T

        @param interaction_matrix: 2D array of shape (num_users, num_items).
        @param n_factors: Number of latent factors to retain.
        @returns Result containing dict with 'user_factors', 'item_factors', 'singular_values'.
        """
        if interaction_matrix.ndim != 2:
            return Err("Interaction matrix must be 2D (users x items).")
        if n_factors <= 0:
            return Err("n_factors must be a positive integer.")

        max_factors = min(interaction_matrix.shape)
        if n_factors > max_factors:
            n_factors = max_factors

        U, S, Vt = np.linalg.svd(interaction_matrix, full_matrices=False)

        user_factors = U[:, :n_factors] * S[:n_factors]  # (num_users, n_factors)
        item_factors = Vt[:n_factors, :].T               # (num_items, n_factors)

        return Ok({
            "user_factors": user_factors,
            "item_factors": item_factors,
            "singular_values": S[:n_factors],
        })

    def predict_ratings(self, user_factors: np.ndarray, item_factors: np.ndarray) -> Result:
        """
        Reconstructs the predicted rating matrix from latent factors.

        R_hat = user_factors @ item_factors^T

        @param user_factors: (num_users, n_factors) array.
        @param item_factors: (num_items, n_factors) array.
        @returns Result containing predicted ratings matrix.
        """
        if user_factors.ndim != 2 or item_factors.ndim != 2:
            return Err("Both factor matrices must be 2D.")
        if user_factors.shape[1] != item_factors.shape[1]:
            return Err("Factor dimensions must match between user and item matrices.")

        predictions = user_factors @ item_factors.T
        return Ok(predictions)
