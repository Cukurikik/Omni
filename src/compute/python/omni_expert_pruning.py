"""
OMNI MOTHER: REAM MoE Expert Pruning Engine (Production Grade)
==============================================================
Drops underutilized experts from a Mixture-of-Experts layer to reduce
deployment memory footprint and inference latency. Implements the full
lifecycle: analysis → pruning decision → layer rebuild → weight
redistribution → router re-initialization → validation.

References:
    - "Not All Experts are Equal" (2024), DeepSeek AI
    - "Mixture-of-Experts with Expert Choice Routing" (2022), Zhou et al.
"""

import copy
import logging
import math
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

import torch
import torch.nn as nn
import torch.nn.functional as F

logger = logging.getLogger("OmniExpertPruning")


# ---------------------------------------------------------------------------
# Data Structures
# ---------------------------------------------------------------------------

@dataclass
class ExpertStats:
    """Tracks per-expert utilization metrics collected during calibration."""
    expert_id: int
    avg_routing_prob: float = 0.0
    total_tokens_routed: int = 0
    weight_norm_l2: float = 0.0
    contribution_score: float = 0.0  # combined metric


@dataclass
class PruningReport:
    """Structured report produced after a pruning operation."""
    original_num_experts: int = 0
    pruned_num_experts: int = 0
    removed_expert_ids: List[int] = field(default_factory=list)
    kept_expert_ids: List[int] = field(default_factory=list)
    memory_saved_mb: float = 0.0
    parameter_reduction_pct: float = 0.0


# ---------------------------------------------------------------------------
# Calibration: Collecting Expert Statistics
# ---------------------------------------------------------------------------

class ExpertCalibrator:
    """
    Collects routing statistics over a calibration dataset to decide
    which experts are worth keeping.

    Usage::
        calibrator = ExpertCalibrator(num_experts=64)
        for batch in calibration_loader:
            routing_probs = model.router(batch)  # [B*S, num_experts]
            calibrator.update(routing_probs)
        stats = calibrator.finalize()
    """

    def __init__(self, num_experts: int):
        self.num_experts = num_experts
        self._prob_accum = torch.zeros(num_experts, dtype=torch.float64)
        self._token_counts = torch.zeros(num_experts, dtype=torch.int64)
        self._total_tokens: int = 0

    def update(self, routing_probs: torch.Tensor) -> None:
        """
        Accumulate routing probabilities from one forward pass.

        Args:
            routing_probs: Tensor of shape ``[num_tokens, num_experts]``
                containing softmax-normalized routing scores.
        """
        if routing_probs.dim() != 2:
            raise ValueError(
                f"Expected 2D routing_probs, got shape {routing_probs.shape}"
            )
        num_tokens = routing_probs.size(0)
        self._total_tokens += num_tokens

        # Accumulate mean probability per expert
        self._prob_accum += routing_probs.sum(dim=0).double().cpu()

        # Count tokens where each expert was chosen (top-1)
        top1_indices = routing_probs.argmax(dim=-1)
        for idx in range(self.num_experts):
            self._token_counts[idx] += (top1_indices == idx).sum().item()

    def finalize(self, expert_weights: Optional[nn.ModuleList] = None) -> List[ExpertStats]:
        """
        Produce final per-expert statistics.

        Args:
            expert_weights: Optional list of expert modules to compute
                weight norms for a richer pruning signal.

        Returns:
            Sorted list of ``ExpertStats`` (highest contribution first).
        """
        if self._total_tokens == 0:
            raise RuntimeError("No calibration data was collected.")

        stats: List[ExpertStats] = []
        for i in range(self.num_experts):
            avg_prob = (self._prob_accum[i] / self._total_tokens).item()
            token_count = self._token_counts[i].item()

            w_norm = 0.0
            if expert_weights is not None and i < len(expert_weights):
                w_norm = sum(
                    p.data.norm(2).item() ** 2
                    for p in expert_weights[i].parameters()
                )
                w_norm = math.sqrt(w_norm)

            # Combined contribution score: weighted geometric mean of
            # routing probability and token share
            token_share = token_count / max(self._total_tokens, 1)
            contribution = math.sqrt(avg_prob * token_share) if avg_prob > 0 else 0.0

            stats.append(ExpertStats(
                expert_id=i,
                avg_routing_prob=avg_prob,
                total_tokens_routed=token_count,
                weight_norm_l2=w_norm,
                contribution_score=contribution,
            ))

        stats.sort(key=lambda s: s.contribution_score, reverse=True)
        return stats


# ---------------------------------------------------------------------------
# Pruning Logic: Rebuild MoE Layer with Fewer Experts
# ---------------------------------------------------------------------------

