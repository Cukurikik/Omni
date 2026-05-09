"""
OMNI MOTHER: Continuous Batching Engine (Production Grade)
Dynamically adds/removes sequences from a running inference batch.
Maximizes GPU utilization by not waiting for the longest sequence.
Ref: "Orca: A Distributed Serving System for Transformer-Based Generative Models"
"""
import logging
import time
from collections import deque
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Callable, Dict, List, Optional
import torch

logger = logging.getLogger("OmniBatch")

class SeqStatus(Enum):
    WAITING = auto()
    RUNNING = auto()
    FINISHED = auto()
    PREEMPTED = auto()

@dataclass
class SequenceRequest:
    seq_id: int
    input_ids: torch.Tensor
    max_new_tokens: int = 256
    temperature: float = 1.0
    top_p: float = 0.9
    eos_token_id: int = 2
    status: SeqStatus = SeqStatus.WAITING
    generated_ids: List[int] = field(default_factory=list)
    arrival_time: float = field(default_factory=time.time)
    start_time: Optional[float] = None
    end_time: Optional[float] = None

    @property
    def total_len(self) -> int:
        return self.input_ids.size(-1) + len(self.generated_ids)

    @property
    def is_done(self) -> bool:
        if len(self.generated_ids) >= self.max_new_tokens:
            return True
        if self.generated_ids and self.generated_ids[-1] == self.eos_token_id:
            return True
        return False

class ContinuousBatchScheduler:
    """
    Iteration-level scheduling: after EACH forward pass, finished sequences
    are evicted and waiting sequences are admitted, maximizing throughput.
    """
    def __init__(self, max_batch_size: int = 32, max_total_tokens: int = 8192):
        self.max_batch = max_batch_size
        self.max_tokens = max_total_tokens
        self.waiting: deque[SequenceRequest] = deque()
        self.running: Dict[int, SequenceRequest] = {}
        self.finished: List[SequenceRequest] = []
        self._next_id = 0

    def add_request(self, input_ids: torch.Tensor, **kwargs) -> int:
        sid = self._next_id
        self._next_id += 1
        req = SequenceRequest(seq_id=sid, input_ids=input_ids, **kwargs)
        self.waiting.append(req)
        logger.info(f"Queued seq {sid} (prompt_len={input_ids.size(-1)})")
        return sid

    def _total_running_tokens(self) -> int:
        return sum(r.total_len for r in self.running.values())

    def schedule(self) -> List[SequenceRequest]:
        """Admit waiting sequences into the running batch if capacity allows."""
        # Evict finished
        to_remove = [sid for sid, r in self.running.items() if r.is_done]
        for sid in to_remove:
            req = self.running.pop(sid)
            req.status = SeqStatus.FINISHED
            req.end_time = time.time()
            self.finished.append(req)
            logger.info(f"Seq {sid} finished ({len(req.generated_ids)} tokens, "
                         f"{req.end_time - (req.start_time or req.arrival_time):.2f}s)")

        # Admit new sequences
        while self.waiting and len(self.running) < self.max_batch:
            candidate = self.waiting[0]
            projected_tokens = self._total_running_tokens() + candidate.input_ids.size(-1)
            if projected_tokens > self.max_tokens:
                break
            req = self.waiting.popleft()
            req.status = SeqStatus.RUNNING
            req.start_time = time.time()
            self.running[req.seq_id] = req

        return list(self.running.values())

    def update_generated(self, seq_id: int, token_id: int) -> None:
        if seq_id in self.running:
            self.running[seq_id].generated_ids.append(token_id)

    @property
    def has_work(self) -> bool:
        return bool(self.waiting or self.running)

    def stats(self) -> Dict:
        return {
            "waiting": len(self.waiting),
            "running": len(self.running),
            "finished": len(self.finished),
            "total_tokens_active": self._total_running_tokens(),
            "throughput_tps": self._compute_throughput(),
        }

    def _compute_throughput(self) -> float:
        if not self.finished:
            return 0.0
        total_tokens = sum(len(r.generated_ids) for r in self.finished)
        total_time = sum(
            (r.end_time or 0) - (r.start_time or r.arrival_time)
            for r in self.finished
        )
        return total_tokens / max(total_time, 1e-6)
