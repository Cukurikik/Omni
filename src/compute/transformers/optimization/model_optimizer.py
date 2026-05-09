"""
OMNI Transformer — Model Optimization Pipeline
Quantization, pruning, distillation, ONNX export.
Learned from: LowinLi/fastgpt, ONNX Runtime
"""
import os, logging
from typing import Optional, Dict, Any
from pathlib import Path
import torch
import torch.nn as nn

logger = logging.getLogger(__name__)


class DynamicQuantizer:
    @staticmethod
    def quantize(model: nn.Module, dtype=torch.qint8) -> nn.Module:
        return torch.quantization.quantize_dynamic(model, {nn.Linear}, dtype=dtype)


class ModelPruner:
    @staticmethod
    def prune(model: nn.Module, amount: float = 0.3) -> Dict[str, float]:
        import torch.nn.utils.prune as prune
        stats = {}
        for name, m in model.named_modules():
            if isinstance(m, nn.Linear):
                prune.l1_unstructured(m, name="weight", amount=amount)
                stats[name] = float((m.weight == 0).sum()) / m.weight.numel()
        return stats


class KnowledgeDistiller:
    def __init__(self, teacher: nn.Module, student: nn.Module, temperature: float = 4.0, alpha: float = 0.5):
        self.teacher, self.student = teacher, student
        self.temperature, self.alpha = temperature, alpha
        self.teacher.eval()

    def compute_loss(self, batch: Dict[str, torch.Tensor]) -> torch.Tensor:
        with torch.inference_mode():
            t_out = self.teacher(**{k: v for k, v in batch.items() if k != "labels"})
        s_out = self.student(**batch)
        soft = nn.functional.kl_div(
            nn.functional.log_softmax(s_out["logits"] / self.temperature, dim=-1),
            nn.functional.softmax(t_out["logits"] / self.temperature, dim=-1),
            reduction="batchmean",
        ) * (self.temperature ** 2)
        hard = s_out.get("loss", torch.tensor(0.0))
        return self.alpha * soft + (1 - self.alpha) * hard


class ONNXExporter:
    @staticmethod
    def export(model: nn.Module, path: str, shape=(1, 128), vocab=32000, opset=17) -> str:
        model.eval()
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        dummy = torch.randint(0, vocab, shape)
        torch.onnx.export(model, (dummy,), path, input_names=["input_ids"], output_names=["logits"],
                          dynamic_axes={"input_ids": {0: "batch", 1: "seq"}, "logits": {0: "batch", 1: "seq"}},
                          opset_version=opset, do_constant_folding=True)
        logger.info(f"ONNX: {path} ({os.path.getsize(path)/1e6:.1f}MB)")
        return path


class ModelProfiler:
    @staticmethod
    def profile(model: nn.Module) -> Dict[str, Any]:
        total = sum(p.numel() for p in model.parameters())
        trainable = sum(p.numel() for p in model.parameters() if p.requires_grad)
        size = sum(p.numel() * p.element_size() for p in model.parameters()) / 1e6
        return {"total_params": total, "trainable": trainable, "size_mb": round(size, 2)}
