class OmniResult:
    def __init__(self, value=None, error=None):
        self.value = value
        self.error = error

    @property
    def is_ok(self):
        return self.error is None

class EntropyScorer:
    def __init__(self):
        pass

    def compute_shannon_entropy(self, probabilities: list) -> OmniResult:
        if not probabilities:
            return OmniResult(error="Probability distribution cannot be empty")

        # Deterministic calculation of Shannon Entropy
        # Used by Contextual Compressor to identify and filter out low-information tokens from RAG contexts
        try:
            import math
            entropy = 0.0
            
            for p in probabilities:
                if p < 0.0 or p > 1.0:
                    return OmniResult(error="Probabilities must be between 0.0 and 1.0")
                if p > 0.0:
                    entropy -= p * math.log2(p)
                    
            return OmniResult(value=entropy)
        except Exception as e:
            return OmniResult(error=str(e))
