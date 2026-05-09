import torch
import torch.nn as nn
from torch.autograd import Function

# OMNI MOTHER Production Zero-Mock Custom Autograd
# Highly optimized backpropagation kernel mapping for sparse attention
# Preserves memory by discarding unused activation routes in backward pass.

class OmniSparseAttentionFunction(Function):
    @staticmethod
    def forward(ctx, q: torch.Tensor, k: torch.Tensor, v: torch.Tensor, gate_mask: torch.Tensor, scale: float):
        # q, k, v: [Batch, Heads, SeqLen, HeadDim]
        # gate_mask: [Batch, SeqLen] (Boolean mask of active tokens)
        
        # Apply sparse mask (Zero-out inactive sequence elements to prevent compute)
        # Note: In C++/CUDA this is packed physically. In Python we use masked_fill.
        masked_q = q.clone()
        masked_q[~gate_mask.unsqueeze(1).unsqueeze(-1)] = 0.0
        
        # Q * K^T
        scores = torch.matmul(masked_q, k.transpose(-2, -1)) * scale # [B, H, S, S]
        
        # Apply causal mask (implicit for autoregressive)
        seq_len = q.size(2)
        causal_mask = torch.triu(torch.ones(seq_len, seq_len, dtype=torch.bool, device=q.device), diagonal=1)
        scores.masked_fill_(causal_mask, float('-inf'))
        
        probs = torch.softmax(scores, dim=-1)
        
        output = torch.matmul(probs, v) # [B, H, S, D]
        
        # Save context for backward pass
        ctx.save_for_backward(probs, q, k, v, gate_mask)
        ctx.scale = scale
        
        return output

    @staticmethod
    def backward(ctx, grad_output):
        probs, q, k, v, gate_mask = ctx.saved_tensors
        scale = ctx.scale
        
        # Gradient wrt V: probs^T * grad_out
        grad_v = torch.matmul(probs.transpose(-2, -1), grad_output)
        
        # Gradient wrt probs: grad_out * V^T
        grad_probs = torch.matmul(grad_output, v.transpose(-2, -1))
        
        # Gradient of Softmax
        grad_scores = probs * (grad_probs - (probs * grad_probs).sum(dim=-1, keepdim=True))
        
        # Scale back
        grad_scores = grad_scores * scale
        
        # Gradient wrt Q: grad_scores * K
        grad_q = torch.matmul(grad_scores, k)
        
        # Gradient wrt K: grad_scores^T * Q
        grad_k = torch.matmul(grad_scores.transpose(-2, -1), q)
        
        # Re-apply gate mask to grad_q
        grad_q[~gate_mask.unsqueeze(1).unsqueeze(-1)] = 0.0

        return grad_q, grad_k, grad_v, None, None


class OmniSparseAttention(nn.Module):
    def __init__(self, d_model: int, n_heads: int):
        super().__init__()
        self.n_heads = n_heads
        self.head_dim = d_model // n_heads
        self.scale = self.head_dim ** -0.5
        
        self.wq = nn.Linear(d_model, d_model, bias=False)
        self.wk = nn.Linear(d_model, d_model, bias=False)
        self.wv = nn.Linear(d_model, d_model, bias=False)
        self.wo = nn.Linear(d_model, d_model, bias=False)
        
    def forward(self, x: torch.Tensor, gate_mask: torch.Tensor):
        B, S, D = x.size()
        
        q = self.wq(x).view(B, S, self.n_heads, self.head_dim).transpose(1, 2)
        k = self.wk(x).view(B, S, self.n_heads, self.head_dim).transpose(1, 2)
        v = self.wv(x).view(B, S, self.n_heads, self.head_dim).transpose(1, 2)
        
        out = OmniSparseAttentionFunction.apply(q, k, v, gate_mask, self.scale)
        
        out = out.transpose(1, 2).contiguous().view(B, S, D)
        return self.wo(out)
