"""
OMNI ClearerVoice Engine — Audio enhancement via spectral gating and Wiener filtering.
Assimilated from: modelscope/ClearerVoice-Studio
Provides: STFT/iSTFT, spectral noise gating, Wiener filter denoising.
"""
import numpy as np
from typing import Optional



ENGINE_VERSION = "1.0.0-omni"
from src.compute.python_core.omni_base_engine import Result, Ok, Err

class Result:
    """Monadic Result base."""
    pass


class Ok(Result):
    """Success variant."""
    def __init__(self, value):
        """Initialize Ok."""
        self.value = value


class Err(Result):
    """Error variant."""
    def __init__(self, error: str):
        """Initialize Err."""
        self.error = error


class OmniClearerVoiceEngine:
    """
    Pure NumPy audio enhancement engine inspired by ClearerVoice-Studio.
    Implements Short-Time Fourier Transform, spectral noise gating,
    and parametric Wiener filtering for voice denoising.

    @since 1.0.0
    @tags ["audio", "denoising", "spectral", "compute"]
    """

    def __init__(self, n_fft: int = 1024, hop_length: int = 256) -> None:
        """
        @param n_fft: FFT window size.
        @param hop_length: Hop between successive frames.
        """
        self._omni_version: str = "3.0.0-OMNI-NEXUS"
        self.n_fft: int = n_fft
        self.hop_length: int = hop_length

    def diagnostics(self) -> Result:
        """Returns engine health status."""
        return Ok({"status": "active", "engine": "ClearerVoice", "capability": "SpectralDenoising"})

    def stft(self, signal: np.ndarray) -> Result:
        """
        Computes the Short-Time Fourier Transform using a Hann window.

        @param signal: 1D audio waveform array.
        @returns Result containing complex STFT matrix of shape (n_fft//2 + 1, num_frames).
        """
        if signal.ndim != 1:
            return Err("Input signal must be 1D.")

        window = np.hanning(self.n_fft)
        # Pad signal to align with hop_length
        pad_len = (self.n_fft - len(signal) % self.hop_length) % self.hop_length
        padded = np.pad(signal, (0, pad_len), mode='constant')

        num_frames = (len(padded) - self.n_fft) // self.hop_length + 1
        freq_bins = self.n_fft // 2 + 1
        stft_matrix = np.zeros((freq_bins, num_frames), dtype=np.complex128)

        for t in range(num_frames):
            start = t * self.hop_length
            frame = padded[start:start + self.n_fft] * window
            spectrum = np.fft.rfft(frame)
            stft_matrix[:, t] = spectrum

        return Ok(stft_matrix)

    def istft(self, stft_matrix: np.ndarray, output_length: Optional[int] = None) -> Result:
        """
        Computes the inverse STFT using overlap-add synthesis.

        @param stft_matrix: Complex STFT matrix of shape (n_fft//2 + 1, num_frames).
        @param output_length: Optional target length of the reconstructed signal.
        @returns Result containing 1D reconstructed waveform.
        """
        if stft_matrix.ndim != 2:
            return Err("STFT matrix must be 2D (freq_bins, num_frames).")

        window = np.hanning(self.n_fft)
        num_frames = stft_matrix.shape[1]
        signal_length = self.n_fft + self.hop_length * (num_frames - 1)

        signal = np.zeros(signal_length, dtype=np.float64)
        window_sum = np.zeros(signal_length, dtype=np.float64)

        for t in range(num_frames):
            start = t * self.hop_length
            frame = np.fft.irfft(stft_matrix[:, t], n=self.n_fft)
            signal[start:start + self.n_fft] += frame * window
            window_sum[start:start + self.n_fft] += window ** 2

        # Normalize by window overlap
        nonzero = window_sum > 1e-12
        signal[nonzero] /= window_sum[nonzero]

        if output_length is not None:
            signal = signal[:output_length]

        return Ok(signal)

    def spectral_gate(self, signal: np.ndarray, noise_estimate: np.ndarray, threshold_db: float = -20.0) -> Result:
        """
        Applies spectral noise gating: attenuates frequency bins below a noise threshold.

        @param signal: 1D audio signal.
        @param noise_estimate: 1D noise-only segment for profile estimation.
        @param threshold_db: Gate threshold in dB above noise floor.
        @returns Result containing 1D denoised signal.
        """
        stft_res = self.stft(signal)
        if isinstance(stft_res, Err):
            return stft_res
        stft_signal = stft_res.value

        noise_stft_res = self.stft(noise_estimate)
        if isinstance(noise_stft_res, Err):
            return noise_stft_res
        noise_stft = noise_stft_res.value

        # Estimate noise power spectral density
        noise_psd = np.mean(np.abs(noise_stft) ** 2, axis=1, keepdims=True)

        # Convert threshold from dB to linear
        threshold_linear = 10.0 ** (threshold_db / 10.0)

        signal_power = np.abs(stft_signal) ** 2
        mask = (signal_power / (noise_psd + 1e-12)) > threshold_linear
        mask = mask.astype(np.float64)

        # Apply gate
        gated_stft = stft_signal * mask

        return self.istft(gated_stft, output_length=len(signal))

    def wiener_filter(self, signal: np.ndarray, noise_estimate: np.ndarray) -> Result:
        """
        Applies a parametric Wiener filter for noise suppression.

        H(f) = max(0, 1 - noise_psd / signal_psd)

        @param signal: 1D noisy audio signal.
        @param noise_estimate: 1D noise-only segment.
        @returns Result containing 1D filtered signal.
        """
        stft_res = self.stft(signal)
        if isinstance(stft_res, Err):
            return stft_res
        stft_signal = stft_res.value

        noise_stft_res = self.stft(noise_estimate)
        if isinstance(noise_stft_res, Err):
            return noise_stft_res
        noise_stft = noise_stft_res.value

        noise_psd = np.mean(np.abs(noise_stft) ** 2, axis=1, keepdims=True)
        signal_psd = np.abs(stft_signal) ** 2

        # Wiener gain
        gain = np.maximum(0.0, 1.0 - noise_psd / (signal_psd + 1e-12))
        filtered_stft = stft_signal * gain

        return self.istft(filtered_stft, output_length=len(signal))
