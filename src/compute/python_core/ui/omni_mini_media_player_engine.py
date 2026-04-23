ENGINE_VERSION = "1.0.0-omni"
# ===========================================================================
# OMNI MINI MEDIA PLAYER ENGINE — Media Playback Control & Metadata
# ===========================================================================
# Source Paradigm: https://github.com/kalkih/mini-media-player
# Domain Layer  : UI (Media Player Component)
# Zero-Prod     : 100% Native — subprocess, json, os, re
# ===========================================================================
"""
mini-media-player teaches us:
  1. Compact media player UI with album art
  2. Media metadata display (title, artist, album, duration)
  3. Playback controls (play, pause, next, prev, volume)
  4. Progress bar with seek
  5. Media source management
  6. Group/speaker management

This engine distills those paradigms into OMNI-native Python for
system media control and audio file metadata extraction.
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

class PlaybackState(Enum):
    PLAYING = "playing"
    PAUSED = "paused"
    STOPPED = "stopped"
    IDLE = "idle"


@dataclass
class MediaTrack:
    title: str = ""
    artist: str = ""
    album: str = ""
    duration_sec: float = 0
    sample_rate: int = 0
    bit_depth: int = 0
    channels: int = 0
    codec: str = ""
    bitrate_kbps: int = 0
    file_path: str = ""
    size_mb: float = 0


@dataclass
class PlayerState:
    state: PlaybackState = PlaybackState.IDLE
    current_track: Optional[MediaTrack] = None
    volume: int = 50
    position_sec: float = 0
    muted: bool = False


# ── Media File Inspector ──────────────────────────────────────────────────

class MediaInspector:
    """Extract metadata from audio/video files using ffprobe."""

    @staticmethod
    def inspect(file_path: str) -> MediaTrack:
        track = MediaTrack(file_path=file_path)
        if not os.path.isfile(file_path):
            return track

        track.size_mb = round(os.path.getsize(file_path) / (1024 * 1024), 2)

        try:
            r = subprocess.run(
                ["ffprobe", "-v", "quiet", "-print_format", "json",
                 "-show_format", "-show_streams", file_path],
                capture_output=True, text=True, timeout=10,
            )
            if r.returncode == 0:
                data = json.loads(r.stdout)

                # Format info
                fmt = data.get("format", {})
                tags = fmt.get("tags", {})
                track.title = tags.get("title", tags.get("TITLE", os.path.basename(file_path)))
                track.artist = tags.get("artist", tags.get("ARTIST", ""))
                track.album = tags.get("album", tags.get("ALBUM", ""))
                track.duration_sec = round(float(fmt.get("duration", 0)), 2)
                track.bitrate_kbps = int(int(fmt.get("bit_rate", 0)) / 1000)

                # Audio stream
                for stream in data.get("streams", []):
                    if stream.get("codec_type") == "audio":
                        track.codec = stream.get("codec_name", "")
                        track.sample_rate = int(stream.get("sample_rate", 0))
                        track.channels = int(stream.get("channels", 0))
                        bits = stream.get("bits_per_raw_sample") or stream.get("bits_per_sample")
                        track.bit_depth = int(bits) if bits else 0
                        break
        except (FileNotFoundError, json.JSONDecodeError):
            track.title = os.path.basename(file_path)

        return track

    @staticmethod
    def scan_library(dir_path: str) -> Dict:
        """Scan a directory for media files and build a library."""
        AUDIO_EXTS = {".mp3", ".flac", ".wav", ".aac", ".ogg", ".m4a", ".opus", ".wma", ".alac"}
        tracks = []
        total_duration = 0

        if os.path.isdir(dir_path):
            for root, _, files in os.walk(dir_path):
                for f in files:
                    if os.path.splitext(f)[1].lower() in AUDIO_EXTS:
                        path = os.path.join(root, f)
                        track = MediaInspector.inspect(path)
                        total_duration += track.duration_sec
                        tracks.append({
                            "title": track.title, "artist": track.artist,
                            "codec": track.codec, "duration": track.duration_sec,
                        })
                        if len(tracks) >= 100:
                            break

        return {
            "directory": dir_path,
            "tracks_found": len(tracks),
            "total_duration_min": round(total_duration / 60, 1),
            "tracks": tracks[:20],
        }


# ── System Media Control ──────────────────────────────────────────────────

class SystemMediaControl:
    """Control system media playback on Windows."""

    @staticmethod
    def send_media_key(key: str) -> Dict:
        """Send media key events (play/pause, next, prev, volume)."""
        if os.name != "nt":
            return {"error": "Windows only"}

        key_map = {
            "play_pause": "0xB3", "next": "0xB0", "prev": "0xB1",
            "stop": "0xB2", "volume_up": "0xAF", "volume_down": "0xAE",
            "mute": "0xAD",
        }
        vk = key_map.get(key)
        if not vk:
            return {"error": f"Unknown key: {key}"}

        ps_cmd = f"""
