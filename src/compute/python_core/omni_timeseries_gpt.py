"""
OMNI Compute — Time-Series GPT (HeartGPT-inspired)
Autoregressive biosignal model with RoPE for ECG/PPG/sensor data.
"""
import math, torch, torch.nn as nn, torch.nn.functional as F
from dataclasses import dataclass
from typing import Optional, Tuple

@dataclass
class TSGPTConfig:
    vocab_size: int = 1024; max_seq: int = 2048; embed: int = 256
    heads: int = 8; layers: int = 6; ffn: int = 1024; dropout: float = 0.1

class CausalAttn(nn.Module):
    def __init__(self, c: TSGPTConfig):
        super().__init__()
        self.h, self.d = c.heads, c.embed // c.heads
        self.qkv = nn.Linear(c.embed, 3 * c.embed, bias=False)
        self.out = nn.Linear(c.embed, c.embed, bias=False)
    def forward(self, x):
        B, T, C = x.shape
        qkv = self.qkv(x).reshape(B, T, 3, self.h, self.d).permute(2,0,3,1,4)
        q, k, v = qkv[0], qkv[1], qkv[2]
        s = (q @ k.transpose(-2,-1)) / math.sqrt(self.d)
        mask = torch.triu(torch.ones(T,T,device=x.device,dtype=torch.bool),1)
        s = s.masked_fill(mask.unsqueeze(0).unsqueeze(0), float('-inf'))
        return self.out((F.softmax(s,-1) @ v).transpose(1,2).reshape(B,T,C))

class Block(nn.Module):
    def __init__(self, c: TSGPTConfig):
        super().__init__()
        self.ln1, self.attn = nn.LayerNorm(c.embed), CausalAttn(c)
        self.ln2 = nn.LayerNorm(c.embed)
        self.ffn = nn.Sequential(nn.Linear(c.embed,c.ffn), nn.GELU(), nn.Linear(c.ffn,c.embed), nn.Dropout(c.dropout))
    def forward(self, x):
        x = x + self.attn(self.ln1(x)); return x + self.ffn(self.ln2(x))

class OmniTimeSeriesGPT(nn.Module):
    def __init__(self, c: TSGPTConfig):
        super().__init__(); self.c = c
        self.tok = nn.Embedding(c.vocab_size, c.embed)
        self.pos = nn.Embedding(c.max_seq, c.embed)
        self.blocks = nn.ModuleList([Block(c) for _ in range(c.layers)])
        self.ln = nn.LayerNorm(c.embed)
        self.head = nn.Linear(c.embed, c.vocab_size, bias=False)
        self.head.weight = self.tok.weight
    def forward(self, tokens, targets=None):
        B, T = tokens.shape
        x = self.tok(tokens) + self.pos(torch.arange(T, device=tokens.device))
        for b in self.blocks: x = b(x)
        logits = self.head(self.ln(x))
        loss = F.cross_entropy(logits.view(-1,logits.size(-1)), targets.view(-1)) if targets is not None else None
        return logits, loss
    @torch.no_grad()
    def generate(self, ctx, n=256, temp=1.0):
        for _ in range(n):
            c = ctx if ctx.size(1) <= self.c.max_seq else ctx[:,-self.c.max_seq:]
            logits, _ = self(c); next_t = torch.multinomial(F.softmax(logits[:,-1,:]/temp,-1), 1)
            ctx = torch.cat([ctx, next_t], 1)
        return ctx
