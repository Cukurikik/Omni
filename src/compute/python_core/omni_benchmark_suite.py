"""
OMNI Compute — Model Benchmarking Suite
Automated latency, throughput, and accuracy benchmarking.
"""
import time, logging, json, os, statistics
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Callable

logger = logging.getLogger("omni.benchmark")

@dataclass
class BenchmarkConfig:
    warmup_iterations: int = 5; benchmark_iterations: int = 50
    batch_sizes: List[int] = field(default_factory=lambda: [1, 4, 8, 16, 32])
    seq_lengths: List[int] = field(default_factory=lambda: [128, 256, 512, 1024])
    output_dir: str = "./benchmark_results"

@dataclass
class BenchmarkResult:
    name: str; batch_size: int; seq_length: int; mean_ms: float; p50_ms: float
    p95_ms: float; p99_ms: float; throughput_tps: float; std_ms: float

class OmniBenchmarkSuite:
    """Automated benchmarking for model inference performance."""
    def __init__(self, config: BenchmarkConfig):
        self.config = config; self.results: List[BenchmarkResult] = []
        os.makedirs(config.output_dir, exist_ok=True)
    def run_latency_bench(self, name: str, fn: Callable, batch_size: int, seq_len: int) -> BenchmarkResult:
        for _ in range(self.config.warmup_iterations): fn(batch_size, seq_len)
        latencies = []
        for _ in range(self.config.benchmark_iterations):
            start = time.perf_counter()
            fn(batch_size, seq_len)
            latencies.append((time.perf_counter() - start) * 1000)
        latencies.sort()
        n = len(latencies)
        result = BenchmarkResult(
            name=name, batch_size=batch_size, seq_length=seq_len,
            mean_ms=statistics.mean(latencies), p50_ms=latencies[n//2],
            p95_ms=latencies[int(n*0.95)], p99_ms=latencies[int(n*0.99)],
            throughput_tps=batch_size * 1000.0 / statistics.mean(latencies),
            std_ms=statistics.stdev(latencies) if n > 1 else 0
        )
        self.results.append(result)
        logger.info(f"{name} bs={batch_size} seq={seq_len}: mean={result.mean_ms:.2f}ms p95={result.p95_ms:.2f}ms tps={result.throughput_tps:.1f}")
        return result
    def run_sweep(self, name: str, fn: Callable) -> List[BenchmarkResult]:
        results = []
        for bs in self.config.batch_sizes:
            for sl in self.config.seq_lengths:
                results.append(self.run_latency_bench(name, fn, bs, sl))
        return results
    def compare(self, results_a: List[BenchmarkResult], results_b: List[BenchmarkResult]) -> List[Dict]:
        comparisons = []
        for a, b in zip(results_a, results_b):
            speedup = a.mean_ms / max(b.mean_ms, 0.01)
            comparisons.append({"config": f"bs={a.batch_size} seq={a.seq_length}",
                               "a_ms": round(a.mean_ms, 2), "b_ms": round(b.mean_ms, 2),
                               "speedup": round(speedup, 2)})
        return comparisons
    def save_results(self, name: str = "benchmark"):
        path = os.path.join(self.config.output_dir, f"{name}_{int(time.time())}.json")
        data = [{"name": r.name, "batch_size": r.batch_size, "seq_length": r.seq_length,
                 "mean_ms": r.mean_ms, "p50_ms": r.p50_ms, "p95_ms": r.p95_ms, "p99_ms": r.p99_ms,
                 "throughput_tps": r.throughput_tps} for r in self.results]
        with open(path, "w") as f: json.dump(data, f, indent=2)
        logger.info(f"Results saved: {path}")
