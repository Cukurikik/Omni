ENGINE_VERSION = "1.0.0-omni"
# ===========================================================================
# OMNI YOUTUBE SHORTS PIPELINE ENGINE — Video Content Pipeline
# ===========================================================================
# Source Paradigm: https://github.com/rushindrasinha/youtube-shorts-pipeline
# Domain Layer  : Compute (Video Content Pipeline)
# Zero-Prod     : 100% Native — subprocess, json, os, re, hashlib
# ===========================================================================
"""
youtube-shorts-pipeline teaches us:
  1. Content ideation → scripting → recording → editing → publishing
  2. Video metadata optimization (title, description, tags)
  3. Thumbnail generation pipeline
  4. Video format conversion (aspect ratio, resolution)
  5. Batch processing for content factories
  6. Analytics tracking per video

This engine distills those paradigms into OMNI-native Python for
video processing pipeline (ffmpeg), metadata management, and publishing.
"""

import hashlib
import json
import os
import re
import sqlite3
import subprocess
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional


# ── Data Models ──────────────────────────────────────────────────────────────

class VideoFormat(Enum):
    LANDSCAPE = "16:9"     # 1920x1080
    PORTRAIT = "9:16"      # 1080x1920 (Shorts/Reels/TikTok)
    SQUARE = "1:1"         # 1080x1080 (Instagram)

class PipelineStage(Enum):
    IDEATION = "ideation"
    SCRIPTED = "scripted"
    RECORDED = "recorded"
    EDITED = "edited"
    RENDERED = "rendered"
    PUBLISHED = "published"


@dataclass
class VideoProject:
    project_id: str
    title: str
    description: str = ""
    tags: List[str] = field(default_factory=list)
    stage: PipelineStage = PipelineStage.IDEATION
    source_path: str = ""
    output_path: str = ""
    format: VideoFormat = VideoFormat.PORTRAIT
    duration_sec: float = 0
    resolution: str = ""
    file_size_mb: float = 0
    created_at: float = 0


# ── Video Inspector ────────────────────────────────────────────────────────

class VideoInspector:
    """Inspect video files using ffprobe."""

    @staticmethod
    def check_ffmpeg() -> Dict:
        tools = {}
        for tool in ["ffmpeg", "ffprobe"]:
            try:
                r = subprocess.run([tool, "-version"], capture_output=True, text=True, timeout=5)
                tools[tool] = r.returncode == 0
            except FileNotFoundError:
                tools[tool] = False
        return tools

    @staticmethod
    def inspect(path: str) -> Dict:
        if not os.path.isfile(path):
            return {"error": "File not found"}
        try:
            r = subprocess.run(
                ["ffprobe", "-v", "quiet", "-print_format", "json",
                 "-show_format", "-show_streams", path],
                capture_output=True, text=True, timeout=15,
            )
            if r.returncode != 0:
                return {"error": "ffprobe failed"}

            data = json.loads(r.stdout)
            fmt = data.get("format", {})
            result = {
                "duration_sec": round(float(fmt.get("duration", 0)), 2),
                "size_mb": round(int(fmt.get("size", 0)) / (1024 * 1024), 2),
                "bitrate_kbps": int(int(fmt.get("bit_rate", 0)) / 1000),
                "format": fmt.get("format_name", ""),
            }
            for stream in data.get("streams", []):
                if stream.get("codec_type") == "video":
                    result["video_codec"] = stream.get("codec_name", "")
                    result["width"] = stream.get("width", 0)
                    result["height"] = stream.get("height", 0)
                    result["fps"] = eval(stream.get("r_frame_rate", "0/1")) if "/" in stream.get("r_frame_rate", "") else 0
                elif stream.get("codec_type") == "audio":
                    result["audio_codec"] = stream.get("codec_name", "")
                    result["sample_rate"] = int(stream.get("sample_rate", 0))
            return result
        except Exception as e:
            return {"error": str(e)[:256]}


# ── Video Converter ────────────────────────────────────────────────────────

