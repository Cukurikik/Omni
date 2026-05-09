"""
omni_ring_attention.py — Ring Attention for Infinite Context
Layer: Compute / AI
Inspired by: haoliuhb/ringattention

Implements Ring Attention, extending context windows exponentially by passing 
Key and Value blocks across a logical GPU ring topology during the attention 
computation, avoiding quadratic memory bottlenecks. Zero mock.
"""

import torch
import torch.nn as nn
import torch.distributed as dist

class OmniRingAttention(nn.Module):
    def __init__(self, process_group=None):
        super().__init__()
        self.process_group = process_group if process_group else dist.group.WORLD
        if dist.is_initialized():
            self.world_size = dist.get_world_size(self.process_group)
            self.rank = dist.get_rank(self.process_group)
            # Define the ring neighbors
            self.next_rank = (self.rank + 1) % self.world_size
            self.prev_rank = (self.rank - 1 + self.world_size) % self.world_size
        else:
            self.world_size = 1
            self.rank = 0
            self.next_rank = 0
            self.prev_rank = 0

    def forward(self, local_q: torch.Tensor, local_k: torch.Tensor, local_v: torch.Tensor) -> torch.Tensor:
        """
        local_q, local_k, local_v: (Batch, NumHeads, LocalSeqLen, HeadDim)
        """
        if self.world_size == 1:
            # Fallback to standard attention
            scores = torch.matmul(local_q, local_k.transpose(-2, -1)) / (local_q.shape[-1] ** 0.5)
            attn = torch.softmax(scores, dim=-1)
            return torch.matmul(attn, local_v)

        # Initialize Ring statistics (FlashAttention style)
        # For simplicity in this native mock-free implementation, we accumulate
        # the unnormalized outputs and the normalization factors.
        d = local_q.shape[-1]
        out = torch.zeros_like(local_q) # (B, H, L_seq, D)
        l = torch.zeros((*local_q.shape[:-1], 1), device=local_q.device) # Denominator
        m = torch.full((*local_q.shape[:-1], 1), float('-inf'), device=local_q.device) # Max

        current_k, current_v = local_k, local_v

        # Circulate K and V blocks around the ring
        for step in range(self.world_size):
            # 1. Compute local attention with current K and V blocks
            # S_ij = Q @ K_j^T
            scores = torch.matmul(local_q, current_k.transpose(-2, -1)) / (d ** 0.5)
            
            # Incremental Softmax update
            m_tilde = torch.max(scores, dim=-1, keepdim=True).values
            m_new = torch.max(m, m_tilde)
            
            # P_ij = exp(S_ij - m_tilde)
            P = torch.exp(scores - m_tilde)
            
            # l_new = exp(m - m_new) * l + exp(m_tilde - m_new) * sum(P)
            l_new = torch.exp(m - m_new) * l + torch.exp(m_tilde - m_new) * torch.sum(P, dim=-1, keepdim=True)
            
            # out_new = diag(l_new)^-1 * (diag(l) * exp(m - m_new) * out + exp(m_tilde - m_new) * P @ V_j)
            out_scaled = torch.exp(m - m_new) * out
            pv_scaled = torch.exp(m_tilde - m_new) * torch.matmul(P, current_v)
            
            out = (out_scaled * l + pv_scaled) / l_new
            
            # Update running stats
            m = m_new
            l = l_new

            # 2. P2P Communication: Send current K, V to next node, receive from prev node
            if step < self.world_size - 1:
                next_k = torch.empty_like(current_k)
                next_v = torch.empty_like(current_v)
                
                # Asynchronous Send/Recv
                req_send_k = dist.isend(current_k, self.next_rank, group=self.process_group, tag=0)
                req_send_v = dist.isend(current_v, self.next_rank, group=self.process_group, tag=1)
                
                req_recv_k = dist.irecv(next_k, self.prev_rank, group=self.process_group, tag=0)
                req_recv_v = dist.irecv(next_v, self.prev_rank, group=self.process_group, tag=1)
                
                req_send_k.wait()
                req_send_v.wait()
                req_recv_k.wait()
                req_recv_v.wait()
                
                current_k, current_v = next_k, next_v

        return out
