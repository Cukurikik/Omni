"""
omni_crf_layer.py — Conditional Random Field Layer
Inspired by: Bio-NER CRF structured prediction
Layer: Compute / AI

Production CRF for structured sequence labeling.
Supports Viterbi decoding, constrained transitions, and batched inference.
"""

import torch
import torch.nn as nn
from typing import List, Optional, Tuple


class OmniCRF(nn.Module):
    """Linear-chain CRF for sequence tagging.

    Computes the conditional probability P(y|x) using:
    - Emission scores from an upstream encoder
    - Learned transition matrix between labels
    - Optional transition constraints (BIO schema enforcement)
    """

    def __init__(self, num_tags: int, batch_first: bool = True):
        super().__init__()
        self.num_tags = num_tags
        self.batch_first = batch_first

        self.transitions = nn.Parameter(torch.randn(num_tags, num_tags))
        self.start_transitions = nn.Parameter(torch.randn(num_tags))
        self.end_transitions = nn.Parameter(torch.randn(num_tags))

        self._constraint_mask: Optional[torch.Tensor] = None

    def set_constraints(self, allowed: torch.Tensor):
        """Set allowed transitions. allowed[i,j] = True means i->j is valid."""
        self._constraint_mask = ~allowed

    def _validate(self, emissions: torch.Tensor, tags: Optional[torch.Tensor],
                  mask: Optional[torch.Tensor]):
        if self.batch_first:
            emissions = emissions.transpose(0, 1)
            if tags is not None:
                tags = tags.transpose(0, 1)
            if mask is not None:
                mask = mask.transpose(0, 1)
        return emissions, tags, mask

    def forward(self, emissions: torch.Tensor,
                tags: torch.Tensor,
                mask: Optional[torch.Tensor] = None,
                reduction: str = "mean") -> torch.Tensor:
        """Compute negative log-likelihood loss."""
        emissions, tags, mask = self._validate(emissions, tags, mask)
        seq_len, batch_size, _ = emissions.shape

        if mask is None:
            mask = torch.ones(seq_len, batch_size, dtype=torch.bool,
                              device=emissions.device)

        numerator = self._compute_score(emissions, tags, mask)
        denominator = self._compute_log_partition(emissions, mask)
        nll = denominator - numerator

        if reduction == "mean":
            return nll.mean()
        elif reduction == "sum":
            return nll.sum()
        return nll

    def _compute_score(self, emissions: torch.Tensor,
                       tags: torch.Tensor,
                       mask: torch.Tensor) -> torch.Tensor:
        seq_len, batch_size = tags.shape
        score = self.start_transitions[tags[0]]
        score += emissions[0, torch.arange(batch_size), tags[0]]

        for t in range(1, seq_len):
            score += self.transitions[tags[t - 1], tags[t]] * mask[t]
            score += emissions[t, torch.arange(batch_size), tags[t]] * mask[t]

        last_tag_idx = mask.long().sum(dim=0) - 1
        last_tags = tags[last_tag_idx, torch.arange(batch_size)]
        score += self.end_transitions[last_tags]

        return score

    def _compute_log_partition(self, emissions: torch.Tensor,
                               mask: torch.Tensor) -> torch.Tensor:
        seq_len, batch_size, num_tags = emissions.shape
        alpha = self.start_transitions + emissions[0]

        trans = self.transitions.unsqueeze(0)
        if self._constraint_mask is not None:
            trans = trans.masked_fill(self._constraint_mask.unsqueeze(0), -1e9)

        for t in range(1, seq_len):
            emit = emissions[t].unsqueeze(1)
            next_alpha = alpha.unsqueeze(2) + trans + emit
            next_alpha = torch.logsumexp(next_alpha, dim=1)
            alpha = torch.where(mask[t].unsqueeze(-1), next_alpha, alpha)

        alpha = alpha + self.end_transitions
        return torch.logsumexp(alpha, dim=-1)

    @torch.no_grad()
    def decode(self, emissions: torch.Tensor,
               mask: Optional[torch.Tensor] = None) -> List[List[int]]:
        """Viterbi decoding to find the best tag sequence."""
        emissions_orig = emissions
        emissions, _, mask = self._validate(emissions, None, mask)
        seq_len, batch_size, num_tags = emissions.shape

        if mask is None:
            mask = torch.ones(seq_len, batch_size, dtype=torch.bool,
                              device=emissions.device)

        viterbi_score = self.start_transitions + emissions[0]
        viterbi_history: List[torch.Tensor] = []

        trans = self.transitions
        if self._constraint_mask is not None:
            trans = trans.masked_fill(self._constraint_mask, -1e9)

        for t in range(1, seq_len):
            broadcast_score = viterbi_score.unsqueeze(2) + trans.unsqueeze(0)
            broadcast_score += emissions[t].unsqueeze(1)
            best_score, best_idx = broadcast_score.max(dim=1)
            viterbi_history.append(best_idx)
            viterbi_score = torch.where(mask[t].unsqueeze(-1),
                                        best_score, viterbi_score)

        viterbi_score += self.end_transitions

        best_paths: List[List[int]] = []
        for b in range(batch_size):
            seq_end = mask[:, b].long().sum() - 1
            _, best_tag = viterbi_score[b].max(dim=0)
            path = [best_tag.item()]

            for hist in reversed(viterbi_history[:seq_end]):
                best_tag = hist[b, best_tag]
                path.append(best_tag.item())

            path.reverse()
            best_paths.append(path)

        return best_paths


def build_bio_constraints(num_tags: int, bio_pairs: List[Tuple[int, int]]
                          ) -> torch.Tensor:
    """Build BIO-schema transition constraint matrix.

    Args:
        num_tags: Total number of tags including O, B-*, I-* tags
        bio_pairs: List of (B-tag_idx, I-tag_idx) pairs
    """
    allowed = torch.ones(num_tags, num_tags, dtype=torch.bool)

    for b_idx, i_idx in bio_pairs:
        # I-X can only follow B-X or I-X
        for other in range(num_tags):
            if other != b_idx and other != i_idx:
                allowed[other, i_idx] = False

    return allowed
