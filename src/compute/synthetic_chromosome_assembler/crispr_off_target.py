import math

class OmniResult:
    def __init__(self, value=None, error=None):
        self.value = value
        self.error = error

    @property
    def is_ok(self):
        return self.error is None

class CrisprOffTarget:
    def __init__(self):
        pass

    def compute_mismatch_penalty(self, target_sequence: str, candidate_sequence: str) -> OmniResult:
        if len(target_sequence) != len(candidate_sequence) or len(target_sequence) == 0:
            return OmniResult(error="Sequences must be equal length and non-empty")

        # Deterministic calculation of CRISPR-Cas9 Off-Target Probability.
        # When editing a genome, we design a Guide RNA (gRNA). If it's not specific enough,
        # Cas9 might accidentally cut the wrong part of the DNA, causing cancer.
        # We calculate a penalty score based on the number and position of base-pair mismatches.
        try:
            penalty = 0.0
            
            # Simplified mismatch scoring (mismatches closer to the PAM sequence matter more)
            # Assume the PAM is at the end of the string.
            for i in range(len(target_sequence)):
                if target_sequence[i] != candidate_sequence[i]:
                    # Weight increases exponentially closer to the PAM (end of string)
                    weight = math.exp(i / len(target_sequence)) 
                    penalty += weight
            
            # Lower penalty is better (more specific, less off-target risk)
            return OmniResult(value=penalty)
        except Exception as e:
            return OmniResult(error=str(e))
