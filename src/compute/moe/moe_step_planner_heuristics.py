# moe_step_planner_heuristics.py — Compute Layer: MoE Step Planner Heuristics
# Evaluates latency pressure and dynamically adjusts TensorRT-LLM batching windows.

from dataclasses import dataclass
from typing import List

@dataclass
class BatchMetric:
    batch_size: int
    tail_latency_ms: float
    throughput_tokens: float

class PlannerHeuristics:
    def __init__(self, target_latency_ms: float):
        self.target_latency = target_latency_ms
        self.history: List[BatchMetric] = []
        
    def add_metric(self, metric: BatchMetric) -> None:
        self.history.append(metric)
        if len(self.history) > 100:
            self.history.pop(0)
            
    def compute_optimal_batch_size(self, current_queue_size: int) -> int:
        """
        Monadic-style heuristic evaluating historical tail latency 
        against the strict SLA target.
        """
        if not self.history:
            return min(8, current_queue_size)
            
        recent_avg_latency = sum(m.tail_latency_ms for m in self.history[-5:]) / 5
        last_batch_size = self.history[-1].batch_size
        
        if recent_avg_latency < self.target_latency * 0.8:
            # Under target, can increase batch size to improve throughput
            return min(last_batch_size + 4, current_queue_size)
        elif recent_avg_latency > self.target_latency:
            # SLA breached, must reduce batch size
            return max(1, last_batch_size - 2)
            
        return last_batch_size
