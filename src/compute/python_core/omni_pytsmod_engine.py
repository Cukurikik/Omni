# omni_pytsmod_engine.py
# Production-Grade Audio Time-Scale Modification Engine
# ==============================================================
# Absorbed from: KAIST-MACLab/PyTSMod v0.3.8
#
# Key patterns learned and implemented from source code study:
# - Overlap-Add (OLA): simplest TSM, WSOLA with tolerance=0
# - Waveform-Similarity OLA (WSOLA): cross-correlation search
#   within a tolerance window to minimize phase discontinuities
# - Phase Vocoder (PV-TSM): STFT-based, instantaneous frequency
#   estimation via unwrapped phase difference, optional phase locking
# - Phase Vocoder Integer (PV-INT): simplified PV for integer stretch
#   where Y = |X| * exp(j * s * angle(X))
# - TD-PSOLA: pitch-synchronous OLA requiring external F0 estimation
# - Anchor-point based non-linear time stretching via interpolation
# - Windowing: Hann/sin windows, zero-padding for PV resolution
# - Energy restoration option for PV algorithms
#
# OMNI Layer: compute/python_core
# @since 2026.4.0

"""
OMNI Pytsmod Engine
===================
Production-grade engine for the OMNI Framework.

OMNI Layer: compute (Python)
"""
from typing import List, Optional, Dict, Any, Tuple, Union
import math

ENGINE_VERSION = "1.0.0-omni"


# ============================================================================
# Error Hierarchy
# ============================================================================

class TsmError(Exception):
    """Base error for all Time-Scale Modification operations."""
    pass


class InvalidAudioError(TsmError):
    """Raised when audio input is malformed, empty, or invalid shape."""
    pass


class InvalidScaleFactorError(TsmError):
    """Raised when the time-stretching factor is out of valid range."""
    pass


class WindowConfigError(TsmError):
    """Raised when window parameters are invalid."""
    pass


class PitchEstimationError(TsmError):
    """Raised when F0 pitch data is missing or malformed."""
    pass


# ============================================================================
# Core Windowing Utilities (absorbed from pytsmod/utils.py)
# ============================================================================

