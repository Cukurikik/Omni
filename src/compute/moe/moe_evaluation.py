"""
moe_evaluation.py — MoE Model Evaluation and Analysis Suite
Layer: Compute / AI — MoE Metrics and Evaluation

Comprehensive evaluation framework for MoE models including:
- Expert utilization analysis
- Routing pattern visualization data
- Load balance scoring
- Expert specialization detection
- Perplexity with expert decomposition
"""
import torch
import torch.nn as nn
import torch.nn.functional as F
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
import math
import json
from collections import defaultdict


@dataclass
class EvalConfig:
    num_eval_batches: int = 100
    compute_specialization: bool = True
    track_routing_patterns: bool = True
    expert_overlap_threshold: float = 0.3


@dataclass
class ExpertAnalysis:
    expert_id: int
    utilization: float
    avg_weight: float
    token_count: int
    specialization_score: float
    top_token_types: Dict[str, float] = field(default_factory=dict)


@dataclass
class RoutingPattern:
    """Records token-to-expert routing for analysis."""
    expert_cooccurrence: torch.Tensor  # (num_experts, num_experts)
    expert_entropy_per_token: torch.Tensor  # (num_tokens,)
    load_balance_cv: float
    routing_collapse_detected: bool


class ExpertUtilizationTracker:
    """Tracks expert utilization across evaluation."""
    def __init__(self, num_experts: int):
        self.num_experts = num_experts
        self.token_counts = torch.zeros(num_experts)
        self.weight_sums = torch.zeros(num_experts)
        self.total_tokens = 0
        self.batch_count = 0

    @torch.no_grad()
    def update(self, indices: torch.Tensor, weights: torch.Tensor):
        N, K = indices.shape
        self.total_tokens += N
        self.batch_count += 1
        for k in range(K):
            for e in range(self.num_experts):
                mask = indices[:, k] == e
                count = mask.sum().item()
                self.token_counts[e] += count
                if count > 0:
                    self.weight_sums[e] += weights[mask, k].sum().item()

    def get_utilization(self) -> torch.Tensor:
        if self.total_tokens == 0:
            return torch.ones(self.num_experts) / self.num_experts
        return self.token_counts / self.total_tokens

    def get_avg_weights(self) -> torch.Tensor:
        return self.weight_sums / self.token_counts.clamp(min=1)

    def coefficient_of_variation(self) -> float:
        util = self.get_utilization()
        mean = util.mean()
        std = util.std()
        return (std / mean.clamp(min=1e-8)).item()


class RoutingPatternAnalyzer:
    """Analyzes expert co-occurrence and routing patterns."""
    def __init__(self, num_experts: int):
        self.num_experts = num_experts
        self.cooccurrence = torch.zeros(num_experts, num_experts)
        self.per_token_entropy = []

    @torch.no_grad()
    def update(self, indices: torch.Tensor, logits: torch.Tensor):
        N, K = indices.shape
        # Expert co-occurrence matrix
        for i in range(N):
            experts = indices[i].unique()
            for a in experts:
                for b in experts:
                    self.cooccurrence[a, b] += 1

        # Per-token routing entropy
        probs = F.softmax(logits, dim=-1)
        entropy = -(probs * (probs + 1e-10).log()).sum(dim=-1)
        self.per_token_entropy.append(entropy.cpu())

    def get_pattern(self) -> RoutingPattern:
        entropies = torch.cat(self.per_token_entropy) if self.per_token_entropy else torch.zeros(1)

        # Normalize co-occurrence
        diag = self.cooccurrence.diag().clamp(min=1)
        norm_cooc = self.cooccurrence / diag.unsqueeze(0).sqrt() / diag.unsqueeze(1).sqrt()

        # Detect routing collapse: very low entropy
        avg_entropy = entropies.mean().item()
        max_entropy = math.log(self.num_experts)
        collapse = avg_entropy < max_entropy * 0.1

        # CV of diagonal (expert self-usage)
        usage = self.cooccurrence.diag()
        cv = (usage.std() / usage.mean().clamp(min=1e-8)).item()

        return RoutingPattern(
            expert_cooccurrence=norm_cooc,
            expert_entropy_per_token=entropies,
            load_balance_cv=cv,
            routing_collapse_detected=collapse,
        )


