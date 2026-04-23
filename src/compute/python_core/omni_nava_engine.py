# omni_nava_engine.py
# Production-Grade Cross-Platform Audio Playback
# ==============================================================
# Absorbed from: openscilab/nava
#
# Key patterns learned:
# - Zero-dependency audio triggering
# - System platform branching using built-ins (winsound, afplay, aplay)
#
# OMNI Layer: compute/python_core
# @since 2026.4.0

"""
OMNI Nava Engine
================
Production-grade engine for the OMNI Framework.

OMNI Layer: compute (Python)
"""
import sys
import os
import subprocess
import logging
from typing import Dict, Any

ENGINE_VERSION = "1.0.0-omni"
from src.compute.python_core.omni_base_engine import Result, Ok, Err
logger = logging.getLogger("OmniNavaEngine")

class OmniNavaEngineError(Exception):
    """Production engine class for OmniNavaEngineError."""

    def __init__(self, code="UNKNOWN", message=""):
        """Initialize OmniNavaEngineError."""
        self.code = code
        self.message = message
    pass

    def diagnostics(self):
        """Return engine health diagnostics."""
        return {
            "engine_id": "omni-nava-error",
            "version": getattr(self, "VERSION", "1.0.0"),
            "status": "operational",
        }


class OmniNavaEngine:
    """
    Executes raw audio files seamlessly via native OS primitives
    without requiring third-party libraries (pygame, pyaudio, etc).
    """

    def __init__(self):
        """Initialize OmniNavaEngine."""
        self.platform = sys.platform
        self._is_ready = True

    def play_audio(self, filepath: str, async_play: bool = False) -> Dict[str, Any]:
        """
        Triggers playback across Windows (winsound), macOS (afplay), Linux (aplay).
        Uses monadic error returns to avoid breaking the core loop.
        """
        if not os.path.exists(filepath):
            return {"status": "error", "error": "File not found"}

        try:
            if self.platform.startswith('win'):
                self._play_windows(filepath, async_play)
            elif self.platform.startswith('darwin'):
                self._play_macos(filepath, async_play)
            elif self.platform.startswith('linux'):
                self._play_linux(filepath, async_play)
            else:
                return {"status": "error", "error": f"Unsupported platform: {self.platform}"}

            return {
                "status": "success",
                "data": {
                    "platform": self.platform,
                    "file": filepath,
                    "async_mode": async_play
                }
            }
        except Exception as e:
            return {"status": "error", "error": f"Playback failure: {str(e)}"}

    def _play_windows(self, filepath: str, async_play: bool):
        import winsound
        flags = winsound.SND_FILENAME
        if async_play:
            flags |= winsound.SND_ASYNC
        winsound.PlaySound(filepath, flags)

    def _play_macos(self, filepath: str, async_play: bool):
        if async_play:
            subprocess.Popen(['afplay', filepath])
        else:
            subprocess.call(['afplay', filepath])

    def _play_linux(self, filepath: str, async_play: bool):
        # Prefer aplay for WAV, paplay for general PulseAudio integration
        cmd = ['aplay', filepath] 
        if async_play:
            subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        else:
            subprocess.call(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    def diagnostics(self):
        """Return engine health diagnostics."""
        return {
            "engine_id": "omni-nava",
            "version": getattr(self, "VERSION", "1.0.0"),
            "status": "operational",
        }

    def engine_diagnostics(self) -> Dict[str, str]:
        """Performs engine diagnostics operation for OmniNavaEngine."""
        return {
            "engine": "OmniNavaEngine",
            "platform": self.platform,
            "status": "ready"
        }
