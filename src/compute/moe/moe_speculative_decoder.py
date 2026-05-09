"""
moe_speculative_decoder.py — Speculative Decoding for MoE Models
Reference: banfeb/nano-vLLM-MS2 (MoE + Speculative Decoding)
Layer: Compute / AI — MoE Inference Optimization

Speculative decoding uses a small draft model to generate candidate
tokens, then verifies them in parallel with the large MoE target model.
Accepted tokens skip individual forward passes, yielding 2-3x speedup.
"""
import torch
import torch.nn as nn
import torch.nn.functional as F
from typing import Optional, Tuple, List
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)


@dataclass
class SpecDecodeConfig:
    max_draft_tokens: int = 5
    temperature: float = 1.0
    top_p: float = 0.9
    top_k: int = 50
    verify_temperature: float = 1.0


class DraftModel(nn.Module):
    """Lightweight draft model for token proposal.

    Uses a small dense transformer (no MoE) as the draft model.
    The draft model should be ~10x smaller than the target MoE model
    but share the same vocabulary and tokenizer.
    """
    def __init__(self, vocab_size, dim=256, num_layers=4, num_heads=4):
        super().__init__()
        self.embed = nn.Embedding(vocab_size, dim)
        layer = nn.TransformerEncoderLayer(
            d_model=dim, nhead=num_heads, dim_feedforward=dim * 4,
            batch_first=True, norm_first=True)
        self.transformer = nn.TransformerEncoder(layer, num_layers=num_layers)
        self.norm = nn.LayerNorm(dim)
        self.lm_head = nn.Linear(dim, vocab_size, bias=False)

    def forward(self, input_ids):
        S = input_ids.shape[1]
        causal_mask = nn.Transformer.generate_square_subsequent_mask(
            S, device=input_ids.device)
        x = self.embed(input_ids)
        x = self.transformer(x, mask=causal_mask, is_causal=True)
        return self.lm_head(self.norm(x))


def _sample_token(logits, temperature=1.0, top_k=50, top_p=0.9):
    """Sample a token from logits with temperature, top-k, and top-p."""
    if temperature <= 0:
        return logits.argmax(dim=-1)

    logits = logits / temperature

    # Top-k filtering
    if top_k > 0:
        top_k = min(top_k, logits.shape[-1])
        threshold = torch.topk(logits, top_k, dim=-1).values[..., -1:]
        logits = logits.masked_fill(logits < threshold, float("-inf"))

    # Top-p (nucleus) filtering
    if 0 < top_p < 1.0:
        sorted_logits, sorted_idx = torch.sort(logits, descending=True, dim=-1)
        cum_probs = torch.cumsum(F.softmax(sorted_logits, dim=-1), dim=-1)
        mask = cum_probs - F.softmax(sorted_logits, dim=-1) > top_p
        sorted_logits[mask] = float("-inf")
        logits = sorted_logits.scatter(-1, sorted_idx, sorted_logits)

    probs = F.softmax(logits, dim=-1)
    return torch.multinomial(probs.view(-1, probs.shape[-1]), 1).view(probs.shape[:-1])


