class OmniResult:
    def __init__(self, value=None, error=None):
        self.value = value
        self.error = error

    @property
    def is_ok(self):
        return self.error is None

class WeightScaling:
    def __init__(self):
        pass

    def compute_int4_quantization_scale(self, float_weights: list) -> OmniResult:
        if not float_weights:
            return OmniResult(error="Weights array cannot be empty")

        # Deterministic calculation of scaling factors for INT4 quantization
        # Used to shrink massive LLMs to run on tiny Edge/IoT devices
        try:
            max_val = max(float_weights)
            min_val = min(float_weights)
            
            abs_max = max(abs(max_val), abs(min_val))
            
            if abs_max == 0:
                return OmniResult(value=0.0)
                
            # INT4 range is [-8, 7]. Scale floats to this range.
            scale = abs_max / 7.0
            
            return OmniResult(value=scale)
        except Exception as e:
            return OmniResult(error=str(e))
