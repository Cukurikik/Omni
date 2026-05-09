"""OMNI Compute — DeBERTa (Disentangled Attention)"""
import logging
import math
from typing import List

logger = logging.getLogger("omni.deberta")

class DeBERTaAttention:
    """
    DeBERTa: Decoding-enhanced BERT with Disentangled Attention.
    Represents each word using two vectors: content and position.
    """
    def __init__(self, seq_len: int, d_model: int = 512):
        self.seq_len = seq_len
        self.d_model = d_model
        # Simulated relative position embeddings
        self.rel_pos_emb = [[0.01 * (i - j) for _ in range(d_model)] for i in range(seq_len) for j in range(seq_len)]
        logger.info("Initialized DeBERTa Disentangled Attention")

    def forward(self, content_states: List[List[float]]) -> List[List[float]]:
        """Computes content-to-content and content-to-position attention."""
        output = [[0.0]*self.d_model for _ in range(self.seq_len)]
        
        for i in range(self.seq_len):
            context = [0.0]*self.d_model
            weight_sum = 0.0
            
            for j in range(self.seq_len):
                # Content-to-Content
                c2c = sum(content_states[i][d] * content_states[j][d] for d in range(self.d_model))
                
                # Content-to-Position
                pos_idx = i * self.seq_len + j
                c2p = sum(content_states[i][d] * self.rel_pos_emb[pos_idx][d] for d in range(self.d_model))
                
                # Position-to-Content
                p2c = sum(self.rel_pos_emb[pos_idx][d] * content_states[j][d] for d in range(self.d_model))
                
                score = c2c + c2p + p2c
                w = math.exp(min(score / math.sqrt(self.d_model * 3), 20.0))
                
                weight_sum += w
                for d in range(self.d_model):
                    context[d] += w * content_states[j][d]
                    
            if weight_sum > 0:
                output[i] = [c / weight_sum for c in context]
                
        return output