class MoESpeculativeDecoder:
    """Speculative decoding engine for MoE target models.

    Algorithm:
    1. Draft model generates K candidate tokens autoregressively
    2. Target MoE model verifies all K tokens in a single forward pass
    3. Accept tokens where target agrees with draft (adjusted by acceptance prob)
    4. Resample from target distribution at first rejection point
    """
    def __init__(self, target_model, draft_model, config: SpecDecodeConfig):
        self.target = target_model
        self.draft = draft_model
        self.config = config
        self.device = next(target_model.parameters()).device

        self.stats = {"total_draft": 0, "accepted": 0, "calls": 0}

    @torch.no_grad()
    def generate(
        self,
        input_ids: torch.Tensor,
        max_new_tokens: int = 128,
        eos_token_id: Optional[int] = None,
    ) -> torch.Tensor:
        """Generate tokens using speculative decoding."""
        generated = input_ids.clone()

        tokens_generated = 0
        while tokens_generated < max_new_tokens:
            remaining = max_new_tokens - tokens_generated
            draft_len = min(self.config.max_draft_tokens, remaining)

            # Step 1: Draft model generates candidate tokens
            draft_tokens, draft_probs = self._draft_generate(generated, draft_len)

            # Step 2: Verify with target model
            accepted, new_token = self._verify(generated, draft_tokens, draft_probs)

            # Step 3: Accept verified tokens
            n_accepted = accepted.shape[1] if accepted.dim() > 1 else 0
            if n_accepted > 0:
                generated = torch.cat([generated, accepted], dim=1)
                tokens_generated += n_accepted
                self.stats["accepted"] += n_accepted

            # Step 4: Append resampled token from target
            if new_token is not None and tokens_generated < max_new_tokens:
                generated = torch.cat([generated, new_token], dim=1)
                tokens_generated += 1

            self.stats["total_draft"] += draft_len
            self.stats["calls"] += 1

            # Check EOS
            if eos_token_id is not None and generated[0, -1].item() == eos_token_id:
                break

        return generated

    def _draft_generate(self, context, num_tokens):
        """Generate candidate tokens with the draft model."""
        draft_ids = context.clone()
        all_probs = []

        for _ in range(num_tokens):
            logits = self.draft(draft_ids)[:, -1]
            probs = F.softmax(logits / max(self.config.temperature, 1e-8), dim=-1)
            next_token = _sample_token(
                logits, self.config.temperature,
                self.config.top_k, self.config.top_p)
            all_probs.append(probs)
            draft_ids = torch.cat([draft_ids, next_token.unsqueeze(-1)], dim=1)

        # Return only the new tokens and their probabilities
        new_tokens = draft_ids[:, context.shape[1]:]
        stacked_probs = torch.stack(all_probs, dim=1)
        return new_tokens, stacked_probs

    def _verify(self, context, draft_tokens, draft_probs):
        """Verify draft tokens against target model."""
        B = context.shape[0]
        K = draft_tokens.shape[1]

        # Single forward pass through target with all draft tokens
        full_input = torch.cat([context, draft_tokens], dim=1)
        target_output = self.target(full_input)
        target_logits = target_output["logits"] if isinstance(target_output, dict) \
            else target_output

        # Extract target probabilities at draft positions
        start_pos = context.shape[1] - 1  # -1 because logits are shifted
        target_probs_at_draft = F.softmax(
            target_logits[:, start_pos:start_pos + K] /
            max(self.config.verify_temperature, 1e-8), dim=-1)

        # Acceptance criterion: accept if p_target(x) / p_draft(x) >= uniform
        accepted_tokens = []
        n_accepted = 0

        for i in range(K):
            token = draft_tokens[:, i]
            p_target = target_probs_at_draft[:, i].gather(1, token.unsqueeze(-1)).squeeze(-1)
            p_draft = draft_probs[:, i].gather(1, token.unsqueeze(-1)).squeeze(-1)

            # Acceptance probability
            accept_prob = (p_target / p_draft.clamp(min=1e-8)).clamp(max=1.0)
            uniform = torch.rand_like(accept_prob)

            if (uniform < accept_prob).all():
                accepted_tokens.append(token.unsqueeze(1))
                n_accepted += 1
            else:
                break

        # Accepted tokens
        if accepted_tokens:
            accepted = torch.cat(accepted_tokens, dim=1)
        else:
            accepted = torch.empty(B, 0, dtype=torch.long, device=context.device)

        # Resample from adjusted target distribution at rejection point
        resample_pos = start_pos + n_accepted
        if resample_pos < target_logits.shape[1]:
            resample_logits = target_logits[:, resample_pos]
            if n_accepted < K:
                # Adjust distribution: max(0, p_target - p_draft)
                target_p = F.softmax(resample_logits / max(self.config.verify_temperature, 1e-8), dim=-1)
                draft_p = draft_probs[:, n_accepted] if n_accepted < draft_probs.shape[1] \
                    else torch.zeros_like(target_p)
                adjusted = (target_p - draft_p).clamp(min=0)
                adjusted = adjusted / adjusted.sum(dim=-1, keepdim=True).clamp(min=1e-8)
                new_token = torch.multinomial(adjusted, 1)
            else:
                new_token = _sample_token(
                    resample_logits, self.config.temperature,
                    self.config.top_k, self.config.top_p).unsqueeze(-1)
        else:
            new_token = None

        return accepted, new_token

    def get_stats(self):
        """Return speculative decoding performance statistics."""
        calls = max(self.stats["calls"], 1)
        return {
            "acceptance_rate": self.stats["accepted"] / max(self.stats["total_draft"], 1),
            "avg_accepted_per_call": self.stats["accepted"] / calls,
            "total_target_calls": calls,
            "speedup_estimate": (self.stats["accepted"] + calls) / calls,
        }
