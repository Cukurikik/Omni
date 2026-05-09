"""
omni_speculative_decode.py — Speculative Decoding Engine
Layer: Compute / AI
Inspired by: pytorch/gpt-fast

Implements Speculative Decoding, which uses a smaller, faster "draft" model 
to predict K tokens in advance, then verifies them with a single forward pass 
of the large "target" model. Massively speeds up autoregressive generation. Zero mock.
"""

import torch
import torch.nn as nn

class OmniSpeculativeDecoder:
    def __init__(self, target_model: nn.Module, draft_model: nn.Module, gamma: int = 4):
        """
        gamma: Number of tokens the draft model predicts ahead per step.
        """
        self.target_model = target_model
        self.draft_model = draft_model
        self.gamma = gamma

    def sample_token(self, logits: torch.Tensor, temperature: float = 1.0) -> torch.Tensor:
        if temperature == 0.0:
            return torch.argmax(logits, dim=-1, keepdim=True)
        probs = torch.softmax(logits / temperature, dim=-1)
        return torch.multinomial(probs, num_samples=1)

    @torch.no_grad()
    def generate(self, input_ids: torch.Tensor, max_new_tokens: int, temperature: float = 0.0) -> torch.Tensor:
        """
        input_ids: (Batch=1, SeqLen)
        """
        generated = input_ids
        
        while generated.shape[1] < input_ids.shape[1] + max_new_tokens:
            # --- DRAFT PHASE ---
            draft_ids = generated
            for _ in range(self.gamma):
                draft_logits = self.draft_model(draft_ids) # (1, Seq, Vocab)
                next_draft_logit = draft_logits[:, -1, :]
                next_draft_token = self.sample_token(next_draft_logit, temperature)
                draft_ids = torch.cat([draft_ids, next_draft_token], dim=1)
                
            # The drafted tokens we proposed (excluding original generated)
            proposed_tokens = draft_ids[:, generated.shape[1]:]

            # --- VERIFICATION PHASE ---
            # Run the target model on the draft sequence in parallel (1 pass!)
            target_logits = self.target_model(draft_ids) # (1, Seq, Vocab)
            
            # Extract logits corresponding to the proposed tokens
            # target_logits is shifted by 1 relative to input ids for next-token prediction
            verif_logits = target_logits[:, generated.shape[1]-1 : generated.shape[1]-1+self.gamma, :]

            # --- ACCEPT/REJECT LOGIC ---
            n_accepted = 0
            for i in range(self.gamma):
                target_token = self.sample_token(verif_logits[:, i, :], temperature)
                if target_token.item() == proposed_tokens[:, i].item():
                    n_accepted += 1
                else:
                    # Mismatch found. Reject this and all subsequent draft tokens.
                    # Append the correct target token.
                    generated = torch.cat([generated, proposed_tokens[:, :i], target_token], dim=1)
                    break
            else:
                # All drafted tokens were accepted! We still need to append the final token
                # predicted by the target model at the end of the draft sequence.
                final_target_token = self.sample_token(target_logits[:, -1, :], temperature)
                generated = torch.cat([generated, proposed_tokens, final_target_token], dim=1)
                
        return generated[:, :input_ids.shape[1] + max_new_tokens]
