"""
OMNI Compute Layer - RecLM
Recommendation Instruction Tuning (BPR Gradient Descent).
"""
import numpy as np

class RecommendationTuner:
    def __init__(self, learning_rate: float = 0.01):
        self.learning_rate = learning_rate

    def update_embeddings(self, user_emb: np.ndarray, item_emb: np.ndarray, target: float) -> tuple[np.ndarray, np.ndarray]:
        # BPR (Bayesian Personalized Ranking) gradient calculation
        prediction = np.dot(user_emb, item_emb)
        error = target - prediction
        
        # Gradient descent step
        user_grad = error * item_emb
        item_grad = error * user_emb
        
        new_user_emb = user_emb + self.learning_rate * user_grad
        new_item_emb = item_emb + self.learning_rate * item_grad
        
        return new_user_emb, new_item_emb
