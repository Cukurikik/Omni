"""
OMNI Transformer — Model Benchmarking Suite
Latency, throughput, and memory benchmarks for transformer models.
"""
import time
import torch
import torch.nn as nn
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)


@dataclass
class BenchmarkConfig:
    batch_sizes: List[int] = None
    seq_lengths: List[int] = None
    num_warmup: int = 5
    num_iterations: int = 20
    device: str = "cuda"

    def __post_init__(self):
        if self.batch_sizes is None:
            self.batch_sizes = [1, 4, 8, 16, 32]
        if self.seq_lengths is None:
            self.seq_lengths = [128, 256, 512, 1024]


class ModelBenchmark:
    """Comprehensive benchmarking for transformer models."""
    def __init__(self, model: nn.Module, config: BenchmarkConfig = None):
        self.model = model
        self.config = config or BenchmarkConfig()
        self.device = torch.device(self.config.device if torch.cuda.is_available() else "cpu")
        self.model.to(self.device).eval()

    @torch.inference_mode()
    def benchmark_latency(self, batch_size: int = 1, seq_len: int = 128,
                           vocab_size: int = 32000) -> Dict[str, float]:
        """Measure inference latency."""
        input_ids = torch.randint(0, vocab_size, (batch_size, seq_len), device=self.device)
        # Warmup
        for _ in range(self.config.num_warmup):
            self.model(input_ids)
        if torch.cuda.is_available():
            torch.cuda.synchronize()

        times = []
        for _ in range(self.config.num_iterations):
            start = time.perf_counter()
            self.model(input_ids)
            if torch.cuda.is_available():
                torch.cuda.synchronize()
            times.append((time.perf_counter() - start) * 1000)

        return {
            "mean_ms": sum(times) / len(times),
            "min_ms": min(times),
            "max_ms": max(times),
            "p50_ms": sorted(times)[len(times) // 2],
            "p99_ms": sorted(times)[int(len(times) * 0.99)],
            "throughput_tokens_per_sec": batch_size * seq_len / (sum(times) / len(times) / 1000),
        }

    @torch.inference_mode()
    def benchmark_memory(self, batch_size: int = 1, seq_len: int = 512,
                          vocab_size: int = 32000) -> Dict[str, float]:
        """Measure GPU memory usage."""
        if not torch.cuda.is_available():
            return {"allocated_mb": 0, "peak_mb": 0}
        torch.cuda.reset_peak_memory_stats()
        torch.cuda.empty_cache()

        baseline = torch.cuda.memory_allocated() / 1e6
        input_ids = torch.randint(0, vocab_size, (batch_size, seq_len), device=self.device)
        self.model(input_ids)
        torch.cuda.synchronize()

        return {
            "model_mb": baseline,
            "peak_mb": torch.cuda.max_memory_allocated() / 1e6,
            "activation_mb": (torch.cuda.max_memory_allocated() - torch.cuda.memory_allocated()) / 1e6,
        }

    def full_benchmark(self, vocab_size: int = 32000) -> List[Dict]:
        """Run full benchmark across batch sizes and sequence lengths."""
        results = []
        for bs in self.config.batch_sizes:
            for sl in self.config.seq_lengths:
                try:
                    latency = self.benchmark_latency(bs, sl, vocab_size)
                    memory = self.benchmark_memory(bs, sl, vocab_size)
                    result = {"batch_size": bs, "seq_len": sl, **latency, **memory}
                    results.append(result)
                    logger.info(f"B={bs} S={sl}: {latency['mean_ms']:.1f}ms, {latency['throughput_tokens_per_sec']:.0f} tok/s")
                except RuntimeError as e:
                    logger.warning(f"OOM at B={bs} S={sl}: {e}")
                    if torch.cuda.is_available():
                        torch.cuda.empty_cache()
        return results
