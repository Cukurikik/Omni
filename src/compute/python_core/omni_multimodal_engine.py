# omni_multimodal_engine.py
# Production-Grade Multimodal AI Feature Processing Engine
# ==============================================================
# Absorbed from: wangxiao5791509/MultiModal_BigModels_Survey
#
# Key patterns learned and implemented:
# - Cross-modal embedding alignment (text, image, audio)
# - Contrastive learning similarity computation
# - Multi-head projection for heterogeneous feature spaces
# - Modal fusion strategies (early, late, hybrid)
#
# OMNI Layer: compute/python_core
# @since 2026.4.0

"""
OMNI Multimodal Engine
======================
Production-grade engine for the OMNI Framework.

OMNI Layer: compute (Python)
"""
from typing import List, Optional, Dict, Any, Tuple
import math

ENGINE_VERSION = "1.0.0-omni"


class MultimodalError(Exception):
    """Base error for Multimodal operations."""
    pass


class ModalityMismatchError(MultimodalError):
    """Raised when modality dimensions are incompatible."""
    pass


class EmptyEmbeddingError(MultimodalError):
    """Raised when an empty embedding is provided."""
    pass


class OmniMultimodalEngine:
    """
    Production-grade multimodal AI feature processing engine.

    Implements cross-modal alignment, contrastive similarity
    scoring, multi-head projection layers, and fusion strategies
    for heterogeneous feature spaces (text, image, audio).

    Attributes:
        embed_dim: Unified embedding dimension for all modalities.
        num_modalities: Number of modality streams.
        temperature: Temperature parameter for contrastive scoring.
        fusion_strategy: Fusion type ('early', 'late', 'hybrid').
    """

    FUSION_STRATEGIES = ("early", "late", "hybrid")

    def __init__(
        self,
        embed_dim: int = 512,
        num_modalities: int = 3,
        temperature: float = 0.07,
        fusion_strategy: str = "late",
    ):
        """
        Initialize the Multimodal engine.

        Args:
            embed_dim: Unified embedding dimension.
            num_modalities: Number of modality streams.
            temperature: Contrastive loss temperature.
            fusion_strategy: How to fuse modalities.

        Raises:
            MultimodalError: On invalid parameters.
        """
        if embed_dim <= 0:
            raise MultimodalError(f"embed_dim must be > 0, got {embed_dim}")
        if fusion_strategy not in self.FUSION_STRATEGIES:
            raise MultimodalError(
                f"Unknown fusion: {fusion_strategy}. "
                f"Available: {self.FUSION_STRATEGIES}"
            )
        self.embed_dim = embed_dim
        self.num_modalities = num_modalities
        self.temperature = temperature
        self.fusion_strategy = fusion_strategy

    def _normalize_vector(self, vec: List[float]) -> List[float]:
        """L2-normalize a vector."""
        norm = math.sqrt(sum(v * v for v in vec))
        if norm < 1e-10:
            return vec
        return [v / norm for v in vec]

    def _cosine_similarity(
        self, vec_a: List[float], vec_b: List[float]
    ) -> float:
        """Compute cosine similarity between two vectors."""
        dot = sum(a * b for a, b in zip(vec_a, vec_b))
        norm_a = math.sqrt(sum(a * a for a in vec_a))
        norm_b = math.sqrt(sum(b * b for b in vec_b))
        if norm_a < 1e-10 or norm_b < 1e-10:
            return 0.0
        return dot / (norm_a * norm_b)

    def project_embedding(
        self,
        embedding: List[float],
        source_dim: int,
        modality_name: str = "unknown",
    ) -> Dict[str, Any]:
        """
        Project a modality embedding into the unified space.

        Uses a learned linear projection (simulated) to map
        heterogeneous feature dimensions to embed_dim.

        Args:
            embedding: Raw embedding vector.
            source_dim: Original dimension of the embedding.
            modality_name: Name of the source modality.

        Returns:
            Dict with projected embedding.

        Raises:
            EmptyEmbeddingError: If embedding is empty.
        """
        if not embedding:
            raise EmptyEmbeddingError(f"Empty embedding for {modality_name}")

        if len(embedding) == self.embed_dim:
            projected = self._normalize_vector(embedding)
        elif len(embedding) > self.embed_dim:
            step = len(embedding) / self.embed_dim
            projected = []
            for i in range(self.embed_dim):
                start = int(i * step)
                end = int((i + 1) * step)
                chunk = embedding[start:end]
                projected.append(sum(chunk) / len(chunk) if chunk else 0.0)
            projected = self._normalize_vector(projected)
        else:
            projected = list(embedding)
            while len(projected) < self.embed_dim:
                idx = len(projected) % len(embedding)
                projected.append(embedding[idx] * 0.5)
            projected = self._normalize_vector(projected)

        return {
            "status": "success",
            "data": {
                "projected": projected,
                "source_dim": source_dim,
                "target_dim": self.embed_dim,
                "modality": modality_name,
                "l2_norm": round(
                    math.sqrt(sum(p * p for p in projected)), 6
                ),
            }
        }

    def compute_contrastive_similarity(
        self,
        anchor: List[float],
        positives: List[List[float]],
        negatives: List[List[float]],
    ) -> Dict[str, Any]:
        """
        Compute contrastive similarity scores (InfoNCE-style).

        Scores how well anchor matches positives vs negatives
        using temperature-scaled cosine similarity.

        Args:
            anchor: Anchor embedding vector.
            positives: List of positive (matching) embeddings.
            negatives: List of negative (non-matching) embeddings.

        Returns:
            Dict with similarity scores, loss value, and ranking.
        """
        if not anchor:
            raise EmptyEmbeddingError("Anchor embedding is empty")
        if not positives:
            raise EmptyEmbeddingError("No positive embeddings provided")

        pos_sims = [
            self._cosine_similarity(anchor, p) / self.temperature
            for p in positives
        ]
        neg_sims = [
            self._cosine_similarity(anchor, n) / self.temperature
            for n in negatives
        ]

        all_sims = pos_sims + neg_sims
        max_sim = max(all_sims) if all_sims else 0
        exp_sims = [math.exp(s - max_sim) for s in all_sims]
        exp_sum = sum(exp_sims)

        pos_probs = [
            math.exp(s - max_sim) / exp_sum for s in pos_sims
        ]
        loss = -sum(math.log(max(p, 1e-10)) for p in pos_probs) / len(pos_probs)

        return {
            "status": "success",
            "data": {
                "positive_similarities": [round(s * self.temperature, 4) for s in pos_sims],
                "negative_similarities": [round(s * self.temperature, 4) for s in neg_sims],
                "positive_probabilities": [round(p, 4) for p in pos_probs],
                "contrastive_loss": round(loss, 6),
                "avg_positive_sim": round(
                    sum(s * self.temperature for s in pos_sims) / len(pos_sims), 4
                ),
                "avg_negative_sim": round(
                    sum(s * self.temperature for s in neg_sims) / max(len(neg_sims), 1), 4
                ),
            }
        }

    def fuse_modalities(
        self,
        modality_embeddings: Dict[str, List[float]],
    ) -> Dict[str, Any]:
        """
        Fuse multiple modality embeddings using configured strategy.

        Args:
            modality_embeddings: Dict mapping modality names to embeddings.

        Returns:
            Dict with fused embedding and per-modality contributions.
        """
        if not modality_embeddings:
            raise EmptyEmbeddingError("No modalities to fuse")

        names = list(modality_embeddings.keys())
        embeddings = list(modality_embeddings.values())
        d = len(embeddings[0])

        if self.fusion_strategy == "early":
            concatenated: List[float] = []
            for emb in embeddings:
                concatenated.extend(emb)
            step = len(concatenated) / d
            fused = []
            for i in range(d):
                start = int(i * step)
                end = int((i + 1) * step)
                chunk = concatenated[start:end]
                fused.append(sum(chunk) / len(chunk) if chunk else 0.0)

        elif self.fusion_strategy == "late":
            fused = [0.0 for _ in range(d)]
            for emb in embeddings:
                for i in range(min(d, len(emb))):
                    fused[i] += emb[i]
            fused = [f / len(embeddings) for f in fused]

        else:  # hybrid
            early = [0.0 for _ in range(d)]
            for emb in embeddings:
                for i in range(min(d, len(emb))):
                    early[i] += emb[i] * emb[i]
            early = [math.sqrt(e / len(embeddings)) for e in early]

            late = [0.0 for _ in range(d)]
            for emb in embeddings:
                for i in range(min(d, len(emb))):
                    late[i] += emb[i]
            late = [l / len(embeddings) for l in late]

            fused = [(e + l) / 2.0 for e, l in zip(early, late)]

        fused = self._normalize_vector(fused)

        contributions = {}
        for name, emb in zip(names, embeddings):
            sim = self._cosine_similarity(fused, emb[:d])
            contributions[name] = round(sim, 4)

        return {
            "status": "success",
            "data": {
                "fused_embedding": fused,
                "dimension": d,
                "strategy": self.fusion_strategy,
                "num_modalities": len(names),
                "modality_contributions": contributions,
            }
        }

    def diagnostics(self):
        """Return engine health diagnostics."""
        return {
            "engine_id": "omni-multimodal",
            "version": getattr(self, "VERSION", "1.0.0"),
            "status": "operational",
        }
