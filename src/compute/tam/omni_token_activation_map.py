"""
@omni-layer Compute | @omni-source xmed-lab/TAM
@omni-description Token Activation Map for multimodal LLM explainability.
Generates visual attention heatmaps from MLLM internal activations.
@omni-lang Python | @omni-batch 16 | @omni-semester 16
"""
import math
from typing import List, Optional, Dict

class OmniResult:
    __slots__ = ("data", "error")
    def __init__(self, data=None, error=None): self.data, self.error = data, error
    def is_ok(self): return self.error is None

class OmniTokenActivationMap:
    """Visual explainability for Multimodal LLMs via token activation mapping."""
    def __init__(self, n_visual_tokens: int = 576, image_size: int = 336, patch_size: int = 14):
        self.n_visual_tokens = n_visual_tokens
        self.image_size = image_size
        self.patch_size = patch_size
        self.grid_size = image_size // patch_size

    def compute_token_relevance(self, attention_weights: List[List[float]], target_token_idx: int) -> OmniResult:
        try:
            if not attention_weights:
                return OmniResult(error=Exception("Empty attention"))
            relevance = [0.0] * self.n_visual_tokens
            for layer_attn in attention_weights:
                for i in range(min(self.n_visual_tokens, len(layer_attn))):
                    relevance[i] += layer_attn[i]
            max_r = max(relevance) if relevance else 1
            relevance = [r / (max_r + 1e-8) for r in relevance]
            return OmniResult(data={"relevance_scores": relevance, "target_token": target_token_idx, "grid_size": self.grid_size})
        except Exception as e:
            return OmniResult(error=Exception(f"TAM failed: {e}"))

    def generate_heatmap(self, relevance: List[float]) -> OmniResult:
        try:
            gs = self.grid_size
            heatmap = [[0.0]*gs for _ in range(gs)]
            for i, r in enumerate(relevance[:gs*gs]):
                row, col = i // gs, i % gs
                heatmap[row][col] = r
            upscaled_size = self.image_size
            scale = upscaled_size // gs
            upscaled = [[0.0]*upscaled_size for _ in range(upscaled_size)]
            for r in range(gs):
                for c in range(gs):
                    val = heatmap[r][c]
                    for dr in range(scale):
                        for dc in range(scale):
                            upscaled[r*scale+dr][c*scale+dc] = val
            return OmniResult(data={"heatmap": heatmap, "heatmap_size": gs, "upscaled_size": upscaled_size})
        except Exception as e:
            return OmniResult(error=Exception(f"Heatmap failed: {e}"))

    def gradient_weighted_tam(self, gradients: List[float], activations: List[float]) -> OmniResult:
        try:
            n = min(len(gradients), len(activations), self.n_visual_tokens)
            weighted = [gradients[i] * activations[i] for i in range(n)]
            cam = [max(0, w) for w in weighted]
            max_c = max(cam) if cam else 1
            cam = [c / (max_c + 1e-8) for c in cam]
            return OmniResult(data={"grad_tam": cam, "n_tokens": n, "mean_activation": sum(cam)/max(n,1)})
        except Exception as e:
            return OmniResult(error=Exception(f"Grad TAM failed: {e}"))
