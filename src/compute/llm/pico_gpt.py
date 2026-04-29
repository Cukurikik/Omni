import torch
import torch.nn as nn
from typing import Optional, Tuple, List, Dict, Any, Union
import math

class OmniResult:
    def __init__(self, success: bool, value: Any = None, error: str = None):
        self.success = success
        self.value = value
        self.error = error

    @classmethod
    def ok(cls, value: Any):
        return cls(True, value=value)

    @classmethod
    def err(cls, error: str):
        return cls(False, error=error)

    def unwrap(self) -> Any:
        if not self.success:
            raise ValueError(f"Unwrap failed: {self.error}")
        return self.value

class RotaryPositionalEmbedding(nn.Module):
    def __init__(self, dim: int, max_seq_len: int = 4096):
        super().__init__()
        inv_freq = 1.0 / (10000 ** (torch.arange(0, dim, 2).float() / dim))
        self.register_buffer("inv_freq", inv_freq)
        self.max_seq_len = max_seq_len
        self._seq_len_cached = 0
        self._cos_cached = None
        self._sin_cached = None

    def _update_cos_sin_cache(self, seq_len: int, device: torch.device):
        if seq_len > self._seq_len_cached:
            t = torch.arange(seq_len, device=device, dtype=self.inv_freq.dtype)
            freqs = torch.einsum("i,j->ij", t, self.inv_freq)
            emb = torch.cat((freqs, freqs), dim=-1)
            self._cos_cached = emb.cos()
            self._sin_cached = emb.sin()
            self._seq_len_cached = seq_len

    def forward(self, q: torch.Tensor, k: torch.Tensor) -> Tuple[torch.Tensor, torch.Tensor]:
        seq_len = q.shape[1]
        self._update_cos_sin_cache(seq_len, q.device)
        cos = self._cos_cached[:seq_len].unsqueeze(0).unsqueeze(2)
        sin = self._sin_cached[:seq_len].unsqueeze(0).unsqueeze(2)
        
        def apply_rotary(x):
            x1, x2 = x[..., :x.shape[-1]//2], x[..., x.shape[-1]//2:]
            rotated = torch.cat((-x2, x1), dim=-1)
            return (x * cos) + (rotated * sin)
            
        return apply_rotary(q), apply_rotary(k)

class MultiHeadAttention(nn.Module):
    def __init__(self, d_model: int, num_heads: int):
        super().__init__()
        assert d_model % num_heads == 0
        self.d_model = d_model
        self.num_heads = num_heads
        self.head_dim = d_model // num_heads
        
        self.q_proj = nn.Linear(d_model, d_model, bias=False)
        self.k_proj = nn.Linear(d_model, d_model, bias=False)
        self.v_proj = nn.Linear(d_model, d_model, bias=False)
        self.o_proj = nn.Linear(d_model, d_model, bias=False)
        self.rope = RotaryPositionalEmbedding(self.head_dim)

    def forward(self, x: torch.Tensor, mask: Optional[torch.Tensor] = None) -> OmniResult:
        B, T, C = x.shape
        q = self.q_proj(x).view(B, T, self.num_heads, self.head_dim)
        k = self.k_proj(x).view(B, T, self.num_heads, self.head_dim)
        v = self.v_proj(x).view(B, T, self.num_heads, self.head_dim)
        
        q, k = self.rope(q, k)
        
        q = q.transpose(1, 2) # B, H, T, hd
        k = k.transpose(1, 2)
        v = v.transpose(1, 2)
        
        scores = torch.matmul(q, k.transpose(-2, -1)) / math.sqrt(self.head_dim)
        if mask is not None:
            scores = scores.masked_fill(mask == 0, float('-inf'))
            
        attn = torch.softmax(scores, dim=-1)
        out = torch.matmul(attn, v)
        out = out.transpose(1, 2).contiguous().view(B, T, C)
        
        projected = self.o_proj(out)
        return OmniResult.ok(projected)

class FeedForward(nn.Module):
    def __init__(self, d_model: int, hidden_dim: int):
        super().__init__()
        self.w1 = nn.Linear(d_model, hidden_dim, bias=False)
        self.w2 = nn.Linear(hidden_dim, d_model, bias=False)
        self.w3 = nn.Linear(d_model, hidden_dim, bias=False)
        self.silu = nn.SiLU()

    def forward(self, x: torch.Tensor) -> OmniResult:
        hidden = self.silu(self.w1(x)) * self.w3(x)
        return OmniResult.ok(self.w2(hidden))

class TransformerBlock(nn.Module):
    def __init__(self, d_model: int, num_heads: int, hidden_dim: int):
        super().__init__()
        self.attn = MultiHeadAttention(d_model, num_heads)
        self.ffn = FeedForward(d_model, hidden_dim)
        self.ln1 = nn.LayerNorm(d_model)
        self.ln2 = nn.LayerNorm(d_model)

    def forward(self, x: torch.Tensor, mask: Optional[torch.Tensor] = None) -> OmniResult:
        attn_res = self.attn(self.ln1(x), mask)
        if not attn_res.success: return attn_res
        x = x + attn_res.value
        
        ffn_res = self.ffn(self.ln2(x))
        if not ffn_res.success: return ffn_res
        x = x + ffn_res.value
        
        return OmniResult.ok(x)

class PicoGPT(nn.Module):
    def __init__(self, vocab_size: int, d_model: int, num_heads: int, num_layers: int, hidden_dim: int):
        super().__init__()
        self.embedding = nn.Embedding(vocab_size, d_model)
        self.layers = nn.ModuleList([
            TransformerBlock(d_model, num_heads, hidden_dim) for _ in range(num_layers)
        ])
        self.ln_f = nn.LayerNorm(d_model)
        self.lm_head = nn.Linear(d_model, vocab_size, bias=False)
        self.lm_head.weight = self.embedding.weight

    def forward(self, input_ids: torch.Tensor) -> OmniResult:
        B, T = input_ids.shape
        x = self.embedding(input_ids)
        mask = torch.tril(torch.ones(T, T, device=input_ids.device)).view(1, 1, T, T)
        
        for layer in self.layers:
            res = layer(x, mask)
            if not res.success: return res
            x = res.value
            
        x = self.ln_f(x)
        logits = self.lm_head(x)
        return OmniResult.ok(logits)
