ENGINE_VERSION = "1.0.0-omni"
# ===========================================================================
# OMNI FFMPEG BUILDER ENGINE — FFmpeg Command Builder & Video Processing
# ===========================================================================
# Source Paradigm: https://github.com/rendi-api/ffmpeg-cheatsheet
# Domain Layer  : Compute (FFmpeg Command Construction)
# Zero-Mock     : 100% Native — subprocess, json, os, re
# ===========================================================================
"""
ffmpeg-cheatsheet teaches us:
  1. Comprehensive FFmpeg command patterns for every use case
  2. Video/audio format conversion
  3. Encoding presets (H.264, H.265, VP9, AV1)
  4. Filter chains (scale, crop, overlay, fade)
  5. Audio extraction and manipulation
  6. Streaming and chunking (HLS, DASH)

This engine distills those paradigms into OMNI-native Python for
programmatic FFmpeg command building and execution.
"""

import json
import os
import re
import subprocess
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional


# ── Data Models ──────────────────────────────────────────────────────────────

class VideoCodec(Enum):
    H264 = "libx264"
    H265 = "libx265"
    VP9 = "libvpx-vp9"
    AV1 = "libaom-av1"
    COPY = "copy"


class AudioCodec(Enum):
    AAC = "aac"
    MP3 = "libmp3lame"
    OPUS = "libopus"
    FLAC = "flac"
    COPY = "copy"


class Preset(Enum):
    ULTRAFAST = "ultrafast"
    FAST = "fast"
    MEDIUM = "medium"
    SLOW = "slow"
    VERYSLOW = "veryslow"


# ── FFmpeg Command Builder ────────────────────────────────────────────────

class FFmpegCommandBuilder:
    """Build FFmpeg commands programmatically."""

    def __init__(self):
        self._input: str = ""
        self._output: str = ""
        self._vcodec: str = ""
        self._acodec: str = ""
        self._preset: str = ""
        self._crf: str = ""
        self._resolution: str = ""
        self._fps: str = ""
        self._bitrate_v: str = ""
        self._bitrate_a: str = ""
        self._filters: List[str] = []
        self._extra: List[str] = []
        self._overwrite: bool = True

    def input(self, path: str) -> "FFmpegCommandBuilder":
        self._input = path
        return self

    def output(self, path: str) -> "FFmpegCommandBuilder":
        self._output = path
        return self

    def video_codec(self, codec: VideoCodec) -> "FFmpegCommandBuilder":
        self._vcodec = codec.value
        return self

    def audio_codec(self, codec: AudioCodec) -> "FFmpegCommandBuilder":
        self._acodec = codec.value
        return self

    def preset(self, p: Preset) -> "FFmpegCommandBuilder":
        self._preset = p.value
        return self

    def crf(self, val: int) -> "FFmpegCommandBuilder":
        self._crf = str(val)
        return self

    def resolution(self, w: int, h: int) -> "FFmpegCommandBuilder":
        self._resolution = f"{w}:{h}"
        return self

    def fps(self, val: int) -> "FFmpegCommandBuilder":
        self._fps = str(val)
        return self

    def add_filter(self, f: str) -> "FFmpegCommandBuilder":
        self._filters.append(f)
        return self

    def trim(self, start: str, duration: str = "") -> "FFmpegCommandBuilder":
        self._extra.extend(["-ss", start])
        if duration:
            self._extra.extend(["-t", duration])
        return self

    def build(self) -> List[str]:
        cmd = ["ffmpeg"]
        if self._overwrite:
            cmd.append("-y")
        if self._input:
            cmd.extend(["-i", self._input])
        if self._vcodec:
            cmd.extend(["-c:v", self._vcodec])
        if self._acodec:
            cmd.extend(["-c:a", self._acodec])
        if self._preset:
            cmd.extend(["-preset", self._preset])
        if self._crf:
            cmd.extend(["-crf", self._crf])
        if self._resolution:
            self._filters.append(f"scale={self._resolution}")
        if self._fps:
            cmd.extend(["-r", self._fps])
        if self._filters:
            cmd.extend(["-vf", ",".join(self._filters)])
        if self._bitrate_v:
            cmd.extend(["-b:v", self._bitrate_v])
        if self._bitrate_a:
            cmd.extend(["-b:a", self._bitrate_a])
        cmd.extend(self._extra)
        if self._output:
            cmd.append(self._output)
        return cmd

    def build_string(self) -> str:
        return " ".join(self.build())


# ── Preset Templates ──────────────────────────────────────────────────────

