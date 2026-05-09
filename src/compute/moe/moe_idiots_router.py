# moe_idiots_router.py — Compute Layer: Mixture of Idiots Experts Router
# PyTorch based routing logic selecting specialized "idiot" subnetworks based on embeddings.

import math
from typing import Tuple, List

class IdiotsRouter:
    def __init__(self, num_experts: int, top_k: int):
        self.num_experts = num_experts
        self.top_k = top_k
        
    def _compute_similarity(self, token_embedding: List[float], expert_centroid: List[float]) -> float:
        # Dot product similarity
        return sum(t * e for t, e in zip(token_embedding, expert_centroid))

    def route_tokens(self, token_embeddings: List[List[float]], expert_centroids: List[List[float]]) -> Tuple[List[List[int]], List[List[float]]]:
        """
        Routes tokens to the top-K experts.
        Returns expert indices and their routing weights.
        """
        batch_indices = []
        batch_weights = []
        
        for token in token_embeddings:
            scores = [self._compute_similarity(token, centroid) for centroid in expert_centroids]
            
            # Get top K indices
            indexed_scores = list(enumerate(scores))
            indexed_scores.sort(key=lambda x: x[1], reverse=True)
            
            top_k_items = indexed_scores[:self.top_k]
            indices = [x[0] for x in top_k_items]
            raw_weights = [x[1] for x in top_k_items]
            
            # Softmax normalization
            max_w = max(raw_weights)
            exp_weights = [math.exp(w - max_w) for w in raw_weights]
            sum_exp = sum(exp_weights)
            norm_weights = [w / sum_exp for w in exp_weights]
            
            batch_indices.append(indices)
            batch_weights.append(norm_weights)
            
        return batch_indices, batch_weights