Add-Type -TypeDefinition 'using System.Runtime.InteropServices; public class KBD {{ [DllImport("user32.dll")] public static extern void keybd_event(byte k, byte s, uint f, int e); }}' -Language CSharp
[KBD]::keybd_event({vk}, 0, 0, 0)
[KBD]::keybd_event({vk}, 0, 2, 0)
"""
        try:
            r = subprocess.run(["powershell", "-Command", ps_cmd],
                               capture_output=True, text=True, timeout=5)
            return {"sent": key, "success": r.returncode == 0}
        except Exception as e:
            return {"error": str(e)[:256]}

    @staticmethod
    def get_now_playing() -> Dict:
        """Get currently playing media info (Windows)."""
        if os.name != "nt":
            return {"error": "Windows only"}
        ps_cmd = """
$s = Get-Process | Where-Object { $_.MainWindowTitle -ne '' } |
  Select-Object ProcessName, MainWindowTitle |
  Where-Object { $_.ProcessName -match 'spotify|chrome|firefox|vlc|wmplayer|groove|foobar|musicbee' } |
  Select-Object -First 3
$s | ConvertTo-Json
"""
        try:
            r = subprocess.run(["powershell", "-Command", ps_cmd],
                               capture_output=True, text=True, timeout=5)
            if r.returncode == 0 and r.stdout.strip():
                data = json.loads(r.stdout)
                if isinstance(data, dict):
                    data = [data]
                return {"players": [{"app": d.get("ProcessName", ""),
                                     "title": d.get("MainWindowTitle", "")} for d in data]}
            return {"players": []}
        except Exception:
            return {"players": []}


# ── Playlist Generator ────────────────────────────────────────────────────

class PlaylistGenerator:
    """Generate M3U playlists from audio files."""

    @staticmethod
    def generate_m3u(tracks: List[MediaTrack], output_path: str) -> Dict:
        lines = ["#EXTM3U"]
        for t in tracks:
            dur = int(t.duration_sec)
            display = f"{t.artist} - {t.title}" if t.artist else t.title
            lines.append(f"#EXTINF:{dur},{display}")
            lines.append(t.file_path)

        os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))
        return {"generated": output_path, "tracks": len(tracks)}


# ── The Main Engine ─────────────────────────────────────────────────────────

class OmniMiniMediaPlayerEngine:
    """
    OMNI Mini Media Player Engine — Zero-Prod Media Playback & Metadata.

    Capabilities (all native subprocess):
      - Audio file metadata extraction via ffprobe
      - Media library scanning
      - System media key control (play/pause/next/prev)
      - Now-playing detection
      - M3U playlist generation
    """

    def __init__(self):
        self.inspector = MediaInspector()
        self.control = SystemMediaControl()
        self.playlist = PlaylistGenerator()

    def inspect_file(self, path: str) -> Dict:
        t = self.inspector.inspect(path)
        return {
            "title": t.title, "artist": t.artist, "album": t.album,
            "codec": t.codec, "duration_sec": t.duration_sec,
            "sample_rate": t.sample_rate, "bit_depth": t.bit_depth,
            "bitrate_kbps": t.bitrate_kbps, "size_mb": t.size_mb,
        }

    def now_playing(self) -> Dict:
        return self.control.get_now_playing()

    def diagnostics(self) -> Dict:
        has_ffprobe = False
        try:
            r = subprocess.run(["ffprobe", "-version"], capture_output=True, text=True, timeout=3)
            has_ffprobe = r.returncode == 0
        except FileNotFoundError:
            pass
        now = self.control.get_now_playing()
        return {
            "engine": "OmniMiniMediaPlayerEngine",
            "status": "active",
            "ffprobe": has_ffprobe,
            "now_playing": now,
            "capabilities": ["file_inspect", "library_scan", "media_keys",
                             "now_playing", "m3u_playlist", "metadata_extract"],
        }


if __name__ == "__main__":
    engine = OmniMiniMediaPlayerEngine()
    print(json.dumps(engine.diagnostics(), indent=2))
