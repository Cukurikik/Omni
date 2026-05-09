"""OMNI Compute — Flash Decoding Scheduler"""
import time, logging; from dataclasses import dataclass, field; from typing import Dict, List
logger = logging.getLogger("omni.flash_decode")

@dataclass
class FlashDecodeConfig:
    max_batch: int = 256; split_k: int = 8; page_size: int = 256
    max_seq_len: int = 131072

class FlashDecodeScheduler:
    """Parallel KV-cache decoding across split-K partitions."""
    def __init__(self, config: FlashDecodeConfig):
        self.config = config; self.stats = {"total": 0, "splits_used": 0}
    def compute_splits(self, seq_len: int) -> int:
        if seq_len < 1024: return 1
        if seq_len < 8192: return min(4, self.config.split_k)
        return self.config.split_k
    def schedule_decode(self, batch_seq_lens: List[int]) -> List[Dict]:
        plan = []
        for i, sl in enumerate(batch_seq_lens):
            splits = self.compute_splits(sl)
            chunk = (sl + splits - 1) // splits
            partitions = []
            for s in range(splits):
                start = s * chunk; end = min(start + chunk, sl)
                if start < end: partitions.append({"start": start, "end": end, "pages": (end-start+self.config.page_size-1)//self.config.page_size})
            plan.append({"seq_idx": i, "seq_len": sl, "num_splits": splits, "partitions": partitions})
            self.stats["total"] += 1; self.stats["splits_used"] += splits
        return plan
    def get_stats(self) -> Dict:
        avg = self.stats["splits_used"] / max(self.stats["total"], 1)
        return {**self.stats, "avg_splits": round(avg, 2)}
