"""
OMNI MOTHER: Switch Transformer Architecture (Production Grade)
===============================================================
Full implementation of the Switch Transformer from Fedus, Zoph & Shazeer (2021).
Includes:
  - Top-1 Router with load-balancing auxiliary loss
  - Capacity-factor based token dropping
  - Expert-level feed-forward networks with configurable hidden dimension
  - Jitter noise for training stability
  - Complete forward pass with auxiliary loss accumulation

References:
    - "Switch Transformers: Scaling to Trillion Parameter Models with
       Simple and Efficient Sparsity" — arXiv:2101.03961
"""

import logging
import math
from dataclasses import dataclass
from typing import Optional, Tuple

import torch
import torch.nn as nn
import torch.nn.functional as F

logger = logging.getLogger("OmniSwitchTransformer")


@dataclass
class SwitchConfig:
    """Configuration for a Switch Transformer MoE layer."""
    d_model: int = 768
    d_ff: int = 3072
    num_experts: int = 16
    capacity_factor: float = 1.25
    jitter_noise: float = 0.01
    aux_loss_weight: float = 0.01
    dropout: float = 0.1
    expert_dropout: float = 0.0


class SwitchRouter(nn.Module):
    """
    Top-1 gating router with jitter noise and load-balancing loss.

    During training, multiplicative jitter noise is applied to the router
    logits to encourage exploration of all experts.
    """

    def __init__(self, d_model: int, num_experts: int, jitter_noise: float = 0.01):
        super().__init__()
        self.num_experts = num_experts
        self.jitter_noise = jitter_noise
        self.classifier = nn.Linear(d_model, num_experts, bias=False)

    def _compute_jitter(self, x: torch.Tensor) -> torch.Tensor:
        """Apply multiplicative jitter during training."""
        if self.training and self.jitter_noise > 0:
            noise = torch.empty_like(x).uniform_(
                1.0 - self.jitter_noise, 1.0 + self.jitter_noise
            )
            return x * noise
        return x

    def forward(
        self, hidden_states: torch.Tensor
    ) -> Tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
        """
        Args:
            hidden_states: ``[batch, seq_len, d_model]``

        Returns:
            - top1_gate_scores: ``[batch * seq_len]``
              Softmax probability of the selected expert.
            - top1_expert_indices: ``[batch * seq_len]``
              Index of the selected expert per token.
            - router_probs: ``[batch * seq_len, num_experts]``
              Full softmax distribution (needed for aux loss).
        """
        batch, seq_len, _ = hidden_states.shape
        flat = hidden_states.view(-1, hidden_states.size(-1))

        logits = self.classifier(self._compute_jitter(flat))
        router_probs = F.softmax(logits, dim=-1)

        top1_gate_scores, top1_expert_indices = router_probs.max(dim=-1)

        return top1_gate_scores, top1_expert_indices, router_probs


class SwitchExpert(nn.Module):
    """
    A single feed-forward expert network.
    Architecture: Linear → GELU → Dropout → Linear → Dropout
    """

    def __init__(self, d_model: int, d_ff: int, dropout: float = 0.0):
        super().__init__()
        self.w1 = nn.Linear(d_model, d_ff, bias=False)
        self.w2 = nn.Linear(d_ff, d_model, bias=False)
        self.act = nn.GELU()
        self.dropout = nn.Dropout(dropout)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.dropout(self.w2(self.dropout(self.act(self.w1(x)))))


