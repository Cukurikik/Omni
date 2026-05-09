"""
moe_token_entropy_logger.py — Compute / Analytics
Layer: Compute / Analytics — Routing Confidence Analysis

Logs and analyzes the Shannon entropy of the router's probability
distribution over experts. High entropy indicates the router is "confused"
and distributing probability uniformly; low entropy indicates high confidence
(hard specialization).
"""
import torch
import torch.nn as nn
from typing import Dict, List
import math
import logging

logger = logging.getLogger(__name__)


class TokenEntropyLogger(nn.Module):
    """Tracks routing entropy over batches."""
    def __init__(self, num_experts: int):
        super().__init__()
        self.num_experts = num_experts
        self.max_entropy = math.log(num_experts)
        
        self.total_tokens = 0
        self.sum_entropy = 0.0
        
        # Track entropy distribution (histogram)
        self.entropy_bins = 10
        self.register_buffer("entropy_histogram", torch.zeros(self.entropy_bins))

    @torch.no_grad()
    def update(self, routing_probs: torch.Tensor):
        """
        Updates the running entropy statistics.
        Args:
            routing_probs: (N, num_experts) post-softmax probabilities.
        """
        if routing_probs.numel() == 0:
            return
            
        N = routing_probs.shape[0]
        
        # Calculate Shannon entropy: -sum(p * log(p))
        # Add epsilon to prevent log(0)
        epsilon = 1e-9
        entropy = -torch.sum(routing_probs * torch.log(routing_probs + epsilon), dim=-1)
        
        self.total_tokens += N
        self.sum_entropy += entropy.sum().item()
        
        # Update histogram (normalize entropy to [0, 1] relative to max possible)
        normalized_entropy = entropy / self.max_entropy
        
        # Bin indices: 0 to 9
        bin_indices = (normalized_entropy * self.entropy_bins).long().clamp(0, self.entropy_bins - 1)
        
        hist_update = torch.bincount(bin_indices, minlength=self.entropy_bins).float()
        self.entropy_histogram += hist_update

    def get_stats(self) -> Dict[str, float]:
        """Returns the current entropy statistics."""
        avg_entropy = self.sum_entropy / max(self.total_tokens, 1)
        avg_normalized = avg_entropy / self.max_entropy
        
        return {
            "avg_entropy_nats": avg_entropy,
            "avg_normalized_entropy": avg_normalized,
            "max_possible_entropy": self.max_entropy,
            "total_tokens_sampled": self.total_tokens,
            "confidence_score": 1.0 - avg_normalized # 1.0 = absolute certainty, 0.0 = random guessing
        }

    def get_histogram_normalized(self) -> List[float]:
        """Returns the entropy histogram normalized to percentages."""
        total = self.entropy_histogram.sum().item()
        if total == 0:
            return [0.0] * self.entropy_bins
        return (self.entropy_histogram / total).tolist()
        
    def reset(self):
        """Reset statistics for a new epoch/window."""
        self.total_tokens = 0
        self.sum_entropy = 0.0
        self.entropy_histogram.zero_()
