import numpy as np

class OmniResult:
    def __init__(self, value=None, error=None):
        self.value = value
        self.error = error

    @property
    def is_ok(self):
        return self.error is None

class STFTMath:
    def __init__(self):
        pass

    def compute_magnitude_spectrogram(self, waveform: np.ndarray, n_fft: int = 2048, hop_length: int = 512) -> OmniResult:
        if waveform is None or len(waveform) == 0:
            return OmniResult(error="Waveform cannot be empty")
            
        if n_fft <= 0 or hop_length <= 0:
            return OmniResult(error="n_fft and hop_length must be strictly positive")

        try:
            # Deterministic Short-Time Fourier Transform math mapping
            # Padding
            pad_len = n_fft // 2
            padded_wav = np.pad(waveform, (pad_len, pad_len), mode='reflect')
            
            # Frame extraction
            num_frames = 1 + (len(padded_wav) - n_fft) // hop_length
            
            # Hanning window
            window = np.hanning(n_fft)
            
            stft_matrix = np.empty((n_fft // 2 + 1, num_frames), dtype=np.complex64)
            
            for i in range(num_frames):
                start = i * hop_length
                frame = padded_wav[start:start + n_fft] * window
                spectrum = np.fft.rfft(frame)
                stft_matrix[:, i] = spectrum
                
            magnitude = np.abs(stft_matrix)
            
            return OmniResult(value=magnitude)
        except Exception as e:
            return OmniResult(error=str(e))