class FFmpegTemplates:
    """Pre-built FFmpeg command templates for common tasks."""

    @staticmethod
    def compress_video(input_p: str, output_p: str, crf: int = 23) -> List[str]:
        return (FFmpegCommandBuilder().input(input_p).output(output_p)
                .video_codec(VideoCodec.H264).audio_codec(AudioCodec.AAC)
                .preset(Preset.MEDIUM).crf(crf).build())

    @staticmethod
    def to_shorts(input_p: str, output_p: str) -> List[str]:
        return (FFmpegCommandBuilder().input(input_p).output(output_p)
                .video_codec(VideoCodec.H264).audio_codec(AudioCodec.AAC)
                .crf(23).preset(Preset.FAST)
                .add_filter("scale=1080:1920:force_original_aspect_ratio=decrease")
                .add_filter("pad=1080:1920:(ow-iw)/2:(oh-ih)/2")
                .build())

    @staticmethod
    def extract_audio(input_p: str, output_p: str) -> List[str]:
        return ["ffmpeg", "-y", "-i", input_p, "-vn", "-c:a", "libmp3lame",
                "-b:a", "192k", output_p]

    @staticmethod
    def create_gif(input_p: str, output_p: str, fps: int = 10, width: int = 480) -> List[str]:
        return (FFmpegCommandBuilder().input(input_p).output(output_p)
                .add_filter(f"fps={fps},scale={width}:-1:flags=lanczos")
                .build())

    @staticmethod
    def generate_thumbnail(input_p: str, output_p: str, at_sec: float = 1) -> List[str]:
        return ["ffmpeg", "-y", "-i", input_p, "-ss", str(at_sec),
                "-vframes", "1", output_p]

    @staticmethod
    def concat_videos(file_list: str, output_p: str) -> List[str]:
        return ["ffmpeg", "-y", "-f", "concat", "-safe", "0",
                "-i", file_list, "-c", "copy", output_p]

    @staticmethod
    def to_hls(input_p: str, output_dir: str) -> List[str]:
        playlist = os.path.join(output_dir, "playlist.m3u8")
        segment = os.path.join(output_dir, "segment_%03d.ts")
        return ["ffmpeg", "-y", "-i", input_p, "-c:v", "libx264",
                "-c:a", "aac", "-hls_time", "10", "-hls_list_size", "0",
                "-hls_segment_filename", segment, playlist]


# ── FFmpeg Executor ───────────────────────────────────────────────────────

class FFmpegExecutor:
    """Execute FFmpeg commands and return results."""

    @staticmethod
    def check_ffmpeg() -> Dict:
        tools = {}
        for tool in ["ffmpeg", "ffprobe"]:
            try:
                r = subprocess.run([tool, "-version"], capture_output=True, text=True, timeout=5)
                version = r.stdout.split("\n")[0] if r.returncode == 0 else ""
                tools[tool] = {"installed": r.returncode == 0, "version": version}
            except FileNotFoundError:
                tools[tool] = {"installed": False}
        return tools

    @staticmethod
    def run(cmd: List[str], timeout: int = 300) -> Dict:
        start = time.perf_counter()
        try:
            r = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
            return {
                "exit_code": r.returncode,
                "duration_sec": round(time.perf_counter() - start, 2),
                "output": r.stderr[-1024:] if r.stderr else r.stdout[-1024:],
                "success": r.returncode == 0,
            }
        except Exception as e:
            return {"exit_code": -1, "error": str(e)[:256], "success": False}


# ── The Main Engine ─────────────────────────────────────────────────────────

class OmniFFmpegBuilderEngine:
    """
    OMNI FFmpeg Builder Engine — Zero-Mock Video Processing Command Builder.

    Capabilities (all native subprocess):
      - Fluent FFmpeg command builder API
      - Pre-built templates (compress, shorts, audio, gif, hls)
      - Command execution with timing
      - Available tools detection
    """

    def __init__(self):
        self.builder = FFmpegCommandBuilder
        self.templates = FFmpegTemplates()
        self.executor = FFmpegExecutor()

    def get_template(self, template: str, input_p: str, output_p: str) -> Dict:
        templates = {
            "compress": self.templates.compress_video,
            "shorts": self.templates.to_shorts,
            "extract_audio": self.templates.extract_audio,
            "gif": self.templates.create_gif,
            "thumbnail": self.templates.generate_thumbnail,
        }
        fn = templates.get(template)
        if not fn:
            return {"error": f"Unknown: {template}", "available": list(templates.keys())}
        cmd = fn(input_p, output_p)
        return {"template": template, "command": " ".join(cmd)}

    def diagnostics(self) -> Dict:
        tools = self.executor.check_ffmpeg()
        return {
            "engine": "OmniFFmpegBuilderEngine",
            "status": "active",
            "tools": tools,
            "templates": ["compress", "shorts", "extract_audio", "gif",
                           "thumbnail", "concat", "hls"],
            "codecs": {"video": [c.value for c in VideoCodec],
                       "audio": [c.value for c in AudioCodec]},
            "capabilities": ["cmd_builder", "templates", "execution",
                             "codec_select", "filter_chain", "hls_stream"],
        }


if __name__ == "__main__":
    engine = OmniFFmpegBuilderEngine()
    print(json.dumps(engine.diagnostics(), indent=2))
