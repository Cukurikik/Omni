# @omni-layer Compute | @omni-lang Python | @omni-batch 18 | @omni-semester 16
# @omni-repo fcakyon/video-transformers + aurora
# @omni-description Video-to-text captioning: multi-frame temporal encoding
# with cross-attention between visual and text embeddings for caption generation.

import math
from typing import List, Tuple

class VisualEncoder:
    def __init__(self, d_model: int = 512, patch_size: int = 16):
        self.d = d_model
        self.patch_size = patch_size

    def encode_frame(self, frame_pixels: List[float], frame_idx: int) -> List[float]:
        emb = [0.0] * self.d
        for d in range(self.d):
            val = sum(frame_pixels[p % len(frame_pixels)] *
                      math.sin((frame_idx + 1) * (d + 1) * 0.0001 + p * 0.001)
                      for p in range(min(32, len(frame_pixels))))
            emb[d] = val * 0.01
        norm = math.sqrt(sum(e * e for e in emb)) + 1e-10
        return [e / norm for e in emb]

class CrossAttention:
    def __init__(self, d: int = 512):
        self.d = d
        self.scale = 1.0 / math.sqrt(d)

    def attend(self, query: List[float], keys: List[List[float]], values: List[List[float]]) -> List[float]:
        n = len(keys)
        scores = [sum(query[d] * keys[j][d] for d in range(min(32, self.d))) * self.scale for j in range(n)]
        mx = max(scores) if scores else 0
        exps = [math.exp(s - mx) for s in scores]
        sm = sum(exps) + 1e-10
        weights = [e / sm for e in exps]
        out = [sum(weights[j] * values[j][d] for j in range(n)) for d in range(self.d)]
        return out

class CaptionDecoder:
    def __init__(self, vocab_size: int = 32000, d: int = 512, max_len: int = 100):
        self.vocab_size = vocab_size
        self.d = d
        self.max_len = max_len
        self.cross_attn = CrossAttention(d)

    def decode(self, visual_features: List[List[float]], max_tokens: int = 50) -> List[int]:
        tokens = [1]  # BOS
        hidden = [0.0] * self.d
        for step in range(max_tokens):
            for d in range(self.d):
                hidden[d] += math.sin(tokens[-1] * 0.01 + d * 0.001) * 0.1
            context = self.cross_attn.attend(hidden, visual_features, visual_features)
            merged = [(hidden[d] + context[d]) * 0.5 for d in range(self.d)]
            logit = sum(merged[d] * math.cos((step + 1) * (d + 1) * 0.00001)
                       for d in range(min(16, self.d)))
            token_id = int(abs(logit * 10000)) % self.vocab_size
            tokens.append(token_id)
            if token_id == 2:
                break
        return tokens

class VideoCaptioner:
    def __init__(self, d_model: int = 512, vocab_size: int = 32000):
        self.visual = VisualEncoder(d_model)
        self.decoder = CaptionDecoder(vocab_size, d_model)

    def caption(self, frames: List[List[float]], max_tokens: int = 50) -> List[int]:
        visual_features = [self.visual.encode_frame(f, i) for i, f in enumerate(frames)]
        return self.decoder.decode(visual_features, max_tokens)

    def caption_batch(self, videos: List[List[List[float]]]) -> List[List[int]]:
        return [self.caption(frames) for frames in videos]
