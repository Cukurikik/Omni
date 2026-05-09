"""
OMNI Transformer — Model Export & Deployment Utilities
Export models to various formats for production deployment.
"""
import torch
import torch.nn as nn
from typing import Dict, Optional
from pathlib import Path
import json
import logging

logger = logging.getLogger(__name__)


class SafeTensorsExporter:
    """Export model weights in safetensors format."""
    @staticmethod
    def export(model: nn.Module, path: str, metadata: Optional[Dict] = None) -> str:
        try:
            from safetensors.torch import save_file
        except ImportError:
            logger.warning("safetensors not installed, falling back to torch.save")
            torch.save(model.state_dict(), path)
            return path

        Path(path).parent.mkdir(parents=True, exist_ok=True)
        state_dict = {k: v.contiguous() for k, v in model.state_dict().items()}
        save_file(state_dict, path, metadata=metadata)
        logger.info(f"Exported to safetensors: {path}")
        return path


class TorchScriptExporter:
    """Export model to TorchScript for C++ inference."""
    @staticmethod
    def export_traced(model: nn.Module, path: str, example_input: torch.Tensor) -> str:
        model.eval()
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        traced = torch.jit.trace(model, example_input)
        traced.save(path)
        logger.info(f"Exported TorchScript (traced): {path}")
        return path

    @staticmethod
    def export_scripted(model: nn.Module, path: str) -> str:
        model.eval()
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        scripted = torch.jit.script(model)
        scripted.save(path)
        logger.info(f"Exported TorchScript (scripted): {path}")
        return path


class ModelCard:
    """Generate model card for documentation."""
    @staticmethod
    def generate(
        model: nn.Module,
        model_name: str,
        description: str = "",
        task: str = "text-generation",
        language: str = "en",
        license_type: str = "MIT",
        **kwargs
    ) -> str:
        total_params = sum(p.numel() for p in model.parameters())
        trainable = sum(p.numel() for p in model.parameters() if p.requires_grad)
        size_mb = sum(p.numel() * p.element_size() for p in model.parameters()) / 1e6

        card = f"""---
model_name: {model_name}
task: {task}
language: {language}
license: {license_type}
---

# {model_name}

{description}

## Model Details
- **Parameters:** {total_params:,}
- **Trainable:** {trainable:,}
- **Size:** {size_mb:.1f} MB
- **Framework:** OMNI Transformer Engine

## Architecture
```
{model}
```

## Usage
```python
from omni.compute.transformers import {model.__class__.__name__}
model = {model.__class__.__name__}.from_pretrained("{model_name}")
```
"""
        return card

    @staticmethod
    def save(card: str, path: str) -> None:
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w") as f:
            f.write(card)
        logger.info(f"Model card saved: {path}")
