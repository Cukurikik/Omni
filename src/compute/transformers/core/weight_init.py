"""
OMNI Transformer — Weight Initialization Strategies
Production initialization for stable transformer training.
"""
import torch
import torch.nn as nn
import math
from typing import Optional
import logging

logger = logging.getLogger(__name__)


def _normal_init(module: nn.Module, mean: float = 0.0, std: float = 0.02) -> None:
    if isinstance(module, (nn.Linear, nn.Embedding)):
        nn.init.normal_(module.weight, mean=mean, std=std)
        if hasattr(module, 'bias') and module.bias is not None:
            nn.init.zeros_(module.bias)


def _xavier_init(module: nn.Module) -> None:
    if isinstance(module, nn.Linear):
        nn.init.xavier_uniform_(module.weight)
        if module.bias is not None:
            nn.init.zeros_(module.bias)


def _kaiming_init(module: nn.Module) -> None:
    if isinstance(module, nn.Linear):
        nn.init.kaiming_normal_(module.weight, mode='fan_in', nonlinearity='relu')
        if module.bias is not None:
            nn.init.zeros_(module.bias)


def gpt2_init(model: nn.Module, n_layers: int) -> None:
    """GPT-2 style initialization with residual scaling."""
    for name, param in model.named_parameters():
        if "weight" in name:
            if "embed" in name:
                nn.init.normal_(param, mean=0.0, std=0.02)
            elif any(proj in name for proj in ["o_proj", "down_proj"]):
                # Scale residual projections by 1/sqrt(2*N)
                nn.init.normal_(param, mean=0.0, std=0.02 / math.sqrt(2 * n_layers))
            elif param.dim() >= 2:
                nn.init.normal_(param, mean=0.0, std=0.02)
        elif "bias" in name:
            nn.init.zeros_(param)


def muP_init(model: nn.Module, width: int, base_width: int = 256) -> None:
    """Maximal Update Parameterization (muP) initialization."""
    scale = math.sqrt(base_width / width)
    for name, param in model.named_parameters():
        if param.dim() >= 2:
            fan_in = param.shape[1] if param.dim() >= 2 else param.shape[0]
            std = scale / math.sqrt(fan_in)
            nn.init.normal_(param, mean=0.0, std=std)
        elif "bias" in name:
            nn.init.zeros_(param)


def initialize_model(model: nn.Module, strategy: str = "gpt2", **kwargs) -> None:
    """Apply initialization strategy to model."""
    strategies = {
        "normal": lambda m: m.apply(_normal_init),
        "xavier": lambda m: m.apply(_xavier_init),
        "kaiming": lambda m: m.apply(_kaiming_init),
        "gpt2": lambda m: gpt2_init(m, kwargs.get("n_layers", 12)),
        "mup": lambda m: muP_init(m, kwargs.get("width", 768)),
    }
    if strategy not in strategies:
        raise ValueError(f"Unknown strategy: {strategy}")
    strategies[strategy](model)
    n_params = sum(p.numel() for p in model.parameters())
    logger.info(f"Initialized {n_params:,} parameters with '{strategy}' strategy")
