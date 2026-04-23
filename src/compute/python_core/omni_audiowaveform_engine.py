"""
+============================================================================+
|  OMNI AUDIOWAVEFORM ENGINE                                                 |
|  Engine Layer: Compute / Audio Visualization                               |
|  Source Study: bbc/audiowaveform                                           |
|  Purpose: PCM peak min/max extractor for efficient waveform rendering.     |
|  License: OMNI-Enterprise                                                  |
+============================================================================+
"""

import struct
import math
import json
from typing import Dict, Any, List, Tuple, Optional

ENGINE_VERSION: str = "1.0.0-omni"
from src.compute.python_core.omni_base_engine import Result, Ok, Err


class OmniAudiowaveformEngine:
    """
    Production-grade PCM waveform data extractor for UI rendering.

    Learned from bbc/audiowaveform:
    - Divides audio into sample windows (e.g., 256 samples per window)
    - Computes min/max amplitude peaks per window
    - Exports as JSON for lightweight waveform visualization
    - Prevents UI from rendering billions of raw PCM points

    This engine computes waveform peaks natively without external libraries.
    """

    def __init__(self, sample_rate: int = 44100, samples_per_pixel: int = 256) -> None:
        """Initialize OmniAudiowaveformEngine."""
        self._sample_rate: int = sample_rate
        self._samples_per_pixel: int = samples_per_pixel

    def compute_peaks(self, samples: List[float]) -> List[Tuple[float, float]]:
        """
        Compute min/max amplitude peaks per window stride.

        Args:
            samples: List of PCM float samples in [-1.0, 1.0].

        Returns:
            List of (min_peak, max_peak) tuples per window.
        """
        peaks: List[Tuple[float, float]] = []
        n: int = len(samples)
        stride: int = self._samples_per_pixel

        for start in range(0, n, stride):
            window: List[float] = samples[start:start + stride]
            if not window:
                break
            min_val: float = min(window)
            max_val: float = max(window)
            peaks.append((round(min_val, 6), round(max_val, 6)))

        return peaks

    def peaks_to_json(self, peaks: List[Tuple[float, float]], bits: int = 8) -> Dict[str, Any]:
        """
        Convert peaks to audiowaveform-compatible JSON format.

        Args:
            peaks: List of (min, max) peak tuples.
            bits: Bit depth for integer quantization (8 or 16).

        Returns:
            JSON-serializable dict in audiowaveform format.
        """
        scale: int = (2 ** (bits - 1)) - 1
        data: List[int] = []

        for min_val, max_val in peaks:
            data.append(int(min_val * scale))
            data.append(int(max_val * scale))

        return {
            "version": 2,
            "channels": 1,
            "sample_rate": self._sample_rate,
            "samples_per_pixel": self._samples_per_pixel,
            "bits": bits,
            "length": len(peaks),
            "data": data,
        }

    def read_wav_pcm(self, filepath: str) -> Tuple[List[float], int]:
        """
        Read raw PCM samples from a WAV file header.

        Args:
            filepath: Path to the WAV file.

        Returns:
            Tuple of (samples list, sample_rate).
        """
        with open(filepath, "rb") as f:
            riff: bytes = f.read(4)
            if riff != b"RIFF":
                return [], 0
            f.read(4)  # file size
            wave: bytes = f.read(4)
            if wave != b"WAVE":
                return [], 0

            # Find fmt chunk
            sample_rate: int = 44100
            bits_per_sample: int = 16
            num_channels: int = 1

            while True:
                chunk_id: bytes = f.read(4)
                if len(chunk_id) < 4:
                    break
                chunk_size: int = struct.unpack("<I", f.read(4))[0]

                if chunk_id == b"fmt ":
                    fmt_data: bytes = f.read(chunk_size)
                    audio_format = struct.unpack("<H", fmt_data[0:2])[0]
                    num_channels = struct.unpack("<H", fmt_data[2:4])[0]
                    sample_rate = struct.unpack("<I", fmt_data[4:8])[0]
                    bits_per_sample = struct.unpack("<H", fmt_data[14:16])[0]

                elif chunk_id == b"data":
                    raw_data: bytes = f.read(chunk_size)
                    bytes_per_sample: int = bits_per_sample // 8
                    fmt_char: str = "<h" if bits_per_sample == 16 else "<b"
                    max_val: float = float(2 ** (bits_per_sample - 1))

                    samples: List[float] = []
                    for i in range(0, len(raw_data) - bytes_per_sample + 1, bytes_per_sample * num_channels):
                        value: int = struct.unpack(fmt_char, raw_data[i:i + bytes_per_sample])[0]
                        samples.append(value / max_val)

                    self._sample_rate = sample_rate
                    return samples, sample_rate
                else:
                    f.read(chunk_size)

        return [], 0

    def generate_waveform_data(self, filepath: str) -> Dict[str, Any]:
        """
        Full pipeline: read WAV -> compute peaks -> export JSON.

        Args:
            filepath: Path to WAV file.

        Returns:
            Audiowaveform-compatible JSON data.
        """
        samples, sr = self.read_wav_pcm(filepath)
        peaks = self.compute_peaks(samples)
        return self.peaks_to_json(peaks)

    def evaluate_health(self) -> Dict[str, Any]:
        """Return engine health and status information."""
        return {
            "engine": "OmniAudiowaveformEngine",
            "version": ENGINE_VERSION,
            "status": "operational",
            "sample_rate": self._sample_rate,
            "samples_per_pixel": self._samples_per_pixel,
            "capabilities": ["peak_extraction", "wav_parsing", "json_export", "waveform_render"],
        }

    def diagnostics(self):
        """Return engine health diagnostics."""
        return {
            "engine_id": "omni-audiowaveform",
            "version": getattr(self, "VERSION", "1.0.0"),
            "status": "operational",
        }
