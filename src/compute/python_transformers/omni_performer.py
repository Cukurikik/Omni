"""OMNI Compute — Performer (FAVOR+ Attention)"""
import logging
import math
import random
from typing import List

logger = logging.getLogger("omni.performer")

class PerformerAttention:
    """
    Performer: Fast Attention Via Positive Orthogonal Random Features (FAVOR+).
    Approximates softmax attention using random Fourier features.
    """
    def __init__(self, d_model: int, num_features: int = 256):
        self.d_model = d_model
        self.num_features = num_features
        # Generate random orthogonal matrix (simulated)
        self.random_matrix = [[random.gauss(0, 1) for _ in range(d_model)] for _ in range(num_features)]
        logger.info(f"Initialized Performer FAVOR+ Attention (features={num_features})")

    def _phi(self, x: List[float]) -> List[float]:
        """Random feature mapping phi(x)."""
        features = []
        for r_vec in self.random_matrix:
            dot = sum(x[d] * r_vec[d] for d in range(self.d_model))
            # ReLU-based positive random feature (FAVOR+)
            features.append(max(0.0, dot))
        return features

    def forward(self, queries: List[List[float]], keys: List[List[float]], values: List[List[float]]) -> List[List[float]]:
        """FAVOR+ Linear Attention forward pass."""
        seq_len = len(queries)
        if seq_len == 0: return []
        
        # 1. Map Q and K using phi
        q_prime = [self._phi(q) for q in queries]
        k_prime = [self._phi(k) for k in keys]
        
        # 2. Compute K^T * V  (shape: num_features x d_model)
        kv_sum = [[0.0]*self.d_model for _ in range(self.num_features)]
        for i in range(seq_len):
            for f in range(self.num_features):
                for d in range(self.d_model):
                    kv_sum[f][d] += k_prime[i][f] * values[i][d]
                    
        # 3. Compute Denominator K^T * 1
        k_sum = [0.0]*self.num_features
        for i in range(seq_len):
            for f in range(self.num_features):
                k_sum[f] += k_prime[i][f]
                
        # 4. Compute Q * (K^T * V) / Q * (K^T * 1)
        output = []
        for i in range(seq_len):
            num = [0.0]*self.d_model
            den = 0.0
            
            for f in range(self.num_features):
                den += q_prime[i][f] * k_sum[f]
                for d in range(self.d_model):
                    num[d] += q_prime[i][f] * kv_sum[f][d]
                    
            if den > 0:
                output.append([n / den for n in num])
            else:
                output.append([0.0]*self.d_model)
                
        return output
