"""
OMNI Transformer — Speculative Decoding
Speed up autoregressive generation using draft model verification.
Learned from: speculative decoding research, DeepMind/Google patterns
"""
import torch
import torch.nn.functional as F
from typing import Optional, Tuple, Dict
import logging

logger = logging.getLogger(__name__)


class SpeculativeDecoder:
    """Production speculative decoding for faster LLM inference."""
    def __init__(self, target_model, draft_model, num_speculative_tokens: int = 5):
        self.target = target_model
        self.draft = draft_model
        self.K = num_speculative_tokens
        self.device = next(target_model.parameters()).device
        self.target.eval()
        self.draft.eval()
        self.stats = {"accepted": 0, "rejected": 0, "total": 0}

    @torch.inference_mode()
    def generate(self, input_ids: torch.Tensor, max_new_tokens: int = 256,
                 temperature: float = 1.0, eos_token_id: Optional[int] = None) -> torch.Tensor:
        generated = input_ids.clone()

        tokens_generated = 0
        while tokens_generated < max_new_tokens:
            # Step 1: Draft K tokens
            draft_tokens, draft_probs = self._draft_tokens(generated, temperature)

            # Step 2: Verify with target model (single forward pass for K+1 positions)
            candidate = torch.cat([generated, draft_tokens], dim=1)
            target_output = self.target(candidate)
            target_logits = target_output["logits"] if isinstance(target_output, dict) else target_output

            # Get target probabilities at draft positions
            start_pos = generated.size(1) - 1
            target_probs = F.softmax(target_logits[:, start_pos:start_pos + self.K] / temperature, dim=-1)

            # Step 3: Accept/reject each draft token
            n_accepted = 0
            for i in range(self.K):
                draft_token = draft_tokens[:, i]
                p_target = target_probs[:, i]
                p_draft = draft_probs[:, i]

                # Acceptance probability: min(1, p_target / p_draft)
                draft_prob = torch.gather(p_draft, 1, draft_token.unsqueeze(1)).squeeze(1)
                target_prob = torch.gather(p_target, 1, draft_token.unsqueeze(1)).squeeze(1)

                accept_ratio = target_prob / (draft_prob + 1e-10)
                accept = torch.rand_like(accept_ratio) < accept_ratio

                if accept.all():
                    n_accepted += 1
                    self.stats["accepted"] += 1
                else:
                    # Resample from adjusted distribution
                    adjusted = F.relu(p_target[:, :] - p_draft[:, :])
                    adjusted = adjusted / (adjusted.sum(dim=-1, keepdim=True) + 1e-10)
                    new_token = torch.multinomial(adjusted.squeeze(0) if adjusted.dim() > 1 else adjusted, 1)
                    generated = torch.cat([generated, draft_tokens[:, :i], new_token.view(1, 1)], dim=1)
                    tokens_generated += i + 1
                    self.stats["rejected"] += 1
                    break
            else:
                # All K tokens accepted, sample one more from target
                bonus_probs = F.softmax(target_logits[:, start_pos + self.K] / temperature, dim=-1)
                bonus_token = torch.multinomial(bonus_probs, 1)
                generated = torch.cat([generated, draft_tokens, bonus_token], dim=1)
                tokens_generated += self.K + 1

            self.stats["total"] += 1

            if eos_token_id is not None and generated[0, -1].item() == eos_token_id:
                break

        return generated

    def _draft_tokens(self, prefix: torch.Tensor, temperature: float) -> Tuple[torch.Tensor, torch.Tensor]:
        draft_tokens = []
        draft_probs = []
        current = prefix.clone()

        for _ in range(self.K):
            output = self.draft(current)
            logits = output["logits"][:, -1:] if isinstance(output, dict) else output[:, -1:]
            probs = F.softmax(logits.squeeze(1) / temperature, dim=-1)
            token = torch.multinomial(probs, 1)
            draft_tokens.append(token)
            draft_probs.append(probs.unsqueeze(1))
            current = torch.cat([current, token], dim=1)

        return torch.cat(draft_tokens, dim=1), torch.cat(draft_probs, dim=1)

    @property
    def acceptance_rate(self) -> float:
        total = self.stats["accepted"] + self.stats["rejected"]
        return self.stats["accepted"] / total if total > 0 else 0.0
