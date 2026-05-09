"""
OMNI Compute — Data Selection Engine (Data-Whisperer-inspired)
Few-shot ICL data selection for efficient LLM fine-tuning.
"""
import logging, hashlib, random
from dataclasses import dataclass, field
from typing import List, Optional, Callable
import numpy as np

logger = logging.getLogger("omni.data_selector")

@dataclass
class DataSample:
    text: str; label: str = ""; quality_score: float = 0.0
    embedding: Optional[List[float]] = None
    sample_id: str = ""
    def __post_init__(self):
        if not self.sample_id:
            self.sample_id = hashlib.md5(self.text.encode()).hexdigest()[:12]

@dataclass
class SelectionConfig:
    target_size: int = 1000; diversity_weight: float = 0.3
    quality_weight: float = 0.5; relevance_weight: float = 0.2
    min_text_length: int = 50; max_text_length: int = 4096
    dedup_threshold: float = 0.95

class OmniDataSelector:
    """Production data selector for LLM fine-tuning datasets."""
    def __init__(self, config: SelectionConfig):
        self.config = config
        self.corpus: List[DataSample] = []
    def add_samples(self, samples: List[DataSample]):
        filtered = [s for s in samples if self.config.min_text_length <= len(s.text) <= self.config.max_text_length]
        self.corpus.extend(filtered)
        logger.info(f"Added {len(filtered)}/{len(samples)} samples (total={len(self.corpus)})")
    def deduplicate(self) -> int:
        if not self.corpus: return 0
        seen, unique, removed = set(), [], 0
        for s in self.corpus:
            fp = hashlib.md5(s.text.strip().lower().encode()).hexdigest()
            if fp not in seen: seen.add(fp); unique.append(s)
            else: removed += 1
        self.corpus = unique
        logger.info(f"Dedup removed {removed} samples")
        return removed
    def select_diverse(self, embed_fn: Callable[[List[str]], List[List[float]]]) -> List[DataSample]:
        """Select diverse subset using greedy farthest-point sampling."""
        if len(self.corpus) <= self.config.target_size: return self.corpus
        texts = [s.text for s in self.corpus]
        embeddings = np.array(embed_fn(texts), dtype=np.float32)
        norms = np.linalg.norm(embeddings, axis=1, keepdims=True)
        embeddings = embeddings / np.where(norms == 0, 1, norms)
        selected_idx = [random.randint(0, len(self.corpus) - 1)]
        min_dists = np.ones(len(self.corpus)) * np.inf
        for _ in range(self.config.target_size - 1):
            last_emb = embeddings[selected_idx[-1]]
            dists = 1.0 - embeddings @ last_emb
            min_dists = np.minimum(min_dists, dists)
            min_dists[selected_idx] = -1
            next_idx = int(np.argmax(min_dists))
            selected_idx.append(next_idx)
        return [self.corpus[i] for i in selected_idx]
    def compute_quality_scores(self, scorer_fn: Callable[[str], float]):
        for s in self.corpus: s.quality_score = scorer_fn(s.text)
    def get_stats(self) -> dict:
        lengths = [len(s.text) for s in self.corpus]
        return {"total": len(self.corpus), "avg_len": np.mean(lengths) if lengths else 0,
                "min_len": min(lengths) if lengths else 0, "max_len": max(lengths) if lengths else 0}
