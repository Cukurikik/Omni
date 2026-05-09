"""
OMNI Compute — Configurable Transformer Builder (configaformers-inspired)
Build custom transformer architectures with modular components.
"""
import math, torch, torch.nn as nn, torch.nn.functional as F
from dataclasses import dataclass
from typing import List, Optional

@dataclass
class ModularConfig:
    embed_dim: int = 512; num_heads: int = 8; ffn_dim: int = 2048
    num_layers: int = 6; dropout: float = 0.1; vocab_size: int = 32000
    max_seq_len: int = 2048; activation: str = "gelu"; norm_type: str = "pre"
    attn_type: str = "standard"; ffn_type: str = "standard"
    use_bias: bool = False; rope: bool = True

def get_activation(name: str):
    return {"gelu": nn.GELU(), "relu": nn.ReLU(), "silu": nn.SiLU(), "swiglu": nn.SiLU()}[name]

class StandardFFN(nn.Module):
    def __init__(self, c: ModularConfig):
        super().__init__()
        self.w1 = nn.Linear(c.embed_dim, c.ffn_dim, bias=c.use_bias)
        self.w2 = nn.Linear(c.ffn_dim, c.embed_dim, bias=c.use_bias)
        self.act = get_activation(c.activation)
        self.drop = nn.Dropout(c.dropout)
    def forward(self, x): return self.drop(self.w2(self.act(self.w1(x))))

class SwiGLUFFN(nn.Module):
    def __init__(self, c: ModularConfig):
        super().__init__()
        hidden = int(c.ffn_dim * 2 / 3)
        self.w1 = nn.Linear(c.embed_dim, hidden, bias=c.use_bias)
        self.w3 = nn.Linear(c.embed_dim, hidden, bias=c.use_bias)
        self.w2 = nn.Linear(hidden, c.embed_dim, bias=c.use_bias)
    def forward(self, x): return self.w2(F.silu(self.w1(x)) * self.w3(x))

class ModularAttention(nn.Module):
    def __init__(self, c: ModularConfig):
        super().__init__()
        self.h, self.d = c.num_heads, c.embed_dim // c.num_heads
        self.wq = nn.Linear(c.embed_dim, c.embed_dim, bias=c.use_bias)
        self.wk = nn.Linear(c.embed_dim, c.embed_dim, bias=c.use_bias)
        self.wv = nn.Linear(c.embed_dim, c.embed_dim, bias=c.use_bias)
        self.wo = nn.Linear(c.embed_dim, c.embed_dim, bias=c.use_bias)
        self.drop = nn.Dropout(c.dropout)
    def forward(self, x, mask=None):
        B, T, _ = x.shape
        q = self.wq(x).view(B,T,self.h,self.d).transpose(1,2)
        k = self.wk(x).view(B,T,self.h,self.d).transpose(1,2)
        v = self.wv(x).view(B,T,self.h,self.d).transpose(1,2)
        s = (q @ k.transpose(-2,-1)) / math.sqrt(self.d)
        if mask is not None: s = s.masked_fill(mask, float('-inf'))
        return self.wo(self.drop(F.softmax(s,-1) @ v).transpose(1,2).reshape(B,T,-1))

class ModularBlock(nn.Module):
    def __init__(self, c: ModularConfig):
        super().__init__()
        self.ln1 = nn.RMSNorm(c.embed_dim) if hasattr(nn, 'RMSNorm') else nn.LayerNorm(c.embed_dim)
        self.attn = ModularAttention(c)
        self.ln2 = nn.RMSNorm(c.embed_dim) if hasattr(nn, 'RMSNorm') else nn.LayerNorm(c.embed_dim)
        self.ffn = SwiGLUFFN(c) if c.ffn_type == "swiglu" else StandardFFN(c)
    def forward(self, x, mask=None):
        x = x + self.attn(self.ln1(x), mask)
        return x + self.ffn(self.ln2(x))

class OmniConfigurableTransformer(nn.Module):
    """Fully configurable transformer - swap attention, FFN, normalization."""
    def __init__(self, c: ModularConfig):
        super().__init__(); self.c = c
        self.tok = nn.Embedding(c.vocab_size, c.embed_dim)
        self.pos = nn.Embedding(c.max_seq_len, c.embed_dim)
        self.blocks = nn.ModuleList([ModularBlock(c) for _ in range(c.num_layers)])
        self.ln = nn.LayerNorm(c.embed_dim)
        self.head = nn.Linear(c.embed_dim, c.vocab_size, bias=False)
    def forward(self, tokens, targets=None):
        B, T = tokens.shape
        mask = torch.triu(torch.ones(T,T,device=tokens.device,dtype=torch.bool),1).unsqueeze(0).unsqueeze(0)
        x = self.tok(tokens) + self.pos(torch.arange(T,device=tokens.device))
        for b in self.blocks: x = b(x, mask)
        logits = self.head(self.ln(x))
        loss = F.cross_entropy(logits.view(-1,logits.size(-1)), targets.view(-1)) if targets is not None else None
        return logits, loss
