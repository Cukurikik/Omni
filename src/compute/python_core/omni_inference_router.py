"""OMNI Compute — Inference Router / Model Multiplexer"""
import time, logging, hashlib; from dataclasses import dataclass, field
from typing import Dict, List, Optional
from collections import defaultdict
logger = logging.getLogger("omni.router")

@dataclass
class ModelEndpoint:
    model_id: str; url: str; weight: float = 1.0; healthy: bool = True
    active_requests: int = 0; total_requests: int = 0; total_latency_ms: float = 0.0
    @property
    def avg_latency(self) -> float: return self.total_latency_ms / max(self.total_requests, 1)

class OmniInferenceRouter:
    """Route inference requests to optimal model endpoint."""
    def __init__(self, strategy: str = "least_loaded"):
        self.strategy = strategy  # least_loaded | round_robin | hash | random
        self.endpoints: Dict[str, List[ModelEndpoint]] = defaultdict(list)
        self.rr_counter: Dict[str, int] = defaultdict(int)
    def register(self, model_id: str, endpoint: ModelEndpoint):
        self.endpoints[model_id].append(endpoint)
    def route(self, model_id: str, prompt: str = "") -> Optional[ModelEndpoint]:
        eps = [e for e in self.endpoints.get(model_id, []) if e.healthy]
        if not eps: return None
        if self.strategy == "least_loaded":
            return min(eps, key=lambda e: e.active_requests)
        elif self.strategy == "round_robin":
            idx = self.rr_counter[model_id] % len(eps)
            self.rr_counter[model_id] += 1; return eps[idx]
        elif self.strategy == "hash":
            h = int(hashlib.md5(prompt.encode()).hexdigest(), 16)
            return eps[h % len(eps)]
        else:
            import random; return random.choice(eps)
    def record_request(self, ep: ModelEndpoint, latency_ms: float):
        ep.total_requests += 1; ep.total_latency_ms += latency_ms
    def get_stats(self) -> Dict:
        result = {}
        for model_id, eps in self.endpoints.items():
            result[model_id] = [{"url": e.url, "healthy": e.healthy, "active": e.active_requests,
                                  "total": e.total_requests, "avg_ms": round(e.avg_latency, 2)} for e in eps]
        return result
