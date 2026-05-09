# @omni-layer Compute | @omni-lang Python | @omni-batch 18 | @omni-semester 16
# @omni-repo fcakyon/video-transformers + wenhaochai/aurora
# @omni-description Video transformer: frame-level ViT + temporal attention
# for video classification and captioning, inspired by video-transformers
# and AuroraCap architectures.

import math
from dataclasses import dataclass
from typing import List, Tuple

@dataclass
class VideoConfig:
    n_frames: int = 16
    frame_size: int = 224
    patch_size: int = 16
    d_model: int = 768
    n_heads: int = 12
    n_temporal_layers: int = 4
    n_classes: int = 400
    vocab_size: int = 32000

class FrameEncoder:
    def __init__(self, cfg: VideoConfig):
        self.n_patches = (cfg.frame_size // cfg.patch_size) ** 2
        self.d = cfg.d_model

    def encode_frame(self, pixels: List[float], frame_idx: int) -> List[float]:
        emb = [0.0]*self.d
        for d in range(self.d):
            val = 0.0
            for p in range(min(16, len(pixels))):
                val += pixels[p]*math.sin((frame_idx+1)*(d+1)*0.001+p*0.01)
            emb[d] = val*0.01 + math.sin(frame_idx*0.1+d*0.01)*0.02
        norm = math.sqrt(sum(e*e for e in emb))+1e-10
        return [e/norm for e in emb]

class TemporalAttention:
    def __init__(self, d: int, n_heads: int):
        self.d = d
        self.scale = 1.0/math.sqrt(d//n_heads)

    def forward(self, frame_embs: List[List[float]]) -> List[List[float]]:
        n = len(frame_embs)
        scores = [[0.0]*n for _ in range(n)]
        for i in range(n):
            for j in range(n):
                dot = sum(frame_embs[i][k]*frame_embs[j][k] for k in range(min(32,self.d)))
                scores[i][j] = dot*self.scale
        for i in range(n):
            mx = max(scores[i])
            exps = [math.exp(s-mx) for s in scores[i]]
            sm = sum(exps)+1e-10
            scores[i] = [e/sm for e in exps]
        out = []
        for i in range(n):
            vec = [sum(scores[i][j]*frame_embs[j][d] for j in range(n)) for d in range(self.d)]
            out.append(vec)
        return out

class VideoClassifier:
    def __init__(self, cfg: VideoConfig):
        self.cfg = cfg
        self.encoder = FrameEncoder(cfg)
        self.temporal = TemporalAttention(cfg.d_model, cfg.n_heads)

    def classify(self, frames: List[List[float]]) -> List[float]:
        embs = [self.encoder.encode_frame(f, i) for i, f in enumerate(frames)]
        refined = self.temporal.forward(embs)
        pooled = [sum(refined[f][d] for f in range(len(refined)))/len(refined) for d in range(self.cfg.d_model)]
        logits = [sum(pooled[d]*math.sin((c+1)*(d+1)*0.001) for d in range(min(32,self.cfg.d_model))) for c in range(self.cfg.n_classes)]
        mx = max(logits)
        exps = [math.exp(l-mx) for l in logits]
        sm = sum(exps)+1e-10
        return [e/sm for e in exps]

class VideoCaptioner:
    def __init__(self, cfg: VideoConfig):
        self.cfg = cfg
        self.encoder = FrameEncoder(cfg)
        self.temporal = TemporalAttention(cfg.d_model, cfg.n_heads)

    def caption(self, frames: List[List[float]], max_len: int = 50) -> List[int]:
        embs = [self.encoder.encode_frame(f, i) for i, f in enumerate(frames)]
        ctx = self.temporal.forward(embs)
        pooled = [sum(ctx[f][d] for f in range(len(ctx)))/len(ctx) for d in range(self.cfg.d_model)]
        tokens = []
        for t in range(max_len):
            logit = sum(pooled[d]*math.cos((t+1)*(d+1)*0.0001) for d in range(min(16,len(pooled))))
            token_id = int(abs(logit)*1000) % self.cfg.vocab_size
            tokens.append(token_id)
            if token_id == 2:
                break
        return tokens
