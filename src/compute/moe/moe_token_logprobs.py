"""
moe_token_logprobs.py — Compute / Inference
Layer: Compute / AI — Log-Probability Extractor

Advanced API clients (like OpenAI's API) allow users to request the `logprobs`
of the top-K alternative tokens for each generated token. This module extracts 
those probabilities directly from the final MoE language modeling head.
"""

import torch
import torch.nn.functional as F
from typing import List, Dict

class LogprobExtractor:
    def __init__(self, top_k: int = 5):
        self.top_k = top_k
        print(f"[Logprobs] Extractor initialized (Tracking Top-{top_k} alternative tokens)")

    def extract(self, logits: torch.Tensor, tokenizer) -> List[Dict]:
        """
        logits: (Batch=1, SeqLen=1, VocabSize)
        tokenizer: object with a `.decode(id)` method
        
        Returns a structured dictionary of the chosen token and its top alternatives.
        """
        # Squeeze batch and seq dims assuming streaming token-by-token generation
        logits_1d = logits.squeeze() 
        
        # Calculate log probabilities
        logprobs = F.log_softmax(logits_1d, dim=-1)
        
        # Get the highest probability tokens
        top_logprobs, top_indices = torch.topk(logprobs, self.top_k)
        
        results = []
        for i in range(self.top_k):
            token_id = top_indices[i].item()
            lprob = top_logprobs[i].item()
            
            # Decode token ID to string
            try:
                # E.g. [1234] -> " Apple"
                token_str = tokenizer.decode([token_id]) 
            except Exception:
                token_str = "<UNK>"
                
            results.append({
                "token": token_str,
                "token_id": token_id,
                "logprob": round(lprob, 4),
                "prob_percent": round(torch.exp(top_logprobs[i]).item() * 100, 2)
            })
            
        return results

# Example Usage:
# extractor = LogprobExtractor(top_k=3)
# token_stats = extractor.extract(model_logits, my_rust_tokenizer)
# print(token_stats[0]) # -> {'token': ' hello', 'token_id': 45, 'logprob': -0.012, 'prob_percent': 98.8}
