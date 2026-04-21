"""
OMNI Xlnet Engine
=================
Production-grade engine for the OMNI Framework.

OMNI Layer: compute (Python)
"""
import numpy as np
from typing import Dict, Any, List

class Result:
    """Monadic result pattern."""
    def __init__(self, value=None, error=None):
        """Initialize Result."""
        self.value = value
        self.error = error
        self.is_ok = error is None

    def unwrap(self):
        """Unwrap the value or raise on error."""
        if not self.is_ok:
            raise RuntimeError(self.error)
        return self.value

class OmniXlnetEngine:
    """
    omni-xlnet
    
    A zero-mock native engine simulating Permutation Language Modeling (PLM) architectures.
    Implements a strict Two-Stream Self-Attention abstraction projecting Query and Content 
    streams over factorized random permutation masks natively in NumPy.
    """
    
    ENGINE_VERSION = "omni-s6-b8.1.0"
    
    def __init__(self, d_model: int = 128, n_heads: int = 4):
        """Initialize OmniXlnetEngine."""
        self.d_model = d_model
        self.n_heads = n_heads
        self.d_head = d_model // n_heads
        
        np.random.seed(42)
        # Content Stream Weights
        self.W_q_c = np.random.randn(d_model, d_model).astype(np.float32) / np.sqrt(d_model)
        self.W_k_c = np.random.randn(d_model, d_model).astype(np.float32) / np.sqrt(d_model)
        self.W_v_c = np.random.randn(d_model, d_model).astype(np.float32) / np.sqrt(d_model)
        
        # Query Stream Weights
        self.W_q_g = np.random.randn(d_model, d_model).astype(np.float32) / np.sqrt(d_model)

    def _softmax(self, x: np.ndarray, axis: int = -1) -> np.ndarray:
        x_max = np.max(x, axis=axis, keepdims=True)
        exp_x = np.exp(x - x_max)
        return exp_x / np.sum(exp_x, axis=axis, keepdims=True)

    def _generate_plm_mask(self, seq_len: int) -> np.ndarray:
        """
        Generates a casual PLM mask based on a random factorization order.
        Returns a boolean mask: mask[i, j] is True if seq[i] can see seq[j].
        """
        permutation = np.random.permutation(seq_len)
        mask = np.zeros((seq_len, seq_len), dtype=bool)
        
        for i in range(seq_len):
            # i-th element in sequence. Its factorization index is rank_i
            rank_i = np.where(permutation == i)[0][0]
            for j in range(seq_len):
                rank_j = np.where(permutation == j)[0][0]
                # Can see if it appeared before in the permutation order
                # Content stream can see itself
                if rank_j <= rank_i:
                    mask[i, j] = True
                    
        return mask

    def forward_two_stream_attention(self, content_seq: np.ndarray, query_seq: np.ndarray) -> Result:
        """
        Executes a single structural step of XLNet Two-Stream Self-Attention.
        content_seq: (seq_len, d_model) - Initialized with token embeddings.
        query_seq: (seq_len, d_model) - Initialized with trainable positional/target vectors.
        """
        try:
            seq_len, dm = content_seq.shape
            if dm != self.d_model:
                return Result(error=f"Expected d_model {self.d_model}.")
                
            # Generate Autoregressive Permutation Mask
            plm_mask_content = self._generate_plm_mask(seq_len)
            
            # Query mask: query stream cannot see its own content token (to predict it)
            plm_mask_query = plm_mask_content.copy()
            np.fill_diagonal(plm_mask_query, False)
            
            # 1. Content Stream Attention
            # Q_C = C * W_q_c
            Q_C = np.dot(content_seq, self.W_q_c)
            # K_C = C * W_k_c
            K_C = np.dot(content_seq, self.W_k_c)
            # V_C = C * W_v_c
            V_C = np.dot(content_seq, self.W_v_c)
            
            # Attention scores: Q_C x K_C^T
            scores_C = np.dot(Q_C, K_C.T) / np.sqrt(self.d_head)
            # Apply Mask: -inf where mask is False
            scores_C = np.where(plm_mask_content, scores_C, -1e9)
            attn_weights_C = self._softmax(scores_C, axis=-1)
            
            # New Content Stream = attn * V_C
            content_out = np.dot(attn_weights_C, V_C)
            
            # 2. Query Stream Attention
            # Q_G = G * W_q_g (G represents query stream sequence)
            Q_G = np.dot(query_seq, self.W_q_g)
            
            # Query stream uses Content stream's Keys and Values for context calculation
            scores_G = np.dot(Q_G, K_C.T) / np.sqrt(self.d_head)
            scores_G = np.where(plm_mask_query, scores_G, -1e9)
            attn_weights_G = self._softmax(scores_G, axis=-1)
            
            # New Query Stream
            query_out = np.dot(attn_weights_G, V_C)
            
            return Result(value={
                "content_output": content_out,
                "query_output": query_out,
                "plm_mask": plm_mask_content
            })
            
        except Exception as e:
            return Result(error=f"Two-Stream Attention error: {str(e)}")

    def diagnostics(self) -> Dict[str, Any]:
        """OMNI Registry compliance."""
        return {
            "engine": "OmniXlnetEngine",
            "version": self.ENGINE_VERSION,
            "status": "operational",
            "mechanisms": ["Permutation Mask Generation", "Two-Stream Auto-regressive Attention"]
        }
