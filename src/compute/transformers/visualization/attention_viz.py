"""
OMNI Transformer — Attention Visualization
Tools for interpreting and visualizing attention patterns.
Learned from: BertViz patterns, transformer interpretability research
"""
import torch
from typing import List, Dict, Optional, Tuple
import json
import logging

logger = logging.getLogger(__name__)


class AttentionVisualizer:
    """Extract and format attention patterns for visualization."""
    def __init__(self, model, tokenizer=None):
        self.model = model
        self.tokenizer = tokenizer
        self._hooks = []
        self._attention_maps = {}

    def register_hooks(self) -> None:
        """Register forward hooks to capture attention weights."""
        for name, module in self.model.named_modules():
            if hasattr(module, 'self_attn') or 'attn' in name.lower():
                hook = module.register_forward_hook(self._capture_attention(name))
                self._hooks.append(hook)

    def _capture_attention(self, name: str):
        def hook(module, input, output):
            if isinstance(output, tuple) and len(output) > 1 and output[1] is not None:
                self._attention_maps[name] = output[1].detach().cpu()
        return hook

    def remove_hooks(self) -> None:
        for hook in self._hooks:
            hook.remove()
        self._hooks.clear()

    @torch.inference_mode()
    def get_attention_maps(self, input_ids: torch.Tensor) -> Dict[str, torch.Tensor]:
        self._attention_maps.clear()
        self.register_hooks()
        self.model(input_ids)
        self.remove_hooks()
        return self._attention_maps

    def attention_to_json(self, attention_maps: Dict[str, torch.Tensor],
                          tokens: Optional[List[str]] = None) -> str:
        """Export attention maps as JSON for web visualization."""
        result = {"layers": [], "tokens": tokens or []}
        for name, attn in sorted(attention_maps.items()):
            # attn shape: (B, H, S, S) — take first batch
            layer_data = {
                "name": name,
                "num_heads": attn.shape[1],
                "attention": attn[0].tolist(),
            }
            result["layers"].append(layer_data)
        return json.dumps(result)

    @staticmethod
    def compute_attention_entropy(attention: torch.Tensor) -> torch.Tensor:
        """Compute entropy of attention distributions (higher = more uniform)."""
        # attention: (B, H, S_q, S_k)
        eps = 1e-10
        entropy = -(attention * (attention + eps).log()).sum(dim=-1)
        return entropy  # (B, H, S_q)

    @staticmethod
    def compute_attention_distance(attention: torch.Tensor) -> torch.Tensor:
        """Average attention distance (how far each token attends)."""
        B, H, S_q, S_k = attention.shape
        positions = torch.arange(S_k, device=attention.device).float()
        query_positions = torch.arange(S_q, device=attention.device).float()
        distances = (positions.unsqueeze(0) - query_positions.unsqueeze(1)).abs()
        avg_distance = (attention * distances.unsqueeze(0).unsqueeze(0)).sum(dim=-1)
        return avg_distance  # (B, H, S_q)

    @staticmethod
    def head_importance(attention_maps: Dict[str, torch.Tensor]) -> Dict[str, List[float]]:
        """Estimate head importance via attention entropy."""
        importance = {}
        for name, attn in attention_maps.items():
            entropy = -(attn * (attn + 1e-10).log()).sum(dim=-1).mean(dim=(0, 2))
            importance[name] = entropy.tolist()
        return importance
