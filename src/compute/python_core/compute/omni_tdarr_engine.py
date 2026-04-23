ENGINE_VERSION = "1.0.0-omni"
# ===========================================================================
# OMNI TDARR ENGINE — Distributed Media Transcoding & Health Check Automation
# ===========================================================================
# Source Paradigm: https://github.com/HaveAGitGat/Tdarr
# Domain Layer  : Compute (Media Processing)
# Zero-Prod     : 100% Native — subprocess (ffmpeg/ffprobe), os, sqlite3
# ===========================================================================
"""
Tdarr teaches us:
  1. Distributed server-node architecture for parallel transcoding
  2. Conditional transcoding rules (codec, container, bitrate, resolution)
  3. Plugin/flow system for processing stacks
  4. Health checking for media file corruption detection
  5. Library analytics (disk savings, codec distribution)
  6. FFmpeg/HandBrake as underlying execution engines

This engine distills those paradigms into OMNI-native Python media
automation using ONLY stdlib + ffmpeg/ffprobe subprocess calls.
"""

import hashlib
import json
import os
import sqlite3
import subprocess
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Tuple


# ── Data Models ──────────────────────────────────────────────────────────────

class MediaCodec(Enum):
    H264 = "h264"
    H265 = "hevc"
    VP9 = "vp9"
    AV1 = "av1"
    AAC = "aac"
    OPUS = "opus"
    FLAC = "flac"
    UNKNOWN = "unknown"


class TranscodeAction(Enum):
    SKIP = "skip"
    TRANSCODE = "transcode"
    REMUX = "remux"
    HEALTH_CHECK = "health_check"


@dataclass
class MediaInfo:
    path: str
    size_bytes: int = 0
    container: str = ""           # mkv, mp4, avi...
    duration_seconds: float = 0
    video_codec: str = ""
    video_resolution: str = ""    # "1920x1080"
    video_bitrate_kbps: int = 0
    audio_codec: str = ""
    audio_channels: int = 0
    subtitle_count: int = 0
    is_healthy: bool = True
    probe_error: str = ""


@dataclass
class TranscodeRule:
    name: str
    condition: str                # "codec!=hevc", "container!=mkv", "bitrate>5000"
    target_codec: str = "hevc"
    target_container: str = "mkv"
    target_bitrate_kbps: int = 0  # 0 = auto/CRF
    crf: int = 23
    preset: str = "medium"
    hw_accel: str = ""            # "nvenc", "qsv", "vaapi", ""


@dataclass
class TranscodeJob:
    source: MediaInfo
    action: TranscodeAction
    rule_name: str = ""
    output_path: str = ""
    started_at: float = 0
    finished_at: float = 0
    exit_code: int = -1
    size_before: int = 0
    size_after: int = 0
    savings_pct: float = 0
    error: str = ""


# ── FFprobe Media Analyzer ──────────────────────────────────────────────────

