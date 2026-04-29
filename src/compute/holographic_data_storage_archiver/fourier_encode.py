import math

class OmniResult:
    def __init__(self, value=None, error=None):
        self.value = value
        self.error = error

    @property
    def is_ok(self):
        return self.error is None

class FourierEncode:
    def __init__(self):
        pass

    def compute_spatial_frequency(self, bit_pattern_integer: int, wavelength_nm: float) -> OmniResult:
        if wavelength_nm <= 0:
            return OmniResult(error="Wavelength must be positive")

        # Deterministic calculation of Fourier-transform Holographic encoding
        # Instead of storing bits as magnetic dots on a hard drive, holographic storage
        # encodes pages of data as optical interference patterns in a 3D crystal, allowing 100+ year archiving.
        try:
            # Simulated calculation of the spatial frequency grating
            # based on the Bragg condition.
            spatial_freq = (2.0 * math.pi) / (wavelength_nm * 1e-9)
            
            # Incorporate the data payload deterministically
            modulated_freq = spatial_freq * (1.0 + (bit_pattern_integer % 100) / 1000.0)
            
            return OmniResult(value=modulated_freq)
        except Exception as e:
            return OmniResult(error=str(e))
