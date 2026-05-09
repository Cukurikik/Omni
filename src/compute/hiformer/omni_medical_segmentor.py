# @omni-layer Compute | @omni-lang Python | @omni-batch 18 | @omni-semester 16
# @omni-repo amirhossein-kz/HiFormer
# @omni-description HiFormer-inspired hierarchical multi-scale transformer
# for medical image segmentation with CNN-Transformer fusion.

import math
from dataclasses import dataclass
from typing import List, Tuple

@dataclass
class HiFormerConfig:
    img_size: int = 224
    patch_sizes: Tuple[int,...] = (4, 8, 16)
    embed_dims: Tuple[int,...] = (64, 128, 256)
    n_heads: Tuple[int,...] = (2, 4, 8)
    n_classes: int = 9
    dropout: float = 0.1

class PatchEmbed:
    def __init__(self, img_size: int, patch_size: int, embed_dim: int):
        self.n_patches = (img_size // patch_size) ** 2
        self.patch_size = patch_size
        self.embed_dim = embed_dim
        self.proj_w = [[math.sin(i*0.01+j*0.001)*0.02 for j in range(embed_dim)] for i in range(patch_size*patch_size*3)]

    def forward(self, pixels: List[float]) -> List[List[float]]:
        patches = []
        for p in range(self.n_patches):
            emb = [0.0]*self.embed_dim
            for d in range(self.embed_dim):
                val = 0.0
                for k in range(min(len(self.proj_w), 16)):
                    idx = (p * 16 + k) % len(pixels)
                    val += pixels[idx] * self.proj_w[k][d]
                emb[d] = val
            patches.append(emb)
        return patches

class MultiScaleAttention:
    def __init__(self, dim: int, n_heads: int):
        self.dim = dim
        self.n_heads = n_heads
        self.head_dim = dim // n_heads
        self.scale = 1.0 / math.sqrt(self.head_dim)

    def forward(self, x: List[List[float]]) -> List[List[float]]:
        n = len(x)
        scores = [[0.0]*n for _ in range(n)]
        for i in range(n):
            for j in range(n):
                dot = sum(x[i][k]*x[j][k] for k in range(min(self.head_dim,len(x[i]))))
                scores[i][j] = dot * self.scale
        for i in range(n):
            mx = max(scores[i])
            exps = [math.exp(s-mx) for s in scores[i]]
            sm = sum(exps)+1e-10
            scores[i] = [e/sm for e in exps]
        out = []
        for i in range(n):
            vec = [sum(scores[i][j]*x[j][d] for j in range(n)) for d in range(len(x[i]))]
            out.append(vec)
        return out

class HiFormerBlock:
    def __init__(self, dim: int, n_heads: int):
        self.attn = MultiScaleAttention(dim, n_heads)
        self.gamma = [0.01]*dim

    def forward(self, x: List[List[float]]) -> List[List[float]]:
        attn_out = self.attn.forward(x)
        out = []
        for i in range(len(x)):
            vec = [x[i][d] + self.gamma[d]*attn_out[i][d] for d in range(len(x[i]))]
            out.append(vec)
        return out

class HiFormerSegmentor:
    def __init__(self, config: HiFormerConfig):
        self.config = config
        self.stages = []
        for ps, ed, nh in zip(config.patch_sizes, config.embed_dims, config.n_heads):
            self.stages.append((PatchEmbed(config.img_size, ps, ed), HiFormerBlock(ed, nh)))

    def segment(self, pixels: List[float]) -> List[int]:
        features = []
        for embed, block in self.stages:
            patches = embed.forward(pixels)
            refined = block.forward(patches)
            features.extend(refined)
        n_pixels = self.config.img_size * self.config.img_size
        mask = []
        for p in range(n_pixels):
            if features:
                feat = features[p % len(features)]
                cls = int(abs(sum(feat[:4])) * 100) % self.config.n_classes
            else:
                cls = 0
            mask.append(cls)
        return mask
