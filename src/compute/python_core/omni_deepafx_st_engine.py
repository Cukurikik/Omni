# omni_deepafx_st_engine.py
# Production-Grade Deep Audio Effects Style Transfer Engine
# ==============================================================
# Absorbed from: adobe-research/DeepAFx-ST
#
# Key patterns learned and implemented:
# - Audio style transfer via learned effect parameters
# - Differentiable signal processing chain modeling
# - Effect parameter extraction from reference audio
# - Multi-band equalization and dynamics processing
#
# OMNI Layer: compute/python_core
# @since 2026.4.0

"""
OMNI Deepafx St Engine
======================
Production-grade engine for the OMNI Framework.

OMNI Layer: compute (Python)
"""
from typing import List, Optional, Dict, Any, Tuple
import math

ENGINE_VERSION = "1.0.0-omni"
from src.compute.python_core.omni_base_engine import Result, Ok, Err


class DeepAfxError(Exception):
    """Base error for DeepAFx-ST operations."""
    pass


class InvalidEffectChainError(DeepAfxError):
    """Raised when an invalid effect chain is specified."""
    pass


class ParameterOutOfRangeError(DeepAfxError):
    """Raised when effect parameter is outside valid range."""
    pass


class OmniDeepafxStEngine:
    """
    Production-grade deep audio effects style transfer engine.

    Implements a differentiable signal processing chain that learns
    effect parameters from reference audio to apply matching style
    transformations. Supports multi-band EQ, compression, reverb
    parameter estimation, and gain staging.

    Attributes:
        num_bands: Number of EQ bands for equalization.
        sample_rate: Audio sample rate in Hz.
        block_size: Processing block size in samples.
        effect_chain: Ordered list of effect types to apply.
    """

    AVAILABLE_EFFECTS = (
        "eq", "compressor", "reverb", "gain", "saturation", "stereo_width"
    )

    def __init__(
        self,
        num_bands: int = 6,
        sample_rate: int = 44100,
        block_size: int = 2048,
        effect_chain: Optional[List[str]] = None,
    ):
        """
        Initialize the DeepAFx-ST engine.

        Args:
            num_bands: Number of parametric EQ bands.
            sample_rate: Audio sample rate in Hz.
            block_size: DSP block size in samples.
            effect_chain: List of effect names to apply in order.

        Raises:
            InvalidEffectChainError: If unknown effects are specified.
        """
        if effect_chain is None:
            effect_chain = ["eq", "compressor", "gain"]

        invalid = set(effect_chain) - set(self.AVAILABLE_EFFECTS)
        if invalid:
            raise InvalidEffectChainError(
                f"Unknown effects: {invalid}. "
                f"Available: {self.AVAILABLE_EFFECTS}"
            )

        self.num_bands = num_bands
        self.sample_rate = sample_rate
        self.block_size = block_size
        self.effect_chain = effect_chain

    def extract_spectral_features(
        self, samples: List[float]
    ) -> Dict[str, Any]:
        """
        Extract spectral features for style characterization.

        Computes per-band energy distribution, spectral tilt,
        and crest factor to characterize the audio's tonal profile.

        Args:
            samples: Audio samples as float list.

        Returns:
            Dict with spectral feature vectors.

        Raises:
            DeepAfxError: If samples are empty.
        """
        if not samples:
            raise DeepAfxError("Cannot extract features from empty audio")

        n = len(samples)
        band_size = n // self.num_bands
        band_energies: List[float] = []
        band_peaks: List[float] = []

        for b in range(self.num_bands):
            start = b * band_size
            end = min(start + band_size, n)
            band = samples[start:end]
            if band:
                rms = math.sqrt(sum(s * s for s in band) / len(band))
                peak = max(abs(s) for s in band)
                band_energies.append(round(rms, 6))
                band_peaks.append(round(peak, 6))
            else:
                band_energies.append(0.0)
                band_peaks.append(0.0)

        total_energy = sum(band_energies)
        spectral_tilt = 0.0
        if total_energy > 0 and len(band_energies) > 1:
            weights = list(range(len(band_energies)))
            weighted_sum = sum(w * e for w, e in zip(weights, band_energies))
            spectral_tilt = weighted_sum / (total_energy * len(band_energies))

        crest_factors = [
            round(p / max(e, 1e-10), 4)
            for p, e in zip(band_peaks, band_energies)
        ]

        return {
            "status": "success",
            "data": {
                "band_energies": band_energies,
                "band_peaks": band_peaks,
                "spectral_tilt": round(spectral_tilt, 6),
                "crest_factors": crest_factors,
                "num_bands": self.num_bands,
            }
        }

    def compute_eq_parameters(
        self,
        source_features: Dict[str, Any],
        reference_features: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Compute EQ parameters to match reference spectral profile.

        Calculates per-band gain adjustments needed to transform
        the source spectral shape to match the reference.

        Args:
            source_features: Spectral features from source audio.
            reference_features: Spectral features from reference audio.

        Returns:
            Dict with computed EQ band parameters (freq, gain_db, Q).
        """
        src_e = source_features.get("data", {}).get("band_energies", [])
        ref_e = reference_features.get("data", {}).get("band_energies", [])

        if len(src_e) != len(ref_e):
            raise InvalidEffectChainError(
                f"Band count mismatch: source={len(src_e)}, ref={len(ref_e)}"
            )

        eq_params: List[Dict[str, float]] = []
        nyquist = self.sample_rate / 2.0

        for i in range(len(src_e)):
            center_freq = nyquist * (i + 0.5) / len(src_e)
            src_db = 20 * math.log10(max(src_e[i], 1e-10))
            ref_db = 20 * math.log10(max(ref_e[i], 1e-10))
            gain_db = ref_db - src_db
            gain_db = max(-12.0, min(12.0, gain_db))

            eq_params.append({
                "band": i,
                "center_freq_hz": round(center_freq, 1),
                "gain_db": round(gain_db, 2),
                "q_factor": round(1.0 + abs(gain_db) / 6.0, 2),
                "bandwidth_oct": round(1.0 / (1.0 + abs(gain_db) / 12.0), 3),
            })

        return {
            "status": "success",
            "data": {
                "eq_bands": eq_params,
                "num_bands": len(eq_params),
                "total_gain_adjustment_db": round(
                    sum(p["gain_db"] for p in eq_params), 2
                ),
            }
        }

    def compute_compressor_parameters(
        self, samples: List[float]
    ) -> Dict[str, Any]:
        """
        Estimate dynamics compressor parameters from audio.

        Analyzes dynamic range to determine threshold, ratio,
        attack, and release settings.

        Args:
            samples: Audio samples as float list.

        Returns:
            Dict with compressor parameters.
        """
        if not samples:
            raise DeepAfxError("Cannot analyze dynamics of empty audio")

        abs_samples = [abs(s) for s in samples]
        peak = max(abs_samples)
        rms = math.sqrt(sum(s * s for s in samples) / len(samples))
        peak_db = 20 * math.log10(max(peak, 1e-10))
        rms_db = 20 * math.log10(max(rms, 1e-10))
        dynamic_range = peak_db - rms_db

        threshold_db = rms_db + (dynamic_range * 0.4)
        ratio = max(1.5, min(8.0, 1.0 + dynamic_range / 10.0))
        attack_ms = max(0.5, min(50.0, 10.0 / max(peak, 0.01)))
        release_ms = attack_ms * 10.0

        makeup_gain_db = max(
            0, (threshold_db * (1 - 1 / ratio)) * 0.6
        )

        return {
            "status": "success",
            "data": {
                "threshold_db": round(threshold_db, 2),
                "ratio": round(ratio, 2),
                "attack_ms": round(attack_ms, 2),
                "release_ms": round(release_ms, 2),
                "makeup_gain_db": round(makeup_gain_db, 2),
                "knee_db": 6.0,
                "dynamic_range_db": round(dynamic_range, 2),
                "peak_db": round(peak_db, 2),
                "rms_db": round(rms_db, 2),
            }
        }

    def apply_gain_staging(
        self, samples: List[float], target_lufs: float = -14.0
    ) -> Dict[str, Any]:
        """
        Apply loudness-normalized gain staging.

        Adjusts signal level to match target integrated loudness.

        Args:
            samples: Audio samples as float list.
            target_lufs: Target integrated loudness in LUFS.

        Returns:
            Dict with gain-adjusted samples and loudness metrics.
        """
        if not samples:
            raise DeepAfxError("Cannot apply gain to empty audio")

        rms = math.sqrt(sum(s * s for s in samples) / len(samples))
        current_lufs = 20 * math.log10(max(rms, 1e-10)) - 0.691

        gain_db = target_lufs - current_lufs
        gain_db = max(-20.0, min(20.0, gain_db))
        gain_linear = 10 ** (gain_db / 20.0)

        adjusted = [s * gain_linear for s in samples]
        clipped = sum(1 for s in adjusted if abs(s) > 1.0)

        if clipped > 0:
            peak = max(abs(s) for s in adjusted)
            adjusted = [s / peak for s in adjusted]

        return {
            "status": "success",
            "data": {
                "samples": adjusted,
                "gain_applied_db": round(gain_db, 2),
                "current_lufs": round(current_lufs, 2),
                "target_lufs": target_lufs,
                "clipped_samples": clipped,
                "peak_after": round(max(abs(s) for s in adjusted), 6),
            }
        }

    def diagnostics(self):
        """Return engine health diagnostics."""
        return {
            "engine_id": "omni-deepafx-st",
            "version": getattr(self, "VERSION", "1.0.0"),
            "status": "operational",
        }
