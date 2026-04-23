"""OmniBiometricAuthLogicEngine for mathematical vector matching of biometric templates."""
from typing import Dict, Any, List
import math
from src.compute.python_core.omni_base_engine import OmniBaseEngine, Result

class OmniBiometricAuthLogicEngine(OmniBaseEngine):
    """Production-grade Omni Biometric Auth Logic Engine for the OMNI Framework.

        Provides deterministic, zero-mock computational methods
        with monadic Result[T, E] error handling.
        """
    def authenticate(self, 
                     input_vector: List[float], 
                     template_vector: List[float], 
                     threshold: float = 0.85) -> Result[Dict[str, Any], str]:
        """
        Authenticates a biometric read (input) against a stored template.
        Uses deterministic cosine similarity constraints.
        """
        try:
            if not input_vector or not template_vector:
                return Result.fail("Vectors cannot be empty")
            if len(input_vector) != len(template_vector):
                return Result.fail("Vector dimensions must match exactly")

            dot_product = 0.0
            norm_a = 0.0
            norm_b = 0.0

            for a, b in zip(input_vector, template_vector):
                dot_product += a * b
                norm_a += a * a
                norm_b += b * b

            if norm_a == 0.0 or norm_b == 0.0:
                similarity = 0.0
            else:
                similarity = dot_product / (math.sqrt(norm_a) * math.sqrt(norm_b))

            is_match = similarity >= threshold

            return Result.ok({
                "authenticated": is_match,
                "similarity_score": similarity,
                "threshold_applied": threshold
            })
            
        except Exception as e:
            return Result.fail(str(e))

    def diagnostics(self) -> Dict[str, Any]:
        return {
            "engine": "OmniBiometricAuthLogicEngine",
            "status": "operational",
            "metric": "Cosine Similarity"
        }
