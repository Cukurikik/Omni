import math

class EBindError(Exception):
    pass

class Result:
    def __init__(self, value=None, error=None):
        self.value = value
        self.error = error

    def is_ok(self) -> bool:
        return self.error is None

    def unwrap(self):
        if not self.is_ok():
            raise self.error
        return self.value

# OMNI Engine: ebind
# 5-way embedding constraints mapping (Text, Audio, Image, Video, 3D PC)
class EBind5WayEngine:
    def __init__(self, max_fusion_penalty: float = 0.5):
        self.max_penalty = max_fusion_penalty

    def calculate_5way_similarity(self, modality_scores: list[float]) -> Result:
        try:
            if not modality_scores or len(modality_scores) != 5:
                  return Result(error=EBindError("5-Way embedding engine requires strict 5-dimensional bounds"))

            for score in modality_scores:
                if score < 0.0 or score > 1.0:
                    return Result(error=EBindError("Similarity manifold breached 0.0-1.0 limits"))

            # Compute harmonic mean for non-zero scores to prevent strong modalities from dominating
            valid_scores = [s for s in modality_scores if s > 0.01]
            if not valid_scores:
                return Result(value={"fused_similarity": 0.0, "is_aligned": False})

            harmonic_mean = len(valid_scores) / sum(1.0 / s for s in valid_scores)

            penalty = self.max_penalty * (5 - len(valid_scores))
            final_similarity = max(0.0, harmonic_mean - penalty)

            return Result(value={
                "fused_similarity": final_similarity,
                "is_aligned": final_similarity > 0.6,
                "active_modalities": len(valid_scores)
            })

        except Exception as e:
            return Result(error=EBindError(f"5-Way embedding calculation limits crushed: {str(e)}"))
