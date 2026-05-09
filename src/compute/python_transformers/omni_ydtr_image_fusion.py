"""OMNI Compute — YDTR: Y-shape Dynamic Transformer for Image Fusion"""
import logging
from typing import List, Tuple, Dict
import math

logger = logging.getLogger("omni.ydtr")

class DynamicAttention:
    """Dynamic self-attention for multimodal fusion."""
    def __init__(self, dim: int, heads: int):
        self.dim = dim
        self.heads = heads
        self.scale = (dim // heads) ** -0.5

    def compute(self, q: List[float], k: List[float], v: List[float]) -> List[float]:
        # Simplified dot-product attention
        scores = [q[i] * k[i] * self.scale for i in range(len(q))]
        # Softmax
        max_s = max(scores)
        exp_s = [math.exp(s - max_s) for s in scores]
        sum_exp = sum(exp_s)
        attn = [e / sum_exp for e in exp_s]
        # Multiply by V
        out = [attn[i] * v[i] for i in range(len(v))]
        return out

class YShapeDynamicTransformer:
    """
    YDTR: Infrared and Visible Image Fusion via Y-shape Dynamic Transformer.
    Takes two image modalities (IR and Visible), encodes them separately,
    and fuses them dynamically.
    """
    def __init__(self, channels: int = 64, patch_size: int = 8):
        self.channels = channels
        self.patch_size = patch_size
        self.cross_attn = DynamicAttention(channels, 8)
        logger.info(f"Initialized YDTR Fusion Engine with {channels} channels")

    def patch_embed(self, image: List[List[float]]) -> List[List[float]]:
        """Extract patches and embed into tokens."""
        # Simulated embedding
        tokens = []
        for row in image:
            tokens.append([v * 0.1 for v in row])
        return tokens

    def dynamic_fusion_module(self, ir_tokens: List[List[float]], vi_tokens: List[List[float]]) -> List[List[float]]:
        """Fuse Infrared and Visible tokens dynamically."""
        fused = []
        for i in range(len(ir_tokens)):
            # Cross attention: IR queries VI, VI queries IR
            ir_attn = self.cross_attn.compute(q=ir_tokens[i], k=vi_tokens[i], v=vi_tokens[i])
            vi_attn = self.cross_attn.compute(q=vi_tokens[i], k=ir_tokens[i], v=ir_tokens[i])
            
            # Feature gating mechanism (Y-shape fusion)
            gate = [math.tanh(ir_attn[j] + vi_attn[j]) for j in range(len(ir_attn))]
            
            fused_token = [
                gate[j] * ir_attn[j] + (1 - gate[j]) * vi_attn[j]
                for j in range(len(ir_attn))
            ]
            fused.append(fused_token)
        return fused

    def reconstruct(self, fused_tokens: List[List[float]]) -> List[List[float]]:
        """Reconstruct fused image from tokens."""
        # Simulated reconstruction (Deconv)
        return [[t * 10.0 for t in token] for token in fused_tokens]

    def process(self, ir_image: List[List[float]], vi_image: List[List[float]]) -> List[List[float]]:
        """End-to-end YDTR processing."""
        if len(ir_image) != len(vi_image):
            raise ValueError("IR and VI images must have the same dimensions")
            
        ir_feat = self.patch_embed(ir_image)
        vi_feat = self.patch_embed(vi_image)
        
        fused_feat = self.dynamic_fusion_module(ir_feat, vi_feat)
        
        output_image = self.reconstruct(fused_feat)
        return output_image

