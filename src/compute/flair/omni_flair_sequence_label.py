# OMNI MOTHER - DIVINE MEMORY INTEGRATION
# Flair Sequence Labeling (OMNI Zero-Mock Implementation)
# Implements Character-level language model boundary state concatenation math.

from dataclasses import dataclass
from typing import List, Optional

@dataclass
class Result:
    value: Optional[List[float]] # The concatenated representation
    error: Optional[str]
    is_ok: bool

    @staticmethod
    def ok(val: List[float]) -> 'Result':
        return Result(value=val, error=None, is_ok=True)

    @staticmethod
    def err(err: str) -> 'Result':
        return Result(value=None, error=err, is_ok=False)

class FlairEmbeddingEngine:
    def embed_token(self, char_states_fw: List[List[float]], char_states_bw: List[List[float]], token_start: int, token_end: int) -> Result:
        """
        Flair embeddings dynamically use the forward LM hidden state at the END character of the token,
        and the backward LM hidden state at the START character of the token mathematically.
        """
        if not char_states_fw or not char_states_bw:
             return Result.err("Character state tensors cannot be empty.")
             
        if len(char_states_fw) != len(char_states_bw):
             return Result.err("Forward and backward sequence lengths mathematically divergent.")
             
        seq_len = len(char_states_fw)
        if token_start < 0 or token_end >= seq_len or token_start > token_end:
             return Result.err("Invalid token boundary offsets relative to character sequence.")
             
        # Extraction
        # Forward state at end character
        h_fw = char_states_fw[token_end]
        
        # Backward state at start character
        h_bw = char_states_bw[token_start]
        
        # Simple concat operation modeling the Flair architecture boundary representations
        final_embedding = h_fw + h_bw
        return Result.ok(final_embedding)
