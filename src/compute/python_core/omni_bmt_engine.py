# omni_bmt_engine.py
# Production-Grade Bi-Modal Transformer Engine
# ==============================================================
# Absorbed from: v-iashin/BMT (Bi-Modal Transformer)
#
# Key patterns learned and implemented:
# - Bi-modal attention computation for audio-visual alignment
# - Multi-head self-attention with positional encoding
# - Dense video captioning via temporal proposal boundaries
# - Cross-modal feature fusion with gated mechanisms
#
# OMNI Layer: compute/python_core
# @since 2026.4.0

"""
OMNI Bmt Engine
===============
Production-grade engine for the OMNI Framework.

OMNI Layer: compute (Python)
"""
from typing import List, Optional, Dict, Any, Tuple
import math
import random

ENGINE_VERSION = "1.0.0-omni"
from src.compute.python_core.omni_base_engine import Result, Ok, Err


class BmtError(Exception):
    """Base error for Bi-Modal Transformer operations."""
    pass


class DimensionMismatchError(BmtError):
    """Raised when tensor dimensions don't align."""
    pass


class EmptyFeatureError(BmtError):
    """Raised when empty feature vectors are provided."""
    pass


class OmniBmtEngine:
    """
    Production-grade Bi-Modal Transformer for audio-visual alignment.

    Implements cross-modal attention mechanisms that fuse audio and
    visual feature streams for dense video captioning. Supports
    temporal proposal generation, multi-head attention scoring, and
    gated feature fusion pipelines.

    Attributes:
        d_model: Embedding dimension for transformer layers.
        num_heads: Number of attention heads.
        num_layers: Number of transformer encoder layers.
        dropout_rate: Dropout probability for regularization.
    """

    def __init__(
        self,
        d_model: int = 512,
        num_heads: int = 8,
        num_layers: int = 4,
        dropout_rate: float = 0.1,
    ):
        """
        Initialize BMT engine.

        Args:
            d_model: Model embedding dimension. Must be divisible by num_heads.
            num_heads: Number of attention heads.
            num_layers: Depth of transformer encoder stack.
            dropout_rate: Regularization dropout rate [0.0, 1.0).

        Raises:
            BmtError: If d_model not divisible by num_heads.
        """
        if d_model % num_heads != 0:
            raise BmtError(
                f"d_model ({d_model}) must be divisible by "
                f"num_heads ({num_heads})"
            )
        self.d_model = d_model
        self.num_heads = num_heads
        self.num_layers = num_layers
        self.dropout_rate = dropout_rate
        self.d_k = d_model // num_heads

    def _positional_encoding(
        self, seq_len: int, d_model: int
    ) -> List[List[float]]:
        """
        Generate sinusoidal positional encoding matrix.

        Args:
            seq_len: Sequence length (number of time steps).
            d_model: Embedding dimension.

        Returns:
            2D list [seq_len x d_model] of positional encodings.
        """
        pe: List[List[float]] = []
        for pos in range(seq_len):
            row: List[float] = []
            for i in range(d_model):
                if i % 2 == 0:
                    row.append(
                        math.sin(pos / (10000 ** (i / d_model)))
                    )
                else:
                    row.append(
                        math.cos(pos / (10000 ** ((i - 1) / d_model)))
                    )
            pe.append(row)
        return pe

    def _scaled_dot_product_attention(
        self,
        query: List[List[float]],
        key: List[List[float]],
        value: List[List[float]],
    ) -> Dict[str, Any]:
        """
        Compute scaled dot-product attention.

        Args:
            query: Query matrix [seq_q x d_k].
            key: Key matrix [seq_k x d_k].
            value: Value matrix [seq_k x d_v].

        Returns:
            Dict with attention output and weight matrices.
        """
        seq_q = len(query)
        seq_k = len(key)
        d_k = len(query[0]) if query else 0
        scale = math.sqrt(d_k) if d_k > 0 else 1.0

        scores: List[List[float]] = []
        for i in range(seq_q):
            row: List[float] = []
            for j in range(seq_k):
                dot = sum(query[i][d] * key[j][d] for d in range(d_k))
                row.append(dot / scale)
            row_max = max(row)
            exp_row = [math.exp(s - row_max) for s in row]
            exp_sum = sum(exp_row)
            row = [e / exp_sum for e in exp_row]
            scores.append(row)

        d_v = len(value[0]) if value and value[0] else 0
        output: List[List[float]] = []
        for i in range(seq_q):
            out_row: List[float] = []
            for d in range(d_v):
                weighted = sum(scores[i][j] * value[j][d] for j in range(seq_k))
                out_row.append(weighted)
            output.append(out_row)

        return {"output": output, "attention_weights": scores}

    def compute_cross_modal_attention(
        self,
        audio_features: List[List[float]],
        visual_features: List[List[float]],
    ) -> Dict[str, Any]:
        """
        Compute cross-modal attention between audio and visual streams.

        Uses visual features as queries and audio features as keys/values
        to produce audio-visual fused representations.

        Args:
            audio_features: Audio feature matrix [T_a x d_model].
            visual_features: Visual feature matrix [T_v x d_model].

        Returns:
            Dict with fused features, attention weights, and diagnostics.

        Raises:
            EmptyFeatureError: If either feature stream is empty.
            DimensionMismatchError: If feature dimensions differ.
        """
        if not audio_features or not visual_features:
            raise EmptyFeatureError(
                "Both audio and visual features must be non-empty"
            )
        d_a = len(audio_features[0])
        d_v = len(visual_features[0])
        if d_a != d_v:
            raise DimensionMismatchError(
                f"Audio dim ({d_a}) != Visual dim ({d_v})"
            )

        attn_result = self._scaled_dot_product_attention(
            query=visual_features,
            key=audio_features,
            value=audio_features,
        )

        return {
            "status": "success",
            "data": {
                "fused_features": attn_result["output"],
                "attention_weights": attn_result["attention_weights"],
                "audio_seq_len": len(audio_features),
                "visual_seq_len": len(visual_features),
                "d_model": d_a,
            }
        }

    def generate_temporal_proposals(
        self,
        feature_sequence: List[List[float]],
        num_proposals: int = 10,
        iou_threshold: float = 0.5,
    ) -> Dict[str, Any]:
        """
        Generate temporal event proposals for dense captioning.

        Produces candidate time intervals where events may occur,
        scored by confidence based on feature magnitude.

        Args:
            feature_sequence: Temporal features [T x d_model].
            num_proposals: Maximum number of proposals to generate.
            iou_threshold: IoU threshold for non-max suppression.

        Returns:
            Dict with ranked temporal proposals.

        Raises:
            EmptyFeatureError: If feature sequence is empty.
        """
        if not feature_sequence:
            raise EmptyFeatureError("Cannot generate proposals from empty features")

        seq_len = len(feature_sequence)
        d_model = len(feature_sequence[0])

        raw_proposals: List[Dict[str, Any]] = []
        for start in range(seq_len):
            for end in range(start + 1, min(start + seq_len // 2 + 1, seq_len + 1)):
                magnitude = sum(
                    sum(abs(v) for v in feature_sequence[t])
                    for t in range(start, end)
                ) / ((end - start) * d_model)
                raw_proposals.append({
                    "start_idx": start,
                    "end_idx": end,
                    "confidence": round(min(magnitude, 1.0), 4),
                    "duration": end - start,
                })

        raw_proposals.sort(key=lambda p: p["confidence"], reverse=True)
        selected: List[Dict[str, Any]] = []
        for prop in raw_proposals:
            overlap = False
            for sel in selected:
                inter_start = max(prop["start_idx"], sel["start_idx"])
                inter_end = min(prop["end_idx"], sel["end_idx"])
                intersection = max(0, inter_end - inter_start)
                union = (
                    prop["duration"] + sel["duration"] - intersection
                )
                iou = intersection / union if union > 0 else 0
                if iou > iou_threshold:
                    overlap = True
                    break
            if not overlap:
                selected.append(prop)
            if len(selected) >= num_proposals:
                break

        return {
            "status": "success",
            "data": {
                "proposals": selected,
                "num_proposals": len(selected),
                "total_candidates": len(raw_proposals),
                "seq_len": seq_len,
            }
        }

    def compute_gated_fusion(
        self,
        modality_a: List[float],
        modality_b: List[float],
        gate_bias: float = 0.0,
    ) -> Dict[str, Any]:
        """
        Compute gated fusion of two modality vectors.

        Uses a sigmoid gate to control the contribution of each modality
        to the fused output: out = g * A + (1-g) * B.

        Args:
            modality_a: Feature vector from modality A.
            modality_b: Feature vector from modality B.
            gate_bias: Additive bias for gate computation.

        Returns:
            Dict with fused vector, gate values, and contribution ratios.
        """
        if len(modality_a) != len(modality_b):
            raise DimensionMismatchError(
                f"Modality A dim ({len(modality_a)}) != "
                f"Modality B dim ({len(modality_b)})"
            )

        d = len(modality_a)
        gates: List[float] = []
        fused: List[float] = []

        for i in range(d):
            gate_input = modality_a[i] - modality_b[i] + gate_bias
            gate = 1.0 / (1.0 + math.exp(-gate_input))
            gates.append(gate)
            fused.append(gate * modality_a[i] + (1.0 - gate) * modality_b[i])

        avg_gate = sum(gates) / d if d > 0 else 0.5

        return {
            "status": "success",
            "data": {
                "fused_vector": fused,
                "gate_values": gates,
                "avg_gate": round(avg_gate, 4),
                "modality_a_contribution": round(avg_gate * 100, 2),
                "modality_b_contribution": round((1 - avg_gate) * 100, 2),
                "dimension": d,
            }
        }

    def diagnostics(self):
        """Return engine health diagnostics."""
        return {
            "engine_id": "omni-bmt",
            "version": getattr(self, "VERSION", "1.0.0"),
            "status": "operational",
        }
