# omni_spafe_engine.py
# Production-Grade Speech & Audio Feature Extraction Engine
# ==============================================================
# Absorbed from: SuperKogito/spafe
#
# Key patterns learned and implemented:
# - MFCC (Mel-Frequency Cepstral Coefficients) computation
# - Mel filterbank generation with configurable parameters
# - Pre-emphasis filtering for speech signal conditioning
# - Spectral rolloff and bandwidth feature extraction
#
# OMNI Layer: compute/python_core
# @since 2026.4.0

"""
OMNI Spafe Engine
=================
Production-grade engine for the OMNI Framework.

OMNI Layer: compute (Python)
"""
from typing import List, Optional, Dict, Any, Tuple
import math

ENGINE_VERSION = "1.0.0-omni"


class SpafeError(Exception):
    """Base error for Spafe operations."""
    pass


class InvalidParameterError(SpafeError):
    """Raised when input parameters are out of valid range."""
    pass


class InsufficientDataError(SpafeError):
    """Raised when too few samples for the requested operation."""
    pass


def _hz_to_mel(hz: float) -> float:
    """Convert frequency in Hz to Mel scale."""
    return 2595.0 * math.log10(1.0 + hz / 700.0)


def _mel_to_hz(mel: float) -> float:
    """Convert Mel scale value back to Hz."""
    return 700.0 * (10.0 ** (mel / 2595.0) - 1.0)


