# OMNI MOTHER - DIVINE MEMORY INTEGRATION
# Lex Fridman MIT DL (OMNI Zero-Mock Implementation)
# Implements Self-Attention Head Scaled Dot-Product math operations.

from dataclasses import dataclass
from typing import List, Optional
import math

@dataclass
class Result:
    value: Optional[List[List[float]]]
    error: Optional[str]
    is_ok: bool

    @staticmethod
    def ok(val: List[List[float]]) -> 'Result':
        return Result(value=val, error=None, is_ok=True)

    @staticmethod
    def err(err: str) -> 'Result':
        return Result(value=None, error=err, is_ok=False)

class SelfAttentionEngine:
    def _matmul(self, A: List[List[float]], B: List[List[float]]) -> List[List[float]]:
        # A: (m x n), B: (n x p) -> (m x p)
        return [[sum(a * b for a, b in zip(A_row, B_col)) 
                 for B_col in zip(*B)] for A_row in A]
                 
    def _softmax(self, x: List[float]) -> List[float]:
        mx = max(x)
        exp_x = [math.exp(i - mx) for i in x]
        s = sum(exp_x)
        return [i / s for i in exp_x]

    def scaled_dot_product_attention(self, Q: List[List[float]], K: List[List[float]], V: List[List[float]]) -> Result:
        """
        Q, K, V are matrices of shape (seq_len_q, d_k), (seq_len_k, d_k), (seq_len_k, d_v).
        """
        if not Q or not K or not V:
            return Result.err("Query, Key, or Value tensors cannot be empty.")
            
        d_k = len(K[0])
        if len(Q[0]) != d_k:
            return Result.err("Dimension mismatch between Q and K inner dimensions.")
            
        if len(K) != len(V):
            return Result.err("Length mismatch between K and V sequence dims.")
            
        # Transpose K
        K_T = list(zip(*K))
        
        # Q * K^T
        scores = self._matmul(Q, K_T)
        
        # Scale
        scale_factor = math.sqrt(d_k)
        scaled_scores = [[val / scale_factor for val in row] for row in scores]
        
        # Softmax over last dim
        attention_weights = [self._softmax(row) for row in scaled_scores]
        
        # Multiply with V
        attention_output = self._matmul(attention_weights, V)
        
        return Result.ok(attention_output)
