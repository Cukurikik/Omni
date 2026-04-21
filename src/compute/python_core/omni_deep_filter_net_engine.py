"""
OMNI DeepFilterNet Engine — Full-band speech enhancement via deep filtering primitives.

Assimilated from: Rikorose/DeepFilterNet (4.1k ★)
Paper: "DeepFilterNet: A Low Complexity Speech Enhancement Framework for Full-Band Audio"
       (ICASSP 2022, Schröter et al.)

Implements the core algorithmic building blocks of the DeepFilterNet speech enhancement
framework in pure NumPy:
  - Real-time STFT/ISTFT with Hann window and overlap-add
  - ERB (Equivalent Rectangular Bandwidth) filterbank for perceptual frequency grouping
  - Deep Filtering: complex multi-frame spectral coefficient filtering
  - Spectral gain estimation (Wiener, ideal ratio mask)
  - Noise PSD estimation via minimum statistics
  - Post-filter for residual noise over-attenuation
  - Quality metrics: SNR, segmental SNR, waveform correlation

OMNI Domain: compute/ (Python)
CODE RULE 001-005 compliant. Only numpy dependency.
"""

from __future__ import annotations

import math
from typing import Any, Dict, Optional, Tuple

import numpy as np


ENGINE_VERSION: str = "1.0.0-omni"
ENGINE_NAME: str = "OmniDeepFilterNetEngine"


# ---------------------------------------------------------------------------
# Monadic Result
# ---------------------------------------------------------------------------

class Result:
    """Monadic Result base."""
    pass


class Ok(Result):
    """Success variant."""
    def __init__(self, value: Any) -> None:
        """Initialize Ok."""
        self.value = value


class Err(Result):
    """Error variant."""
    def __init__(self, error: str) -> None:
        """Initialize Err."""
        self.error = error


# ---------------------------------------------------------------------------
# Engine
# ---------------------------------------------------------------------------