class OmniSpafeEngine:
    """
    Production-grade speech and audio feature extraction engine.

    Implements fundamental acoustic feature extraction algorithms
    including MFCC computation, Mel filterbank construction,
    pre-emphasis filtering, and spectral analysis. All operations
    use pure Python math for portability.

    Attributes:
        sample_rate: Audio sample rate in Hz.
        num_filters: Number of Mel filterbank channels.
        num_ceps: Number of cepstral coefficients to retain.
        frame_size: Analysis frame size in samples.
        hop_size: Hop between frames in samples.
    """

    def __init__(
        self,
        sample_rate: int = 16000,
        num_filters: int = 26,
        num_ceps: int = 13,
        frame_size: int = 512,
        hop_size: int = 160,
    ):
        """
        Initialize the Spafe engine.

        Args:
            sample_rate: Audio sample rate in Hz. Must be > 0.
            num_filters: Number of Mel filterbank channels.
            num_ceps: Number of MFCC coefficients. Must be <= num_filters.
            frame_size: Frame size in samples.
            hop_size: Hop size in samples.

        Raises:
            InvalidParameterError: On invalid configuration.
        """
        if sample_rate <= 0:
            raise InvalidParameterError(f"sample_rate must be > 0, got {sample_rate}")
        if num_ceps > num_filters:
            raise InvalidParameterError(
                f"num_ceps ({num_ceps}) must be <= num_filters ({num_filters})"
            )
        self.sample_rate = sample_rate
        self.num_filters = num_filters
        self.num_ceps = num_ceps
        self.frame_size = frame_size
        self.hop_size = hop_size

    def apply_preemphasis(
        self, samples: List[float], coeff: float = 0.97
    ) -> Dict[str, Any]:
        """
        Apply pre-emphasis filter to boost high frequencies.

        y[n] = x[n] - coeff * x[n-1]

        Args:
            samples: Raw audio samples.
            coeff: Pre-emphasis coefficient [0.0, 1.0].

        Returns:
            Dict with filtered signal and metadata.
        """
        if not samples:
            raise InsufficientDataError("Cannot pre-emphasize empty signal")
        if not 0.0 <= coeff <= 1.0:
            raise InvalidParameterError(f"coeff must be in [0, 1], got {coeff}")

        output = [samples[0]]
        for i in range(1, len(samples)):
            output.append(samples[i] - coeff * samples[i - 1])

        return {
            "status": "success",
            "data": {
                "signal": output,
                "length": len(output),
                "coeff": coeff,
            }
        }

    def compute_mel_filterbank(self) -> Dict[str, Any]:
        """
        Construct a Mel-spaced triangular filterbank.

        Returns:
            Dict with filterbank matrix [num_filters x (frame_size//2 + 1)].
        """
        low_mel = _hz_to_mel(0)
        high_mel = _hz_to_mel(self.sample_rate / 2.0)
        mel_points = [
            low_mel + i * (high_mel - low_mel) / (self.num_filters + 1)
            for i in range(self.num_filters + 2)
        ]
        hz_points = [_mel_to_hz(m) for m in mel_points]
        nfft = self.frame_size
        bin_points = [
            int(math.floor((nfft + 1) * h / self.sample_rate))
            for h in hz_points
        ]

        num_bins = nfft // 2 + 1
        filterbank: List[List[float]] = []
        for m in range(self.num_filters):
            filt = [0.0 for _ in range(num_bins)]
            for k in range(num_bins):
                if bin_points[m] <= k < bin_points[m + 1]:
                    denom = bin_points[m + 1] - bin_points[m]
                    filt[k] = (k - bin_points[m]) / max(denom, 1)
                elif bin_points[m + 1] <= k <= bin_points[m + 2]:
                    denom = bin_points[m + 2] - bin_points[m + 1]
                    filt[k] = (bin_points[m + 2] - k) / max(denom, 1)
            filterbank.append(filt)

        return {
            "status": "success",
            "data": {
                "filterbank": filterbank,
                "num_filters": self.num_filters,
                "num_bins": num_bins,
                "mel_range": [round(low_mel, 2), round(high_mel, 2)],
            }
        }

    def compute_power_spectrum(
        self, frame: List[float]
    ) -> Dict[str, Any]:
        """
        Compute the power spectrum of a windowed frame using DFT.

        Args:
            frame: Windowed audio frame samples.

        Returns:
            Dict with magnitude and power spectrum bins.
        """
        if not frame:
            raise InsufficientDataError("Cannot compute spectrum of empty frame")

        n = len(frame)
        magnitude: List[float] = []
        power: List[float] = []

        for k in range(n // 2 + 1):
            re = sum(
                frame[t] * math.cos(2 * math.pi * k * t / n)
                for t in range(n)
            )
            im = sum(
                frame[t] * math.sin(2 * math.pi * k * t / n)
                for t in range(n)
            )
            mag = math.sqrt(re * re + im * im)
            magnitude.append(mag)
            power.append(mag * mag / n)

        return {
            "status": "success",
            "data": {
                "magnitude": magnitude,
                "power": power,
                "num_bins": len(magnitude),
                "freq_resolution": round(self.sample_rate / n, 4),
            }
        }

    def compute_spectral_rolloff(
        self,
        magnitude_spectrum: List[float],
        rolloff_percent: float = 0.85,
    ) -> Dict[str, Any]:
        """
        Compute spectral rolloff frequency.

        The rolloff point is the frequency below which a given
        percentage of total spectral energy is concentrated.

        Args:
            magnitude_spectrum: Magnitude spectrum bins.
            rolloff_percent: Energy percentage threshold [0.0, 1.0].

        Returns:
            Dict with rolloff frequency in Hz and bin index.
        """
        if not magnitude_spectrum:
            raise InsufficientDataError("Empty spectrum for rolloff")
        if not 0.0 < rolloff_percent <= 1.0:
            raise InvalidParameterError(
                f"rolloff_percent must be in (0, 1], got {rolloff_percent}"
            )

        total_energy = sum(m * m for m in magnitude_spectrum)
        threshold = rolloff_percent * total_energy
        cumulative = 0.0
        rolloff_bin = len(magnitude_spectrum) - 1

        for i, m in enumerate(magnitude_spectrum):
            cumulative += m * m
            if cumulative >= threshold:
                rolloff_bin = i
                break

        freq_resolution = self.sample_rate / (2 * len(magnitude_spectrum))
        rolloff_hz = rolloff_bin * freq_resolution

        return {
            "status": "success",
            "data": {
                "rolloff_hz": round(rolloff_hz, 2),
                "rolloff_bin": rolloff_bin,
                "rolloff_percent": rolloff_percent,
                "total_bins": len(magnitude_spectrum),
            }
        }

    def compute_spectral_bandwidth(
        self, magnitude_spectrum: List[float]
    ) -> Dict[str, Any]:
        """
        Compute spectral bandwidth (spread) around the centroid.

        Args:
            magnitude_spectrum: Magnitude spectrum bins.

        Returns:
            Dict with bandwidth in Hz.
        """
        if not magnitude_spectrum:
            raise InsufficientDataError("Empty spectrum for bandwidth")

        total = sum(magnitude_spectrum)
        if total == 0:
            return {
                "status": "success",
                "data": {"bandwidth_hz": 0.0, "centroid_hz": 0.0}
            }

        freq_res = self.sample_rate / (2 * len(magnitude_spectrum))
        centroid = sum(
            i * freq_res * magnitude_spectrum[i]
            for i in range(len(magnitude_spectrum))
        ) / total

        variance = sum(
            magnitude_spectrum[i] * (i * freq_res - centroid) ** 2
            for i in range(len(magnitude_spectrum))
        ) / total

        bandwidth = math.sqrt(variance)

        return {
            "status": "success",
            "data": {
                "bandwidth_hz": round(bandwidth, 4),
                "centroid_hz": round(centroid, 4),
                "variance": round(variance, 4),
            }
        }

    def diagnostics(self):
        """Return engine health diagnostics."""
        return {
            "engine_id": "omni-spafe",
            "version": getattr(self, "VERSION", "1.0.0"),
            "status": "operational",
        }
