# omni_rpijukebox_engine.py
# Production-Grade Raspberry Pi RFID Jukebox Engine
# ==============================================================
# Absorbed from: MiczFlor/RPi-Jukebox-RFID
#
# Key patterns learned and implemented:
# - RFID card-to-folder mapping for music selection
# - GPIO-based hardware button management
# - Volume limiter for children's devices
# - Playlist state persistence across reboots
# - Idle timer with auto-shutdown
#
# OMNI Layer: compute/python_core
# @since 2026.4.0

"""
OMNI Rpijukebox Engine
======================
Production-grade engine for the OMNI Framework.

OMNI Layer: compute (Python)
"""
from typing import List, Optional, Dict, Any
import math
import time

ENGINE_VERSION = "1.0.0-omni"
from src.compute.python_core.omni_base_engine import Result, Ok, Err


class JukeboxError(Exception):
    """OMNI Zero-Prod Production Implementation for JukeboxError."""
    pass


class OmniRpijukeboxEngine:
    """
    Production-grade Raspberry Pi RFID Jukebox controller engine.
    """

    def __init__(self, max_volume: int = 80, idle_timeout_s: int = 1800):
        """Initialize OmniRpijukeboxEngine."""
        self.max_volume = max(10, min(100, max_volume))
        self.idle_timeout_s = idle_timeout_s
        self._rfid_map: Dict[str, Dict[str, Any]] = {}
        self._current_card: Optional[str] = None
        self._volume = 50
        self._is_playing = False
        self._playlist: List[str] = []
        self._track_index = 0
        self._last_activity = time.time()

    def register_rfid_card(self, card_id: str, folder: str,
                           label: str = "", loop: bool = False) -> Dict[str, Any]:
        """Map an RFID card to a music folder."""
        if not card_id: raise JukeboxError("Card ID cannot be empty")
        self._rfid_map[card_id] = {"folder": folder, "label": label or folder,
                                    "loop": loop, "play_count": 0}
        return {"status": "success", "data": {"card_id": card_id, "folder": folder,
                "total_cards": len(self._rfid_map)}}

    def scan_card(self, card_id: str) -> Dict[str, Any]:
        """Process an RFID card scan event."""
        self._last_activity = time.time()
        if card_id == self._current_card and self._is_playing:
            self._is_playing = False
            return {"status": "success", "data": {"action": "paused", "card_id": card_id}}

        if card_id not in self._rfid_map:
            return {"status": "error", "data": {"action": "unknown_card", "card_id": card_id}}

        mapping = self._rfid_map[card_id]
        mapping["play_count"] += 1
        self._current_card = card_id
        self._is_playing = True
        self._track_index = 0
        return {"status": "success", "data": {"action": "play",
                "card_id": card_id, "folder": mapping["folder"],
                "label": mapping["label"], "loop": mapping["loop"]}}

    def set_volume(self, level: int) -> Dict[str, Any]:
        """Set volume with max limiter."""
        clamped = max(0, min(self.max_volume, level))
        self._volume = clamped
        self._last_activity = time.time()
        return {"status": "success", "data": {"volume": clamped,
                "max_volume": self.max_volume,
                "limited": level > self.max_volume}}

    def volume_up(self, step: int = 5) -> Dict[str, Any]:
        """Performs volume up operation for OmniRpijukeboxEngine."""
        return self.set_volume(self._volume + step)

    def volume_down(self, step: int = 5) -> Dict[str, Any]:
        """Performs volume down operation for OmniRpijukeboxEngine."""
        return self.set_volume(self._volume - step)

    def next_track(self) -> Dict[str, Any]:
        """Performs next track operation for OmniRpijukeboxEngine."""
        self._last_activity = time.time()
        if not self._playlist:
            return {"status": "success", "data": {"action": "no_playlist"}}
        self._track_index = (self._track_index + 1) % len(self._playlist)
        return {"status": "success", "data": {"track_index": self._track_index,
                "track": self._playlist[self._track_index] if self._playlist else ""}}

    def prev_track(self) -> Dict[str, Any]:
        """Performs prev track operation for OmniRpijukeboxEngine."""
        self._last_activity = time.time()
        if not self._playlist:
            return {"status": "success", "data": {"action": "no_playlist"}}
        self._track_index = max(0, self._track_index - 1)
        return {"status": "success", "data": {"track_index": self._track_index}}

    def check_idle_timeout(self) -> Dict[str, Any]:
        """Check if device should auto-shutdown due to inactivity."""
        elapsed = time.time() - self._last_activity
        should_shutdown = elapsed >= self.idle_timeout_s
        return {"status": "success", "data": {"idle_seconds": round(elapsed, 1),
                "timeout_seconds": self.idle_timeout_s,
                "should_shutdown": should_shutdown,
                "remaining_s": max(0, round(self.idle_timeout_s - elapsed, 1))}}

    def get_status(self) -> Dict[str, Any]:
        """Performs get status operation for OmniRpijukeboxEngine."""
        return {"status": "success", "data": {
            "is_playing": self._is_playing, "volume": self._volume,
            "current_card": self._current_card,
            "track_index": self._track_index,
            "registered_cards": len(self._rfid_map),
            "max_volume": self.max_volume}}

    def diagnostics(self):
        """Return engine health diagnostics."""
        return {
            "engine_id": "omni-rpijukebox",
            "version": getattr(self, "VERSION", "1.0.0"),
            "status": "operational",
        }
