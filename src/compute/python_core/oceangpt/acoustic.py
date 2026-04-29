import numpy as np

class AcousticProcessor:
    def compute_rms(self, waveform: np.ndarray) -> float:
        if len(waveform) == 0:
            return 0.0
        return float(np.sqrt(np.mean(waveform**2)))