class VideoConverter:
    """Convert video formats for different platforms."""

    PRESETS = {
        VideoFormat.PORTRAIT: {"w": 1080, "h": 1920, "label": "9:16 (Shorts)"},
        VideoFormat.LANDSCAPE: {"w": 1920, "h": 1080, "label": "16:9 (YouTube)"},
        VideoFormat.SQUARE: {"w": 1080, "h": 1080, "label": "1:1 (Instagram)"},
    }

    @staticmethod
    def convert(input_path: str, output_path: str, target: VideoFormat,
                quality: str = "medium") -> Dict:
        """Convert video to target format."""
        preset = VideoConverter.PRESETS[target]
        crf = {"high": "18", "medium": "23", "low": "28"}.get(quality, "23")

        os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
        cmd = [
            "ffmpeg", "-i", input_path, "-y",
            "-vf", f"scale={preset['w']}:{preset['h']}:force_original_aspect_ratio=decrease,"
                   f"pad={preset['w']}:{preset['h']}:(ow-iw)/2:(oh-ih)/2",
            "-c:v", "libx264", "-crf", crf, "-preset", "fast",
            "-c:a", "aac", "-b:a", "128k",
            output_path,
        ]
        try:
            r = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
            if r.returncode == 0 and os.path.isfile(output_path):
                size = round(os.path.getsize(output_path) / (1024 * 1024), 2)
                return {"status": "success", "output": output_path, "size_mb": size,
                        "format": preset["label"]}
            return {"status": "error", "stderr": r.stderr[-512:]}
        except FileNotFoundError:
            return {"status": "error", "error": "ffmpeg not found"}
        except Exception as e:
            return {"status": "error", "error": str(e)[:256]}

    @staticmethod
    def extract_thumbnail(video_path: str, output_path: str, at_sec: float = 1) -> Dict:
        """Extract a thumbnail from a video."""
        os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
        try:
            r = subprocess.run(
                ["ffmpeg", "-i", video_path, "-ss", str(at_sec),
                 "-vframes", "1", "-y", output_path],
                capture_output=True, text=True, timeout=15,
            )
            if os.path.isfile(output_path):
                return {"saved": output_path, "at_sec": at_sec}
            return {"error": r.stderr[-256:]}
        except Exception as e:
            return {"error": str(e)[:256]}


# ── Metadata Optimizer ────────────────────────────────────────────────────

class MetadataOptimizer:
    """Optimize video metadata for discoverability."""

    @staticmethod
    def optimize_title(title: str, max_len: int = 100) -> str:
        title = title.strip()
        if len(title) > max_len:
            title = title[:max_len - 3] + "..."
        return title

    @staticmethod
    def generate_tags(title: str, description: str) -> List[str]:
        text = f"{title} {description}".lower()
        words = re.findall(r'\b[a-z]{3,15}\b', text)
        word_freq = {}
        stop_words = {"the", "and", "for", "with", "this", "that", "from", "are", "was", "will", "has"}
        for w in words:
            if w not in stop_words:
                word_freq[w] = word_freq.get(w, 0) + 1
        sorted_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
        return [w for w, _ in sorted_words[:15]]

    @staticmethod
    def generate_description(title: str, tags: List[str], max_len: int = 5000) -> str:
        lines = [title, "", "📌 Key Topics:"]
        for tag in tags[:10]:
            lines.append(f"• {tag.capitalize()}")
        lines.extend(["", f"🏷️ Tags: {', '.join(f'#{t}' for t in tags[:10])}"])
        return "\n".join(lines)[:max_len]


# ── Project Store (SQLite) ────────────────────────────────────────────────

class ProjectStore:
    def __init__(self, db_path: str = ""):
        if not db_path:
            try:
                db_path = os.path.join(os.path.dirname(__file__), "..", ".shorts_pipeline.db")
            except NameError:
                db_path = os.path.join(os.getcwd(), ".shorts_pipeline.db")
        self.db_path = db_path
        conn = sqlite3.connect(self.db_path)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS projects (
                project_id TEXT PRIMARY KEY, title TEXT,
                stage TEXT, format TEXT, duration REAL,
                created_at REAL
            )
        """)
        conn.commit()
        conn.close()

    def save(self, project: VideoProject):
        conn = sqlite3.connect(self.db_path)
        conn.execute(
            "INSERT OR REPLACE INTO projects VALUES (?,?,?,?,?,?)",
            (project.project_id, project.title, project.stage.value,
             project.format.value, project.duration_sec, project.created_at),
        )
        conn.commit()
        conn.close()


# ── The Main Engine ─────────────────────────────────────────────────────────

class OmniShortsPipelineEngine:
    """
    OMNI Shorts Pipeline Engine — Zero-Prod Video Content Pipeline.

    Capabilities (all native ffmpeg subprocess):
      - Video inspection (codec, resolution, duration, bitrate)
      - Format conversion (portrait/landscape/square)
      - Thumbnail extraction
      - Metadata optimization (title, tags, description)
      - SQLite project tracking
    """

    def __init__(self):
        self.inspector = VideoInspector()
        self.converter = VideoConverter()
        self.metadata = MetadataOptimizer()
        self.store = ProjectStore()

    def inspect_video(self, path: str) -> Dict:
        return self.inspector.inspect(path)

    def optimize_metadata(self, title: str, description: str = "") -> Dict:
        optimized_title = self.metadata.optimize_title(title)
        tags = self.metadata.generate_tags(title, description)
        desc = self.metadata.generate_description(optimized_title, tags)
        return {"title": optimized_title, "tags": tags, "description": desc[:500]}

    def diagnostics(self) -> Dict:
        tools = self.inspector.check_ffmpeg()
        return {
            "engine": "OmniShortsPipelineEngine",
            "status": "active",
            "tools": tools,
            "capabilities": ["video_inspect", "format_convert", "thumbnail_extract",
                             "metadata_optimize", "tag_generate", "project_track"],
            "formats": [f.value for f in VideoFormat],
        }


if __name__ == "__main__":
    engine = OmniShortsPipelineEngine()
    print(json.dumps(engine.diagnostics(), indent=2))
