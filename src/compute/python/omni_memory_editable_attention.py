import torch
import torch.nn as nn
import torch.nn.functional as F
import math

class OmniMemoryEditableAttention(nn.Module):
    """
    OMNI Framework - Memory Editable Attention
    Zero-mock implementation allowing dynamic editing of attention key-value pairs 
    to alter knowledge without full network retraining.
    """
    def __init__(self, dim: int, heads: int = 8, dim_head: int = 64):
        super().__init__()
        self.heads = heads
        self.scale = dim_head ** -0.5
        inner_dim = heads * dim_head

        self.to_q = nn.Linear(dim, inner_dim, bias=False)
        self.to_k = nn.Linear(dim, inner_dim, bias=False)
        self.to_v = nn.Linear(dim, inner_dim, bias=False)
        self.to_out = nn.Linear(inner_dim, dim)

        # Persistent explicit memory banks that can be directly edited
        self.memory_keys = nn.Parameter(torch.randn(1, heads, 128, dim_head))
        self.memory_values = nn.Parameter(torch.randn(1, heads, 128, dim_head))

    def edit_memory(self, index: int, new_key: torch.Tensor, new_value: torch.Tensor):
        """ In-place modification of explicit memory """
        with torch.no_grad():
            self.memory_keys[:, :, index, :] = new_key
            self.memory_values[:, :, index, :] = new_value

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        b, n, _, h = *x.shape, self.heads
        
        q = self.to_q(x).view(b, n, h, -1).transpose(1, 2)
        k = self.to_k(x).view(b, n, h, -1).transpose(1, 2)
        v = self.to_v(x).view(b, n, h, -1).transpose(1, 2)

        # Concat persistent memory to sequence keys/values
        mem_k = self.memory_keys.expand(b, -1, -1, -1)
        mem_v = self.memory_values.expand(b, -1, -1, -1)
        
        k = torch.cat((mem_k, k), dim=2)
        v = torch.cat((mem_v, v), dim=2)

        dots = torch.matmul(q, k.transpose(-1, -2)) * self.scale
        attn = F.softmax(dots, dim=-1)
        
        out = torch.matmul(attn, v)
        out = out.transpose(1, 2).reshape(b, n, -1)
        return self.to_out(out)
