"""
moe_onnx_exporter.py — ONNX Export Pipeline for MoE Models
Layer: Compute / AI — MoE Deployment

Exports MoE models to ONNX format with proper handling of:
- Dynamic expert routing (conditional subgraphs)
- Variable batch/sequence lengths
- Expert-parallel sharding metadata
- Quantization-aware export
"""
import torch
import torch.nn as nn
import torch.nn.functional as F
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
import logging
import json
import os

logger = logging.getLogger(__name__)


@dataclass
class OnnxExportConfig:
    opset_version: int = 17
    dynamic_axes: bool = True
    export_router_separately: bool = True
    export_experts_separately: bool = False
    output_dir: str = "./onnx_export"
    fp16: bool = True
    include_metadata: bool = True
    optimize: bool = True


class MoEModelWrapper(nn.Module):
    """Wrapper that flattens MoE routing for ONNX-compatible export."""
    def __init__(self, model, num_experts, top_k):
        super().__init__()
        self.model = model
        self.num_experts = num_experts
        self.top_k = top_k

    def forward(self, input_ids: torch.Tensor) -> Tuple[torch.Tensor, torch.Tensor]:
        output = self.model(input_ids)
        if isinstance(output, dict):
            logits = output.get("logits", output.get("output"))
            aux = output.get("aux_loss", torch.tensor(0.0))
            return logits, aux
        return output, torch.tensor(0.0)


class RouterExporter:
    """Exports just the router component for efficient routing-only inference."""
    def __init__(self, router: nn.Module, num_experts: int, dim: int):
        self.router = router
        self.num_experts = num_experts
        self.dim = dim

    def export(self, path: str, config: OnnxExportConfig):
        wrapper = self._create_wrapper()
        dummy = torch.randn(1, 16, self.dim)
        dynamic = {"input": {0: "batch", 1: "seq_len"},
                    "output": {0: "batch", 1: "seq_len"}} if config.dynamic_axes else None

        torch.onnx.export(
            wrapper, dummy, path,
            input_names=["input"],
            output_names=["expert_indices", "expert_weights"],
            dynamic_axes=dynamic,
            opset_version=config.opset_version,
            do_constant_folding=config.optimize)
        logger.info(f"Router exported to {path}")

    def _create_wrapper(self):
        class RouterWrapper(nn.Module):
            def __init__(self, router, top_k):
                super().__init__()
                self.router = router
                self.top_k = top_k
            def forward(self, x):
                if hasattr(self.router, 'gate'):
                    logits = self.router.gate(x)
                else:
                    logits = self.router(x)
                probs = F.softmax(logits, dim=-1)
                w, idx = torch.topk(probs, self.top_k, dim=-1)
                return idx, w / w.sum(dim=-1, keepdim=True).clamp(min=1e-8)
        return RouterWrapper(self.router, 2)


class ExpertExporter:
    """Exports individual experts as separate ONNX models."""
    def __init__(self, experts: nn.ModuleList, dim: int):
        self.experts = experts
        self.dim = dim

    def export_all(self, output_dir: str, config: OnnxExportConfig):
        os.makedirs(output_dir, exist_ok=True)
        for idx, expert in enumerate(self.experts):
            path = os.path.join(output_dir, f"expert_{idx}.onnx")
            dummy = torch.randn(1, self.dim)
            dynamic = {"input": {0: "num_tokens"},
                        "output": {0: "num_tokens"}} if config.dynamic_axes else None

            torch.onnx.export(
                expert, dummy, path,
                input_names=["input"],
                output_names=["output"],
                dynamic_axes=dynamic,
                opset_version=config.opset_version,
                do_constant_folding=config.optimize)
            logger.info(f"Expert {idx} exported to {path}")


class MoEOnnxExporter:
    """Complete MoE ONNX export pipeline."""
    def __init__(self, model: nn.Module, config: OnnxExportConfig = None):
        self.model = model
        self.config = config or OnnxExportConfig()
        self._num_experts = 0
        self._dim = 0
        self._discover_architecture()

    def _discover_architecture(self):
        for m in self.model.modules():
            if hasattr(m, 'experts') and isinstance(m.experts, nn.ModuleList):
                self._num_experts = len(m.experts)
                first_expert = m.experts[0]
                for child in first_expert.children():
                    if isinstance(child, nn.Linear):
                        self._dim = child.in_features
                        break
                break

    def export(self) -> Dict[str, str]:
        """Export the full MoE model."""
        os.makedirs(self.config.output_dir, exist_ok=True)
        exported = {}

        # Full model export
        full_path = os.path.join(self.config.output_dir, "full_model.onnx")
        self._export_full(full_path)
        exported["full_model"] = full_path

        # Router-only export
        if self.config.export_router_separately:
            router_path = os.path.join(self.config.output_dir, "router.onnx")
            self._export_router(router_path)
            exported["router"] = router_path

        # Per-expert export
        if self.config.export_experts_separately:
            expert_dir = os.path.join(self.config.output_dir, "experts")
            self._export_experts(expert_dir)
            exported["experts_dir"] = expert_dir

        # Metadata
        if self.config.include_metadata:
            meta_path = os.path.join(self.config.output_dir, "metadata.json")
            self._write_metadata(meta_path, exported)
            exported["metadata"] = meta_path

        logger.info(f"Export complete: {exported}")
        return exported

    def _export_full(self, path: str):
        model = self.model
        if self.config.fp16:
            model = model.half()

        dummy = torch.randint(0, 100, (1, 32))
        if self.config.fp16:
            dummy = dummy.long()

        try:
            torch.onnx.export(
                model, dummy, path,
                input_names=["input_ids"],
                output_names=["logits"],
                dynamic_axes={"input_ids": {0: "batch", 1: "seq_len"},
                              "logits": {0: "batch", 1: "seq_len"}}
                    if self.config.dynamic_axes else None,
                opset_version=self.config.opset_version,
                do_constant_folding=self.config.optimize)
        except Exception as e:
            logger.error(f"Full model export failed: {e}")
            raise

    def _export_router(self, path: str):
        for m in self.model.modules():
            if hasattr(m, 'router') or hasattr(m, 'gate'):
                router = getattr(m, 'router', getattr(m, 'gate', None))
                if router is not None:
                    exporter = RouterExporter(router, self._num_experts, self._dim)
                    exporter.export(path, self.config)
                    return
        logger.warning("No router found for export")

    def _export_experts(self, expert_dir: str):
        for m in self.model.modules():
            if hasattr(m, 'experts') and isinstance(m.experts, nn.ModuleList):
                exporter = ExpertExporter(m.experts, self._dim)
                exporter.export_all(expert_dir, self.config)
                return

    def _write_metadata(self, path: str, exported: Dict):
        metadata = {
            "format": "onnx",
            "opset_version": self.config.opset_version,
            "num_experts": self._num_experts,
            "hidden_dim": self._dim,
            "fp16": self.config.fp16,
            "files": exported,
            "export_config": {
                "dynamic_axes": self.config.dynamic_axes,
                "optimized": self.config.optimize,
            }
        }
        with open(path, "w") as f:
            json.dump(metadata, f, indent=2)