class MediaProbe:
    """Probe media files using native ffprobe subprocess."""

    @staticmethod
    def probe(filepath: str) -> MediaInfo:
        """Extract media info using ffprobe JSON output."""
        info = MediaInfo(path=filepath)

        if not os.path.isfile(filepath):
            info.probe_error = "File not found"
            info.is_healthy = False
            return info

        info.size_bytes = os.path.getsize(filepath)
        info.container = os.path.splitext(filepath)[1].lstrip(".").lower()

        try:
            result = subprocess.run(
                ["ffprobe", "-v", "quiet", "-print_format", "json",
                 "-show_format", "-show_streams", filepath],
                capture_output=True, text=True, timeout=30,
            )

            if result.returncode != 0:
                info.probe_error = result.stderr[:256]
                info.is_healthy = False
                return info

            data = json.loads(result.stdout)

            # Format info
            fmt = data.get("format", {})
            info.duration_seconds = float(fmt.get("duration", 0))

            # Stream analysis
            for stream in data.get("streams", []):
                codec_type = stream.get("codec_type", "")

                if codec_type == "video" and not info.video_codec:
                    info.video_codec = stream.get("codec_name", "unknown")
                    width = stream.get("width", 0)
                    height = stream.get("height", 0)
                    info.video_resolution = f"{width}x{height}"
                    bit_rate = stream.get("bit_rate", fmt.get("bit_rate", "0"))
                    info.video_bitrate_kbps = int(bit_rate) // 1000 if bit_rate else 0

                elif codec_type == "audio" and not info.audio_codec:
                    info.audio_codec = stream.get("codec_name", "unknown")
                    info.audio_channels = stream.get("channels", 0)

                elif codec_type == "subtitle":
                    info.subtitle_count += 1

        except FileNotFoundError:
            info.probe_error = "ffprobe not found on PATH"
            info.is_healthy = False
        except json.JSONDecodeError:
            info.probe_error = "Failed to parse ffprobe JSON"
            info.is_healthy = False
        except Exception as e:
            info.probe_error = str(e)[:256]
            info.is_healthy = False

        return info


# ── Health Checker ───────────────────────────────────────────────────────────

class HealthChecker:
    """Check media file integrity using ffmpeg decode test."""

    @staticmethod
    def check(filepath: str) -> Dict:
        """Run full decode check — detects corrupted frames/streams."""
        try:
            result = subprocess.run(
                ["ffmpeg", "-v", "error", "-i", filepath,
                 "-f", "null", "-"],
                capture_output=True, text=True, timeout=300,
            )
            errors = result.stderr.strip()
            return {
                "file": filepath,
                "healthy": len(errors) == 0,
                "errors": errors[:1024] if errors else "",
                "exit_code": result.returncode,
            }
        except FileNotFoundError:
            return {"file": filepath, "healthy": False, "errors": "ffmpeg not found"}
        except subprocess.TimeoutExpired:
            return {"file": filepath, "healthy": False, "errors": "Health check timeout (300s)"}
        except Exception as e:
            return {"file": filepath, "healthy": False, "errors": str(e)[:256]}


# ── Rule Engine ──────────────────────────────────────────────────────────────

class RuleEngine:
    """Evaluate transcoding rules against media files."""

    @staticmethod
    def evaluate(media: MediaInfo, rule: TranscodeRule) -> TranscodeAction:
        """Determine the action for a file based on a rule's condition."""
        condition = rule.condition.lower().strip()

        # Parse condition: "codec!=hevc", "container!=mkv", "bitrate>5000"
        if "codec!=" in condition:
            target = condition.split("!=")[1].strip()
            if media.video_codec.lower() != target:
                return TranscodeAction.TRANSCODE

        elif "container!=" in condition:
            target = condition.split("!=")[1].strip()
            if media.container.lower() != target:
                return TranscodeAction.REMUX

        elif "bitrate>" in condition:
            threshold = int(condition.split(">")[1].strip())
            if media.video_bitrate_kbps > threshold:
                return TranscodeAction.TRANSCODE

        return TranscodeAction.SKIP


# ── Transcoder ───────────────────────────────────────────────────────────────