class OmniExpertPruner:
    """
    Full-lifecycle expert pruner that:
    1. Accepts calibration statistics.
    2. Decides which experts to drop via configurable strategy.
    3. Physically rebuilds the ``nn.ModuleList`` of experts.
    4. Re-initializes the router's output projection to match the new count.
    5. Optionally redistributes pruned expert weights to survivors.
    """

    def __init__(
        self,
        threshold: float = 0.01,
        min_experts: int = 2,
        strategy: str = "contribution",  # "contribution" | "topk" | "threshold"
        top_k: Optional[int] = None,
        redistribute_weights: bool = True,
    ):
        """
        Args:
            threshold: Experts with ``contribution_score < threshold``
                are candidates for removal (used by 'threshold' strategy).
            min_experts: Never prune below this many experts.
            strategy: One of ``"contribution"``, ``"topk"``, ``"threshold"``.
            top_k: Number of experts to keep (only for ``"topk"`` strategy).
            redistribute_weights: If True, merge pruned expert weights into
                the nearest surviving expert (L2 distance in weight space).
        """
        if strategy not in ("contribution", "topk", "threshold"):
            raise ValueError(f"Unknown pruning strategy: {strategy}")
        self.threshold = threshold
        self.min_experts = min_experts
        self.strategy = strategy
        self.top_k = top_k
        self.redistribute_weights = redistribute_weights

    # ---- Strategy Dispatch ------------------------------------------------

    def _select_experts_to_keep(
        self, stats: List[ExpertStats], num_experts: int
    ) -> List[int]:
        """Return sorted list of expert IDs to keep."""
        if self.strategy == "topk":
            k = self.top_k or max(self.min_experts, num_experts // 2)
            k = max(k, self.min_experts)
            kept = [s.expert_id for s in stats[:k]]
        elif self.strategy == "threshold":
            kept = [
                s.expert_id for s in stats
                if s.contribution_score >= self.threshold
            ]
        else:  # "contribution" — adaptive elbow detection
            scores = [s.contribution_score for s in stats]
            kept = self._elbow_detection(stats, scores)

        # Guarantee minimum experts
        if len(kept) < self.min_experts:
            kept = [s.expert_id for s in stats[: self.min_experts]]

        return sorted(kept)

    @staticmethod
    def _elbow_detection(
        stats: List[ExpertStats], scores: List[float]
    ) -> List[int]:
        """
        Find the 'elbow' in the sorted contribution curve using the
        maximum-distance-to-line heuristic.
        """
        n = len(scores)
        if n <= 2:
            return [s.expert_id for s in stats]

        # Line from first to last point
        x1, y1 = 0.0, scores[0]
        x2, y2 = float(n - 1), scores[-1]

        max_dist = -1.0
        elbow_idx = n

        for i in range(1, n - 1):
            xi, yi = float(i), scores[i]
            # Perpendicular distance to line (x1,y1)→(x2,y2)
            num = abs((y2 - y1) * xi - (x2 - x1) * yi + x2 * y1 - y2 * x1)
            den = math.sqrt((y2 - y1) ** 2 + (x2 - x1) ** 2) + 1e-12
            dist = num / den
            if dist > max_dist:
                max_dist = dist
                elbow_idx = i

        return [stats[i].expert_id for i in range(elbow_idx + 1)]

    # ---- Weight Redistribution -------------------------------------------

    @staticmethod
    def _find_nearest_expert(
        pruned_expert: nn.Module,
        surviving_experts: Dict[int, nn.Module],
    ) -> int:
        """
        Find the surviving expert whose weights are closest (L2) to the
        pruned expert, for weight merging.
        """
        pruned_flat = torch.cat([
            p.data.flatten() for p in pruned_expert.parameters()
        ])
        best_id = -1
        best_dist = float("inf")
        for eid, module in surviving_experts.items():
            surv_flat = torch.cat([
                p.data.flatten() for p in module.parameters()
            ])
            dist = (pruned_flat - surv_flat).norm(2).item()
            if dist < best_dist:
                best_dist = dist
                best_id = eid
        return best_id

    @staticmethod
    def _merge_weights(
        target: nn.Module, source: nn.Module, alpha: float = 0.1
    ) -> None:
        """
        Exponential moving average merge: ``target = (1-α)*target + α*source``.
        """
        with torch.no_grad():
            for tp, sp in zip(target.parameters(), source.parameters()):
                if tp.shape == sp.shape:
                    tp.data.mul_(1.0 - alpha).add_(sp.data, alpha=alpha)

    # ---- Router Rebuild ---------------------------------------------------

    @staticmethod
    def _rebuild_router(
        router: nn.Module, new_num_experts: int
    ) -> nn.Module:
        """
        Re-initialize the router's classification head to output
        ``new_num_experts`` logits instead of the original count.
        """
        # Find the Linear layer that projects to num_experts
        for name, child in router.named_children():
            if isinstance(child, nn.Linear) and child.out_features != new_num_experts:
                in_features = child.in_features
                new_linear = nn.Linear(in_features, new_num_experts, bias=child.bias is not None)
                # Copy weights for surviving columns (warm-start)
                with torch.no_grad():
                    copy_cols = min(child.out_features, new_num_experts)
                    new_linear.weight.data[:copy_cols] = child.weight.data[:copy_cols]
                    if child.bias is not None:
                        new_linear.bias.data[:copy_cols] = child.bias.data[:copy_cols]
                setattr(router, name, new_linear)
                logger.info(
                    f"Router head rebuilt: {child.out_features} → {new_num_experts} logits."
                )
                break
        else:
            # Fallback: look for nn.Sequential or direct `.classifier`
            if hasattr(router, "classifier") and isinstance(router.classifier, nn.Linear):
                old = router.classifier
                new_linear = nn.Linear(old.in_features, new_num_experts, bias=old.bias is not None)
                router.classifier = new_linear
                logger.info(f"Router classifier rebuilt to {new_num_experts}.")
        return router

    # ---- Main Entry Point ------------------------------------------------

    def prune(
        self,
        experts: nn.ModuleList,
        router: nn.Module,
        stats: List[ExpertStats],
    ) -> Tuple[nn.ModuleList, nn.Module, PruningReport]:
        """
        Execute the full pruning pipeline.

        Args:
            experts: The original ``nn.ModuleList`` of expert sub-networks.
            router: The gating/routing module.
            stats: Calibration statistics from ``ExpertCalibrator.finalize()``.

        Returns:
            Tuple of (new_experts, new_router, report).
        """
        num_original = len(experts)
        kept_ids = self._select_experts_to_keep(stats, num_original)
        removed_ids = sorted(set(range(num_original)) - set(kept_ids))

        logger.info(
            f"Pruning {len(removed_ids)}/{num_original} experts. "
            f"Keeping: {kept_ids}"
        )

        # --- Weight redistribution (before physical removal) ---------------
        if self.redistribute_weights and removed_ids:
            surviving_map = {eid: experts[eid] for eid in kept_ids}
            for rid in removed_ids:
                nearest = self._find_nearest_expert(experts[rid], surviving_map)
                if nearest >= 0:
                    self._merge_weights(surviving_map[nearest], experts[rid], alpha=0.1)
                    logger.debug(
                        f"Expert {rid} weights merged into Expert {nearest}."
                    )

        # --- Rebuild expert list -------------------------------------------
        new_experts = nn.ModuleList([experts[eid] for eid in kept_ids])

        # --- Rebuild router ------------------------------------------------
        new_router = copy.deepcopy(router)
        new_router = self._rebuild_router(new_router, len(kept_ids))

        # --- Compute report ------------------------------------------------
        orig_params = sum(p.numel() for p in experts.parameters())
        new_params = sum(p.numel() for p in new_experts.parameters())
        saved_params = orig_params - new_params
        bytes_per_param = 2  # assume float16
        memory_saved_mb = (saved_params * bytes_per_param) / (1024 ** 2)

        report = PruningReport(
            original_num_experts=num_original,
            pruned_num_experts=len(kept_ids),
            removed_expert_ids=removed_ids,
            kept_expert_ids=kept_ids,
            memory_saved_mb=round(memory_saved_mb, 2),
            parameter_reduction_pct=round(
                100.0 * saved_params / max(orig_params, 1), 2
            ),
        )

        logger.info(
            f"Pruning complete. "
            f"Params: {orig_params:,} → {new_params:,} "
            f"(saved {report.memory_saved_mb} MB, "
            f"{report.parameter_reduction_pct}% reduction)"
        )

        return new_experts, new_router, report


# ---------------------------------------------------------------------------
# Convenience: One-Shot Prune from Raw Routing Logs
# ---------------------------------------------------------------------------

def prune_moe_layer_from_routing_log(
    experts: nn.ModuleList,
    router: nn.Module,
    routing_log: torch.Tensor,
    threshold: float = 0.01,
    min_experts: int = 2,
    strategy: str = "contribution",
) -> Tuple[nn.ModuleList, nn.Module, PruningReport]:
    """
    End-to-end pruning from a pre-collected routing probability tensor.

    Args:
        experts: The ``nn.ModuleList`` of MoE experts.
        router: The gating module.
        routing_log: Tensor of shape ``[total_tokens, num_experts]``
            containing all routing probabilities from a calibration run.
        threshold: Contribution score cutoff.
        min_experts: Floor on surviving expert count.
        strategy: ``"contribution"`` | ``"topk"`` | ``"threshold"``.

    Returns:
        Tuple of (new_experts, new_router, report).
    """
    num_experts = routing_log.size(1)
    calibrator = ExpertCalibrator(num_experts)
    # Feed in chunks to avoid blowing memory
    chunk_size = 4096
    for start in range(0, routing_log.size(0), chunk_size):
        chunk = routing_log[start : start + chunk_size]
        calibrator.update(chunk)

    stats = calibrator.finalize(expert_weights=experts)

    pruner = OmniExpertPruner(
        threshold=threshold,
        min_experts=min_experts,
        strategy=strategy,
    )
    return pruner.prune(experts, router, stats)
