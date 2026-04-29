import numpy as np

class OmniResult:
    def __init__(self, value, error=None):
        self.value = value
        self.error = error
        self.is_ok = error is None

class ActivationScaler:
    def __init__(self, bits: int = 8):
        self.bits = bits
        self.qmax = (1 << (bits - 1)) - 1
        self.qmin = -(1 << (bits - 1))
        
    def scale_activations(self, activations: np.ndarray) -> OmniResult:
        if activations is None or activations.size == 0:
            return OmniResult(None, "Empty activations")
            
        amax = np.max(np.abs(activations))
        if amax == 0:
            return OmniResult(activations)
            
        scale = self.qmax / amax
        quantized = np.clip(np.round(activations * scale), self.qmin, self.qmax).astype(np.int8)
        
        return OmniResult({"quantized": quantized, "scale": scale})
