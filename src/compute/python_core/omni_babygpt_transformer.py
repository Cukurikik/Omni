from typing import List

class OmniBabyGPTTransformer:
    """OMNI Compute Layer: BabyGPT Generative Transformer"""
    
    def __init__(self, vocab_size: int = 1000):
        self.vocab_size = vocab_size

    def generate_tokens(self, prompt_tokens: List[int], max_new: int) -> List[int]:
        if not prompt_tokens:
            return []
            
        # Deterministic pseudo-generation
        output = list(prompt_tokens)
        current = sum(prompt_tokens)
        
        for _ in range(max_new):
            current = (current * 17 + 31) % self.vocab_size
            output.append(current)
            
        return output
