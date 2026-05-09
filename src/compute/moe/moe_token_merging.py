"""
moe_token_merging.py — Token Merging for MoE Efficiency
Layer: Compute / AI — MoE Token Optimization

Reduces computational cost by merging similar tokens before expert
processing. Merged tokens are unmerged after expert computation,
distributing the output to all original token positions.
"""
import torch
import torch.nn as nn
import torch.nn.functional as F
from typing import Tuple, Dict


class TokenMerger(nn.Module):
    """Merges similar tokens to reduce expert computation cost."""
    def __init__(self, dim, merge_ratio=0.5, similarity_threshold=0.8):
        super().__init__()
        self.merge_ratio = merge_ratio
        self.threshold = similarity_threshold
        self.proj = nn.Linear(dim, dim // 4, bias=False)  # lightweight projection

    def forward(self, tokens: torch.Tensor) -> Tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
        """Merge similar tokens.

        Returns:
            merged_tokens: reduced token set
            merge_map: mapping from merged to original positions
            merge_weights: contribution weights for unmerging
        """
        N, D = tokens.shape
        num_keep = max(1, int(N * (1 - self.merge_ratio)))

        # Compute pairwise similarity using lightweight projection
        proj = F.normalize(self.proj(tokens), dim=-1)
        sim = proj @ proj.T
        sim.fill_diagonal_(0)

        # Find most similar pairs
        merge_scores = sim.max(dim=-1).values
        _, sort_idx = merge_scores.sort(descending=True)

        # Split into kept and merged sets
        keep_idx = sort_idx[N - num_keep:]
        merge_idx = sort_idx[:N - num_keep]

        # For each merged token, find its nearest kept token
        kept_proj = proj[keep_idx]
        merged_proj = proj[merge_idx]
        assignments = (merged_proj @ kept_proj.T).argmax(dim=-1)

        # Create merged tokens by averaging with assigned kept tokens
        merged_tokens = tokens[keep_idx].clone()
        merge_weights = torch.ones(num_keep, device=tokens.device)

        for i, (m_idx, k_assign) in enumerate(zip(merge_idx, assignments)):
            k_pos = k_assign.item()
            old_w = merge_weights[k_pos]
            new_w = old_w + 1
            merged_tokens[k_pos] = (merged_tokens[k_pos] * old_w + tokens[m_idx]) / new_w
            merge_weights[k_pos] = new_w

        # Build unmerge map
        unmerge_map = torch.zeros(N, dtype=torch.long, device=tokens.device)
        for i, idx in enumerate(keep_idx):
            unmerge_map[idx] = i
        for m_idx, k_assign in zip(merge_idx, assignments):
            unmerge_map[m_idx] = k_assign

        return merged_tokens, unmerge_map, merge_weights

    @staticmethod
    def unmerge(merged_output: torch.Tensor, unmerge_map: torch.Tensor,
                original_size: int) -> torch.Tensor:
        """Distribute merged output back to original positions."""
        return merged_output[unmerge_map[:original_size]]


class MoEWithTokenMerging(nn.Module):
    """MoE layer with token merging for reduced computation."""
    def __init__(self, dim, num_experts, top_k=2, merge_ratio=0.3):
        super().__init__()
        self.merger = TokenMerger(dim, merge_ratio)
        self.gate = nn.Linear(dim, num_experts, bias=False)
        self.experts = nn.ModuleList([
            nn.Sequential(
                nn.Linear(dim, dim * 4, bias=False),
                nn.SiLU(),
                nn.Linear(dim * 4, dim, bias=False),
            ) for _ in range(num_experts)
        ])
        self.norm = nn.LayerNorm(dim)
        self.num_experts = num_experts
        self.top_k = top_k

    def forward(self, x: torch.Tensor) -> Dict[str, torch.Tensor]:
        B, S, D = x.shape
        residual = x
        flat = self.norm(x).reshape(-1, D)
        N = flat.shape[0]

        # Token merging
        merged, unmerge_map, _ = self.merger(flat)
        M = merged.shape[0]

        # Route merged tokens
        logits = self.gate(merged)
        topk_w, topk_idx = torch.topk(F.softmax(logits, dim=-1), self.top_k, dim=-1)

        # Process through experts
        output = torch.zeros_like(merged)
        for e in range(self.num_experts):
            mask = (topk_idx == e).any(dim=-1)
            if not mask.any():
                continue
            tok = mask.nonzero(as_tuple=True)[0]
            e_out = self.experts[e](merged[tok])
            for k in range(self.top_k):
                km = topk_idx[tok, k] == e
                if km.any():
                    ki = tok[km]
                    output[ki] += e_out[km] * topk_w[ki, k].unsqueeze(-1)

        # Unmerge back to original positions
        unmerged = TokenMerger.unmerge(output, unmerge_map, N)
        result = unmerged.reshape(B, S, D) + residual

        return {
            "output": result,
            "merged_tokens": M,
            "original_tokens": N,
            "compression_ratio": M / N,
            "aux_loss": torch.tensor(0.0, device=x.device),
        }
