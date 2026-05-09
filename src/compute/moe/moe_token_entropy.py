"""
moe_token_entropy.py — Compute / Observability
Layer: Compute / AI — Hallucination Detection via Entropy

Analyzes the output probability distribution from the MoE experts.
If the expert outputs a token with extremely high entropy (a flat probability 
distribution where it's guessing among many words), this module flags the 
output as a probable hallucination.
"""

import torch
import torch.nn.functional as F

class TokenEntropyAnalyzer:
    def __init__(self, entropy_threshold: float = 2.5):
        self.entropy_threshold = entropy_threshold
        print(f"[Entropy Monitor] Initialized Hallucination Detector (Threshold: {entropy_threshold})")

    def calculate_entropy(self, logits: torch.Tensor) -> torch.Tensor:
        """
        Calculates Shannon Entropy given raw logits.
        logits: (Batch, VocabSize)
        Returns: (Batch,)
        """
        # Convert logits to probabilities
        probs = F.softmax(logits, dim=-1)
        
        # Calculate entropy: -sum(p * log(p))
        # Add epsilon to prevent log(0)
        log_probs = torch.log(probs + 1e-9)
        entropy = -torch.sum(probs * log_probs, dim=-1)
        
        return entropy

    def analyze_generation_step(self, step_logits: torch.Tensor, expert_id: int):
        """
        Analyzes the logits produced by a specific expert for a single token generation step.
        """
        entropies = self.calculate_entropy(step_logits)
        
        # Check for hallucinations across the batch
        for i, ent in enumerate(entropies):
            if ent.item() > self.entropy_threshold:
                print(f"[Entropy Alert] High Entropy detected on Batch {i} by Expert {expert_id}! "
                      f"(Entropy: {ent.item():.3f}). Potential Hallucination!")
                
        return entropies.mean().item()

# Usage:
# analyzer = TokenEntropyAnalyzer()
# logits = expert(hidden_states) # (1, 32000)
# analyzer.analyze_generation_step(logits, expert_id=4)
