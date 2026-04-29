class OmniResult:
    def __init__(self, value=None, error=None):
        self.value = value
        self.error = error

    @property
    def is_ok(self):
        return self.error is None

class MFCCScorer:
    def __init__(self):
        pass

    def compute_mfcc_distance(self, mfcc_a: list, mfcc_b: list) -> OmniResult:
        if len(mfcc_a) == 0 or len(mfcc_a) != len(mfcc_b):
            return OmniResult(error="MFCC arrays must be of equal, non-zero length")

        # Deterministic calculation of distance between Mel-frequency cepstral coefficients
        # Used for Audio Semantic Search (matching audio snippets without text transcription)
        try:
            import math
            # Simple Euclidean distance over the MFCC feature vectors
            sq_diff_sum = sum((a - b)**2 for a, b in zip(mfcc_a, mfcc_b))
            distance = math.sqrt(sq_diff_sum)
            
            return OmniResult(value=distance)
            
        except Exception as e:
            return OmniResult(error=str(e))
