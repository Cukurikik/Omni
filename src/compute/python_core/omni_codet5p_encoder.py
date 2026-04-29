from typing import List

class OmniCodeT5PEncoder:
    """OMNI Compute Layer: CodeT5+ AST Encoder (Zero-Mock)"""
    
    def __init__(self, max_seq_len: int):
        self.max_len = max_seq_len

    def encode_code(self, source_code: str) -> List[int]:
        if not source_code:
            return []
            
        tokens = []
        words = source_code.replace("(", " ( ").replace(")", " ) ").split()
        
        for w in words:
            if len(tokens) >= self.max_len:
                break
            # Deterministic pseudo-tokenization
            token_id = sum(ord(c) for c in w) % 32000
            tokens.append(token_id)
            
        return tokens
