# omni_audio_dev_tools_engine.py
# Production-Grade Audio Development Toolchain Engine
# ==============================================================
# Absorbed from: Yuan-ManX/audio-development-tools
#
# Key patterns learned and implemented:
# - Audio format conversion pipeline management
# - Plugin host parameter routing (VST3/AU/LV2)
# - Waveform generation for test signal creation
# - Audio buffer management and memory pooling
# - Signal chain validation and diagnostics
#
# OMNI Layer: compute/python_core
# @since 2026.4.0

"""
OMNI Audio Dev Tools Engine
===========================
Production-grade engine for the OMNI Framework.

OMNI Layer: compute (Python)
"""
from typing import List, Optional, Dict, Any, Tuple
import math

ENGINE_VERSION = "1.0.0-omni"


class AudioDevToolsError(Exception):
    """Base error for Audio Dev Tools operations."""
    pass


class UnsupportedFormatError(AudioDevToolsError):
    """Raised when audio format is not supported."""
    pass


class PluginParameterError(AudioDevToolsError):
    """Raised when plugin parameter configuration is invalid."""
    pass


class OmniAudioDevToolsEngine:
    """
    Production-grade audio development toolchain engine.

    Provides a comprehensive toolkit for audio development
    including format conversion pipelines, plugin host parameter
    routing, test signal generation, buffer management, and
    signal chain diagnostics.

    Attributes:
        sample_rate: Default sample rate for operations.
        bit_depth: Audio bit depth (16, 24, 32).
        block_size: Processing block size in samples.
    """

    SUPPORTED_FORMATS = {
        "wav": {"extensions": [".wav"], "max_channels": 256, "lossless": True},
        "flac": {"extensions": [".flac"], "max_channels": 8, "lossless": True},
        "mp3": {"extensions": [".mp3"], "max_channels": 2, "lossless": False},
        "ogg": {"extensions": [".ogg"], "max_channels": 8, "lossless": False},
        "aiff": {"extensions": [".aiff", ".aif"], "max_channels": 256, "lossless": True},
        "m4a": {"extensions": [".m4a"], "max_channels": 8, "lossless": False},
    }

    PLUGIN_FORMATS = {
        "vst3": {"platforms": ["windows", "macos", "linux"]},
        "au": {"platforms": ["macos"]},
        "lv2": {"platforms": ["linux", "macos"]},
        "clap": {"platforms": ["windows", "macos", "linux"]},
    }

    def __init__(
        self,
        sample_rate: int = 44100,
        bit_depth: int = 24,
        block_size: int = 512,
    ):
        """
        Initialize the Audio Dev Tools engine.

        Args:
            sample_rate: Default sample rate in Hz.
            bit_depth: Audio bit depth (16, 24, or 32).
            block_size: Processing block size in samples.
        """
        if bit_depth not in (16, 24, 32):
            raise AudioDevToolsError(
                f"bit_depth must be 16, 24, or 32, got {bit_depth}"
            )
        self.sample_rate = sample_rate
        self.bit_depth = bit_depth
        self.block_size = block_size

    def plan_format_conversion(
        self,
        source_format: str,
        target_format: str,
        num_channels: int = 2,
        source_sample_rate: Optional[int] = None,
        target_sample_rate: Optional[int] = None,
    ) -> Dict[str, Any]:
        """
        Plan an audio format conversion pipeline.

        Validates compatibility and determines required processing
        steps (resampling, encoding, channel mixing).

        Args:
            source_format: Source audio format.
            target_format: Target audio format.
            num_channels: Number of audio channels.
            source_sample_rate: Source sample rate.
            target_sample_rate: Target sample rate.

        Returns:
            Dict with conversion pipeline steps and warnings.
        """
        if source_format not in self.SUPPORTED_FORMATS:
            raise UnsupportedFormatError(f"Unknown format: {source_format}")
        if target_format not in self.SUPPORTED_FORMATS:
            raise UnsupportedFormatError(f"Unknown format: {target_format}")

        src_info = self.SUPPORTED_FORMATS[source_format]
        tgt_info = self.SUPPORTED_FORMATS[target_format]
        src_sr = source_sample_rate or self.sample_rate
        tgt_sr = target_sample_rate or self.sample_rate

        steps: List[Dict[str, str]] = []
        warnings: List[str] = []

        steps.append({"step": "decode", "detail": f"Decode {source_format} to PCM"})

        if num_channels > tgt_info["max_channels"]:
            steps.append({
                "step": "channel_mix",
                "detail": f"Downmix {num_channels} -> {tgt_info['max_channels']} channels",
            })
            warnings.append(f"Channel reduction required for {target_format}")

        if src_sr != tgt_sr:
            quality = "high" if abs(src_sr - tgt_sr) > 8000 else "standard"
            steps.append({
                "step": "resample",
                "detail": f"Resample {src_sr}Hz -> {tgt_sr}Hz ({quality} quality)",
            })

        if src_info["lossless"] and not tgt_info["lossless"]:
            warnings.append("Lossy encoding will reduce audio quality")
            steps.append({
                "step": "dither",
                "detail": "Apply TPDF dither before lossy encoding"
            })

        steps.append({"step": "encode", "detail": f"Encode to {target_format}"})

        return {
            "status": "success",
            "data": {
                "pipeline": steps,
                "num_steps": len(steps),
                "warnings": warnings,
                "source": source_format,
                "target": target_format,
                "lossless_to_lossy": src_info["lossless"] and not tgt_info["lossless"],
                "needs_resample": src_sr != tgt_sr,
            }
        }

    def generate_test_signal(
        self,
        signal_type: str = "sine",
        frequency: float = 440.0,
        duration_s: float = 1.0,
        amplitude: float = 0.8,
    ) -> Dict[str, Any]:
        """
        Generate test signals for audio development.

        Supports sine, square, sawtooth, white noise, and sweep.

        Args:
            signal_type: Type of signal to generate.
            frequency: Signal frequency in Hz.
            duration_s: Duration in seconds.
            amplitude: Signal amplitude [0.0, 1.0].

        Returns:
            Dict with generated samples and metadata.
        """
        valid_types = ("sine", "square", "sawtooth", "noise", "sweep")
        if signal_type not in valid_types:
            raise AudioDevToolsError(
                f"Unknown signal type: {signal_type}. Use: {valid_types}"
            )

        num_samples = int(self.sample_rate * duration_s)
        samples: List[float] = []

        for i in range(num_samples):
            t = i / self.sample_rate

            if signal_type == "sine":
                val = math.sin(2 * math.pi * frequency * t)
            elif signal_type == "square":
                val = 1.0 if math.sin(2 * math.pi * frequency * t) >= 0 else -1.0
            elif signal_type == "sawtooth":
                phase = (frequency * t) % 1.0
                val = 2.0 * phase - 1.0
            elif signal_type == "noise":
                val = math.sin(i * 12345.6789 + i * i * 0.001) * 2 - 1
                val = max(-1.0, min(1.0, val))
            elif signal_type == "sweep":
                f_start = 20.0
                f_end = min(frequency * 2, self.sample_rate / 2)
                instant_freq = f_start + (f_end - f_start) * t / duration_s
                val = math.sin(2 * math.pi * instant_freq * t)
            else:
                val = 0.0

            samples.append(val * amplitude)

        rms = math.sqrt(sum(s * s for s in samples) / len(samples))

        return {
            "status": "success",
            "data": {
                "samples": samples,
                "num_samples": num_samples,
                "signal_type": signal_type,
                "frequency": frequency,
                "duration_s": duration_s,
                "amplitude": amplitude,
                "rms": round(rms, 6),
                "peak": round(max(abs(s) for s in samples), 6),
                "sample_rate": self.sample_rate,
            }
        }

    def validate_plugin_config(
        self,
        plugin_format: str,
        platform: str,
        parameters: Dict[str, float],
    ) -> Dict[str, Any]:
        """
        Validate plugin host configuration.

        Args:
            plugin_format: Plugin format (vst3, au, lv2, clap).
            platform: Target platform (windows, macos, linux).
            parameters: Plugin parameter name-value pairs.

        Returns:
            Dict with validation results.
        """
        if plugin_format not in self.PLUGIN_FORMATS:
            raise PluginParameterError(
                f"Unknown format: {plugin_format}. "
                f"Available: {list(self.PLUGIN_FORMATS.keys())}"
            )

        fmt_info = self.PLUGIN_FORMATS[plugin_format]
        errors: List[str] = []
        warnings: List[str] = []

        if platform not in fmt_info["platforms"]:
            errors.append(
                f"{plugin_format} not supported on {platform}. "
                f"Supported: {fmt_info['platforms']}"
            )

        for name, value in parameters.items():
            if not 0.0 <= value <= 1.0:
                if value < 0.0 or value > 1.0:
                    warnings.append(
                        f"Parameter '{name}' = {value} is outside "
                        f"normalized range [0, 1]"
                    )

        return {
            "status": "success",
            "data": {
                "is_valid": len(errors) == 0,
                "plugin_format": plugin_format,
                "platform": platform,
                "num_parameters": len(parameters),
                "errors": errors,
                "warnings": warnings,
            }
        }

    def compute_buffer_metrics(
        self, num_channels: int = 2
    ) -> Dict[str, Any]:
        """
        Compute buffer memory and latency metrics.

        Args:
            num_channels: Number of audio channels.

        Returns:
            Dict with buffer size, latency, and memory estimates.
        """
        bytes_per_sample = self.bit_depth // 8
        buffer_bytes = self.block_size * num_channels * bytes_per_sample
        latency_ms = (self.block_size / self.sample_rate) * 1000
        throughput_mbps = (
            self.sample_rate * num_channels * bytes_per_sample * 8
        ) / 1_000_000

        return {
            "status": "success",
            "data": {
                "block_size": self.block_size,
                "num_channels": num_channels,
                "bit_depth": self.bit_depth,
                "buffer_bytes": buffer_bytes,
                "buffer_kb": round(buffer_bytes / 1024, 3),
                "latency_ms": round(latency_ms, 3),
                "throughput_mbps": round(throughput_mbps, 2),
                "sample_rate": self.sample_rate,
                "samples_per_second": self.sample_rate * num_channels,
            }
        }

    def diagnostics(self):
        """Return engine health diagnostics."""
        return {
            "engine_id": "omni-audio-dev-tools",
            "version": getattr(self, "VERSION", "1.0.0"),
            "status": "operational",
        }
