"""
OMNI DeepFilterNet Engine — Real-time speech enhancement via deep spectral filtering.
Assimilated from: Rikorose/DeepFilterNet
Provides: ERB filterbank, complex spectral masking, deep filter gain application.
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


class OmniDeepFilterNetEngine:
    """
    Pure NumPy deep filtering engine for speech enhancement.

    DeepFilterNet operates in two stages:
      1. ERB-band gain estimation (coarse spectral envelope)
      2. Complex deep filter (per-bin, multi-frame convolution in the complex STFT domain)

    This engine provides the core signal-processing primitives used in the
    DeepFilterNet pipeline without PyTorch or ONNX dependencies.

    @since 1.0.0
    @tags ["audio", "speech-enhancement", "deep-filter", "erb", "compute"]
    """

    def __init__(self, sr: int = 48000, n_fft: int = 960, hop_length: int = 480) -> None:
        """
        @param sr: Sample rate in Hz.
        @param n_fft: FFT size.
        @param hop_length: Hop between successive STFT frames.
        """
        self._omni_version: str = "3.0.0-OMNI-NEXUS"
        self.sr: int = sr
        self.n_fft: int = n_fft
        self.hop_length: int = hop_length
        self.freq_bins: int = n_fft // 2 + 1

    def diagnostics(self) -> Result:
        """Returns engine health status."""
        return Ok({"status": "active", "engine": "DeepFilterNet", "capability": "ERBDeepFiltering"})

    def erb_frequencies(self, n_bands: int) -> Result:
        """
        Computes center frequencies of n_bands ERB (Equivalent Rectangular Bandwidth) bands
        spanning [0, sr/2].

        f_erb = (10^(band / (21.4)) - 1) * 228.8455 (Glasberg & Moore, 1990)

        @param n_bands: Number of ERB bands.
        @returns Result containing 1D array of center frequencies in Hz.
        """
        if n_bands <= 0:
            return Err("n_bands must be positive.")

        ear_q = 9.26449
        min_bw = 24.7
        max_freq = self.sr / 2.0

        # ERB scale boundaries
        erb_low = ear_q * np.log(1 + 20.0 / (ear_q * min_bw))
        erb_high = ear_q * np.log(1 + max_freq / (ear_q * min_bw))

        erb_points = np.linspace(erb_low, erb_high, n_bands)
        center_freqs = (np.exp(erb_points / ear_q) - 1) * ear_q * min_bw

        return Ok(center_freqs)

    def build_erb_filterbank(self, n_bands: int) -> Result:
        """
        Builds a triangular ERB filterbank matrix mapping FFT bins to ERB bands.

        @param n_bands: Number of ERB bands.
        @returns Result containing (n_bands, freq_bins) filterbank matrix.
        """
        cf_res = self.erb_frequencies(n_bands)
        if isinstance(cf_res, Err):
            return cf_res
        center_freqs = cf_res.value

        fft_freqs = np.linspace(0, self.sr / 2, self.freq_bins)
        filterbank = np.zeros((n_bands, self.freq_bins), dtype=np.float64)

        for i in range(n_bands):
            # Compute ERB bandwidth at this center frequency
            bw = 24.7 * (4.37 * center_freqs[i] / 1000.0 + 1.0)
            low = center_freqs[i] - bw / 2.0
            high = center_freqs[i] + bw / 2.0
            center = center_freqs[i]

            for j in range(self.freq_bins):
                f = fft_freqs[j]
                if low <= f <= center and center > low:
                    filterbank[i, j] = (f - low) / (center - low)
                elif center < f <= high and high > center:
                    filterbank[i, j] = (high - f) / (high - center)

        # Normalize each band to unit sum
        row_sums = filterbank.sum(axis=1, keepdims=True)
        row_sums = np.where(row_sums < 1e-12, 1.0, row_sums)
        filterbank /= row_sums

        return Ok(filterbank)

    def apply_erb_gains(self, stft_magnitude: np.ndarray, erb_gains: np.ndarray, filterbank: np.ndarray) -> Result:
        """
        Applies ERB-band gains to the STFT magnitude spectrum.

        For each frame, the per-band gains are interpolated back to full frequency resolution
        via the transpose of the filterbank matrix.

        @param stft_magnitude: (freq_bins, num_frames) magnitude spectrogram.
        @param erb_gains: (n_bands, num_frames) gain values per ERB band.
        @param filterbank: (n_bands, freq_bins) filterbank matrix.
        @returns Result containing (freq_bins, num_frames) gain-adjusted magnitude.
        """
        if stft_magnitude.ndim != 2 or erb_gains.ndim != 2 or filterbank.ndim != 2:
            return Err("All inputs must be 2D matrices.")
        if stft_magnitude.shape[1] != erb_gains.shape[1]:
            return Err("Frame counts must match between STFT and ERB gains.")
        if filterbank.shape[0] != erb_gains.shape[0]:
            return Err("ERB band count must match between filterbank and gains.")
        if filterbank.shape[1] != stft_magnitude.shape[0]:
            return Err("Filterbank freq_bins must match STFT freq_bins.")

        # Interpolate ERB gains to full-resolution per-bin gains
        full_gains = filterbank.T @ erb_gains  # (freq_bins, num_frames)
        enhanced = stft_magnitude * full_gains

        return Ok(enhanced)

    def complex_deep_filter(
        self,
        stft_complex: np.ndarray,
        filter_coeffs: np.ndarray,
    ) -> Result:
        """
        Applies a complex-valued deep filter to the STFT.

        For each frequency bin f and frame t:
            Y(f, t) = sum_{tau=0}^{L-1} H(f, tau) * X(f, t - tau)

        This is the core operation of DeepFilterNet's second stage.

        @param stft_complex: (freq_bins, num_frames) complex STFT of noisy signal.
        @param filter_coeffs: (freq_bins, filter_length) complex filter taps per bin.
        @returns Result containing (freq_bins, num_frames) filtered complex STFT.
        """
        if stft_complex.ndim != 2:
            return Err("stft_complex must be 2D (freq_bins, num_frames).")
        if filter_coeffs.ndim != 2:
            return Err("filter_coeffs must be 2D (freq_bins, filter_length).")
        if stft_complex.shape[0] != filter_coeffs.shape[0]:
            return Err("freq_bins must match between STFT and filter coefficients.")

        freq_bins, num_frames = stft_complex.shape
        filter_length = filter_coeffs.shape[1]
        output = np.zeros_like(stft_complex)

        for t in range(num_frames):
            for tau in range(filter_length):
                src_t = t - tau
                if 0 <= src_t < num_frames:
                    output[:, t] += filter_coeffs[:, tau] * stft_complex[:, src_t]

        return Ok(output)

    def compute_snr_per_frame(self, clean_stft: np.ndarray, noisy_stft: np.ndarray) -> Result:
        """
        Computes per-frame SNR in dB between clean and noisy STFT magnitudes.

        SNR(t) = 10 * log10( sum|S(f,t)|^2 / sum|N(f,t)|^2 )

        @param clean_stft: (freq_bins, num_frames) clean magnitude.
        @param noisy_stft: (freq_bins, num_frames) noisy magnitude.
        @returns Result containing 1D array of per-frame SNR in dB.
        """
        if clean_stft.shape != noisy_stft.shape:
            return Err("Clean and noisy STFT shapes must match.")

        noise_mag = np.abs(noisy_stft) - np.abs(clean_stft)
        signal_power = np.sum(np.abs(clean_stft) ** 2, axis=0)
        noise_power = np.sum(noise_mag ** 2, axis=0) + 1e-12

        snr_db = 10.0 * np.log10(signal_power / noise_power + 1e-12)
        return Ok(snr_db)
