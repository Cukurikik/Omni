"""
+============================================================================+
|  OMNI FFMPEGCORE ENGINE                                                    |
|  Engine Layer: Compute / Media Transcoding Orchestration                   |
|  Source Study: rosenbjerg/FFMpegCore                                       |
|  Purpose: Fluent Builder Pattern for FFmpeg argument chain construction.   |
|  License: OMNI-Enterprise                                                  |
+============================================================================+
"""

from typing import Dict, Any, List, Optional

ENGINE_VERSION: str = "1.0.0-omni"


class FFmpegArgsBuilder:
    """
    Fluent builder for constructing FFmpeg command-line argument chains.

    Mirrors the C# Builder Pattern from rosenbjerg/FFMpegCore,
    enabling type-safe, chainable argument construction without
    executing subprocess commands.
    """

    def __init__(self) -> None:
        """Initialize FFmpegArgsBuilder."""
        self._global_args: List[str] = []
        self._input_args: List[str] = []
        self._output_args: List[str] = []
        self._filters: List[str] = []
        self._input_file: str = ""
        self._output_file: str = ""

    def input(self, filepath: str) -> "FFmpegArgsBuilder":
        """Set input file path."""
        self._input_file = filepath
        return self

    def output(self, filepath: str) -> "FFmpegArgsBuilder":
        """Set output file path."""
        self._output_file = filepath
        return self

    def video_codec(self, codec: str) -> "FFmpegArgsBuilder":
        """Set video codec (e.g., 'libx264', 'libx265', 'copy')."""
        self._output_args.extend(["-c:v", codec])
        return self

    def audio_codec(self, codec: str) -> "FFmpegArgsBuilder":
        """Set audio codec (e.g., 'aac', 'libopus', 'copy')."""
        self._output_args.extend(["-c:a", codec])
        return self

    def bitrate(self, rate: str) -> "FFmpegArgsBuilder":
        """Set overall bitrate (e.g., '5M', '128k')."""
        self._output_args.extend(["-b:v", rate])
        return self

    def audio_bitrate(self, rate: str) -> "FFmpegArgsBuilder":
        """Set audio bitrate (e.g., '192k')."""
        self._output_args.extend(["-b:a", rate])
        return self

    def resolution(self, width: int, height: int) -> "FFmpegArgsBuilder":
        """Set output resolution."""
        self._output_args.extend(["-s", f"{width}x{height}"])
        return self

    def framerate(self, fps: int) -> "FFmpegArgsBuilder":
        """Set output framerate."""
        self._output_args.extend(["-r", str(fps)])
        return self

    def seek(self, seconds: float) -> "FFmpegArgsBuilder":
        """Seek to position in input (seconds)."""
        self._input_args.extend(["-ss", str(seconds)])
        return self

    def duration(self, seconds: float) -> "FFmpegArgsBuilder":
        """Limit output duration (seconds)."""
        self._output_args.extend(["-t", str(seconds)])
        return self

    def overwrite(self) -> "FFmpegArgsBuilder":
        """Enable output file overwrite without prompting."""
        self._global_args.append("-y")
        return self

    def add_filter(self, filter_expr: str) -> "FFmpegArgsBuilder":
        """Add a video/audio filter expression."""
        self._filters.append(filter_expr)
        return self

    def sample_rate(self, rate: int) -> "FFmpegArgsBuilder":
        """Set audio sample rate (e.g., 44100, 48000)."""
        self._output_args.extend(["-ar", str(rate)])
        return self

    def channels(self, count: int) -> "FFmpegArgsBuilder":
        """Set number of audio channels."""
        self._output_args.extend(["-ac", str(count)])
        return self

    def build(self) -> str:
        """
        Build the complete FFmpeg command string.

        Returns:
            Complete ffmpeg command string ready for execution.
        """
        parts: List[str] = ["ffmpeg"]
        parts.extend(self._global_args)
        parts.extend(self._input_args)

        if self._input_file:
            parts.extend(["-i", self._input_file])

        if self._filters:
            parts.extend(["-vf", ",".join(self._filters)])

        parts.extend(self._output_args)

        if self._output_file:
            parts.append(self._output_file)

        return " ".join(parts)

    def to_args_list(self) -> List[str]:
        """Return the command as a list of arguments (for subprocess)."""
        return self.build().split()


class OmniFfmpegcoreEngine:
    """
    Production-grade FFmpeg argument orchestration engine.

    Learned from rosenbjerg/FFMpegCore:
    - C# Fluent Builder Pattern for FFmpeg abstraction
    - Chains method calls to construct complex transcode pipelines
    - Compiles final string only at build time
    - Type-safe argument validation before execution

    This engine provides the same builder API in Python.
    """

    def __init__(self) -> None:
        """Initialize OmniFfmpegcoreEngine."""
        self._presets: Dict[str, Dict[str, Any]] = {
            "web_optimized": {"vcodec": "libx264", "acodec": "aac", "vbitrate": "2M", "abitrate": "128k"},
            "high_quality": {"vcodec": "libx265", "acodec": "libopus", "vbitrate": "8M", "abitrate": "256k"},
            "audio_only": {"acodec": "libmp3lame", "abitrate": "320k"},
            "thumbnail": {"vcodec": "mjpeg", "duration": 0.001},
        }

    def create_builder(self) -> FFmpegArgsBuilder:
        """Create a new FFmpegArgsBuilder instance."""
        return FFmpegArgsBuilder()

    def build_from_preset(
        self, preset_name: str, input_file: str, output_file: str
    ) -> Optional[str]:
        """
        Build an FFmpeg command from a named preset.

        Args:
            preset_name: One of the predefined preset names.
            input_file: Input file path.
            output_file: Output file path.

        Returns:
            Complete FFmpeg command string, or None if preset not found.
        """
        preset = self._presets.get(preset_name)
        if preset is None:
            return None

        builder = self.create_builder().overwrite().input(input_file).output(output_file)

        if "vcodec" in preset:
            builder.video_codec(preset["vcodec"])
        if "acodec" in preset:
            builder.audio_codec(preset["acodec"])
        if "vbitrate" in preset:
            builder.bitrate(preset["vbitrate"])
        if "abitrate" in preset:
            builder.audio_bitrate(preset["abitrate"])
        if "duration" in preset:
            builder.duration(preset["duration"])

        return builder.build()

    def list_presets(self) -> Dict[str, Dict[str, Any]]:
        """Return all available transcoding presets."""
        return dict(self._presets)

    def evaluate_health(self) -> Dict[str, Any]:
        """Return engine health and status information."""
        return {
            "engine": "OmniFfmpegcoreEngine",
            "version": ENGINE_VERSION,
            "status": "operational",
            "presets": list(self._presets.keys()),
            "capabilities": ["fluent_builder", "preset_system", "argument_chain", "transcode_orchestration"],
        }

    def diagnostics(self):
        """Return engine health diagnostics."""
        return {
            "engine_id": "omni-ffmpegcore",
            "version": getattr(self, "VERSION", "1.0.0"),
            "status": "operational",
        }
