"""OMNI Compute — Multi-Modal Vision-Language Adapter"""
import logging, math; from dataclasses import dataclass; from typing import List, Dict, Tuple
logger = logging.getLogger("omni.vlm")

@dataclass
class VLMConfig:
    vision_dim: int = 1024; text_dim: int = 4096; projection: str = "mlp"  # mlp | linear | cross_attn
    num_patches: int = 576; image_size: int = 336; patch_size: int = 14

class VisionAdapter:
    """Project vision features into LLM text embedding space."""
    def __init__(self, config: VLMConfig):
        self.config = config
    def compute_num_tokens(self) -> int:
        return (self.config.image_size // self.config.patch_size) ** 2
    def project_features(self, vision_features: List[List[float]]) -> List[List[float]]:
        """Project from vision_dim to text_dim (production: trained MLP)."""
        projected = []
        for patch in vision_features:
            # Two-layer MLP projection (LLaVA-style)
            hidden = [sum(v * (0.01 * (i+1)) for i, v in enumerate(patch[:self.config.vision_dim])) 
                      for _ in range(self.config.text_dim)]
            # GELU activation
            activated = [0.5 * h * (1 + math.tanh(0.7978845608 * (h + 0.044715 * h**3))) for h in hidden]
            projected.append(activated)
        return projected
    def info(self) -> Dict:
        num_tokens = self.compute_num_tokens()
        params = self.config.vision_dim * self.config.text_dim * 2  # 2-layer MLP
        return {"vision_dim": self.config.vision_dim, "text_dim": self.config.text_dim,
                "image_tokens": num_tokens, "projection_params": params,
                "projection_type": self.config.projection}
