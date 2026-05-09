from typing import Dict, Any, Optional, Type
import torch
import torch.nn as nn

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

class OmniTransformerHubRegistry:
    """
    OMNI Compute Layer: Centralized Transformer Hub Registry.
    Based on BubbleJoe-BrownU/TransformerHub structural paradigm.
    Maintains a dynamic registry of all transformer architectures (GPT, BERT, ViT) 
    available to the OMNI ecosystem.
    """
    
    _registry: Dict[str, Type[nn.Module]] = {}
    
    @classmethod
    def register_model(cls, name: str, model_class: Type[nn.Module]) -> Result:
        """Registers a new transformer architecture into the Hub."""
        try:
            if name in cls._registry:
                return Result.fail(ValueError(f"Model {name} is already registered."))
                
            cls._registry[name] = model_class
            return Result.ok(True)
        except Exception as e:
            return Result.fail(e)
            
    @classmethod
    def get_model(cls, name: str, config: Dict[str, Any]) -> Result:
        """Instantiates a transformer model from the registry."""
        try:
            if name not in cls._registry:
                return Result.fail(KeyError(f"Model {name} not found in registry."))
                
            model_class = cls._registry[name]
            instance = model_class(**config)
            return Result.ok(instance)
        except Exception as e:
            return Result.fail(e)

# Example generic architectural implementations
class OmniMiniGPT(nn.Module):
    def __init__(self, vocab_size: int = 50000, d_model: int = 512):
        super().__init__()
        self.emb = nn.Embedding(vocab_size, d_model)
        self.layer = nn.TransformerEncoderLayer(d_model=d_model, nhead=8)
        self.fc = nn.Linear(d_model, vocab_size)
        
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.fc(self.layer(self.emb(x)))

class OmniMiniViT(nn.Module):
    def __init__(self, image_size: int = 224, patch_size: int = 16, num_classes: int = 1000):
        super().__init__()
        self.d_model = 256
        self.patch_proj = nn.Conv2d(3, self.d_model, kernel_size=patch_size, stride=patch_size)
        self.layer = nn.TransformerEncoderLayer(d_model=self.d_model, nhead=8)
        self.fc = nn.Linear(self.d_model, num_classes)
        
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        x = self.patch_proj(x).flatten(2).transpose(1, 2)
        return self.fc(self.layer(x).mean(dim=1))

# Self-registration on load
OmniTransformerHubRegistry.register_model("OmniMiniGPT", OmniMiniGPT)
OmniTransformerHubRegistry.register_model("OmniMiniViT", OmniMiniViT)