class Transcoder:
    """Execute FFmpeg transcoding via native subprocess."""

    @staticmethod
    def transcode(source: str, output: str, rule: TranscodeRule) -> TranscodeJob:
        """Transcode a media file according to a rule."""
        probe = MediaProbe.probe(source)
        job = TranscodeJob(
            source=probe,
            action=TranscodeAction.TRANSCODE,
            rule_name=rule.name,
            output_path=output,
            size_before=probe.size_bytes,
        )

        # Build FFmpeg command
        cmd = ["ffmpeg", "-y", "-i", source]

        # Hardware acceleration
        if rule.hw_accel == "nvenc":
            cmd.extend(["-c:v", "hevc_nvenc", "-preset", rule.preset])
        elif rule.hw_accel == "qsv":
            cmd.extend(["-c:v", "hevc_qsv", "-preset", rule.preset])
        else:
            codec_map = {"hevc": "libx265", "h264": "libx264", "av1": "libaom-av1", "vp9": "libvpx-vp9"}
            encoder = codec_map.get(rule.target_codec, "libx265")
            cmd.extend(["-c:v", encoder, "-preset", rule.preset, "-crf", str(rule.crf)])

        # Audio passthrough
        cmd.extend(["-c:a", "copy", "-c:s", "copy"])

        # Target bitrate cap
        if rule.target_bitrate_kbps > 0:
            cmd.extend(["-b:v", f"{rule.target_bitrate_kbps}k"])

        cmd.append(output)

        job.started_at = time.time()
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=7200)
            job.exit_code = result.returncode
            if result.returncode != 0:
                job.error = result.stderr[:1024]
            elif os.path.isfile(output):
                job.size_after = os.path.getsize(output)
                if job.size_before > 0:
                    job.savings_pct = round(
                        (1 - job.size_after / job.size_before) * 100, 2
                    )
        except FileNotFoundError:
            job.error = "ffmpeg not found on PATH"
            job.exit_code = -1
        except subprocess.TimeoutExpired:
            job.error = "Transcode timeout (7200s)"
            job.exit_code = -1
        except Exception as e:
            job.error = str(e)[:256]
            job.exit_code = -1

        job.finished_at = time.time()
        return job


# ── Library Scanner & Analytics ─────────────────────────────────────────────

class LibraryAnalytics:
    """Scan media libraries and compute analytics."""

    MEDIA_EXTENSIONS = {".mkv", ".mp4", ".avi", ".mov", ".wmv", ".flv", ".ts", ".m4v", ".webm"}

    @staticmethod
    def scan_directory(path: str, recursive: bool = True) -> List[str]:
        """Find all media files in a directory."""
        media_files = []
        if not os.path.isdir(path):
            return media_files

        if recursive:
            for root, dirs, files in os.walk(path):
                for f in files:
                    if os.path.splitext(f)[1].lower() in LibraryAnalytics.MEDIA_EXTENSIONS:
                        media_files.append(os.path.join(root, f))
        else:
            for f in os.listdir(path):
                if os.path.splitext(f)[1].lower() in LibraryAnalytics.MEDIA_EXTENSIONS:
                    media_files.append(os.path.join(path, f))

        return media_files

    @staticmethod
    def compute_stats(media_infos: List[MediaInfo]) -> Dict:
        """Compute library-wide statistics."""
        total_size = sum(m.size_bytes for m in media_infos)
        codec_dist = {}
        container_dist = {}
        unhealthy = 0

        for m in media_infos:
            codec_dist[m.video_codec] = codec_dist.get(m.video_codec, 0) + 1
            container_dist[m.container] = container_dist.get(m.container, 0) + 1
            if not m.is_healthy:
                unhealthy += 1

        return {
            "total_files": len(media_infos),
            "total_size_gb": round(total_size / (1024**3), 2),
            "codec_distribution": codec_dist,
            "container_distribution": container_dist,
            "unhealthy_files": unhealthy,
        }


# ── Job History (SQLite) ────────────────────────────────────────────────────