class SwitchMoELayer(nn.Module):
    """
    Full Switch Transformer MoE layer with:
    - Top-1 routing
    - Capacity-factor token dropping
    - Auxiliary load-balancing loss

    The auxiliary loss encourages a uniform distribution of tokens
    across experts, preventing expert collapse.
    """

    def __init__(self, config: SwitchConfig):
        super().__init__()
        self.config = config
        self.router = SwitchRouter(
            config.d_model, config.num_experts, config.jitter_noise
        )
        self.experts = nn.ModuleList([
            SwitchExpert(config.d_model, config.d_ff, config.expert_dropout)
            for _ in range(config.num_experts)
        ])
        self.layer_norm = nn.LayerNorm(config.d_model)
        self.dropout = nn.Dropout(config.dropout)

    def _compute_auxiliary_loss(
        self,
        router_probs: torch.Tensor,
        expert_indices: torch.Tensor,
    ) -> torch.Tensor:
        """
        Computes the load-balancing auxiliary loss from the Switch paper.

        loss = N * Σ_i (f_i * P_i)

        where:
            f_i = fraction of tokens routed to expert i
            P_i = fraction of router probability allocated to expert i
            N   = number of experts
        """
        num_tokens = router_probs.size(0)
        num_experts = self.config.num_experts

        # f_i: fraction of tokens dispatched to each expert
        expert_mask = F.one_hot(expert_indices, num_classes=num_experts).float()
        tokens_per_expert = expert_mask.sum(dim=0)  # [num_experts]
        f = tokens_per_expert / max(num_tokens, 1)

        # P_i: mean routing probability per expert
        p = router_probs.mean(dim=0)  # [num_experts]

        aux_loss = num_experts * torch.sum(f * p)
        return aux_loss

    def _capacity_limited_dispatch(
        self,
        hidden_states: torch.Tensor,
        expert_indices: torch.Tensor,
        gate_scores: torch.Tensor,
    ) -> torch.Tensor:
        """
        Dispatch tokens to experts respecting per-expert capacity limits.
        Tokens that overflow an expert's capacity buffer are dropped
        (their original hidden state passes through unchanged via the
        residual connection).
        """
        num_tokens, d_model = hidden_states.shape
        num_experts = self.config.num_experts
        expert_capacity = int(
            math.ceil(num_tokens / num_experts) * self.config.capacity_factor
        )
        expert_capacity = max(expert_capacity, 1)

        output = torch.zeros_like(hidden_states)
        expert_counts = torch.zeros(num_experts, dtype=torch.long, device=hidden_states.device)

        for token_idx in range(num_tokens):
            eid = expert_indices[token_idx].item()
            if expert_counts[eid] < expert_capacity:
                # Token is within capacity — process it
                token_input = hidden_states[token_idx].unsqueeze(0)
                expert_output = self.experts[eid](token_input)
                output[token_idx] = gate_scores[token_idx] * expert_output.squeeze(0)
                expert_counts[eid] += 1
            else:
                # Token overflow — pass through unchanged (will be added via residual)
                output[token_idx] = 0.0  # zero contribution from MoE

        return output

    def _batched_expert_forward(
        self,
        hidden_states: torch.Tensor,
        expert_indices: torch.Tensor,
        gate_scores: torch.Tensor,
    ) -> torch.Tensor:
        """
        Optimized dispatch: groups tokens by expert for batched matrix
        multiplication, respecting capacity limits.
        """
        num_tokens, d_model = hidden_states.shape
        num_experts = self.config.num_experts
        expert_capacity = int(
            math.ceil(num_tokens / num_experts) * self.config.capacity_factor
        )
        expert_capacity = max(expert_capacity, 1)

        output = torch.zeros_like(hidden_states)

        for eid in range(num_experts):
            mask = expert_indices == eid
            if not mask.any():
                continue

            # Apply capacity limit
            token_positions = mask.nonzero(as_tuple=True)[0]
            if token_positions.size(0) > expert_capacity:
                token_positions = token_positions[:expert_capacity]

            expert_input = hidden_states[token_positions]  # [selected, d_model]
            expert_output = self.experts[eid](expert_input)  # [selected, d_model]
            gated_output = gate_scores[token_positions].unsqueeze(-1) * expert_output
            output[token_positions] = gated_output

        return output

    def forward(
        self, hidden_states: torch.Tensor
    ) -> Tuple[torch.Tensor, torch.Tensor]:
        """
        Args:
            hidden_states: ``[batch, seq_len, d_model]``

        Returns:
            - output: ``[batch, seq_len, d_model]``
            - aux_loss: scalar auxiliary load-balancing loss
        """
        batch, seq_len, d_model = hidden_states.shape
        residual = hidden_states
        normed = self.layer_norm(hidden_states)

        flat = normed.view(-1, d_model)

        gate_scores, expert_indices, router_probs = self.router(normed)

        # Dispatch tokens to experts (batched for efficiency)
        expert_output = self._batched_expert_forward(flat, expert_indices, gate_scores)

        # Residual connection
        output = residual + self.dropout(expert_output.view(batch, seq_len, d_model))

        # Auxiliary loss
        aux_loss = self._compute_auxiliary_loss(router_probs, expert_indices)

        return output, aux_loss * self.config.aux_loss_weight


class SwitchTransformerBlock(nn.Module):
    """
    A full transformer block with Switch MoE replacing the dense FFN.
    Includes self-attention + Switch MoE feed-forward.
    """

    def __init__(self, config: SwitchConfig, num_heads: int = 12):
        super().__init__()
        self.attention = nn.MultiheadAttention(
            config.d_model, num_heads, dropout=config.dropout, batch_first=True
        )
        self.attn_norm = nn.LayerNorm(config.d_model)
        self.moe = SwitchMoELayer(config)

    def forward(
        self,
        x: torch.Tensor,
        attention_mask: Optional[torch.Tensor] = None,
    ) -> Tuple[torch.Tensor, torch.Tensor]:
        """
        Args:
            x: ``[batch, seq_len, d_model]``
            attention_mask: Optional causal or padding mask.

        Returns:
            - output: ``[batch, seq_len, d_model]``
            - aux_loss: scalar
        """
        # Self-attention sub-layer
        normed = self.attn_norm(x)
        attn_out, _ = self.attention(normed, normed, normed, attn_mask=attention_mask)
        x = x + attn_out

        # MoE sub-layer
        moe_out, aux_loss = self.moe(x)

        return moe_out, aux_loss
