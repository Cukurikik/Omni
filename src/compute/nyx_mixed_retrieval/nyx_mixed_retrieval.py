import math

class NyxRetrievalError(Exception):
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

# OMNI Engine: nyx
# Mixed-modal retrieval balancing for universal context injections.
class NyxMixedRetrievalEngine:
    def __init__(self, balance_factor: float = 1.0):
        self.balance_factor = balance_factor

    def compute_mixed_context_weight(self, textual_relevance: float, image_relevance: float) -> Result:
        try:
            if textual_relevance < 0.0 or image_relevance < 0.0:
                 return Result(error=NyxRetrievalError("Relevance topography is negatively defined"))

            # Nyx balances multiple modalities. Here we fuse them based on a balancing parameter.
            fused_relevance = (textual_relevance * self.balance_factor) + image_relevance
            normalized_fusion = fused_relevance / (1.0 + self.balance_factor)

            return Result(value={
                "mixed_relevance_score": normalized_fusion,
                "dominance": "text" if textual_relevance > image_relevance else "image"
            })

        except Exception as e:
            return Result(error=NyxRetrievalError(f"Nyx mixed-modal processing crashed: {str(e)}"))
