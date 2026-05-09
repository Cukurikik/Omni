import torch
import torch.nn as nn
import torch.nn.functional as F
from typing import Optional, Any, Dict

class Result:
    def __init__(self, value: Any = None, error: Optional[Exception] = None):
        self.value = value
        self.error = error
        self.is_success = error is None

    @classmethod
    def ok(cls, value: Any) -> 'Result':
        return cls(value=value)

    @classmethod
    def fail(cls, error: Exception) -> 'Result':
        return cls(error=error)

class CrossAttention(nn.Module):
    def __init__(self, query_dim: int, context_dim: int, heads: int = 8, dim_head: int = 64):
        super().__init__()
        inner_dim = dim_head * heads
        self.heads = heads
        self.scale = dim_head ** -0.5

        self.to_q = nn.Linear(query_dim, inner_dim, bias=False)
        self.to_k = nn.Linear(context_dim, inner_dim, bias=False)
        self.to_v = nn.Linear(context_dim, inner_dim, bias=False)
        
        self.to_out = nn.Linear(inner_dim, query_dim)

    def forward(self, q_input: torch.Tensor, context: torch.Tensor) -> torch.Tensor:
        b = q_input.shape[0]
        q = self.to_q(q_input).view(b, -1, self.heads, -1).transpose(1, 2)
        k = self.to_k(context).view(b, -1, self.heads, -1).transpose(1, 2)
        v = self.to_v(context).view(b, -1, self.heads, -1).transpose(1, 2)

        dots = torch.matmul(q, k.transpose(-1, -2)) * self.scale
        attn = F.softmax(dots, dim=-1)

        out = torch.matmul(attn, v).transpose(1, 2).reshape(b, -1, self.heads * v.shape[-1])
        return self.to_out(out)

class OmniPerceiverEngine:
    """
    OMNI Compute Layer: Perceiver General Perception Engine.
    Handles high-dimensional inputs (images, audio, video) via fixed-size latent bottleneck.
    Based on Rishit-dagli/Perceiver architecture.
    """
    def __init__(self, config: Dict[str, Any]):
        self.num_latents = config.get("num_latents", 256)
        self.latent_dim = config.get("latent_dim", 512)
        self.input_dim = config.get("input_dim", 3) # e.g., 3 for RGB image pixels
        self.num_classes = config.get("num_classes", 1000)
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        
        self.latents = nn.Parameter(torch.randn(self.num_latents, self.latent_dim))
        
        # Cross attention: Latents <- Input
        self.cross_attn = CrossAttention(self.latent_dim, self.input_dim)
        
        # Self attention: Latents <- Latents (using standard PyTorch Transformer layer)
        self.latent_transformer = nn.TransformerEncoderLayer(
            d_model=self.latent_dim, nhead=8, dim_feedforward=self.latent_dim * 4, batch_first=True
        )
        
        self.classifier = nn.Linear(self.latent_dim, self.num_classes)
        
        self.is_initialized = False

    def initialize(self) -> Result:
        try:
            self.cross_attn.to(self.device)
            self.latent_transformer.to(self.device)
            self.classifier.to(self.device)
            self.is_initialized = True
            return Result.ok(True)
        except Exception as e:
            return Result.fail(e)

    def perceive(self, inputs: torch.Tensor) -> Result:
        """
        inputs shape: (batch, num_inputs, input_dim) - e.g., flattened image pixels + pos encodings
        """
        if not self.is_initialized:
            return Result.fail(RuntimeError("Engine not initialized."))
            
        try:
            b = inputs.shape[0]
            inputs = inputs.to(self.device)
            
            # Repeat latents for batch
            latents = self.latents.unsqueeze(0).repeat(b, 1, 1).to(self.device)
            
            # Cross Attend
            latents = self.cross_attn(latents, inputs) + latents
            
            # Self Attend in Latent Space
            latents = self.latent_transformer(latents)
            
            # Global Average Pooling on Latents
            latents_mean = latents.mean(dim=1)
            
            # Classify
            logits = self.classifier(latents_mean)
            
            return Result.ok(logits)
        except Exception as e:
            return Result.fail(e)

def build_perceiver_engine() -> Result:
    config = {"num_latents": 256, "latent_dim": 512, "input_dim": 27, "num_classes": 100}
    engine = OmniPerceiverEngine(config)
    return engine.initialize()
