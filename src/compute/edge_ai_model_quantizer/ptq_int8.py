class OmniResult:
    def __init__(self, value=None, error=None):
        self.value = value
        self.error = error

    @property
    def is_ok(self):
        return self.error is None

class PtqInt8:
    def __init__(self):
        pass

    def compute_quantization_scale(self, min_activation: float, max_activation: float) -> OmniResult:
        if min_activation >= max_activation:
            return OmniResult(error="Min activation must be less than max")

        # Deterministic calculation of Post-Training Quantization (PTQ) scaling factors
        # AI models usually run in 32-bit float (FP32). To run on tiny edge devices (like cameras),
        # we quantize them down to 8-bit integers (INT8), saving 4x memory and increasing speed.
        try:
            # We map the continuous range [min_activation, max_activation] to the discrete range [-128, 127]
            q_min, q_max = -128, 127
            
            # Scale = (max_val - min_val) / (q_max - q_min)
            scale = (max_activation - min_activation) / (q_max - q_min)
            
            # Zero-point = q_min - min_val / scale
            zero_point = round(q_min - (min_activation / scale))
            
            # Clamp zero-point to valid INT8 range
            zero_point = max(q_min, min(q_max, zero_point))
            
            return OmniResult(value={"scale": scale, "zero_point": zero_point})
        except Exception as e:
            return OmniResult(error=str(e))
