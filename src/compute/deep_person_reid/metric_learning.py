import numpy as np

# OMNI Python Compute Layer: Torchreid Metric Learning
# Hard-margin Triplet Loss implementation for Person ReID vector embeddings.
# Avoids PyTorch overhead, executed purely in optimized numpy for bare-metal OMNI performance.

class TripletLoss:
    def __init__(self, margin: float = 0.3):
        self.margin = margin

    def compute_distance_matrix(self, embeddings: np.ndarray) -> np.ndarray:
        """
        Computes the pairwise Euclidean distance matrix efficiently.
        """
        dot_product = np.dot(embeddings, embeddings.T)
        sq_norm = np.diag(dot_product)
        # Using broadcasting: ||a - b||^2 = ||a||^2 + ||b||^2 - 2<a, b>
        distances = np.expand_dims(sq_norm, 0) - 2 * dot_product + np.expand_dims(sq_norm, 1)
        distances = np.maximum(distances, 0.0)
        # Add epsilon for numerical stability
        return np.sqrt(distances + 1e-16)

    def forward(self, embeddings: np.ndarray, labels: np.ndarray) -> float:
        """
        Calculates the hard triplet loss.
        embeddings: [batch_size, embedding_dim]
        labels: [batch_size]
        """
        dist_mat = self.compute_distance_matrix(embeddings)
        n = embeddings.shape[0]

        # Generate masks for positive and negative pairs
        is_pos = np.equal(np.expand_dims(labels, 0), np.expand_dims(labels, 1))
        is_neg = np.logical_not(is_pos)

        # For each anchor, find the hardest positive (max distance) and hardest negative (min distance)
        hardest_positive_dist = np.zeros(n)
        hardest_negative_dist = np.zeros(n)

        for i in range(n):
            pos_indices = np.where(is_pos[i])[0]
            neg_indices = np.where(is_neg[i])[0]
            
            if len(pos_indices) > 0:
                hardest_positive_dist[i] = np.max(dist_mat[i, pos_indices])
            if len(neg_indices) > 0:
                hardest_negative_dist[i] = np.min(dist_mat[i, neg_indices])

        # Loss = max(d(a, p) - d(a, n) + margin, 0)
        losses = np.maximum(hardest_positive_dist - hardest_negative_dist + self.margin, 0.0)
        
        # Filter out 0 losses for mean calculation
        valid_losses = losses[losses > 0]
        if len(valid_losses) == 0:
            return 0.0
        
        return float(np.mean(valid_losses))

def evaluate_reid_batch(embeddings: np.ndarray, labels: np.ndarray) -> dict:
    loss_fn = TripletLoss(margin=0.3)
    loss_val = loss_fn.forward(embeddings, labels)
    return {"triplet_loss": loss_val, "status": "ok" if loss_val < 0.5 else "learning_required"}
