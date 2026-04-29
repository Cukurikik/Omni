import math

class OmniResult:
    def __init__(self, value=None, error=None):
        self.value = value
        self.error = error

    @property
    def is_ok(self):
        return self.error is None

class AudioMath:
    def __init__(self):
        pass

    def compute_mel_filterbank(self, frequencies: list[float], num_mels: int) -> OmniResult:
        if num_mels <= 0:
            return OmniResult(error="Number of mel bands must be positive")
        if not frequencies:
            return OmniResult(error="Frequency bins cannot be empty")

        # Deterministic simulation of Mel-Frequency conversion
        # mel = 2595 * log10(1 + f / 700)
        
        try:
            mel_bins = []
            for f in frequencies:
                if f < 0:
                    return OmniResult(error="Frequencies cannot be negative")
                m = 2595.0 * math.log10(1.0 + f / 700.0)
                mel_bins.append(m)
                
            # Simulate aggregation into num_mels bands
            result_mels = [sum(mel_bins)/len(mel_bins)] * num_mels
            
            return OmniResult(value=result_mels)
        except Exception as e:
            return OmniResult(error=str(e))
