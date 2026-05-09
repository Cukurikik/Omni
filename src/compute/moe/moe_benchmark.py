"""
moe_benchmark.py — MoE Kernel Performance Benchmark Suite
Reference: massif-01/benchmark_moe (vLLM MoE kernel benchmarks)
Layer: Compute / AI — MoE Performance

Benchmarks MoE router + expert execution kernels. Measures token routing
latency, expert computation throughput, all-to-all comm overhead, and
memory footprint across varying expert counts and token volumes.
"""
import torch
import torch.nn as nn
import torch.nn.functional as F
import time
import json
import os
from dataclasses import dataclass, field, asdict
from typing import List, Dict, Optional
import logging

logger = logging.getLogger(__name__)


@dataclass
class BenchmarkConfig:
    num_experts_list: List[int] = field(default_factory=lambda: [4, 8, 16, 32, 64])
    top_k_list: List[int] = field(default_factory=lambda: [1, 2, 4])
    batch_sizes: List[int] = field(default_factory=lambda: [1, 4, 16, 64])
    seq_lengths: List[int] = field(default_factory=lambda: [128, 512, 2048])
    hidden_dims: List[int] = field(default_factory=lambda: [768, 1024, 2048, 4096])
    warmup_iters: int = 5
    bench_iters: int = 20
    device: str = "cuda" if torch.cuda.is_available() else "cpu"
    output_file: str = "moe_benchmark_results.json"
    dtype: str = "float16"


@dataclass
class BenchmarkResult:
    num_experts: int
    top_k: int
    batch_size: int
    seq_len: int
    hidden_dim: int
    total_tokens: int
    router_latency_ms: float
    expert_latency_ms: float
    total_latency_ms: float
    tokens_per_second: float
    memory_mb: float
    expert_utilization: List[float]


class SimpleExpert(nn.Module):
    def __init__(self, dim, ff_mult=4):
        super().__init__()
        ff = int(dim * ff_mult)
        self.w1 = nn.Linear(dim, ff, bias=False)
        self.w2 = nn.Linear(ff, dim, bias=False)

    def forward(self, x):
        return self.w2(F.silu(self.w1(x)))


class BenchMoELayer(nn.Module):
    """Minimal MoE layer for benchmarking, no auxiliary losses."""
    def __init__(self, dim, num_experts, top_k):
        super().__init__()
        self.gate = nn.Linear(dim, num_experts, bias=False)
        self.experts = nn.ModuleList([SimpleExpert(dim) for _ in range(num_experts)])
        self.top_k = top_k
        self.num_experts = num_experts

    def forward(self, x):
        B, S, D = x.shape
        flat = x.reshape(-1, D)
        logits = self.gate(flat)
        weights, indices = torch.topk(F.softmax(logits, dim=-1), self.top_k, dim=-1)
        output = torch.zeros_like(flat)
        for e in range(self.num_experts):
            mask = (indices == e).any(dim=-1)
            if not mask.any():
                continue
            tok = mask.nonzero(as_tuple=True)[0]
            e_out = self.experts[e](flat[tok])
            for k in range(self.top_k):
                km = indices[tok, k] == e
                if km.any():
                    ki = tok[km]
                    output[ki] += e_out[km] * weights[ki, k].unsqueeze(-1)
        return output.reshape(B, S, D), indices


def _get_dtype(name):
    return {"float16": torch.float16, "bfloat16": torch.bfloat16,
            "float32": torch.float32}.get(name, torch.float32)


def benchmark_single(config, num_experts, top_k, batch_size, seq_len, dim):
    """Run a single benchmark configuration."""
    device = torch.device(config.device)
    dtype = _get_dtype(config.dtype)

    model = BenchMoELayer(dim, num_experts, top_k).to(device=device, dtype=dtype)
    model.eval()

    x = torch.randn(batch_size, seq_len, dim, device=device, dtype=dtype)
    total_tokens = batch_size * seq_len

    # Warmup
    for _ in range(config.warmup_iters):
        with torch.no_grad():
            model(x)
    if device.type == "cuda":
        torch.cuda.synchronize()

    # Router benchmark
    flat = x.reshape(-1, dim)
    if device.type == "cuda":
        torch.cuda.synchronize()
    t0 = time.perf_counter()
    for _ in range(config.bench_iters):
        with torch.no_grad():
            logits = model.gate(flat)
            _ = torch.topk(F.softmax(logits, dim=-1), top_k, dim=-1)
    if device.type == "cuda":
        torch.cuda.synchronize()
    router_ms = (time.perf_counter() - t0) / config.bench_iters * 1000

    # Full forward benchmark
    if device.type == "cuda":
        torch.cuda.synchronize()
    t0 = time.perf_counter()
    for _ in range(config.bench_iters):
        with torch.no_grad():
            out, indices = model(x)
    if device.type == "cuda":
        torch.cuda.synchronize()
    total_ms = (time.perf_counter() - t0) / config.bench_iters * 1000
    expert_ms = total_ms - router_ms

    # Expert utilization
    usage = []
    for e in range(num_experts):
        frac = ((indices == e).any(dim=-1).float().sum() / total_tokens).item()
        usage.append(round(frac, 4))

    # Memory
    if device.type == "cuda":
        mem_mb = torch.cuda.max_memory_allocated(device) / (1024 ** 2)
    else:
        mem_mb = sum(p.numel() * p.element_size() for p in model.parameters()) / (1024**2)

    tps = total_tokens / (total_ms / 1000) if total_ms > 0 else 0

    return BenchmarkResult(
        num_experts=num_experts, top_k=top_k, batch_size=batch_size,
        seq_len=seq_len, hidden_dim=dim, total_tokens=total_tokens,
        router_latency_ms=round(router_ms, 3),
        expert_latency_ms=round(expert_ms, 3),
        total_latency_ms=round(total_ms, 3),
        tokens_per_second=round(tps, 1),
        memory_mb=round(mem_mb, 2),
        expert_utilization=usage)


def run_benchmark_suite(config: BenchmarkConfig) -> List[Dict]:
    """Run full benchmark suite across all configurations."""
    results = []
    total = (len(config.num_experts_list) * len(config.top_k_list) *
             len(config.batch_sizes) * len(config.seq_lengths) *
             len(config.hidden_dims))
    idx = 0

    for ne in config.num_experts_list:
        for tk in config.top_k_list:
            if tk > ne:
                continue
            for bs in config.batch_sizes:
                for sl in config.seq_lengths:
                    for hd in config.hidden_dims:
                        idx += 1
                        logger.info(f"[{idx}/{total}] E={ne} K={tk} B={bs} S={sl} D={hd}")
                        try:
                            r = benchmark_single(config, ne, tk, bs, sl, hd)
                            results.append(asdict(r))
                            logger.info(f"  -> {r.total_latency_ms:.1f}ms, "
                                        f"{r.tokens_per_second:.0f} tok/s")
                        except (RuntimeError, torch.cuda.OutOfMemoryError) as e:
                            logger.warning(f"  -> OOM/Error: {e}")
                            if torch.cuda.is_available():
                                torch.cuda.empty_cache()

    with open(config.output_file, "w") as f:
        json.dump(results, f, indent=2)
    logger.info(f"Saved {len(results)} results to {config.output_file}")
    return results


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    cfg = BenchmarkConfig(
        num_experts_list=[4, 8, 16],
        top_k_list=[1, 2],
        batch_sizes=[1, 4],
        seq_lengths=[128, 512],
        hidden_dims=[768])
    run_benchmark_suite(cfg)
