import torch
import torch.nn as nn
import torch.nn.functional as F

class OmniMoBAAttention(nn.Module):
    """
    Mixture of Block Attention (MoBA) Layer.
    Splits long context sequences into blocks and selectively routes them to attention heads.
    Inspired by MoonshotAI/MoBA.
    """
    def __init__(self, d_model: int, num_heads: int, block_size: int, top_k_blocks: int):
        super().__init__()
        assert d_model % num_heads == 0
        self.d_model = d_model
        self.num_heads = num_heads
        self.head_dim = d_model // num_heads
        self.block_size = block_size
        self.top_k_blocks = top_k_blocks
        
        self.q_proj = nn.Linear(d_model, d_model, bias=False)
        self.k_proj = nn.Linear(d_model, d_model, bias=False)
        self.v_proj = nn.Linear(d_model, d_model, bias=False)
        self.o_proj = nn.Linear(d_model, d_model, bias=False)
        
        # Block Router parameters
        self.router_w = nn.Linear(d_model, 1, bias=False)

    def forward(self, hidden_states: torch.Tensor):
        batch_size, seq_len, _ = hidden_states.shape
        
        # Ensure sequence length is divisible by block size for simplicity
        pad_len = (self.block_size - (seq_len % self.block_size)) % self.block_size
        if pad_len > 0:
            hidden_states = F.pad(hidden_states, (0, 0, 0, pad_len))
            seq_len += pad_len
            
        num_blocks = seq_len // self.block_size
        
        Q = self.q_proj(hidden_states).view(batch_size, seq_len, self.num_heads, self.head_dim).transpose(1, 2)
        K = self.k_proj(hidden_states).view(batch_size, seq_len, self.num_heads, self.head_dim).transpose(1, 2)
        V = self.v_proj(hidden_states).view(batch_size, seq_len, self.num_heads, self.head_dim).transpose(1, 2)
        
        # Block representations (average pooling over block size)
        blocks = hidden_states.view(batch_size, num_blocks, self.block_size, self.d_model)
        block_reps = blocks.mean(dim=2) # [batch_size, num_blocks, d_model]
        
        # Route blocks
        block_logits = self.router_w(block_reps).squeeze(-1) # [batch_size, num_blocks]
        top_k_weights, top_k_indices = torch.topk(block_logits, k=min(self.top_k_blocks, num_blocks), dim=-1)
        
        # In a strict MoBA, only the selected blocks' KV cache is used for the query attention
        # Here we simulate the gather. For full speed, custom FlashAttention kernels are used.
        out = torch.zeros_like(hidden_states)
        
        for b in range(batch_size):
            selected_blocks = top_k_indices[b].sort()[0] # keep temporal order
            
            # Construct the sparse KV tensor
            k_sparse_list = []
            v_sparse_list = []
            for idx in selected_blocks:
                start = idx * self.block_size
                end = start + self.block_size
                k_sparse_list.append(K[b:b+1, :, start:end, :])
                v_sparse_list.append(V[b:b+1, :, start:end, :])
                
            K_sparse = torch.cat(k_sparse_list, dim=2)
            V_sparse = torch.cat(v_sparse_list, dim=2)
            
            # Standard attention over sparse KV
            scores = torch.matmul(Q[b:b+1], K_sparse.transpose(-2, -1)) / math.sqrt(self.head_dim)
            attn_weights = F.softmax(scores, dim=-1)
            attn_output = torch.matmul(attn_weights, V_sparse)
            
            out[b:b+1] = attn_output.transpose(1, 2).contiguous().view(1, seq_len, self.d_model)

        if pad_len > 0:
            out = out[:, :-pad_len, :]
            
        return self.o_proj(out)

import math
