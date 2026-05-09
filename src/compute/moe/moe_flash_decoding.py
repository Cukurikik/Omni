"""
moe_flash_decoding.py — Compute / Inference
Layer: Compute / AI — MoE Flash Decoding

Flash Decoding accelerates the auto-regressive generation phase for long contexts.
In MoE, long contexts mean the KV cache is enormous and scattered across experts.
This module splits the KV cache across the sequence dimension, computes attention
in parallel across multiple SMs, and then reduces the results.
"""
import torch

class FlashDecodingAttention:
    """
    Implements the split-K approach for Flash Decoding adapted for MoE.
    """
    def __init__(self, num_splits: int = 4):
        self.num_splits = num_splits

    def forward(
        self, 
        q: torch.Tensor, 
        k_cache: torch.Tensor, 
        v_cache: torch.Tensor, 
        expert_mask: torch.Tensor = None
    ) -> torch.Tensor:
        """
        q: (Batch, 1, NumHeads, HeadDim) - Single query token
        k_cache, v_cache: (Batch, SeqLen, NumHeads, HeadDim)
        expert_mask: Optional boolean mask if KV cache is partitioned by expert
        """
        B, seq_len, H, D = k_cache.shape
        
        # Split KV cache along the sequence dimension
        split_size = seq_len // self.num_splits
        if split_size == 0:
            split_size = seq_len
            actual_splits = 1
        else:
            actual_splits = self.num_splits
            
        # In a real C++/CUDA implementation, these splits are dispatched to different Streaming Multiprocessors
        split_outputs = []
        split_lse = [] # Log-Sum-Exp for final reduction
        
        for i in range(actual_splits):
            start_idx = i * split_size
            end_idx = min((i + 1) * split_size, seq_len)
            
            k_chunk = k_cache[:, start_idx:end_idx, :, :]
            v_chunk = v_cache[:, start_idx:end_idx, :, :]
            
            # 1. Compute chunk attention scores: Q * K^T
            # q shape: (B, H, 1, D)
            # k_chunk shape: (B, H, chunk_len, D)
            q_reshaped = q.transpose(1, 2)
            k_reshaped = k_chunk.transpose(1, 2).transpose(2, 3) # (B, H, D, chunk_len)
            
            scores = torch.matmul(q_reshaped, k_reshaped) / (D ** 0.5) # (B, H, 1, chunk_len)
            
            # 2. Chunk Log-Sum-Exp
            m_i = torch.max(scores, dim=-1, keepdim=True)[0]
            exp_scores = torch.exp(scores - m_i)
            l_i = torch.sum(exp_scores, dim=-1, keepdim=True)
            
            # 3. Chunk Output
            probs = exp_scores / l_i
            out_chunk = torch.matmul(probs, v_chunk.transpose(1, 2)) # (B, H, 1, D)
            
            split_outputs.append(out_chunk)
            split_lse.append(m_i + torch.log(l_i))
            
        # 4. Final Reduction across splits
        if actual_splits == 1:
            return split_outputs[0].transpose(1, 2)
            
        stacked_lse = torch.stack(split_lse, dim=0) # (Splits, B, H, 1, 1)
        stacked_out = torch.stack(split_outputs, dim=0) # (Splits, B, H, 1, D)
        
        global_lse = torch.logsumexp(stacked_lse, dim=0, keepdim=True)
        weights = torch.exp(stacked_lse - global_lse)
        
        final_out = torch.sum(stacked_out * weights, dim=0) # (B, H, 1, D)
        
        return final_out.transpose(1, 2)
