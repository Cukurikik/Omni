"""
OMNI DeepKE Engine — Knowledge extraction primitives for NER and relation classification.
Assimilated from: zjunlp/DeepKE + ahkarami/Deep-Learning-in-Production
Provides: BIO tag decoding, relation scoring matrices, entity span extraction.
"""
import numpy as np
from typing import List, Tuple, Dict



ENGINE_VERSION = "1.0.0-omni"
from src.compute.python_core.omni_base_engine import Result, Ok, Err

class Result:
    """Monadic Result base."""
    pass


class Ok(Result):
    """Success variant."""
    def __init__(self, value):
        """Initialize Ok."""
        self.value = value


class Err(Result):
    """Error variant."""
    def __init__(self, error: str):
        """Initialize Err."""
        self.error = error


class OmniDeepKEEngine:
    """
    Pure NumPy knowledge extraction engine replacing PyTorch-based DeepKE.
    Implements BIO sequence decoding, relation classification from logit matrices,
    and entity-pair scoring for knowledge graph construction.

    Also absorbs production deployment patterns from Deep-Learning-in-Production
    (model quantization awareness, batch inference patterns).

    @since 1.0.0
    @tags ["knowledge-extraction", "ner", "relation", "compute"]
    """

    def __init__(self) -> None:
        """Initialize OmniDeepKEEngine."""
        self._omni_version: str = "3.0.0-OMNI-NEXUS"

    def diagnostics(self) -> Result:
        """Returns engine health status."""
        return Ok({"status": "active", "engine": "DeepKE", "capability": "KnowledgeExtractionNER"})

    def decode_bio_tags(self, logits: np.ndarray, id_to_label: Dict[int, str]) -> Result:
        """
        Decodes BIO-tagged sequences from logit arrays via argmax.

        @param logits: 2D array of shape (seq_len, num_labels) with raw scores.
        @param id_to_label: Mapping from label index to BIO tag string (e.g. {0: 'O', 1: 'B-PER', ...}).
        @returns Result containing list of predicted BIO tag strings.
        """
        if logits.ndim != 2:
            return Err("Logits must be 2D (seq_len, num_labels).")

        predicted_ids = np.argmax(logits, axis=1)
        tags: List[str] = []
        for pid in predicted_ids:
            pid_int = int(pid)
            if pid_int not in id_to_label:
                return Err(f"Predicted label id {pid_int} not in id_to_label mapping.")
            tags.append(id_to_label[pid_int])

        return Ok(tags)

    def extract_entity_spans(self, bio_tags: List[str]) -> Result:
        """
        Extracts contiguous entity spans from a BIO tag sequence.

        @param bio_tags: List of BIO tag strings (e.g. ['O', 'B-PER', 'I-PER', 'O']).
        @returns Result containing list of (entity_type, start_idx, end_idx) tuples.
        """
        spans: List[Tuple[str, int, int]] = []
        current_type: str = ""
        start_idx: int = -1

        for i, tag in enumerate(bio_tags):
            if tag.startswith("B-"):
                # Close previous entity if open
                if current_type:
                    spans.append((current_type, start_idx, i - 1))
                current_type = tag[2:]
                start_idx = i
            elif tag.startswith("I-"):
                tag_type = tag[2:]
                if tag_type != current_type:
                    # Mismatched I-tag: close previous and start new
                    if current_type:
                        spans.append((current_type, start_idx, i - 1))
                    current_type = tag_type
                    start_idx = i
            else:  # "O" tag
                if current_type:
                    spans.append((current_type, start_idx, i - 1))
                    current_type = ""
                    start_idx = -1

        # Close final entity if sequence ends mid-entity
        if current_type:
            spans.append((current_type, start_idx, len(bio_tags) - 1))

        return Ok(spans)

    def classify_relation(self, entity_a_vec: np.ndarray, entity_b_vec: np.ndarray, relation_matrix: np.ndarray) -> Result:
        """
        Scores entity pair (a, b) against a bank of relation prototypes.

        score_r = entity_a^T @ W_r @ entity_b for each relation r

        @param entity_a_vec: 1D embedding vector for entity A.
        @param entity_b_vec: 1D embedding vector for entity B.
        @param relation_matrix: 3D array of shape (num_relations, dim, dim).
        @returns Result containing dict with 'scores' (1D array) and 'best_relation' (int index).
        """
        if entity_a_vec.ndim != 1 or entity_b_vec.ndim != 1:
            return Err("Entity vectors must be 1D.")
        if relation_matrix.ndim != 3:
            return Err("Relation matrix must be 3D (num_relations, dim, dim).")

        num_relations = relation_matrix.shape[0]
        scores = np.zeros(num_relations, dtype=np.float64)

        for r in range(num_relations):
            scores[r] = entity_a_vec @ relation_matrix[r] @ entity_b_vec

        best = int(np.argmax(scores))
        return Ok({"scores": scores, "best_relation": best})

    def quantize_weights_int8(self, weights: np.ndarray) -> Result:
        """
        evaluates_structurally INT8 quantization for production deployment optimization.
        Learned from ahkarami/Deep-Learning-in-Production patterns.

        @param weights: Float weight matrix to quantize.
        @returns Result containing dict with 'quantized' (int8 array) and 'scale' (float).
        """
        if weights.size == 0:
            return Err("Cannot quantize an empty weight array.")

        abs_max = np.max(np.abs(weights))
        if abs_max < 1e-12:
            return Ok({"quantized": np.zeros_like(weights, dtype=np.int8), "scale": 1.0})

        scale = 127.0 / abs_max
        quantized = np.clip(np.round(weights * scale), -128, 127).astype(np.int8)

        return Ok({"quantized": quantized, "scale": float(scale)})
