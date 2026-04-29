from typing import Dict, Any
from dataclasses import dataclass
import numpy as np

# OMNI Fashion Sense AI Engine — Compute Layer
# Absorbing MohitGupta0123/Fashion-Sense-AI: Visual search + FAISS-style similarity.

@dataclass
class FashionResult:
    ok: bool
    matches: list = None
    error: str = None

class OmniFashionSenseEngine:
    def __init__(self, feature_dim: int = 512):
        self.feature_dim = feature_dim
        self.catalog = []
        self.searches = 0

    def add_to_catalog(self, item_id: str, feature_vector: np.ndarray) -> bool:
        if feature_vector.shape != (self.feature_dim,):
            return False
        norm = np.linalg.norm(feature_vector)
        normalized = feature_vector / norm if norm > 0 else feature_vector
        self.catalog.append({"id": item_id, "vec": normalized})
        return True

    def visual_search(self, query_features: np.ndarray, top_k: int = 5) -> FashionResult:
        if query_features.shape != (self.feature_dim,):
            return FashionResult(False, error=f"FashionError: Expected ({self.feature_dim},)")
        if not self.catalog:
            return FashionResult(False, error="FashionError: Empty catalog")
        self.searches += 1
        norm = np.linalg.norm(query_features)
        q = query_features / norm if norm > 0 else query_features
        scores = [(item["id"], float(np.dot(q, item["vec"]))) for item in self.catalog]
        scores.sort(key=lambda x: -x[1])
        return FashionResult(True, matches=scores[:top_k])

    def diagnostics(self) -> Dict[str, Any]:
        return {"engine": "OmniFashionSenseEngine", "catalog_size": len(self.catalog),
                "searches": self.searches, "status": "Operational"}
