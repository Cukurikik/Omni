import torch
import numpy as np

# OMNI MOTHER: PiKV - KV Cache Management System for Mixture of Experts
# Implements memory-efficient dynamic KV cache allocation for MoE decoding

class OmniPiKVManager:
    def __init__(self, max_batch_size: int, max_seq_len: int, num_heads: int, head_dim: int, device: str = 'cuda'):
        self.max_batch_size = max_batch_size
        self.max_seq_len = max_seq_len
        self.num_heads = num_heads
        self.head_dim = head_dim
        self.device = device
        
        # Pre-allocate large KV pool
        self.k_cache = torch.zeros((max_batch_size, max_seq_len, num_heads, head_dim), dtype=torch.float16, device=device)
        self.v_cache = torch.zeros((max_batch_size, max_seq_len, num_heads, head_dim), dtype=torch.float16, device=device)
        
        # Track sequence lengths
        self.seq_lengths = torch.zeros((max_batch_size,), dtype=torch.int32, device=device)

    def allocate(self, batch_idx: int, seq_len: int) -> bool:
        if self.seq_lengths[batch_idx] + seq_len <= self.max_seq_len:
            self.seq_lengths[batch_idx] += seq_len
            return True
        return False

    def free(self, batch_idx: int):
        self.seq_lengths[batch_idx] = 0
        
    def get_cache(self, batch_idx: int):
        seq_len = self.seq_lengths[batch_idx]
        return self.k_cache[batch_idx, :seq_len], self.v_cache[batch_idx, :seq_len]
