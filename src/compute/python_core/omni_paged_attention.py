"""
OMNI Compute — vLLM-style Paged Attention Engine
Paged KV-cache management for high-throughput serving.
"""
import logging, time, math
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple
from collections import deque

logger = logging.getLogger("omni.paged_attn")

BLOCK_SIZE = 16  # tokens per block

@dataclass
class KVBlock:
    block_id: int; num_filled: int = 0; ref_count: int = 1
    key_data: Optional[List[float]] = None; value_data: Optional[List[float]] = None
    @property
    def is_full(self) -> bool: return self.num_filled >= BLOCK_SIZE

class BlockAllocator:
    """Manages physical KV-cache blocks."""
    def __init__(self, num_blocks: int, head_dim: int):
        self.total = num_blocks; self.head_dim = head_dim
        self.free_blocks: deque = deque(range(num_blocks))
        self.blocks: Dict[int, KVBlock] = {}
    def allocate(self) -> Optional[KVBlock]:
        if not self.free_blocks: return None
        bid = self.free_blocks.popleft()
        block = KVBlock(block_id=bid)
        self.blocks[bid] = block
        return block
    def free(self, block_id: int):
        if block_id in self.blocks:
            self.blocks[block_id].ref_count -= 1
            if self.blocks[block_id].ref_count <= 0:
                del self.blocks[block_id]; self.free_blocks.append(block_id)
    @property
    def num_free(self) -> int: return len(self.free_blocks)
    @property
    def utilization(self) -> float: return 1.0 - len(self.free_blocks) / max(self.total, 1)

@dataclass
class SequenceState:
    seq_id: str; prompt_tokens: List[int]; generated_tokens: List[int] = field(default_factory=list)
    block_table: List[int] = field(default_factory=list)
    is_finished: bool = False; arrival_time: float = 0.0
    @property
    def total_len(self) -> int: return len(self.prompt_tokens) + len(self.generated_tokens)
    @property
    def num_blocks_needed(self) -> int: return math.ceil(self.total_len / BLOCK_SIZE)

class OmniPagedAttentionEngine:
    """Paged attention engine for high-throughput LLM serving."""
    def __init__(self, num_gpu_blocks: int = 1024, head_dim: int = 128, num_layers: int = 32):
        self.allocator = BlockAllocator(num_gpu_blocks, head_dim)
        self.num_layers = num_layers; self.head_dim = head_dim
        self.running: Dict[str, SequenceState] = {}
        self.waiting: deque = deque()
        self.stats = {"total_scheduled": 0, "preemptions": 0, "completed": 0, "oom_events": 0}

    def add_request(self, seq_id: str, prompt_tokens: List[int]):
        seq = SequenceState(seq_id=seq_id, prompt_tokens=prompt_tokens, arrival_time=time.time())
        self.waiting.append(seq)
        logger.info(f"Request {seq_id} queued (prompt={len(prompt_tokens)} tokens)")

    def schedule_step(self) -> List[SequenceState]:
        """Schedule sequences for the next step using FCFS."""
        scheduled = list(self.running.values())
        while self.waiting:
            seq = self.waiting[0]
            blocks_needed = seq.num_blocks_needed * self.num_layers
            if self.allocator.num_free >= blocks_needed:
                self.waiting.popleft()
                for _ in range(seq.num_blocks_needed):
                    block = self.allocator.allocate()
                    if block: seq.block_table.append(block.block_id)
                self.running[seq.seq_id] = seq; scheduled.append(seq)
                self.stats["total_scheduled"] += 1
            else:
                if not self.running: self.stats["oom_events"] += 1
                break
        return scheduled

    def process_outputs(self, outputs: Dict[str, int]):
        """Process generated tokens from model output."""
        for seq_id, token_id in outputs.items():
            if seq_id in self.running:
                seq = self.running[seq_id]
                seq.generated_tokens.append(token_id)
                if seq.total_len % BLOCK_SIZE == 0:
                    block = self.allocator.allocate()
                    if block: seq.block_table.append(block.block_id)

    def finish_sequence(self, seq_id: str):
        if seq_id in self.running:
            seq = self.running.pop(seq_id)
            for bid in seq.block_table: self.allocator.free(bid)
            seq.is_finished = True; self.stats["completed"] += 1

    def preempt_lowest_priority(self):
        """Preempt the last-arrived sequence to free blocks."""
        if not self.running: return
        victim_id = max(self.running.keys(), key=lambda k: self.running[k].arrival_time)
        victim = self.running.pop(victim_id)
        for bid in victim.block_table: self.allocator.free(bid)
        victim.block_table.clear(); self.waiting.appendleft(victim)
        self.stats["preemptions"] += 1

    def get_stats(self) -> Dict:
        return {**self.stats, "running": len(self.running), "waiting": len(self.waiting),
                "block_utilization": f"{self.allocator.utilization:.1%}",
                "free_blocks": self.allocator.num_free}
