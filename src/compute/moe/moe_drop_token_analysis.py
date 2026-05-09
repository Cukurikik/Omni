"""
moe_drop_token_analysis.py — Analysis and Recovery of Dropped Tokens
Layer: Compute / AI — MoE Analytics

Monitors token dropping in capacity-constrained MoE routing and
provides mechanisms to recover or approximate dropped tokens to
prevent performance degradation.
"""
import torch
import torch.nn as nn
from typing import Dict, List, Optional
from collections import defaultdict


class DropTokenAnalyzer(nn.Module):
    """Tracks and analyzes tokens dropped due to expert capacity limits."""
    def __init__(self, num_experts: int, dim: int):
        super().__init__()
        self.num_experts = num_experts
        self.dim = dim
        self.total_tokens = 0
        self.total_dropped = 0
        self.dropped_per_expert = torch.zeros(num_experts)
        
        # Keep track of average representations of dropped tokens
        self.register_buffer("dropped_centroids", torch.zeros(num_experts, dim))
        self.dropped_counts = torch.zeros(num_experts)

    @torch.no_grad()
    def update(
        self,
        tokens: torch.Tensor,
        expert_indices: torch.Tensor,
        dropped_mask: torch.Tensor
    ):
        """
        Update statistics with the current batch.
        Args:
            tokens: (N, D) flat token embeddings
            expert_indices: (N,) targeted expert for each token
            dropped_mask: (N,) boolean mask where True means dropped
        """
        self.total_tokens += tokens.size(0)
        self.total_dropped += dropped_mask.sum().item()

        dropped_idx = expert_indices[dropped_mask]
        dropped_toks = tokens[dropped_mask]

        # Update per-expert drop counts
        for eid in range(self.num_experts):
            mask = dropped_idx == eid
            if mask.sum() > 0:
                count = mask.sum().float()
                self.dropped_per_expert[eid] += count
                
                # Exponential moving average of dropped token centroids
                curr_centroid = dropped_toks[mask].mean(dim=0)
                alpha = 0.1
                if self.dropped_counts[eid] == 0:
                    self.dropped_centroids[eid] = curr_centroid
                else:
                    self.dropped_centroids[eid] = (
                        (1 - alpha) * self.dropped_centroids[eid] + 
                        alpha * curr_centroid
                    )
                self.dropped_counts[eid] += count

    def get_stats(self) -> Dict[str, float]:
        rate = self.total_dropped / max(self.total_tokens, 1)
        return {
            "drop_rate": rate,
            "total_dropped": self.total_dropped,
            "worst_expert_drop_rate": (self.dropped_per_expert / max(self.total_tokens, 1)).max().item(),
            "bottleneck_expert": self.dropped_per_expert.argmax().item()
        }


class TokenRecoveryModule(nn.Module):
    """Attempts to recover dropped tokens using a shared lightweight expert."""
    def __init__(self, dim: int):
        super().__init__()
        # Small shared MLP to process dropped tokens
        self.recovery_expert = nn.Sequential(
            nn.Linear(dim, dim * 2, bias=False),
            nn.SiLU(),
            nn.Linear(dim * 2, dim, bias=False)
        )
        self.recovery_gate = nn.Parameter(torch.zeros(1))

    def forward(
        self,
        tokens: torch.Tensor,
        expert_outputs: torch.Tensor,
        dropped_mask: torch.Tensor
    ) -> torch.Tensor:
        """
        Process dropped tokens.
        Args:
            tokens: (B, S, D) original tokens
            expert_outputs: (B, S, D) outputs from MoE (zeros for dropped)
            dropped_mask: (B, S) boolean mask of dropped tokens
        """
        if not dropped_mask.any():
            return expert_outputs

        # Only process dropped tokens
        flat_tokens = tokens[dropped_mask]
        recovered = self.recovery_expert(flat_tokens)
        
        # Gate the recovery to allow the network to ignore it if harmful
        gate = torch.sigmoid(self.recovery_gate)
        
        # Scatter back to the outputs
        result = expert_outputs.clone()
        result[dropped_mask] = recovered * gate
        
        return result
