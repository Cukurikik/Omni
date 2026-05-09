import torch
import torch.nn as nn
import torch.nn.functional as F

class OmniNGrammerAttention(nn.Module):
    """
    Omni N-Grammer Attention Layer.
    Augments Transformer attention with latent n-grams.
    Incorporates n-gram statistics directly into the attention mechanism
    for improved language modeling efficiency and perplexity.
    """
    def __init__(self, dim: int, heads: int = 8, max_ngram: int = 4):
        super().__init__()
        self.dim = dim
        self.heads = heads
        self.max_ngram = max_ngram
        
        self.qkv = nn.Linear(dim, dim * 3, bias=False)
        self.proj = nn.Linear(dim, dim)
        
        # Latent n-gram embedding table mapped by hashed token clusters
        self.ngram_vocab_size = 10000 
        self.ngram_emb = nn.Embedding(self.ngram_vocab_size, dim)
        
        # MLP to mix n-gram representation with token representation
        self.mixer = nn.Sequential(
            nn.Linear(dim * 2, dim),
            nn.GELU(),
            nn.Linear(dim, dim)
        )

    def extract_ngrams(self, x: torch.Tensor) -> torch.Tensor:
        # A true N-Grammer hashes the token IDs. Here we simulate the latent 
        # n-gram extraction by applying a localized 1D convolution over the 
        # hidden states to capture n-gram contextual boundaries.
        B, L, D = x.shape
        x_perm = x.permute(0, 2, 1) # B, D, L
        
        # Simple simulated n-gram aggregation
        ngram_feats = F.avg_pool1d(x_perm, kernel_size=self.max_ngram, stride=1, padding=self.max_ngram//2)
        if ngram_feats.shape[2] > L:
            ngram_feats = ngram_feats[:, :, :L]
        elif ngram_feats.shape[2] < L:
            ngram_feats = F.pad(ngram_feats, (0, L - ngram_feats.shape[2]))
            
        return ngram_feats.permute(0, 2, 1) # B, L, D

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        B, L, D = x.shape
        
        # Augment input with latent n-grams
        ngram_context = self.extract_ngrams(x)
        x_augmented = self.mixer(torch.cat([x, ngram_context], dim=-1))
        
        # Standard Attention on augmented vectors
        qkv = self.qkv(x_augmented).reshape(B, L, 3, self.heads, D // self.heads).permute(2, 0, 3, 1, 4)
        q, k, v = qkv[0], qkv[1], qkv[2]
        
        scale = (D // self.heads) ** -0.5
        attn = (q @ k.transpose(-2, -1)) * scale
        
        # Apply causal mask
        causal_mask = torch.tril(torch.ones((L, L), device=x.device)).view(1, 1, L, L)
        attn = attn.masked_fill(causal_mask == 0, float('-inf'))
        
        attn = attn.softmax(dim=-1)
        out = (attn @ v).transpose(1, 2).reshape(B, L, D)
        
        return self.proj(out)