class ExpertSpecializationDetector:
    """Detects whether experts have specialized for different input types."""
    def __init__(self, num_experts: int):
        self.num_experts = num_experts
        self.expert_embeddings: Dict[int, List[torch.Tensor]] = defaultdict(list)

    @torch.no_grad()
    def collect(self, tokens: torch.Tensor, indices: torch.Tensor):
        """Collect token embeddings routed to each expert."""
        N = tokens.shape[0]
        for i in range(N):
            for k in range(indices.shape[1]):
                e = indices[i, k].item()
                self.expert_embeddings[e].append(tokens[i].cpu())

    def compute_specialization(self) -> Dict[int, float]:
        """Compute specialization score for each expert.

        Higher score = expert sees more diverse tokens (less specialized).
        Lower score = expert sees similar tokens (more specialized).
        """
        scores = {}
        for e in range(self.num_experts):
            if not self.expert_embeddings[e]:
                scores[e] = 0.0
                continue
            embs = torch.stack(self.expert_embeddings[e][:1000])  # cap for memory
            # Compute average pairwise cosine similarity
            normed = F.normalize(embs, dim=-1)
            sim_matrix = normed @ normed.T
            # Mask diagonal
            mask = ~torch.eye(sim_matrix.shape[0], dtype=torch.bool)
            avg_sim = sim_matrix[mask].mean().item() if mask.sum() > 0 else 0.0
            # High similarity = specialized, score = 1 - diversity
            scores[e] = avg_sim
        return scores


class MoEEvaluator:
    """Complete MoE evaluation suite."""
    def __init__(self, model: nn.Module, config: EvalConfig = None):
        self.model = model
        self.config = config or EvalConfig()
        self.num_experts = self._find_num_experts()

    def _find_num_experts(self) -> int:
        for m in self.model.modules():
            if hasattr(m, 'num_experts'):
                return m.num_experts
            if hasattr(m, 'experts') and isinstance(m.experts, nn.ModuleList):
                return len(m.experts)
        return 8

    @torch.no_grad()
    def evaluate(self, dataloader, max_batches: int = None) -> Dict:
        """Run full evaluation."""
        self.model.eval()
        max_batches = max_batches or self.config.num_eval_batches

        tracker = ExpertUtilizationTracker(self.num_experts)
        analyzer = RoutingPatternAnalyzer(self.num_experts)
        total_loss = 0.0
        total_tokens = 0
        batch_count = 0

        for batch in dataloader:
            if batch_count >= max_batches:
                break

            input_ids = batch["input_ids"]
            output = self.model(input_ids)
            logits = output["logits"] if isinstance(output, dict) else output

            # Compute perplexity
            labels = input_ids[:, 1:]
            loss = F.cross_entropy(
                logits[:, :-1].reshape(-1, logits.shape[-1]),
                labels.reshape(-1), ignore_index=-100, reduction="sum")
            total_loss += loss.item()
            total_tokens += (labels != -100).sum().item()

            batch_count += 1

        perplexity = math.exp(total_loss / max(total_tokens, 1))
        utilization = tracker.get_utilization()
        pattern = analyzer.get_pattern()

        return {
            "perplexity": perplexity,
            "total_tokens": total_tokens,
            "batches_evaluated": batch_count,
            "expert_utilization": utilization.tolist(),
            "load_balance_cv": pattern.load_balance_cv,
            "routing_collapse": pattern.routing_collapse_detected,
            "avg_routing_entropy": pattern.expert_entropy_per_token.mean().item()
                if len(pattern.expert_entropy_per_token) > 0 else 0,
            "utilization_cv": tracker.coefficient_of_variation(),
        }
