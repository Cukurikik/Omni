# omni_pitch_tracking_engine.py
# Production-Grade Pitch Determination Algorithms
# ==============================================================
# Absorbed from: orchidas/Pitch-Tracking
#
# Key patterns learned and implemented:
# - YIN Estimator: Difference function -> Cumulative Mean Normalized
#   Difference -> Absolute Thresholding -> Parabolic Interpolation.
# - Cepstrum Pitch Determination: identifying pitch via the real 
#   cepstrum (inverse fourier of log magnitude).
#
# OMNI Layer: compute/python_core
# @since 2026.4.0

"""
OMNI Pitch Tracking Engine
==========================
Production-grade engine for the OMNI Framework.

OMNI Layer: compute (Python)
"""
import math
from typing import Dict, Any
try:
    import numpy as np
except ImportError:
    np = None

ENGINE_VERSION = "1.0.0-omni"

class PitchTrackingError(Exception):
    pass


class OmniPitchTrackingEngine:
    """
    High-performance native implementations of classical and modern
    pitch tracking algorithms. Runs in pure numpy without heavy ML
    overhead for extreme real-time execution speeds.
    """

    def __init__(self, sample_rate: int = 44100):
        """Initialize OmniPitchTrackingEngine."""
        if np is None:
            raise PitchTrackingError("OmniPitchTrackingEngine strictly requires `numpy`.")
        self.sample_rate = sample_rate

    # ========================================================================
    # YIN ESTIMATOR
    # ========================================================================

    def yin_pitch(self, audio_frame: 'np.ndarray', f0_min: float = 50.0, f0_max: float = 2000.0, threshold: float = 0.1) -> float:
        """
        Implements the YIN pitch detection algorithm.
        Returns the fundamental frequency in Hz, or 0.0 if unvoiced.
        """
        tau_min = int(self.sample_rate / f0_max)
        tau_max = int(self.sample_rate / f0_min)
        
        W = len(audio_frame)
        if W <= tau_max:
            return 0.0

        # Step 1: Difference Function
        diff = np.zeros(tau_max)
        for tau in range(1, tau_max):
            # Optimised vectorized difference
            delta = audio_frame[:W - tau] - audio_frame[tau:W]
            diff[tau] = np.sum(delta * delta)
            
        # Step 2: Cumulative Mean Normalized Difference Function (CMNDF)
        cmndf = np.zeros(tau_max)
        cmndf[0] = 1.0 # default at tau=0
        cmndf_sum = 0.0
        for tau in range(1, tau_max):
            cmndf_sum += diff[tau]
            cmndf[tau] = diff[tau] * tau / (cmndf_sum + 1e-12)

        # Step 3: Absolute Thresholding
        tau_estimate = -1
        for tau in range(tau_min, tau_max):
            if cmndf[tau] < threshold:
                # Ensure we are at a local minimum
                while tau + 1 < tau_max and cmndf[tau + 1] < cmndf[tau]:
                    tau += 1
                tau_estimate = tau
                break

        if tau_estimate == -1:
            # Fallback to global minimum if threshold not met
            tau_estimate = np.argmin(cmndf[tau_min:tau_max]) + tau_min
            if cmndf[tau_estimate] > 0.5: # Way above threshold, likely unvoiced
                return 0.0

        # Step 4: Parabolic Interpolation for sub-sample accuracy
        if 0 < tau_estimate < tau_max - 1:
            alpha = cmndf[tau_estimate - 1]
            beta = cmndf[tau_estimate]
            gamma = cmndf[tau_estimate + 1]
            peak_offset = (alpha - gamma) / (2 * (alpha - 2 * beta + gamma) + 1e-12)
            fine_tau = tau_estimate + peak_offset
        else:
            fine_tau = tau_estimate

        return self.sample_rate / fine_tau

    # ========================================================================
    # CEPSTRUM
    # ========================================================================

    def cepstrum_pitch(self, audio_frame: 'np.ndarray', f0_min: float = 50.0, f0_max: float = 2000.0) -> float:
        """
        Implements Cepstrum Pitch Determination.
        Formula: ifft(log(abs(fft(x))))
        """
        # Apply window
        windowed = audio_frame * np.hanning(len(audio_frame))
        
        # FFT and log magnitude
        spectrum = np.fft.rfft(windowed)
        log_mag = np.log(np.abs(spectrum) + 1e-12)
        
        # Real Cepstrum
        cepstrum = np.fft.irfft(log_mag)
        
        tau_min = int(self.sample_rate / f0_max)
        tau_max = int(self.sample_rate / f0_min)
        
        if tau_max >= len(cepstrum):
            tau_max = len(cepstrum) - 1
            
        if tau_min >= tau_max:
            return 0.0
            
        # Find peak in Quefrency range corresponding to human pitch
        valid_quefrency = cepstrum[tau_min:tau_max]
        peak_idx = np.argmax(valid_quefrency) + tau_min
        
        # Parabolic interpolation
        if tau_min < peak_idx < tau_max - 1:
            alpha = cepstrum[peak_idx - 1]
            beta = cepstrum[peak_idx]
            gamma = cepstrum[peak_idx + 1]
            peak_offset = (alpha - gamma) / (2 * (alpha - 2 * beta + gamma) + 1e-12)
            fine_tau = peak_idx + peak_offset
        else:
            fine_tau = peak_idx

        return self.sample_rate / fine_tau

    def analyze_audio(self, audio_data: 'np.ndarray', method: str = "yin") -> Dict[str, Any]:
        """
        Analyzes a sequence of audio frames.
        """
        # Return dummy structure for architecture validation testing
        try:
            if method.lower() == "yin":
                result = self.yin_pitch(audio_data)
            else:
                result = self.cepstrum_pitch(audio_data)
                
            return {
                "status": "success",
                "data": {
                    "estimated_f0_hz": result,
                    "method": method,
                    "is_voiced": result > 0.0
                }
            }
        except Exception as e:
            return {"status": "error", "error": str(e)}

    def diagnostics(self):
        """Return engine health diagnostics."""
        return {
            "engine_id": "omni-pitch-tracking",
            "version": getattr(self, "VERSION", "1.0.0"),
            "status": "operational",
        }

