"""
OMNI Transformer — Data Selection for Efficient Fine-Tuning
Intelligent data selection using few-shot in-context learning.
Learned from: gszfwsb/Data-Whisperer (ACL 2025)
"""
import torch
import torch.nn.functional as F
import logging
from typing import List, Dict, Any, Optional, Callable
from dataclasses import dataclass
import random

logger = logging.getLogger(__name__)


@dataclass
class DataSelectionConfig:
    budget: int = 1000  # Number of samples to select
    scoring_method: str = "influence"  # "influence", "diversity", "uncertainty", "hybrid"
    diversity_weight: float = 0.3
    seed: int = 42


class InfluenceScorer:
    """Score training examples by their influence on target task performance."""
    def __init__(self, embed_fn: Optional[Callable] = None):
        self.embed_fn = embed_fn

    def score(self, candidates: List[Dict], target_examples: List[Dict]) -> List[float]:
        if self.embed_fn is None:
            return [random.random() for _ in candidates]
        cand_texts = [c["text"] for c in candidates]
        target_texts = [t["text"] for t in target_examples]
        cand_embs = torch.tensor(self.embed_fn(cand_texts))
        target_embs = torch.tensor(self.embed_fn(target_texts))
        cand_norm = F.normalize(cand_embs, dim=-1)
        target_norm = F.normalize(target_embs, dim=-1)
        sim_matrix = torch.mm(cand_norm, target_norm.t())
        return sim_matrix.mean(dim=1).tolist()


class DiversitySelector:
    """Select diverse subset using determinantal point process approximation."""
    @staticmethod
    def select(embeddings: torch.Tensor, budget: int) -> List[int]:
        n = embeddings.size(0)
        if budget >= n:
            return list(range(n))
        embeddings = F.normalize(embeddings, dim=-1)
        selected = [random.randint(0, n - 1)]
        for _ in range(budget - 1):
            dists = []
            for i in range(n):
                if i in selected:
                    dists.append(-1.0)
                    continue
                min_sim = min(F.cosine_similarity(embeddings[i:i+1], embeddings[j:j+1]).item() for j in selected)
                dists.append(1.0 - min_sim)
            best = max(range(n), key=lambda i: dists[i])
            selected.append(best)
        return selected


class DataWhisperer:
    """Main data selection pipeline inspired by Data-Whisperer (ACL 2025)."""
    def __init__(self, config: DataSelectionConfig, embed_fn: Optional[Callable] = None):
        self.config = config
        self.embed_fn = embed_fn
        self.influence_scorer = InfluenceScorer(embed_fn)
        random.seed(config.seed)

    def select(self, candidates: List[Dict], target_examples: List[Dict]) -> List[Dict]:
        logger.info(f"Selecting {self.config.budget} from {len(candidates)} candidates")
        if self.config.scoring_method == "influence":
            scores = self.influence_scorer.score(candidates, target_examples)
            indexed = sorted(enumerate(scores), key=lambda x: x[1], reverse=True)
            selected_idx = [i for i, _ in indexed[:self.config.budget]]
        elif self.config.scoring_method == "diversity":
            if self.embed_fn:
                embs = torch.tensor(self.embed_fn([c["text"] for c in candidates]))
                selected_idx = DiversitySelector.select(embs, self.config.budget)
            else:
                selected_idx = random.sample(range(len(candidates)), min(self.config.budget, len(candidates)))
        elif self.config.scoring_method == "hybrid":
            scores = self.influence_scorer.score(candidates, target_examples)
            top_n = min(self.config.budget * 3, len(candidates))
            top_idx = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)[:top_n]
            if self.embed_fn:
                top_embs = torch.tensor(self.embed_fn([candidates[i]["text"] for i in top_idx]))
                div_idx = DiversitySelector.select(top_embs, self.config.budget)
                selected_idx = [top_idx[i] for i in div_idx]
            else:
                selected_idx = top_idx[:self.config.budget]
        else:
            selected_idx = random.sample(range(len(candidates)), min(self.config.budget, len(candidates)))

        selected = [candidates[i] for i in selected_idx]
        logger.info(f"Selected {len(selected)} training examples")
        return selected
