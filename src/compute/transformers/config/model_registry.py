"""
OMNI Transformer — Model Configuration Registry
Centralized configuration for all transformer architectures.
"""
from dataclasses import dataclass, asdict
from typing import Dict, Any, Optional
import json
from pathlib import Path


PRESET_CONFIGS = {
    "omni-tiny": {"embed_dim": 256, "num_layers": 4, "num_heads": 4, "ffn_dim": 1024, "vocab_size": 32000},
    "omni-small": {"embed_dim": 512, "num_layers": 8, "num_heads": 8, "ffn_dim": 2048, "vocab_size": 32000},
    "omni-base": {"embed_dim": 768, "num_layers": 12, "num_heads": 12, "ffn_dim": 3072, "vocab_size": 32000},
    "omni-large": {"embed_dim": 1024, "num_layers": 24, "num_heads": 16, "ffn_dim": 4096, "vocab_size": 32000},
    "omni-xl": {"embed_dim": 2048, "num_layers": 24, "num_heads": 16, "ffn_dim": 8192, "vocab_size": 32000},
    "omni-7b": {"embed_dim": 4096, "num_layers": 32, "num_heads": 32, "num_kv_heads": 8, "ffn_dim": 14336, "vocab_size": 32000},
    "omni-13b": {"embed_dim": 5120, "num_layers": 40, "num_heads": 40, "num_kv_heads": 8, "ffn_dim": 17920, "vocab_size": 32000},
    "vit-base": {"image_size": 224, "patch_size": 16, "embed_dim": 768, "num_layers": 12, "num_heads": 12, "num_classes": 1000},
    "vit-large": {"image_size": 224, "patch_size": 16, "embed_dim": 1024, "num_layers": 24, "num_heads": 16, "num_classes": 1000},
    "bert-base": {"embed_dim": 768, "num_layers": 12, "num_heads": 12, "ffn_dim": 3072, "vocab_size": 30522, "max_seq_len": 512},
    "bert-large": {"embed_dim": 1024, "num_layers": 24, "num_heads": 16, "ffn_dim": 4096, "vocab_size": 30522, "max_seq_len": 512},
}


class ConfigRegistry:
    """Registry for model configurations."""
    _custom_configs: Dict[str, Dict[str, Any]] = {}

    @classmethod
    def get(cls, name: str) -> Dict[str, Any]:
        if name in cls._custom_configs:
            return cls._custom_configs[name].copy()
        if name in PRESET_CONFIGS:
            return PRESET_CONFIGS[name].copy()
        raise KeyError(f"Unknown config: {name}. Available: {list(PRESET_CONFIGS.keys()) + list(cls._custom_configs.keys())}")

    @classmethod
    def register(cls, name: str, config: Dict[str, Any]) -> None:
        cls._custom_configs[name] = config

    @classmethod
    def list_configs(cls) -> list:
        return list(PRESET_CONFIGS.keys()) + list(cls._custom_configs.keys())

    @classmethod
    def save(cls, name: str, path: str) -> None:
        config = cls.get(name)
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w") as f:
            json.dump({"name": name, **config}, f, indent=2)

    @classmethod
    def load(cls, path: str) -> Dict[str, Any]:
        with open(path) as f:
            config = json.load(f)
        name = config.pop("name", Path(path).stem)
        cls.register(name, config)
        return config

    @staticmethod
    def compute_params(config: Dict[str, Any]) -> int:
        """Estimate total parameters for a config."""
        d = config.get("embed_dim", 768)
        L = config.get("num_layers", 12)
        V = config.get("vocab_size", 32000)
        ffn = config.get("ffn_dim", 4 * d)
        # Approximate: embedding + L * (4*d*d + 2*d*ffn) + output
        attn_params = 4 * d * d  # Q, K, V, O projections
        ffn_params = 2 * d * ffn  # up and down projections (or 3x for gated)
        total = V * d + L * (attn_params + ffn_params) + V * d
        return total
