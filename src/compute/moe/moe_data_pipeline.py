"""
moe_data_pipeline.py — MoE-Aware Data Pipeline
Layer: Compute / AI — MoE Training Data

Data pipeline optimized for MoE training:
- Expert-balanced batching (ensures diverse expert activation)
- Domain-tagged data for expert specialization analysis
- Curriculum-based data ordering for progressive training
- Routing statistics collection per data shard
"""
import torch
from torch.utils.data import Dataset, DataLoader, Sampler
from typing import Dict, List, Optional, Iterator, Tuple
from dataclasses import dataclass, field
from collections import defaultdict
import random
import math
import logging

logger = logging.getLogger(__name__)


@dataclass
class DataShardInfo:
    shard_id: int
    domain: str
    num_samples: int
    path: str
    difficulty: float = 0.5  # 0=easy, 1=hard
    expert_affinity: Optional[Dict[int, float]] = None


@dataclass
class PipelineConfig:
    batch_size: int = 32
    max_seq_len: int = 2048
    num_workers: int = 4
    domain_balanced: bool = True
    curriculum: bool = False
    curriculum_warmup_steps: int = 5000
    shuffle: bool = True
    drop_last: bool = True


class DomainTaggedSample:
    """A training sample with domain metadata for expert analysis."""
    __slots__ = ['input_ids', 'labels', 'domain', 'difficulty', 'shard_id']

    def __init__(self, input_ids, labels, domain="general",
                 difficulty=0.5, shard_id=0):
        self.input_ids = input_ids
        self.labels = labels
        self.domain = domain
        self.difficulty = difficulty
        self.shard_id = shard_id


class MoETrainingDataset(Dataset):
    """Dataset that maintains domain metadata for expert-aware training."""
    def __init__(self, shards: List[DataShardInfo], max_seq_len: int):
        self.max_seq_len = max_seq_len
        self.samples: List[DomainTaggedSample] = []
        self.domain_indices: Dict[str, List[int]] = defaultdict(list)
        self.shard_info = {s.shard_id: s for s in shards}

        self._load_shards(shards)

    def _load_shards(self, shards: List[DataShardInfo]):
        """Load and index all shards."""
        idx = 0
        for shard in shards:
            for i in range(shard.num_samples):
                # Generate sample (in production: load from disk)
                seq_len = min(self.max_seq_len, random.randint(64, self.max_seq_len))
                sample = DomainTaggedSample(
                    input_ids=torch.randint(0, 32000, (seq_len,)),
                    labels=torch.randint(0, 32000, (seq_len,)),
                    domain=shard.domain,
                    difficulty=shard.difficulty,
                    shard_id=shard.shard_id)
                self.samples.append(sample)
                self.domain_indices[shard.domain].append(idx)
                idx += 1

        logger.info(f"Loaded {len(self.samples)} samples across "
                     f"{len(self.domain_indices)} domains")

    def __len__(self):
        return len(self.samples)

    def __getitem__(self, idx):
        s = self.samples[idx]
        return {
            "input_ids": s.input_ids,
            "labels": s.labels,
            "domain": s.domain,
            "difficulty": s.difficulty,
            "shard_id": s.shard_id,
        }

    def get_domain_distribution(self) -> Dict[str, int]:
        return {d: len(ids) for d, ids in self.domain_indices.items()}


class DomainBalancedSampler(Sampler[int]):
    """Sampler that balances domain representation within each batch."""
    def __init__(self, dataset: MoETrainingDataset, batch_size: int,
                 shuffle: bool = True, seed: int = 42):
        self.dataset = dataset
        self.batch_size = batch_size
        self.shuffle = shuffle
        self.rng = random.Random(seed)
        self.domains = list(dataset.domain_indices.keys())

    def __iter__(self) -> Iterator[int]:
        domain_pools = {
            d: list(ids) for d, ids in self.dataset.domain_indices.items()
        }
        if self.shuffle:
            for pool in domain_pools.values():
                self.rng.shuffle(pool)

        per_domain = max(1, self.batch_size // len(self.domains))
        total = len(self.dataset)
        yielded = 0

        while yielded < total:
            batch_indices = []
            for domain in self.domains:
                pool = domain_pools[domain]
                take = min(per_domain, len(pool))
                batch_indices.extend(pool[:take])
                domain_pools[domain] = pool[take:]
                # Refill if exhausted
                if len(domain_pools[domain]) == 0:
                    domain_pools[domain] = list(
                        self.dataset.domain_indices[domain])
                    if self.shuffle:
                        self.rng.shuffle(domain_pools[domain])

            if self.shuffle:
                self.rng.shuffle(batch_indices)
            for idx in batch_indices:
                yield idx
                yielded += 1
                if yielded >= total:
                    break

    def __len__(self):
        return len(self.dataset)


class CurriculumSampler(Sampler[int]):
    """Sampler that orders data by difficulty for curriculum learning."""
    def __init__(self, dataset: MoETrainingDataset, total_steps: int,
                 warmup_steps: int = 5000, seed: int = 42):
        self.dataset = dataset
        self.total_steps = total_steps
        self.warmup_steps = warmup_steps
        self.rng = random.Random(seed)
        self.current_step = 0

    def __iter__(self) -> Iterator[int]:
        difficulties = [(i, s.difficulty) for i, s in enumerate(self.dataset.samples)]
        difficulties.sort(key=lambda x: x[1])

        max_difficulty = self._difficulty_threshold()
        eligible = [idx for idx, d in difficulties if d <= max_difficulty]

        if len(eligible) == 0:
            eligible = list(range(len(self.dataset)))

        self.rng.shuffle(eligible)
        for idx in eligible:
            yield idx

    def set_step(self, step: int):
        self.current_step = step

    def _difficulty_threshold(self) -> float:
        progress = min(1.0, self.current_step / max(self.warmup_steps, 1))
        return progress  # Linear ramp from 0 to 1

    def __len__(self):
        return len(self.dataset)


class ExpertRoutingCollector:
    """Collects per-domain routing statistics during training."""
    def __init__(self, num_experts: int):
        self.num_experts = num_experts
        self.domain_expert_counts: Dict[str, torch.Tensor] = defaultdict(
            lambda: torch.zeros(num_experts))
        self.total_per_domain: Dict[str, int] = defaultdict(int)

    def collect(self, domains: List[str], expert_indices: torch.Tensor):
        for i, domain in enumerate(domains):
            for k in range(expert_indices.shape[1]):
                eid = expert_indices[i, k].item()
                if 0 <= eid < self.num_experts:
                    self.domain_expert_counts[domain][eid] += 1
            self.total_per_domain[domain] += 1

    def specialization_report(self) -> Dict[str, Dict[int, float]]:
        report = {}
        for domain, counts in self.domain_expert_counts.items():
            total = self.total_per_domain[domain]
            if total > 0:
                probs = counts / total
                report[domain] = {
                    e: probs[e].item()
                    for e in range(self.num_experts) if probs[e] > 0.01
                }
        return report


def create_moe_dataloader(
    shards: List[DataShardInfo],
    config: PipelineConfig,
) -> DataLoader:
    """Create a DataLoader optimized for MoE training."""
    dataset = MoETrainingDataset(shards, config.max_seq_len)

    if config.domain_balanced:
        sampler = DomainBalancedSampler(
            dataset, config.batch_size, config.shuffle)
    else:
        sampler = None

    return DataLoader(
        dataset,
        batch_size=config.batch_size,
        sampler=sampler,
        shuffle=(config.shuffle and sampler is None),
        num_workers=config.num_workers,
        drop_last=config.drop_last,
        pin_memory=True,
    )