class OmniDeepFilterNetEngine:
    """Production-grade speech enhancement engine inspired by DeepFilterNet.

    Provides the mathematical foundation for full-band (48 kHz) noise suppression
    using deep filtering. Implements:
      - STFT/ISTFT for time-frequency analysis
      - ERB perceptual filterbank
      - Complex deep filtering (core DeepFilterNet innovation)
      - Spectral gain estimation
      - Noise statistics estimation
      - Segmental quality metrics

    @since 1.0.0
    @tags ["audio", "speech-enhancement", "deep-filtering", "noise-suppression", "compute"]
    """

    VERSION = ENGINE_VERSION
    ENGINE_ID = ENGINE_NAME

    def __init__(
        self,
        n_fft: int = 1024,
        hop_length: int = 256,
        sr: int = 48000,
    ) -> None:
        """Initialize engine with STFT parameters.

        @param n_fft: FFT size (default 1024 for 48kHz, ~21ms).
        @param hop_length: Hop size (default 256 for ~5.3ms).
        @param sr: Sample rate (default 48000 Hz).
        """
        self.n_fft = n_fft
        self.hop_length = hop_length
        self.sr = sr
        self._omni_version: str = "3.0.0-OMNI-NEXUS"
        # Pre-compute Hann window
        self._window: np.ndarray = np.hanning(n_fft).astype(np.float64)

    def diagnostics(self) -> Result:
        """Returns engine health status."""
        return Ok({
            "engine": self.ENGINE_ID,
            "version": self.VERSION,
            "status": "operational",
            "n_fft": self.n_fft,
            "hop_length": self.hop_length,
            "sr": self.sr,
            "capabilities": [
                "stft", "istft", "erb_filterbank", "deep_filter",
                "wiener_gain", "ideal_ratio_mask", "noise_psd_estimation",
                "post_filter", "snr", "segmental_snr",
            ],
        })

    # -----------------------------------------------------------------
    # 1. STFT / ISTFT
    # -----------------------------------------------------------------

    def stft(self, signal: np.ndarray) -> Result:
        """Compute Short-Time Fourier Transform.

        Uses a Hann analysis window with zero-phase padding. Output shape
        is (n_frames, n_fft//2 + 1) complex spectral coefficients.

        @param signal: 1D real-valued time-domain audio signal.
        @returns Result containing complex STFT matrix (frames, freq_bins).
        """
        if signal.ndim != 1:
            return Err("Signal must be 1D.")
        if len(signal) < self.n_fft:
            return Err(f"Signal length ({len(signal)}) must be >= n_fft ({self.n_fft}).")

        n = len(signal)
        n_frames = 1 + (n - self.n_fft) // self.hop_length
        n_bins = self.n_fft // 2 + 1

        spec = np.zeros((n_frames, n_bins), dtype=np.complex128)
        for i in range(n_frames):
            start = i * self.hop_length
            frame = signal[start:start + self.n_fft] * self._window
            spec[i, :] = np.fft.rfft(frame)

        return Ok(spec)

    def istft(self, spec: np.ndarray, output_length: Optional[int] = None) -> Result:
        """Compute inverse STFT via overlap-add synthesis.

        @param spec: Complex STFT matrix (n_frames, n_fft//2 + 1).
        @param output_length: Desired output signal length (truncate/pad).
        @returns Result containing reconstructed 1D signal.
        """
        if spec.ndim != 2:
            return Err("Spectrogram must be 2D.")

        n_frames, n_bins = spec.shape
        expected_bins = self.n_fft // 2 + 1
        if n_bins != expected_bins:
            return Err(f"Expected {expected_bins} frequency bins, got {n_bins}.")

        sig_len = self.n_fft + (n_frames - 1) * self.hop_length
        signal = np.zeros(sig_len, dtype=np.float64)
        window_sum = np.zeros(sig_len, dtype=np.float64)

        for i in range(n_frames):
            start = i * self.hop_length
            frame = np.fft.irfft(spec[i, :], n=self.n_fft)
            signal[start:start + self.n_fft] += frame * self._window
            window_sum[start:start + self.n_fft] += self._window ** 2

        # Normalize by window sum (COLA condition)
        nonzero = window_sum > 1e-10
        signal[nonzero] /= window_sum[nonzero]

        if output_length is not None:
            if output_length <= len(signal):
                signal = signal[:output_length]
            else:
                signal = np.pad(signal, (0, output_length - len(signal)))

        return Ok(signal)

    # -----------------------------------------------------------------
    # 2. ERB FILTERBANK
    # -----------------------------------------------------------------

    def erb_filterbank(self, n_erb_bands: int = 32) -> Result:
        """Compute ERB (Equivalent Rectangular Bandwidth) filterbank matrix.

        Maps linear frequency bins to perceptually spaced ERB bands, matching
        the frequency grouping used in DeepFilterNet's encoder.

        ERB scale: f_erb = 9.265 * log(1 + f / (24.7 * 9.265))

        @param n_erb_bands: Number of ERB bands (default 32).
        @returns Result containing (n_erb_bands, n_fft//2 + 1) filterbank matrix.
        """
        if n_erb_bands < 1:
            return Err("n_erb_bands must be >= 1.")

        n_bins = self.n_fft // 2 + 1
        freqs = np.linspace(0, self.sr / 2, n_bins)

        # Convert Hz to ERB number
        def hz_to_erb(f: np.ndarray) -> np.ndarray:
            return 9.265 * np.log1p(f / (24.7 * 9.265))

        erb_lo = hz_to_erb(np.array([0.0]))[0]
        erb_hi = hz_to_erb(np.array([self.sr / 2.0]))[0]
        erb_freqs = hz_to_erb(freqs)

        # ERB band edges
        band_edges = np.linspace(erb_lo, erb_hi, n_erb_bands + 1)

        fb = np.zeros((n_erb_bands, n_bins), dtype=np.float64)
        for b in range(n_erb_bands):
            mask = (erb_freqs >= band_edges[b]) & (erb_freqs < band_edges[b + 1])
            count = np.sum(mask)
            if count > 0:
                fb[b, mask] = 1.0 / count  # normalize per band

        return Ok(fb)

    def apply_erb_filterbank(self, power_spectrum: np.ndarray, filterbank: np.ndarray) -> Result:
        """Apply ERB filterbank to power spectrum.

        @param power_spectrum: (n_frames, n_bins) real power spectrum.
        @param filterbank: (n_erb_bands, n_bins) filterbank matrix.
        @returns Result containing (n_frames, n_erb_bands) ERB power.
        """
        if power_spectrum.ndim != 2 or filterbank.ndim != 2:
            return Err("Both inputs must be 2D.")
        if power_spectrum.shape[1] != filterbank.shape[1]:
            return Err("Frequency bin count mismatch.")
        erb_power = power_spectrum @ filterbank.T
        return Ok(erb_power)

    # -----------------------------------------------------------------
    # 3. DEEP FILTERING (Core Innovation)
    # -----------------------------------------------------------------

    def deep_filter(
        self,
        noisy_spec: np.ndarray,
        filter_coeffs: np.ndarray,
    ) -> Result:
        """Apply deep filtering to noisy complex spectrogram.

        Deep filtering convolves the noisy spectrogram along the frame axis
        with learned complex filter coefficients. For each frequency bin and
        frame, the output is:

            y[t, f] = sum_{l=0}^{L-1} h[t, f, l] * x[t-l, f]

        where h are the (predicted) complex filter coefficients and x is the
        noisy input spectrogram.

        @param noisy_spec: (n_frames, n_bins) complex noisy spectrogram.
        @param filter_coeffs: (n_frames, n_bins, filter_len) complex filter taps.
        @returns Result containing (n_frames, n_bins) filtered complex spectrogram.
        """
        if noisy_spec.ndim != 2:
            return Err("noisy_spec must be 2D complex.")
        if filter_coeffs.ndim != 3:
            return Err("filter_coeffs must be 3D (frames, bins, filter_len).")

        n_frames, n_bins = noisy_spec.shape
        filter_len = filter_coeffs.shape[2]

        if filter_coeffs.shape[0] != n_frames or filter_coeffs.shape[1] != n_bins:
            return Err("filter_coeffs shape mismatch with noisy_spec.")

        output = np.zeros_like(noisy_spec)

        for t in range(n_frames):
            for l in range(filter_len):
                src_t = t - l
                if src_t >= 0:
                    output[t, :] += filter_coeffs[t, :, l] * noisy_spec[src_t, :]

        return Ok(output)

    # -----------------------------------------------------------------
    # 4. SPECTRAL GAIN ESTIMATION
    # -----------------------------------------------------------------

    def ideal_ratio_mask(
        self, clean_spec: np.ndarray, noisy_spec: np.ndarray
    ) -> Result:
        """Compute Ideal Ratio Mask (IRM).

        IRM = |S|^2 / (|S|^2 + |N|^2)
        where S is clean speech and N is noise (derived from noisy - clean).

        @param clean_spec: (n_frames, n_bins) complex clean spectrogram.
        @param noisy_spec: (n_frames, n_bins) complex noisy spectrogram.
        @returns Result containing (n_frames, n_bins) real-valued mask in [0, 1].
        """
        if clean_spec.shape != noisy_spec.shape:
            return Err("clean_spec and noisy_spec must have the same shape.")

        s_power = np.abs(clean_spec) ** 2
        n_power = np.abs(noisy_spec - clean_spec) ** 2
        denom = s_power + n_power
        denom = np.maximum(denom, 1e-10)
        mask = s_power / denom
        return Ok(mask)

    def wiener_gain(
        self,
        noisy_power: np.ndarray,
        noise_power: np.ndarray,
        floor: float = 0.001,
    ) -> Result:
        """Compute Wiener filter gain.

        G = max(1 - noise_power / noisy_power, floor)

        @param noisy_power: (n_frames, n_bins) noisy power spectrum.
        @param noise_power: (n_frames, n_bins) estimated noise power.
        @param floor: Minimum gain (spectral floor, default 0.001 = -30 dB).
        @returns Result containing (n_frames, n_bins) gain values.
        """
        if noisy_power.shape != noise_power.shape:
            return Err("Shapes must match.")
        safe_noisy = np.maximum(noisy_power, 1e-10)
        gain = np.maximum(1.0 - noise_power / safe_noisy, floor)
        return Ok(gain)

    def apply_spectral_gain(
        self, spec: np.ndarray, gain: np.ndarray
    ) -> Result:
        """Apply real-valued spectral gain to a complex spectrogram.

        @param spec: (n_frames, n_bins) complex spectrogram.
        @param gain: (n_frames, n_bins) real gain in [0, 1].
        @returns Result containing (n_frames, n_bins) gained complex spectrogram.
        """
        if spec.shape != gain.shape:
            return Err("spec and gain must have the same shape.")
        return Ok(spec * gain)

    # -----------------------------------------------------------------
    # 5. NOISE PSD ESTIMATION
    # -----------------------------------------------------------------

    def estimate_noise_psd(
        self,
        power_spectrum: np.ndarray,
        alpha: float = 0.98,
        initial_frames: int = 10,
    ) -> Result:
        """Estimate noise PSD using exponential minimum tracking.

        A simplified variant of the Minimum Statistics approach (Martin, 2001)
        used as a reference noise estimator:

        For the first `initial_frames`:
            noise_psd = running average of power
        After that:
            noise_psd = alpha * noise_psd + (1 - alpha) * min(power, noise_psd * 2)

        @param power_spectrum: (n_frames, n_bins) power spectrum.
        @param alpha: Smoothing factor (higher = slower adaptation, default 0.98).
        @param initial_frames: Frames to use for initial noise estimate.
        @returns Result containing (n_frames, n_bins) estimated noise PSD.
        """
        if power_spectrum.ndim != 2:
            return Err("power_spectrum must be 2D.")

        n_frames, n_bins = power_spectrum.shape
        noise_psd = np.zeros_like(power_spectrum)

        if n_frames == 0:
            return Ok(noise_psd)

        # Initialize with average of first few frames
        init_end = min(initial_frames, n_frames)
        init_est = np.mean(power_spectrum[:init_end, :], axis=0)
        noise_psd[0, :] = init_est

        for t in range(1, n_frames):
            if t < init_end:
                noise_psd[t, :] = np.mean(power_spectrum[:t + 1, :], axis=0)
            else:
                # Exponential smoothing with floor tracking
                candidate = np.minimum(power_spectrum[t, :], noise_psd[t - 1, :] * 2.0)
                noise_psd[t, :] = alpha * noise_psd[t - 1, :] + (1.0 - alpha) * candidate

        return Ok(noise_psd)

    # -----------------------------------------------------------------
    # 6. POST-FILTER
    # -----------------------------------------------------------------

    def post_filter(
        self,
        gain: np.ndarray,
        beta: float = 0.02,
    ) -> Result:
        """Apply post-filter to spectral gains for residual noise suppression.

        Following DeepFilterNet's approach of slightly over-attenuating bands
        with very low gain (close to 0):

            gain_pf = gain^(1 + beta / (gain + eps))

        This aggressively attenuates near-zero gains while preserving speech-dominated bands.

        @param gain: (n_frames, n_bins) spectral gain in [0, 1].
        @param beta: Post-filter aggressiveness (default 0.02).
        @returns Result containing (n_frames, n_bins) post-filtered gain.
        """
        if gain.ndim != 2:
            return Err("gain must be 2D.")
        eps = 1e-10
        exponent = 1.0 + beta / (gain + eps)
        pf_gain = np.power(np.maximum(gain, eps), exponent)
        pf_gain = np.clip(pf_gain, 0.0, 1.0)
        return Ok(pf_gain)

    # -----------------------------------------------------------------
    # 7. BAND SPLIT PROCESSING
    # -----------------------------------------------------------------

    def band_split(self, spec: np.ndarray, df_bins: int = 96) -> Result:
        """Split spectrogram into DF-band (low) and ERB-band (high).

        DeepFilterNet processes low frequencies (0 — ~5kHz) with deep filtering
        and high frequencies (~5 — 24kHz) with ERB gain-based masking.

        @param spec: (n_frames, n_bins) complex spectrogram.
        @param df_bins: Number of frequency bins for deep filtering (default 96).
        @returns Result containing dict with 'df_band' and 'erb_band'.
        """
        if spec.ndim != 2:
            return Err("spec must be 2D.")
        n_bins = spec.shape[1]
        if df_bins > n_bins:
            return Err(f"df_bins ({df_bins}) exceeds total bins ({n_bins}).")
        return Ok({
            "df_band": spec[:, :df_bins],
            "erb_band": spec[:, df_bins:],
        })

    def band_merge(self, df_band: np.ndarray, erb_band: np.ndarray) -> Result:
        """Merge DF-band and ERB-band back into full spectrogram.

        @param df_band: (n_frames, df_bins) DF-band spectrogram.
        @param erb_band: (n_frames, erb_bins) ERB-band spectrogram.
        @returns Result containing (n_frames, df_bins + erb_bins) merged spectrogram.
        """
        if df_band.ndim != 2 or erb_band.ndim != 2:
            return Err("Both bands must be 2D.")
        if df_band.shape[0] != erb_band.shape[0]:
            return Err("Frame count mismatch between bands.")
        return Ok(np.hstack([df_band, erb_band]))

    # -----------------------------------------------------------------
    # 8. QUALITY METRICS
    # -----------------------------------------------------------------

    def compute_snr(self, clean: np.ndarray, noisy: np.ndarray) -> Result:
        """Compute Signal-to-Noise Ratio in dB.

        SNR = 10 * log10(||clean||^2 / ||noise||^2)

        @param clean: 1D clean reference signal.
        @param noisy: 1D noisy signal (same length).
        @returns Result containing scalar SNR in dB.
        """
        if clean.shape != noisy.shape or clean.ndim != 1:
            return Err("Both signals must be 1D with same length.")
        noise = noisy - clean
        sig_power = np.sum(clean ** 2)
        noise_power = np.sum(noise ** 2)
        if noise_power < 1e-15:
            return Ok(float('inf'))
        if sig_power < 1e-15:
            return Ok(float('-inf'))
        return Ok(float(10.0 * np.log10(sig_power / noise_power)))

    def compute_segmental_snr(
        self, clean: np.ndarray, noisy: np.ndarray, frame_len: int = 512
    ) -> Result:
        """Compute segmental SNR (average SNR across short frames).

        More perceptually meaningful than global SNR, as it prevents
        loud segments from dominating the metric.

        @param clean: 1D clean reference signal.
        @param noisy: 1D noisy signal.
        @param frame_len: Frame length for segmental analysis.
        @returns Result containing dict with 'mean_snr_db', 'per_frame_snr'.
        """
        if clean.shape != noisy.shape or clean.ndim != 1:
            return Err("Both signals must be 1D with same length.")
        if frame_len < 1:
            return Err("frame_len must be >= 1.")

        n = len(clean)
        n_frames = n // frame_len
        if n_frames == 0:
            return Err("Signal too short for given frame_len.")

        snr_per_frame = np.zeros(n_frames, dtype=np.float64)
        for i in range(n_frames):
            start = i * frame_len
            c = clean[start:start + frame_len]
            n_seg = noisy[start:start + frame_len] - c
            sp = np.sum(c ** 2)
            np_ = np.sum(n_seg ** 2)
            if np_ < 1e-15:
                snr_per_frame[i] = 30.0  # cap at 30 dB
            elif sp < 1e-15:
                snr_per_frame[i] = -30.0
            else:
                snr_per_frame[i] = np.clip(10.0 * np.log10(sp / np_), -30.0, 30.0)

        return Ok({
            "mean_snr_db": float(np.mean(snr_per_frame)),
            "per_frame_snr": snr_per_frame,
        })

    def compute_waveform_correlation(self, clean: np.ndarray, enhanced: np.ndarray) -> Result:
        """Compute normalized correlation between clean and enhanced waveforms.

        A simple proxy for perceptual quality (higher = better).
        rho = (clean · enhanced) / (||clean|| * ||enhanced||)

        @param clean: 1D clean reference signal.
        @param enhanced: 1D enhanced signal.
        @returns Result containing scalar correlation in [-1, 1].
        """
        if clean.shape != enhanced.shape or clean.ndim != 1:
            return Err("Both signals must be 1D with same length.")
        norm_c = np.linalg.norm(clean)
        norm_e = np.linalg.norm(enhanced)
        if norm_c < 1e-15 or norm_e < 1e-15:
            return Ok(0.0)
        return Ok(float(np.dot(clean, enhanced) / (norm_c * norm_e)))

    # -----------------------------------------------------------------
    # 9. FULL ENHANCEMENT PIPELINE (reference implementation)
    # -----------------------------------------------------------------

    def enhance_wiener(self, noisy_signal: np.ndarray, floor: float = 0.01) -> Result:
        """Full Wiener-filter based enhancement pipeline.

        Convenience method that chains: STFT → noise estimation → Wiener gain →
        apply gain → ISTFT.

        @param noisy_signal: 1D noisy audio signal.
        @param floor: Spectral floor for Wiener gain.
        @returns Result containing dict with 'enhanced', 'gain', 'noise_psd'.
        """
        stft_res = self.stft(noisy_signal)
        if isinstance(stft_res, Err):
            return stft_res
        spec = stft_res.value

        power = np.abs(spec) ** 2

        noise_res = self.estimate_noise_psd(power)
        if isinstance(noise_res, Err):
            return noise_res
        noise_psd = noise_res.value

        gain_res = self.wiener_gain(power, noise_psd, floor=floor)
        if isinstance(gain_res, Err):
            return gain_res
        gain = gain_res.value

        enhanced_spec_res = self.apply_spectral_gain(spec, gain)
        if isinstance(enhanced_spec_res, Err):
            return enhanced_spec_res

        istft_res = self.istft(enhanced_spec_res.value, output_length=len(noisy_signal))
        if isinstance(istft_res, Err):
            return istft_res

        return Ok({
            "enhanced": istft_res.value,
            "gain": gain,
            "noise_psd": noise_psd,
        })
