from __future__ import annotations
from typing import Dict, Any, List
import math
from src.compute.python_core.omni_base_engine import Result, Ok, Err

class OmniContentBasedFilteringEngine:
    """
    omni-content-based-filtering
    
    A pure computational bounding limit mapping Cosine Similarity between vectors 
    without installing heavy Machine Learning (scikit-learn) libraries natively.
    """
    
    ENGINE_VERSION = "omni-s11-b6.1.0"
    
    def __init__(self) -> None:
        pass

    def compute_cosine_similarity_matrix(self, target_vector: List[float], reference_vectors: List[Dict[str, Any]]) -> Result:
        """
        Natively isolates string arrays mathematically matching float limits constraints.
        reference_vectors: [{"id": "ItemA", "vector": [1.0, 0.5, ...]}, ...]
        """
        try:
            if not target_vector or not reference_vectors:
                return Err(ValueError("Cannot functionally compare bounds with missing mathematical matrix components."))
                
            results = []
            
            # Target magnitude limit natively
            norm_target = math.sqrt(sum(v**2 for v in target_vector))
            if norm_target == 0:
                return Err(ValueError("Target mathematical limit boundaries result in a Null dimension vector (0)."))
                
            for ref in reference_vectors:
                if "id" not in ref or "vector" not in ref:
                    return Err(ValueError("Reference structurally malformed. Missing id or vector metrics limit."))
                    
                ref_vec = ref["vector"]
                if len(ref_vec) != len(target_vector):
                    return Err(ValueError(f"Dimension Limit Mismatch! Target {len(target_vector)} vs Ref {len(ref_vec)} boundaries."))
                    
                norm_ref = math.sqrt(sum(v**2 for v in ref_vec))
                if norm_ref == 0:
                    continue # Null reference bound
                    
                dot_product = sum(t * r for t, r in zip(target_vector, ref_vec))
                cosine_sim = dot_product / (norm_target * norm_ref)
                
                results.append({
                    "id": ref["id"],
                    "similarity_score": round(cosine_sim, 6)
                })
                
            # Highest similarity first mathematically!
            sorted_results = sorted(results, key=lambda x: x["similarity_score"], reverse=True)
            
            return Ok({
                "ranked_outputs": sorted_results,
                "vector_dimensions": len(target_vector)
            })

        except Exception as e:
            return Err(e)

    def diagnostics(self) -> Dict[str, Any]:
        """Provides similarity computational limits verifications."""
        return {
            "engine": "OmniContentBasedFilteringEngine",
            "version": self.ENGINE_VERSION,
            "status": "operational",
            "complexity": "O(N * M) Native Vector Math Loops"
        }
