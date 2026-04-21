"""
OMNI Recommender Engine
=======================
Production-grade engine for the OMNI Framework.

OMNI Layer: compute (Python)
"""
import numpy as np
from typing import Dict, Any, List, Tuple

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

class OmniRecommenderEngine:
    """
    omni-recommender
    
    A zero-mock native engine capturing advanced Recommender System (RS) logic,
    focusing on Matrix Factorization (Collaborative Filtering) via Stochastic
    Gradient Descent over latent embedding matrices.
    """
    
    ENGINE_VERSION = "omni-s6-b7.1.0"
    
    def __init__(self, num_users: int = 100, num_items: int = 100, latent_dim: int = 16):
        """Initialize OmniRecommenderEngine."""
        self.num_users = num_users
        self.num_items = num_items
        self.latent_dim = latent_dim
        
        # User and Item Latent Matrices
        np.random.seed(42)
        self.user_emb = np.random.normal(scale=1.0/latent_dim, size=(num_users, latent_dim)).astype(np.float32)
        self.item_emb = np.random.normal(scale=1.0/latent_dim, size=(num_items, latent_dim)).astype(np.float32)
        
        # Global bias terms
        self.user_bias = np.zeros(num_users, dtype=np.float32)
        self.item_bias = np.zeros(num_items, dtype=np.float32)
        self.global_bias = 0.0
        
        self.interactions: List[Tuple[int, int, float]] = []

    def feed_interaction(self, user_id: int, item_id: int, rating: float) -> Result:
        """Stores a sparse user-item interaction structure."""
        if user_id >= self.num_users or item_id >= self.num_items:
             return Result(error="ID out of bounds.")
        self.interactions.append((user_id, item_id, rating))
        return Result(value={"status": "stored", "total_interactions": len(self.interactions)})

    def fit(self, epochs: int = 10, lr: float = 0.01, reg: float = 0.02) -> Result:
        """
        Matrix Factorization via SGD optimizing Latent Embeddings.
        Loss = (r - (mu + b_u + b_i + p_u^T q_i))^2 + lambda * (||p||^2 + ||q||^2 + b_u^2 + b_i^2)
        """
        try:
            if not self.interactions:
                 return Result(error="No interactions provided.")
                 
            self.global_bias = np.mean([r for (_, _, r) in self.interactions])
            history_mse = []
            
            for epoch in range(epochs):
                # Shuffle interactions for SGD constraint
                np.random.shuffle(self.interactions)
                
                total_err = 0.0
                for u, i, r in self.interactions:
                    # Current prediction
                    pred_r = self.global_bias + self.user_bias[u] + self.item_bias[i] + np.dot(self.user_emb[u], self.item_emb[i])
                    
                    e = r - pred_r
                    total_err += e * e
                    
                    # Store current latent vector copy
                    u_vec = self.user_emb[u].copy()
                    i_vec = self.item_emb[i].copy()
                    
                    # Update biases
                    self.user_bias[u] += lr * (e - reg * self.user_bias[u])
                    self.item_bias[i] += lr * (e - reg * self.item_bias[i])
                    
                    # Update latent embeddings
                    self.user_emb[u] += lr * (e * i_vec - reg * u_vec)
                    self.item_emb[i] += lr * (e * u_vec - reg * i_vec)
                    
                mse = total_err / len(self.interactions)
                history_mse.append(mse)
                
            return Result(value={"status": "converged", "final_mse": history_mse[-1], "history": history_mse})
            
        except Exception as e:
            return Result(error=f"Matrix Factorization error: {str(e)}")

    def predict(self, user_id: int, item_id: int) -> Result:
        """Predicts the rating bound for a specific user and item pair."""
        try:
            if user_id >= self.num_users or item_id >= self.num_items:
                 return Result(error="ID out of bounds.")
                 
            pred_r = self.global_bias + self.user_bias[user_id] + self.item_bias[item_id] + np.dot(self.user_emb[user_id], self.item_emb[item_id])
            
            return Result(value=float(pred_r))
        except Exception as e:
            return Result(error=f"Prediction error: {str(e)}")

    def diagnostics(self) -> Dict[str, Any]:
        """OMNI Registry compliance."""
        return {
            "engine": "OmniRecommenderEngine",
            "version": self.ENGINE_VERSION,
            "status": "operational",
            "mechanisms": ["Matrix Factorization", "Latent Embeddings", "Stochastic Gradient Descent"]
        }
