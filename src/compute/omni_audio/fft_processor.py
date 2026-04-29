import numpy as np

def compute_spectrogram(audio: np.ndarray, nfft: int = 2048) -> np.ndarray:
    if len(audio) == 0:
        raise ValueError("Audio buffer empty")
    spectrum = np.fft.fft(audio, n=nfft)
    return np.abs(spectrum)[:nfft//2]
