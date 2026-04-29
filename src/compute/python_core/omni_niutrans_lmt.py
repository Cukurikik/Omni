from typing import List

class OmniNiuTransLMT:
    """OMNI Compute Layer: NiuTrans Language Model Translation"""
    
    def __init__(self, vocab_size: int = 32000):
        self.vocab = vocab_size

    def decode_translation(self, token_probs: List[List[float]]) -> List[int]:
        if not token_probs:
            return []
            
        # Greedy decoding deterministic logic
        output_tokens = []
        for probs in token_probs:
            if not probs:
                continue
            max_idx = 0
            max_val = probs[0]
            for i, val in enumerate(probs):
                if val > max_val:
                    max_val = val
                    max_idx = i
            output_tokens.append(max_idx)
            
        return output_tokens