class JobHistory:
    """Persistent job history for transcode audit trail."""

    def __init__(self, db_path: str = ""):
        if not db_path:
            db_path = os.path.join(os.path.dirname(__file__), "..", ".tdarr_jobs.db")
        self.db_path = db_path
        self._init()

    def _init(self):
        conn = sqlite3.connect(self.db_path)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS jobs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                source TEXT, output TEXT, rule_name TEXT,
                action TEXT, exit_code INTEGER,
                size_before INTEGER, size_after INTEGER,
                savings_pct REAL, started_at REAL, finished_at REAL,
                error TEXT
            )
        """)
        conn.commit()
        conn.close()

    def record(self, job: TranscodeJob):
        conn = sqlite3.connect(self.db_path)
        conn.execute(
            "INSERT INTO jobs (source,output,rule_name,action,exit_code,size_before,size_after,savings_pct,started_at,finished_at,error) VALUES (?,?,?,?,?,?,?,?,?,?,?)",
            (job.source.path, job.output_path, job.rule_name,
             job.action.value, job.exit_code,
             job.size_before, job.size_after, job.savings_pct,
             job.started_at, job.finished_at, job.error),
        )
        conn.commit()
        conn.close()

    def get_stats(self) -> Dict:
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute("SELECT COUNT(*), SUM(size_before), SUM(size_after), AVG(savings_pct) FROM jobs WHERE exit_code=0")
        row = c.fetchone()
        conn.close()
        return {
            "total_jobs": row[0] or 0,
            "total_input_gb": round((row[1] or 0) / (1024**3), 2),
            "total_output_gb": round((row[2] or 0) / (1024**3), 2),
            "avg_savings_pct": round(row[3] or 0, 2),
        }


# ── The Main Engine ─────────────────────────────────────────────────────────

class OmniTdarrEngine:
    """
    OMNI Tdarr Engine — Zero-Prod Distributed Media Transcoding Automation.

    Capabilities (all via native ffmpeg/ffprobe subprocess):
      - Media file probing (codec, resolution, bitrate, duration)
      - Health checking (full decode integrity test)
      - Conditional rule-based transcoding
      - Library scanning & analytics
      - Job history persistence (SQLite)
      - HW acceleration support (NVENC, QSV)
    """

    def __init__(self):
        self.probe = MediaProbe()
        self.health = HealthChecker()
        self.rules = RuleEngine()
        self.transcoder = Transcoder()
        self.analytics = LibraryAnalytics()
        self.history = JobHistory()

    def analyze_file(self, filepath: str) -> Dict:
        """Probe a single media file and return structured info."""
        info = self.probe.probe(filepath)
        return {
            "path": info.path, "size_mb": round(info.size_bytes / (1024**2), 2),
            "container": info.container, "video_codec": info.video_codec,
            "resolution": info.video_resolution, "bitrate_kbps": info.video_bitrate_kbps,
            "audio_codec": info.audio_codec, "duration_s": round(info.duration_seconds, 1),
            "subtitles": info.subtitle_count, "healthy": info.is_healthy,
            "error": info.probe_error,
        }

    def check_health(self, filepath: str) -> Dict:
        return self.health.check(filepath)

    def scan_library(self, directory: str) -> Dict:
        """Scan a media library directory and return analytics."""
        files = self.analytics.scan_directory(directory)
        infos = [self.probe.probe(f) for f in files[:100]]  # cap at 100 for speed
        stats = self.analytics.compute_stats(infos)
        stats["scanned_path"] = directory
        return stats

    def check_ffmpeg(self) -> Dict:
        """Check if ffmpeg and ffprobe are available on the system."""
        tools = {}
        for tool in ["ffmpeg", "ffprobe"]:
            try:
                r = subprocess.run([tool, "-version"], capture_output=True, text=True, timeout=5)
                version_line = r.stdout.split("\n")[0] if r.returncode == 0 else ""
                tools[tool] = {"installed": r.returncode == 0, "version": version_line}
            except FileNotFoundError:
                tools[tool] = {"installed": False, "version": ""}
        return tools

    def diagnostics(self) -> Dict:
        ff = self.check_ffmpeg()
        return {
            "engine": "OmniTdarrEngine",
            "status": "active",
            "capabilities": ["media_probe", "health_check", "conditional_transcode",
                             "library_scan", "hw_accel", "job_history"],
            "ffmpeg": ff,
        }


if __name__ == "__main__":
    engine = OmniTdarrEngine()
    print("[Tdarr] FFmpeg Status:")
    print(json.dumps(engine.check_ffmpeg(), indent=2))
