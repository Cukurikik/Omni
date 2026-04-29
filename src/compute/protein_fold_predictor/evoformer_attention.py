class OmniResult:
    def __init__(self, value=None, error=None):
        self.value = value
        self.error = error

    @property
    def is_ok(self):
        return self.error is None

class BioMath:
    def __init__(self):
        pass

    def compute_attention_scores(self, q: list[float], k: list[float], d_k: int) -> OmniResult:
        if len(q) != len(k):
            return OmniResult(error="Query and Key dimensions must match")

        if d_k <= 0:
            return OmniResult(error="Dimension must be positive")

        # Deterministic simulation of Evoformer MSA Attention
        try:
            # Simple dot product
            dot_product = sum(q_i * k_i for q_i, k_i in zip(q, k))
            
            # Scaled dot-product attention score
            score = dot_product / (d_k ** 0.5)
            
            return OmniResult(value=score)
        except Exception as e:
            return OmniResult(error=str(e))
