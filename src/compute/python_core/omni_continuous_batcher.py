"""
OMNI Compute — Continuous Batching Scheduler
Dynamic batching for maximum GPU utilization during inference.
"""
import time, logging, heapq
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple
from collections import deque
from enum import Enum

logger = logging.getLogger("omni.batcher")

class RequestState(Enum):
    WAITING = "waiting"; RUNNING = "running"; COMPLETED = "completed"; TIMEOUT = "timeout"

@dataclass(order=True)
class InferenceRequest:
    priority: int
    request_id: str = field(compare=False)
    prompt_tokens: List[int] = field(compare=False, default_factory=list)
    max_new_tokens: int = field(compare=False, default=256)
    temperature: float = field(compare=False, default=0.7)
    state: RequestState = field(compare=False, default=RequestState.WAITING)
    generated_tokens: List[int] = field(compare=False, default_factory=list)
    arrival_time: float = field(compare=False, default_factory=time.time)
    deadline_ms: float = field(compare=False, default=30000)

    @property
    def is_complete(self) -> bool:
        return len(self.generated_tokens) >= self.max_new_tokens

    @property
    def total_tokens(self) -> int:
        return len(self.prompt_tokens) + len(self.generated_tokens)

class OmniContinuousBatcher:
    """Continuous batching scheduler that maximizes GPU throughput."""
    def __init__(self, max_batch_size: int = 32, max_total_tokens: int = 8192,
                 max_waiting_ms: float = 100):
        self.max_batch = max_batch_size
        self.max_total_tokens = max_total_tokens
        self.max_waiting = max_waiting_ms / 1000.0
        self.waiting: List[InferenceRequest] = []  # min-heap by priority
        self.running: Dict[str, InferenceRequest] = {}
        self.completed: deque = deque(maxlen=10000)
        self.stats = {"batches": 0, "total_requests": 0, "total_tokens": 0, "timeouts": 0,
                      "avg_batch_size": 0.0, "total_latency_ms": 0.0}

    def add_request(self, request: InferenceRequest):
        heapq.heappush(self.waiting, request)
        self.stats["total_requests"] += 1

    def form_batch(self) -> List[InferenceRequest]:
        """Form optimal batch from waiting + running requests."""
        batch = list(self.running.values())
        total_tokens = sum(r.total_tokens for r in batch)

        # Add waiting requests that fit
        temp_waiting = []
        while self.waiting and len(batch) < self.max_batch:
            req = heapq.heappop(self.waiting)
            # Check deadline
            if (time.time() - req.arrival_time) * 1000 > req.deadline_ms:
                req.state = RequestState.TIMEOUT
                self.stats["timeouts"] += 1
                self.completed.append(req)
                continue
            if total_tokens + req.total_tokens <= self.max_total_tokens:
                req.state = RequestState.RUNNING
                self.running[req.request_id] = req
                batch.append(req)
                total_tokens += req.total_tokens
            else:
                temp_waiting.append(req)

        for r in temp_waiting:
            heapq.heappush(self.waiting, r)

        if batch:
            self.stats["batches"] += 1
            n = self.stats["batches"]
            self.stats["avg_batch_size"] = ((self.stats["avg_batch_size"] * (n-1)) + len(batch)) / n

        return batch

    def process_outputs(self, outputs: Dict[str, int]):
        """Update requests with generated tokens."""
        finished = []
        for req_id, token_id in outputs.items():
            if req_id in self.running:
                req = self.running[req_id]
                req.generated_tokens.append(token_id)
                self.stats["total_tokens"] += 1
                if req.is_complete:
                    finished.append(req_id)

        for req_id in finished:
            req = self.running.pop(req_id)
            req.state = RequestState.COMPLETED
            latency = (time.time() - req.arrival_time) * 1000
            self.stats["total_latency_ms"] += latency
            self.completed.append(req)

    def get_stats(self) -> Dict:
        completed_count = len(self.completed)
        avg_lat = self.stats["total_latency_ms"] / max(completed_count, 1)
        return {**self.stats, "waiting": len(self.waiting), "running": len(self.running),
                "completed": completed_count, "avg_latency_ms": round(avg_lat, 2)}
