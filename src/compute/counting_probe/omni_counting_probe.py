from typing import Dict, Any, List
from dataclasses import dataclass
import numpy as np

# OMNI Counting Probe Engine — Compute Layer
# Absorbing Heidelberg-NLP/counting-probe: Vision & Language cross-modal counting eval.
# Cross-modal visual/textual element enumeration logic.

@dataclass
class ProbeResult:
    ok: bool
    predicted_count: int = 0
    confidence: float = 0.0
    error: str = None

class OmniCountingProbeEngine:
    def __init__(self, max_count: int = 10):
        self.max_count = max_count
        self.probes = 0

    def cross_modal_count(self, image_embeddings: np.ndarray, query_vector: np.ndarray) -> ProbeResult:
        """
        image_embeddings: (num_objects, Dim)
        query_vector: (Dim,)
        Calculates cross-modal presence and aggregates a count.
        """
        if image_embeddings.ndim != 2:
            return ProbeResult(False, error="ProbeError: image_embeddings must be (N, Dim)")
        if query_vector.ndim != 1:
            return ProbeResult(False, error="ProbeError: query_vector must be 1D")
        
        try:
            self.probes += 1
            N, dim = image_embeddings.shape
            
            # L2 Normalize
            img_norms = image_embeddings / np.maximum(np.linalg.norm(image_embeddings, axis=1, keepdims=True), 1e-8)
            q_norm = query_vector / max(np.linalg.norm(query_vector), 1e-8)
            
            # Dot similarity (Cosine distance)
            sim_scores = np.dot(img_norms, q_norm)
            
            # Hard threshold for counting logic
            thresh = 0.65
            matches = int(np.sum(sim_scores > thresh))
            
            # Cap at max count and compute mean confidence of matches
            final_count = min(matches, self.max_count)
            match_confidence = float(np.mean(sim_scores[sim_scores > thresh])) if matches > 0 else 0.0
            
            return ProbeResult(True, predicted_count=final_count, confidence=match_confidence)
        except Exception as e:
            return ProbeResult(False, error=f"ProbeError: {str(e)}")

    def diagnostics(self) -> Dict[str, Any]:
        return {"engine": "OmniCountingProbeEngine", "probes": self.probes, "status": "Operational"}
