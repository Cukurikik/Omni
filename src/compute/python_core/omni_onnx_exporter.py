"""
OMNI Compute Layer — ONNX Model Exporter & Optimizer
Inspired by: LowinLi/fastgpt ONNX acceleration patterns.
Production ONNX export pipeline with quantization and graph optimization.
"""

import os
import logging
from dataclasses import dataclass, field
from typing import Optional, Tuple
from pathlib import Path

import torch
import torch.nn as nn
import numpy as np

logger = logging.getLogger("omni.onnx_exporter")


@dataclass
class OnnxExportConfig:
    """Configuration for ONNX model export."""
    opset_version: int = 17
    dynamic_axes: bool = True
    quantize: bool = True
    quantization_mode: str = "dynamic"  # "dynamic" | "static"
    optimize_graph: bool = True
    optimization_level: str = "all"  # "basic" | "extended" | "all"
    fp16: bool = False
    output_dir: str = "./onnx_models"
    verify_output: bool = True
    atol: float = 1e-4


class OmniOnnxExporter:
    """Production ONNX exporter for transformer models."""

    def __init__(self, config: OnnxExportConfig):
        self.config = config
        os.makedirs(config.output_dir, exist_ok=True)

    def export_model(
        self,
        model: nn.Module,
        dummy_input: dict,
        model_name: str,
        input_names: Optional[list] = None,
        output_names: Optional[list] = None,
    ) -> Path:
        """Export PyTorch model to ONNX format."""
        model.eval()
        onnx_path = Path(self.config.output_dir) / f"{model_name}.onnx"

        if input_names is None:
            input_names = list(dummy_input.keys())
        if output_names is None:
            output_names = ["logits"]

        dynamic_axes = None
        if self.config.dynamic_axes:
            dynamic_axes = {
                name: {0: "batch_size", 1: "sequence_length"}
                for name in input_names + output_names
            }

        logger.info(f"Exporting {model_name} to ONNX (opset={self.config.opset_version})")

        torch.onnx.export(
            model,
            tuple(dummy_input.values()),
            str(onnx_path),
            input_names=input_names,
            output_names=output_names,
            dynamic_axes=dynamic_axes,
            opset_version=self.config.opset_version,
            do_constant_folding=True,
        )

        logger.info(f"ONNX model saved to {onnx_path}")

        if self.config.optimize_graph:
            onnx_path = self._optimize_graph(onnx_path, model_name)

        if self.config.quantize:
            onnx_path = self._quantize_model(onnx_path, model_name)

        if self.config.verify_output:
            self._verify_output(model, dummy_input, onnx_path)

        return onnx_path

    def _optimize_graph(self, onnx_path: Path, model_name: str) -> Path:
        """Apply ONNX graph optimizations."""
        try:
            import onnxruntime as ort
            from onnxruntime.transformers import optimizer

            opt_model = optimizer.optimize_model(
                str(onnx_path),
                model_type="bert",
                num_heads=0,
                hidden_size=0,
                optimization_options=None,
            )

            optimized_path = Path(self.config.output_dir) / f"{model_name}_optimized.onnx"
            opt_model.save_model_to_file(str(optimized_path))
            logger.info(f"Optimized model saved: {optimized_path}")
            return optimized_path
        except ImportError:
            logger.warning("onnxruntime not available, skipping optimization")
            return onnx_path

    def _quantize_model(self, onnx_path: Path, model_name: str) -> Path:
        """Quantize ONNX model to INT8."""
        try:
            from onnxruntime.quantization import quantize_dynamic, QuantType

            quantized_path = Path(self.config.output_dir) / f"{model_name}_quantized.onnx"
            quantize_dynamic(
                model_input=str(onnx_path),
                model_output=str(quantized_path),
                weight_type=QuantType.QInt8,
                per_channel=True,
                reduce_range=True,
            )

            original_size = os.path.getsize(onnx_path) / (1024 * 1024)
            quantized_size = os.path.getsize(quantized_path) / (1024 * 1024)
            logger.info(
                f"Quantized: {original_size:.1f}MB -> {quantized_size:.1f}MB "
                f"({(1 - quantized_size/original_size)*100:.1f}% reduction)"
            )
            return quantized_path
        except ImportError:
            logger.warning("onnxruntime.quantization not available")
            return onnx_path

    def _verify_output(self, model: nn.Module, dummy_input: dict, onnx_path: Path):
        """Verify ONNX output matches PyTorch output."""
        try:
            import onnxruntime as ort

            session = ort.InferenceSession(str(onnx_path))
            ort_inputs = {
                k: v.numpy() if isinstance(v, torch.Tensor) else v
                for k, v in dummy_input.items()
            }

            with torch.no_grad():
                pt_output = model(**dummy_input)
                if isinstance(pt_output, tuple):
                    pt_output = pt_output[0]

            ort_output = session.run(None, ort_inputs)[0]
            max_diff = np.max(np.abs(pt_output.numpy() - ort_output))

            if max_diff < self.config.atol:
                logger.info(f"Verification PASSED (max_diff={max_diff:.6f})")
            else:
                logger.warning(f"Verification WARNING: max_diff={max_diff:.6f} > atol={self.config.atol}")
        except Exception as e:
            logger.warning(f"Verification skipped: {e}")


class OmniOnnxInferenceSession:
    """Production ONNX Runtime inference session with optimization."""

    def __init__(self, model_path: str, use_gpu: bool = False, num_threads: int = 4):
        import onnxruntime as ort

        options = ort.SessionOptions()
        options.graph_optimization_level = ort.GraphOptimizationLevel.ORT_ENABLE_ALL
        options.intra_op_num_threads = num_threads
        options.inter_op_num_threads = num_threads
        options.enable_mem_pattern = True

        providers = ["CUDAExecutionProvider", "CPUExecutionProvider"] if use_gpu else ["CPUExecutionProvider"]

        self.session = ort.InferenceSession(model_path, sess_options=options, providers=providers)
        self.input_names = [inp.name for inp in self.session.get_inputs()]
        self.output_names = [out.name for out in self.session.get_outputs()]
        logger.info(f"ONNX session loaded: {model_path} (providers={providers})")

    def run(self, **kwargs) -> np.ndarray:
        """Run inference."""
        inputs = {k: v.numpy() if isinstance(v, torch.Tensor) else v for k, v in kwargs.items()}
        return self.session.run(self.output_names, inputs)

    def benchmark(self, inputs: dict, warmup: int = 5, iterations: int = 50) -> dict:
        """Benchmark inference latency."""
        import time

        np_inputs = {k: v.numpy() if isinstance(v, torch.Tensor) else v for k, v in inputs.items()}

        for _ in range(warmup):
            self.session.run(self.output_names, np_inputs)

        latencies = []
        for _ in range(iterations):
            start = time.perf_counter()
            self.session.run(self.output_names, np_inputs)
            latencies.append((time.perf_counter() - start) * 1000)

        return {
            "mean_ms": float(np.mean(latencies)),
            "p50_ms": float(np.percentile(latencies, 50)),
            "p95_ms": float(np.percentile(latencies, 95)),
            "p99_ms": float(np.percentile(latencies, 99)),
            "throughput_qps": 1000.0 / float(np.mean(latencies)),
        }
