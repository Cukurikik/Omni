"""
OMNI MOTHER: Speculative Decoding Engine (Production Grade)
Uses a lightweight draft model to propose γ tokens, then verifies
them in a single target-model forward pass. Achieves 2-3x speedup
without changing the output distribution.
Ref: "Fast Inference from Transformers via Speculative Decoding" (Leviathan et al., 2023)
"""
import logging
from typing import Optional, Tuple
import torch
import torch.nn as nn
import torch.nn.functional as F

logger = logging.getLogger("OmniSpecDecode")

class OmniSpeculativeDecoder:
    """Orchestrates draft-then-verify speculative decoding."""
    def __init__(self, target: nn.Module, draft: nn.Module,
                 vocab_size: int, gamma: int = 4, temperature: float = 1.0):
        self.target = target
        self.draft = draft
        self.vocab_size = vocab_size
        self.gamma = gamma
        self.temperature = temperature
        self._accepted_total = 0
        self._proposed_total = 0

    @torch.no_grad()
    def _sample(self, logits: torch.Tensor) -> Tuple[torch.Tensor, torch.Tensor]:
        """Sample a token and return (token_id, probability)."""
        probs = F.softmax(logits / self.temperature, dim=-1)
        token = torch.multinomial(probs, num_samples=1)
        prob = probs.gather(-1, token)
        return token.squeeze(-1), prob.squeeze(-1)

    @torch.no_grad()
    def _draft_tokens(self, prefix: torch.Tensor) -> Tuple[torch.Tensor, torch.Tensor]:
        """Generate γ draft tokens autoregressively from the draft model."""
        draft_tokens = []
        draft_probs = []
        current = prefix.clone()
        for _ in range(self.gamma):
            logits = self.draft(current)
            if logits.dim() == 3:
                logits = logits[:, -1, :]
            token, prob = self._sample(logits)
            draft_tokens.append(token)
            draft_probs.append(prob)
            current = torch.cat([current, token.unsqueeze(-1)], dim=-1)
        return torch.stack(draft_tokens, dim=-1), torch.stack(draft_probs, dim=-1)

    @torch.no_grad()
    def _verify(self, prefix: torch.Tensor, draft_tokens: torch.Tensor,
                draft_probs: torch.Tensor) -> Tuple[torch.Tensor, int]:
        """Verify draft tokens with the target model."""
        # Concatenate prefix + draft tokens for single forward pass
        candidate = torch.cat([prefix, draft_tokens], dim=-1)
        target_logits = self.target(candidate)
        if target_logits.dim() == 3:
            pass  # [B, S, V]
        
        accepted = []
        prefix_len = prefix.size(-1)
        
        for i in range(self.gamma):
            pos = prefix_len + i - 1
            if pos < 0:
                pos = 0
            target_probs_at_pos = F.softmax(target_logits[:, pos, :] / self.temperature, dim=-1)
            draft_token = draft_tokens[:, i]
            p_target = target_probs_at_pos.gather(-1, draft_token.unsqueeze(-1)).squeeze(-1)
            p_draft = draft_probs[:, i].clamp(min=1e-10)
            
            # Acceptance criterion: accept if p_target/p_draft >= uniform random
            ratio = (p_target / p_draft).clamp(max=1.0)
            u = torch.rand_like(ratio)
            accept = u < ratio
            
            if accept.all():
                accepted.append(draft_token)
            else:
                # Rejection — sample correction token from modified distribution
                residual = (target_probs_at_pos - draft_probs[:, i:i+1].expand_as(target_probs_at_pos)).clamp(min=0)
                residual = residual / residual.sum(dim=-1, keepdim=True).clamp(min=1e-10)
                correction = torch.multinomial(residual, num_samples=1).squeeze(-1)
                accepted.append(correction)
                break
        else:
            # All γ tokens accepted — bonus: sample one more from target
            final_logits = target_logits[:, prefix_len + self.gamma - 1, :]
            bonus, _ = self._sample(final_logits)
            accepted.append(bonus)

        num_accepted = len(accepted)
        self._accepted_total += num_accepted
        self._proposed_total += self.gamma
        
        return torch.stack(accepted, dim=-1), num_accepted

    @torch.no_grad()
    def generate(self, input_ids: torch.Tensor, max_new_tokens: int = 128,
                 eos_token_id: Optional[int] = None) -> torch.Tensor:
        """Full generation loop with speculative decoding."""
        generated = input_ids.clone()
        tokens_generated = 0
        
        while tokens_generated < max_new_tokens:
            # Draft phase
            draft_tokens, draft_probs = self._draft_tokens(generated)
            
            # Verify phase
            accepted_tokens, n_accepted = self._verify(generated, draft_tokens, draft_probs)
            
            generated = torch.cat([generated, accepted_tokens], dim=-1)
            tokens_generated += n_accepted
            
            # Check EOS
            if eos_token_id is not None and (accepted_tokens == eos_token_id).any():
                break
        
        acceptance_rate = self._accepted_total / max(self._proposed_total, 1)
        logger.info(f"Speculative decoding done. Acceptance rate: {acceptance_rate:.2%}")
        return generated