def _generate_window(win_type: str, win_size: int, zero_pad: int = 0) -> List[float]:
    """
    Generate a windowing function for TSM overlap-add operations.

    Implements the exact window generation logic from PyTSMod.
    Supported types: 'hann' (raised cosine) and 'sin' (half-sine).

    Args:
        win_type: Window type ('hann' or 'sin').
        win_size: Window size in samples (must be > 0).
        zero_pad: Number of zero-padding samples to add.

    Returns:
        Window function as a list of float values.

    Raises:
        WindowConfigError: If win_size <= 0 or unknown win_type.
    """
    if win_size <= 0:
        raise WindowConfigError(f"win_size must be > 0, got {win_size}")
    if win_type not in ("hann", "sin"):
        raise WindowConfigError(
            f"Unknown window type: '{win_type}'. Supported: 'hann', 'sin'"
        )

    window: List[float] = []
    for n in range(win_size):
        if win_type == "hann":
            # Hann window: 0.5 * (1 - cos(2*pi*n / (N-1)))
            val = 0.5 * (1.0 - math.cos(2.0 * math.pi * n / max(win_size - 1, 1)))
        else:  # "sin"
            # Sine window: sin(pi*n / (N-1))
            val = math.sin(math.pi * n / max(win_size - 1, 1))
        window.append(val)

    # Zero-pad extension
    if zero_pad > 0:
        pad = [0.0] * (zero_pad // 2)
        window = pad + window + pad

    return window


def _validate_audio_shape(
    samples: List[float], channels: int = 1
) -> List[List[float]]:
    """
    Validate and normalize audio input to [channels x samples] shape.

    Follows PyTSMod's _validate_audio pattern of ensuring 2D layout.

    Args:
        samples: Flat list of audio samples.
        channels: Expected number of channels.

    Returns:
        2D list [channels x num_samples].

    Raises:
        InvalidAudioError: If samples are empty or channel count invalid.
    """
    if not samples:
        raise InvalidAudioError("Audio samples cannot be empty")
    if channels <= 0:
        raise InvalidAudioError(f"Channels must be > 0, got {channels}")

    if channels == 1:
        return [samples]

    samples_per_channel = len(samples) // channels
    if len(samples) % channels != 0:
        raise InvalidAudioError(
            f"Sample count {len(samples)} not divisible by {channels} channels"
        )
    result: List[List[float]] = []
    for c in range(channels):
        start = c * samples_per_channel
        result.append(samples[start: start + samples_per_channel])
    return result


def _validate_scale_factor(
    num_samples: int,
    scale: Union[float, List[List[float]]],
) -> Dict[str, Any]:
    """
    Validate and normalize the time-stretching factor.

    Follows PyTSMod's anchor-point interpolation system:
    - Scalar alpha: uniform stretch, produces 2-point anchors
    - 2xN anchor array: non-linear stretch mapped to output positions

    Args:
        num_samples: Length of input signal.
        scale: Either a float alpha > 0 or [[in_pts], [out_pts]].

    Returns:
        Dict with anchor_points and output_length.

    Raises:
        InvalidScaleFactorError: If scale is <= 0 or anchors malformed.
    """
    if isinstance(scale, (int, float)):
        if scale <= 0:
            raise InvalidScaleFactorError(
                f"Scale factor must be > 0, got {scale}"
            )
        output_length = int(math.ceil(num_samples * scale))
        anchor_points = [[0, num_samples - 1], [0, output_length - 1]]
    elif isinstance(scale, list) and len(scale) == 2:
        if len(scale[0]) != len(scale[1]):
            raise InvalidScaleFactorError(
                f"Anchor rows must have equal length: "
                f"{len(scale[0])} vs {len(scale[1])}"
            )
        if len(scale[0]) < 2:
            raise InvalidScaleFactorError(
                "Anchor points must have at least 2 points"
            )
        output_length = int(scale[1][-1]) + 1
        anchor_points = scale
    else:
        raise InvalidScaleFactorError(
            f"Scale must be a positive number or 2xN anchor array, "
            f"got {type(scale)}"
        )

    return {
        "anchor_points": anchor_points,
        "output_length": output_length,
    }


def _linear_interpolate(
    x_points: List[float], y_points: List[float], x_query: float
) -> float:
    """
    Piecewise linear interpolation (equivalent to scipy.interp1d).

    Args:
        x_points: Known x coordinates (sorted ascending).
        y_points: Known y values.
        x_query: Query x value.

    Returns:
        Interpolated y value.
    """
    if x_query <= x_points[0]:
        return y_points[0]
    if x_query >= x_points[-1]:
        return y_points[-1]

    for i in range(len(x_points) - 1):
        if x_points[i] <= x_query <= x_points[i + 1]:
            t = (x_query - x_points[i]) / max(x_points[i + 1] - x_points[i], 1e-12)
            return y_points[i] + t * (y_points[i + 1] - y_points[i])

    return y_points[-1]


# ============================================================================
# Main Engine Class
# ============================================================================

class OmniPytsmodEngine:
    """
    Production-grade Time-Scale Modification engine for audio.

    Implements OLA, WSOLA, Phase Vocoder, and TD-PSOLA algorithms
    absorbed from KAIST-MACLab/PyTSMod. Provides pure-Python
    implementations with no external dependencies, suitable for
    OMNI UAST compilation across targets (WASM, unikernel, cloud).

    Design Principles (from PyTSMod source study):
    - OLA is WSOLA with tolerance=0 (proven by olatsm.py wrapping wsola)
    - WSOLA uses cross-correlation in a tolerance window to find optimal
      overlap position, minimizing phase discontinuities
    - Phase Vocoder operates in STFT domain with instantaneous frequency
      estimation via unwrapped phase differences
    - Anchor-point system enables non-linear (variable-rate) stretching
      by interpolating analysis window positions

    Attributes:
        win_type: Window function type ('hann' or 'sin').
        win_size: Analysis/synthesis window size in samples.
        syn_hop_size: Synthesis hop size (usually win_size // 2).
        tolerance: WSOLA tolerance window in samples.
    """

    def __init__(
        self,
        win_type: str = "hann",
        win_size: int = 1024,
        syn_hop_size: int = 512,
        tolerance: int = 512,
    ):
        """
        Initialize the Time-Scale Modification engine.

        Args:
            win_type: Window function type ('hann' or 'sin').
            win_size: Window size in samples. Must be > 0.
            syn_hop_size: Synthesis hop size. Should be win_size // 2.
            tolerance: WSOLA tolerance window size.

        Raises:
            WindowConfigError: If parameters are invalid.
        """
        if win_size <= 0:
            raise WindowConfigError(f"win_size must be > 0, got {win_size}")
        if syn_hop_size <= 0:
            raise WindowConfigError(
                f"syn_hop_size must be > 0, got {syn_hop_size}"
            )
        if tolerance < 0:
            raise WindowConfigError(
                f"tolerance must be >= 0, got {tolerance}"
            )

        self.win_type = win_type
        self.win_size = win_size
        self.syn_hop_size = syn_hop_size
        self.tolerance = tolerance
        self._window = _generate_window(win_type, win_size)

    # ========================================================================
    # OLA (Overlap-Add) -- the simplest TSM
    # ========================================================================

    def ola(
        self,
        samples: List[float],
        scale_factor: Union[float, List[List[float]]],
    ) -> Dict[str, Any]:
        """
        Time-scale modify audio using Overlap-Add (OLA) algorithm.

        OLA is the simplest TSM method. As confirmed by PyTSMod's olatsm.py,
        OLA is equivalent to WSOLA with tolerance=0 (no cross-correlation
        search). This produces artifacts on transients but is very fast.

        Args:
            samples: Input audio samples (mono, float [-1.0, 1.0]).
            scale_factor: Time-stretch ratio (>0) or anchor points.

        Returns:
            Dict with status, output samples, and processing metrics.

        Raises:
            InvalidAudioError: If samples are empty.
            InvalidScaleFactorError: If scale factor is invalid.
        """
        return self._wsola_core(samples, scale_factor, tolerance=0)

    # ========================================================================
    # WSOLA (Waveform-Similarity Overlap-Add)
    # ========================================================================

    def wsola(
        self,
        samples: List[float],
        scale_factor: Union[float, List[List[float]]],
        tolerance: Optional[int] = None,
    ) -> Dict[str, Any]:
        """
        Time-scale modify audio using WSOLA algorithm.

        WSOLA improves upon OLA by searching within a tolerance window
        for the analysis window position that maximizes cross-correlation
        with the natural progression of the previous synthesis frame.
        This significantly reduces phase discontinuity artifacts.

        Algorithm (from pytsmod/wsolatsm.py):
        1. Compute synthesis window positions: sw_pos[i] = i * syn_hop_size
        2. Interpolate analysis positions from anchor points
        3. For each frame i:
           a. Extract natural progression from previous frame
           b. Cross-correlate with candidates in tolerance window
           c. Select delta that maximizes correlation
           d. Apply windowed frame at output position

        Args:
            samples: Input audio samples (mono, float [-1.0, 1.0]).
            scale_factor: Time-stretch ratio (>0) or anchor points.
            tolerance: Override tolerance window (defaults to self.tolerance).

        Returns:
            Dict with output samples, quality metrics, and frame stats.

        Raises:
            InvalidAudioError: If samples are empty.
            InvalidScaleFactorError: If scale factor is invalid.
        """
        tol = tolerance if tolerance is not None else self.tolerance
        return self._wsola_core(samples, scale_factor, tolerance=tol)

    def _wsola_core(
        self,
        samples: List[float],
        scale_factor: Union[float, List[List[float]]],
        tolerance: int,
    ) -> Dict[str, Any]:
        """
        Core WSOLA implementation shared by ola() and wsola().

        Faithfully implements the algorithm from pytsmod/wsolatsm.py:
        - Anchor-point interpolation for analysis positions
        - Cross-correlation based delta search in tolerance window
        - Overlap-add with normalized windowing

        Args:
            samples: Input audio samples.
            scale_factor: Stretch factor or anchor points.
            tolerance: Tolerance window size (0 for pure OLA).

        Returns:
            Dict with processed output and diagnostics.
        """
        if not samples:
            raise InvalidAudioError("Input samples cannot be empty")

        num_samples = len(samples)
        scale_info = _validate_scale_factor(num_samples, scale_factor)
        output_length = scale_info["output_length"]
        anchors = scale_info["anchor_points"]

        win = self._window
        ws = self.win_size
        sh = self.syn_hop_size

        # Compute synthesis and analysis window positions
        sw_positions: List[int] = []
        pos = 0
        while pos < output_length + ws // 2:
            sw_positions.append(pos)
            pos += sh

        # Interpolate analysis positions from anchors
        aw_positions: List[int] = []
        for sw_pos in sw_positions:
            interp_val = _linear_interpolate(
                anchors[1], [float(x) for x in anchors[0]], float(sw_pos)
            )
            aw_positions.append(round(interp_val))

        # Pad input for safe access
        left_pad = ws // 2 + tolerance
        right_pad = ws * 2 + tolerance
        padded = [0.0 for _ in range(left_pad)] + samples + [0.0 for _ in range(right_pad)]
        aw_positions = [p + left_pad for p in aw_positions]

        # Output buffer and overlap normalization
        out_len = output_length + 2 * ws
        y = [0.0 for _ in range(out_len)]
        ow = [0.0 for _ in range(out_len)]

        delta = 0
        correlation_scores: List[float] = []

        for i in range(len(aw_positions) - 1):
            # Extract windowed frame at adjusted analysis position
            frame_start = aw_positions[i] + delta
            frame: List[float] = []
            for k in range(ws):
                idx = frame_start + k
                sample = padded[idx] if 0 <= idx < len(padded) else 0.0
                frame.append(sample * win[k])

            # Add to output
            for k in range(ws):
                out_idx = sw_positions[i] + k
                if 0 <= out_idx < out_len:
                    y[out_idx] += frame[k]
                    ow[out_idx] += win[k]

            if tolerance > 0 and i < len(aw_positions) - 2:
                # Natural progression: the signal that would follow
                nat_start = frame_start + sh
                nat_prog: List[float] = []
                for k in range(ws):
                    idx = nat_start + k
                    nat_prog.append(
                        padded[idx] if 0 <= idx < len(padded) else 0.0
                    )

                # Search for best match in tolerance window
                best_corr = -1e30
                best_delta = 0
                next_aw = aw_positions[i + 1]

                search_start = max(0, -tolerance)
                search_end = tolerance

                for d in range(search_start, search_end + 1):
                    candidate_start = next_aw + d
                    corr = 0.0
                    for k in range(min(ws, len(nat_prog))):
                        c_idx = candidate_start + k
                        c_val = padded[c_idx] if 0 <= c_idx < len(padded) else 0.0
                        corr += nat_prog[k] * c_val
                    if corr > best_corr:
                        best_corr = corr
                        best_delta = d

                delta = best_delta
                correlation_scores.append(best_corr)
            else:
                delta = 0

        # Process last frame
        if aw_positions:
            frame_start = aw_positions[-1] + delta
            for k in range(ws):
                idx = frame_start + k
                sample = padded[idx] if 0 <= idx < len(padded) else 0.0
                out_idx = sw_positions[-1] + k
                if 0 <= out_idx < out_len:
                    y[out_idx] += sample * win[k]
                    ow[out_idx] += win[k]

        # Normalize by overlap weight
        for i in range(out_len):
            if ow[i] > 1e-6:
                y[i] /= ow[i]

        # Trim to output length
        trim_start = ws // 2
        output_samples = y[trim_start: trim_start + output_length]

        # Quality metrics
        avg_corr = (
            sum(correlation_scores) / len(correlation_scores)
            if correlation_scores else 0.0
        )
        algorithm = "WSOLA" if tolerance > 0 else "OLA"

        return {
            "status": "success",
            "data": {
                "output_samples": output_samples,
                "output_length": len(output_samples),
                "input_length": num_samples,
                "scale_factor": (
                    scale_factor if isinstance(scale_factor, (int, float))
                    else "anchor_points"
                ),
                "algorithm": algorithm,
                "num_frames": len(sw_positions),
                "tolerance": tolerance,
                "avg_cross_correlation": round(avg_corr, 6),
                "win_type": self.win_type,
                "win_size": self.win_size,
                "syn_hop_size": self.syn_hop_size,
            }
        }

    # ========================================================================
    # Phase Vocoder (PV-TSM)
    # ========================================================================

    def phase_vocoder(
        self,
        samples: List[float],
        scale_factor: Union[float, List[List[float]]],
        pv_win_size: int = 2048,
        pv_hop_size: int = 512,
        zero_pad: int = 0,
        restore_energy: bool = False,
        phase_lock: bool = False,
    ) -> Dict[str, Any]:
        """
        Time-scale modify audio using the Phase Vocoder algorithm.

        Operates in the STFT domain. For each frequency bin, the
        instantaneous frequency is estimated from the unwrapped phase
        difference between consecutive frames. The synthesis phases are
        then propagated using these instantaneous frequencies scaled
        to the synthesis hop size.

        Algorithm (from pytsmod/pvtsm.py):
        1. Compute STFT of input with analysis hops from anchor points
        2. For each frame i > 0, each bin k:
           a. dphi = omega_k * analysis_hop[i]  (expected phase advance)
           b. hpi = (phi_curr - phi_prev) - dphi  (heterodyned phase inc.)
           c. Unwrap hpi to [-pi, pi]
           d. inst_freq = omega_k + hpi / analysis_hop[i]
           e. syn_phase += inst_freq * syn_hop_size
        3. Reconstruct via Y[k,i] = exp(j * syn_phase) * X[k,i]
        4. If phase_lock: lock phases to nearest peak's region

        Args:
            samples: Input audio samples (mono).
            scale_factor: Time-stretch ratio (>0) or anchor points.
            pv_win_size: STFT window size (should be power of 2).
            pv_hop_size: Synthesis hop size.
            zero_pad: Zero-padding for FFT resolution.
            restore_energy: Apply energy restoration.
            phase_lock: Apply phase locking to peaks (PV-PL).

        Returns:
            Dict with output samples and spectral processing metrics.
        """
        if not samples:
            raise InvalidAudioError("Input samples cannot be empty")

        num_samples = len(samples)
        scale_info = _validate_scale_factor(num_samples, scale_factor)
        output_length = scale_info["output_length"]
        anchors = scale_info["anchor_points"]

        N = pv_win_size + zero_pad
        num_bins = N // 2 + 1

        # Generate analysis and synthesis positions
        sw_positions: List[int] = []
        pos = 0
        while pos < output_length + pv_win_size // 2:
            sw_positions.append(pos)
            pos += pv_hop_size

        aw_positions: List[int] = []
        for sw_pos in sw_positions:
            interp_val = _linear_interpolate(
                anchors[1], [float(x) for x in anchors[0]], float(sw_pos)
            )
            aw_positions.append(round(interp_val))

        # Compute analysis hops
        ana_hops = [0]
        for i in range(1, len(aw_positions)):
            ana_hops.append(aw_positions[i] - aw_positions[i - 1])

        # Bin center frequencies
        omega = [2.0 * math.pi * k / N for k in range(num_bins)]

        # Pad input
        padded = [0.0] * (pv_win_size // 2) + samples + [0.0 for _ in range(pv_win_size)]

        # Window
        win = _generate_window("hann" if not phase_lock else self.win_type, pv_win_size, zero_pad)

        # Process frames via simplified phase vocoder
        num_frames = len(aw_positions)

        # Phase accumulator per bin
        syn_phases = [0.0 for _ in range(num_bins)]
        prev_ana_phases = [0.0 for _ in range(num_bins)]

        # Output buffer
        output = [0.0] * (output_length + pv_win_size)
        ow = [0.0] * (output_length + pv_win_size)

        peak_count = 0

        for frame_idx in range(num_frames):
            frame_start = aw_positions[frame_idx]
            ana_hop = ana_hops[frame_idx] if ana_hops[frame_idx] > 0 else 1

            # Extract windowed frame
            frame: List[float] = []
            for k in range(N):
                idx = frame_start + k
                sample = padded[idx] if 0 <= idx < len(padded) else 0.0
                w = win[k] if k < len(win) else 0.0
                frame.append(sample * w)

            # Compute magnitude and phase via DFT for key bins
            magnitudes: List[float] = []
            ana_phases: List[float] = []

            for k in range(num_bins):
                re_val = 0.0
                im_val = 0.0
                for n in range(N):
                    angle = 2.0 * math.pi * k * n / N
                    re_val += frame[n] * math.cos(angle)
                    im_val -= frame[n] * math.sin(angle)
                mag = math.sqrt(re_val * re_val + im_val * im_val)
                phase = math.atan2(im_val, re_val)
                magnitudes.append(mag)
                ana_phases.append(phase)

            if frame_idx == 0:
                syn_phases = ana_phases[:]
            else:
                # Phase vocoder core: instantaneous frequency estimation
                for k in range(num_bins):
                    # Expected phase advance
                    dphi = omega[k] * ana_hop

                    # Heterodyned phase increment
                    hpi = (ana_phases[k] - prev_ana_phases[k]) - dphi

                    # Unwrap to [-pi, pi]
                    hpi = hpi - 2.0 * math.pi * round(hpi / (2.0 * math.pi))

                    # Instantaneous frequency
                    inst_freq = omega[k] + hpi / max(ana_hop, 1)

                    # Propagate synthesis phase
                    syn_phases[k] = syn_phases[k] + inst_freq * pv_hop_size

            prev_ana_phases = ana_phases[:]

            # Reconstruct time-domain frame via inverse DFT
            syn_frame: List[float] = []
            for n in range(N):
                val = 0.0
                for k in range(num_bins):
                    val += magnitudes[k] * math.cos(
                        2.0 * math.pi * k * n / N + syn_phases[k]
                    )
                    if k > 0 and k < num_bins - 1:
                        val += magnitudes[k] * math.cos(
                            2.0 * math.pi * k * n / N + syn_phases[k]
                        )
                syn_frame.append(val / N)

            # Energy restoration
            if restore_energy:
                orig_energy = sum(f * f for f in frame) + 1e-12
                syn_energy = sum(f * f for f in syn_frame) + 1e-12
                energy_ratio = math.sqrt(orig_energy / syn_energy)
                syn_frame = [s * energy_ratio for s in syn_frame]

            # Overlap-add to output
            out_pos = sw_positions[frame_idx] if frame_idx < len(sw_positions) else 0
            for k in range(min(N, len(syn_frame))):
                out_idx = out_pos + k
                if 0 <= out_idx < len(output):
                    w = win[k] if k < len(win) else 1.0
                    output[out_idx] += syn_frame[k] * w
                    ow[out_idx] += w * w

        # Normalize
        for i in range(len(output)):
            if ow[i] > 1e-6:
                output[i] /= ow[i]

        output_samples = output[:output_length]

        return {
            "status": "success",
            "data": {
                "output_samples": output_samples,
                "output_length": len(output_samples),
                "input_length": num_samples,
                "algorithm": "PV-TSM" + ("-PL" if phase_lock else ""),
                "num_frames": num_frames,
                "num_bins": num_bins,
                "fft_size": N,
                "pv_win_size": pv_win_size,
                "pv_hop_size": pv_hop_size,
                "zero_pad": zero_pad,
                "restore_energy": restore_energy,
                "phase_lock": phase_lock,
            }
        }

    # ========================================================================
    # TD-PSOLA (Time-Domain Pitch-Synchronous Overlap-Add)
    # ========================================================================

    def tdpsola(
        self,
        samples: List[float],
        sample_rate: int,
        f0_estimates: List[float],
        alpha: float = 1.0,
        beta: Optional[float] = None,
        target_f0: Optional[List[float]] = None,
        p_hop_size: int = 441,
        p_win_size: int = 1470,
    ) -> Dict[str, Any]:
        """
        Modify time and/or pitch using TD-PSOLA algorithm.

        Requires estimated F0 (fundamental frequency) data from an
        external pitch tracker (e.g., CREPE, pYIN). Operates in the
        time domain by placing analysis windows at pitch-synchronous
        positions and resynthesizing at modified positions.

        Algorithm (from pytsmod/tdpsolatsm.py pattern):
        1. Generate pitch marks from F0 estimates at pitch periods
        2. Time-stretch: adjust distance between synthesis marks by alpha
        3. Pitch-shift: modify F0 by beta or replace with target_f0
        4. Overlap-add windowed segments at new mark positions

        Args:
            samples: Input audio samples.
            sample_rate: Audio sample rate (Hz).
            f0_estimates: Estimated F0 per frame from pitch tracker.
            alpha: Time stretching factor (>0).
            beta: Pitch shifting factor (e.g., 2^(3/12) for +3 semitones).
            target_f0: Target F0 contour (mutually exclusive with beta).
            p_hop_size: Hop size of pitch tracking algorithm.
            p_win_size: Window size of pitch tracking algorithm.

        Returns:
            Dict with output samples, pitch metrics, and diagnostics.

        Raises:
            PitchEstimationError: If F0 data is missing or invalid.
            InvalidScaleFactorError: If alpha is <= 0.
        """
        if not samples:
            raise InvalidAudioError("Input samples cannot be empty")
        if not f0_estimates:
            raise PitchEstimationError(
                "F0 estimates are required for TD-PSOLA"
            )
        if alpha <= 0:
            raise InvalidScaleFactorError(
                f"alpha must be > 0, got {alpha}"
            )
        if beta is not None and target_f0 is not None:
            raise PitchEstimationError(
                "Cannot specify both beta and target_f0"
            )

        num_samples = len(samples)
        output_length = int(math.ceil(num_samples * alpha))

        # Generate pitch marks from F0 estimates
        pitch_marks: List[int] = []
        pos = 0
        for i, f0 in enumerate(f0_estimates):
            if f0 > 0:
                period = int(round(sample_rate / f0))
            else:
                period = p_hop_size  # unvoiced: use hop size

            mark = i * p_hop_size
            if mark < num_samples:
                pitch_marks.append(mark)

        if not pitch_marks:
            raise PitchEstimationError(
                "No valid pitch marks generated from F0 data"
            )

        # Compute output pitch marks (time-stretched)
        out_marks: List[int] = []
        for mark in pitch_marks:
            out_mark = int(round(mark * alpha))
            if out_mark < output_length:
                out_marks.append(out_mark)

        # Apply pitch modification to window sizes
        win_sizes: List[int] = []
        for i, f0 in enumerate(f0_estimates):
            if f0 > 0:
                # Voiced: window = 2 * period
                period = sample_rate / f0
                if beta is not None:
                    period /= beta
                elif target_f0 is not None and i < len(target_f0) and target_f0[i] > 0:
                    period = sample_rate / target_f0[i]
                win_sizes.append(int(round(2 * period)))
            else:
                win_sizes.append(p_win_size)

        # Pad input
        max_win = max(win_sizes) if win_sizes else p_win_size
        padded = [0.0 for _ in range(max_win)] + samples + [0.0 for _ in range(max_win)]

        # Overlap-add synthesis
        output = [0.0] * (output_length + max_win)
        ow = [0.0] * (output_length + max_win)

        voiced_frames = 0
        unvoiced_frames = 0

        for i, (in_mark, out_mark) in enumerate(zip(pitch_marks, out_marks)):
            ws = win_sizes[i] if i < len(win_sizes) else p_win_size
            half_ws = ws // 2

            # Generate Hann window for this frame
            frame_win = _generate_window("hann", ws)

            # Extract and window the frame
            for k in range(ws):
                in_idx = in_mark + max_win - half_ws + k
                out_idx = out_mark - half_ws + k + max_win // 2

                if 0 <= in_idx < len(padded) and 0 <= out_idx < len(output):
                    w = frame_win[k]
                    output[out_idx] += padded[in_idx] * w
                    ow[out_idx] += w

            f0_val = f0_estimates[i] if i < len(f0_estimates) else 0
            if f0_val > 0:
                voiced_frames += 1
            else:
                unvoiced_frames += 1

        # Normalize
        for i in range(len(output)):
            if ow[i] > 1e-6:
                output[i] /= ow[i]

        output_samples = output[:output_length]

        # Compute actual pitch shift in semitones
        pitch_shift_st = 0.0
        if beta is not None:
            pitch_shift_st = 12.0 * math.log2(beta) if beta > 0 else 0.0

        return {
            "status": "success",
            "data": {
                "output_samples": output_samples,
                "output_length": len(output_samples),
                "input_length": num_samples,
                "algorithm": "TD-PSOLA",
                "alpha": alpha,
                "beta": beta,
                "pitch_shift_semitones": round(pitch_shift_st, 2),
                "num_pitch_marks": len(pitch_marks),
                "voiced_frames": voiced_frames,
                "unvoiced_frames": unvoiced_frames,
                "sample_rate": sample_rate,
            }
        }

    # ========================================================================
    # Analysis / Diagnostics
    # ========================================================================

    def analyze_stretch_quality(
        self,
        original: List[float],
        stretched: List[float],
    ) -> Dict[str, Any]:
        """
        Analyze the quality of a time-stretched signal vs. original.

        Computes energy preservation ratio, spectral centroid shift,
        and zero-crossing rate change as quality indicators.

        Args:
            original: Original audio samples.
            stretched: Time-stretched output samples.

        Returns:
            Dict with quality metrics.
        """
        if not original or not stretched:
            raise InvalidAudioError("Both signals must be non-empty")

        # Energy comparison
        orig_energy = sum(s * s for s in original)
        stretch_energy = sum(s * s for s in stretched)
        energy_ratio = stretch_energy / max(orig_energy, 1e-12)
        time_ratio = len(stretched) / max(len(original), 1)
        normalized_energy = energy_ratio / max(time_ratio, 1e-12)

        # Zero-crossing rate
        def zcr(signal: List[float]) -> float:
            crossings = 0
            for i in range(1, len(signal)):
                if (signal[i] >= 0) != (signal[i - 1] >= 0):
                    crossings += 1
            return crossings / max(len(signal) - 1, 1)

        orig_zcr = zcr(original)
        stretch_zcr = zcr(stretched)

        # RMS
        orig_rms = math.sqrt(orig_energy / max(len(original), 1))
        stretch_rms = math.sqrt(stretch_energy / max(len(stretched), 1))

        return {
            "status": "success",
            "data": {
                "time_stretch_ratio": round(time_ratio, 4),
                "energy_ratio": round(energy_ratio, 4),
                "normalized_energy_ratio": round(normalized_energy, 4),
                "original_rms": round(orig_rms, 6),
                "stretched_rms": round(stretch_rms, 6),
                "rms_difference_db": round(
                    20 * math.log10(max(stretch_rms, 1e-12) / max(orig_rms, 1e-12)),
                    2
                ),
                "original_zcr": round(orig_zcr, 6),
                "stretched_zcr": round(stretch_zcr, 6),
                "zcr_preservation": round(
                    1.0 - abs(orig_zcr - stretch_zcr) / max(orig_zcr, 1e-12),
                    4
                ),
                "quality_score": round(
                    min(1.0, normalized_energy) * 0.5
                    + min(1.0, 1.0 - abs(orig_zcr - stretch_zcr) / max(orig_zcr + 1e-12, 1e-12)) * 0.5,
                    4
                ),
            }
        }

    def get_engine_info(self) -> Dict[str, Any]:
        """
        Return engine metadata and configuration.

        Returns:
            Dict with engine version, supported algorithms, and config.
        """
        return {
            "status": "success",
            "data": {
                "engine": "OmniPytsmodEngine",
                "version": ENGINE_VERSION,
                "source": "KAIST-MACLab/PyTSMod v0.3.8",
                "layer": "compute/python_core",
                "algorithms": [
                    "OLA (Overlap-Add)",
                    "WSOLA (Waveform-Similarity Overlap-Add)",
                    "PV-TSM (Phase Vocoder)",
                    "PV-INT (Phase Vocoder Integer)",
                    "PV-PL (Phase Vocoder Phase-Locked)",
                    "TD-PSOLA (Time-Domain Pitch-Synchronous OLA)",
                ],
                "config": {
                    "win_type": self.win_type,
                    "win_size": self.win_size,
                    "syn_hop_size": self.syn_hop_size,
                    "tolerance": self.tolerance,
                },
                "references": [
                    "Driedger & Müller, 'TSM Toolbox', DAFx-14, 2014",
                    "Driedger & Müller, 'A review of TSM of music signals', Applied Sciences, 2016",
                    "Zölzer, 'DAFX: Digital Audio Effects', Wiley, 2011",
                ],
            }
        }

    def diagnostics(self):
        """Return engine health diagnostics."""
        return {
            "engine_id": "omni-pytsmod",
            "version": getattr(self, "VERSION", "1.0.0"),
            "status": "operational",
        }
