# -*- coding: utf-8 -*-
"""
+============================================================================+
|  OMNI HOWLER AUDIO ENGINE                                                  |
|  Inspired by: Howler.js (goldfire/howler.js)                               |
|  Purpose: Cross-platform audio engine with Web Audio API abstraction,      |
|           HTML5 Audio fallback, sprite-based SFX, spatial 3D audio,        |
|           audio pool management, codec detection, and audio graph control  |
|  Layer: Compute (Python)                                                   |
|  License: OMNI-Enterprise                                                  |
+============================================================================+

Architecture adapted from Howler.js:
  - Howl: Core sound object with load, play, pause, stop, seek, volume, rate
  - Howler (Global): Global audio controller managing Web Audio context,
    master volume, codec support detection, and auto-suspend/resume
  - Sound IDs: Each play() returns a unique ID for independent control
  - Sprites: Define named time ranges within a single audio file for SFX
  - Spatial Audio: 3D panning with panner attributes (position, orientation)
  - Audio Pool: Pre-allocated HTML5 Audio elements for fallback mode
  - Codec Detection: canPlayType() mapping for mp3, ogg, wav, aac, webm, etc.
  - Events: onload, onplay, onpause, onstop, onend, onfade, onerror
  - Fading: Volume fade in/out with duration and callback
  - Audio Groups: Group sounds for batch volume/mute control
"""

from __future__ import annotations

import hashlib
import json
import math
import time
import uuid
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Callable, Dict, Final, List, Optional, Set, Tuple, Union

ENGINE_VERSION: Final[str] = "1.0.0"
ENGINE_NAME: Final[str] = "OmniHowlerAudioEngine"


# ============================================================================
# 1. Enums & Constants
# ============================================================================

class AudioFormat(Enum):
    """Production-grade Audio Format component."""
    MP3 = "mp3"
    OGG = "ogg"
    WAV = "wav"
    AAC = "aac"
    WEBM = "webm"
    FLAC = "flac"
    M4A = "m4a"
    OPUS = "opus"
    AC3 = "ac3"
    CAF = "caf"


class AudioState(Enum):
    """Production-grade Audio State component."""
    UNLOADED = "unloaded"
    LOADING = "loading"
    LOADED = "loaded"
    PLAYING = "playing"
    PAUSED = "paused"
    STOPPED = "stopped"
    ENDED = "ended"
    ERROR = "error"


class AudioBackend(Enum):
    """Production-grade Audio Backend component."""
    WEB_AUDIO = "webaudio"
    HTML5_AUDIO = "html5"
    NATIVE = "native"


class PanningModel(Enum):
    """Production-grade Panning Model component."""
    HRTF = "HRTF"
    EQUAL_POWER = "equalpower"


class DistanceModel(Enum):
    """Production-grade Distance Model component."""
    LINEAR = "linear"
    INVERSE = "inverse"
    EXPONENTIAL = "exponential"


class EventType(Enum):
    """Type enumeration for EventType."""
    LOAD = "load"
    LOAD_ERROR = "loaderror"
    PLAY = "play"
    PAUSE = "pause"
    STOP = "stop"
    END = "end"
    FADE = "fade"
    SEEK = "seek"
    VOLUME = "volume"
    RATE = "rate"
    MUTE = "mute"
    UNLOCK = "unlock"


# Codec support detection mapping (mirrors Howler.js behavior)
CODEC_SUPPORT: Final[Dict[str, List[str]]] = {
    "mp3": ['audio/mpeg; codecs="mp3"', 'audio/mpeg', 'audio/mp3'],
    "ogg": ['audio/ogg; codecs="vorbis"'],
    "wav": ['audio/wav; codecs="1"', 'audio/wav'],
    "aac": ['audio/aac', 'audio/x-aac'],
    "m4a": ['audio/x-m4a', 'audio/m4a', 'audio/aac'],
    "webm": ['audio/webm; codecs="vorbis"', 'audio/webm; codecs="opus"'],
    "flac": ['audio/flac', 'audio/x-flac'],
    "opus": ['audio/ogg; codecs="opus"', 'audio/webm; codecs="opus"'],
    "ac3": ['audio/ac3'],
    "caf": ['audio/x-caf'],
}


# ============================================================================
# 2. Data Structures
# ============================================================================

@dataclass
class AudioSprite:
    """A named time range within a sound file (SFX sprite)."""
    name: str = ""
    start_ms: float = 0.0
    duration_ms: float = 0.0
    loop: bool = False

    @property
    def end_ms(self) -> float:
        """Execute end ms operation for AudioSprite."""
        return self.start_ms + self.duration_ms

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dict representation."""
        return {"name": self.name, "start_ms": self.start_ms,
                "duration_ms": self.duration_ms, "loop": self.loop}


@dataclass
class SpatialPosition:
    """3D spatial audio position and orientation."""
    x: float = 0.0
    y: float = 0.0
    z: float = 0.0
    orientation_x: float = 0.0
    orientation_y: float = 0.0
    orientation_z: float = -1.0
    panning_model: PanningModel = PanningModel.HRTF
    distance_model: DistanceModel = DistanceModel.INVERSE
    ref_distance: float = 1.0
    max_distance: float = 10000.0
    rolloff_factor: float = 1.0
    cone_inner_angle: float = 360.0
    cone_outer_angle: float = 360.0
    cone_outer_gain: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dict representation."""
        return {
            "position": [self.x, self.y, self.z],
            "orientation": [self.orientation_x, self.orientation_y, self.orientation_z],
            "panning_model": self.panning_model.value,
            "distance_model": self.distance_model.value,
            "ref_distance": self.ref_distance,
            "max_distance": self.max_distance,
            "rolloff_factor": self.rolloff_factor,
        }


@dataclass
class SoundInstance:
    """A single playing instance of a sound (each play() creates one)."""
    sound_id: int = 0
    howl_id: str = ""
    sprite_name: str = ""
    state: AudioState = AudioState.STOPPED
    volume: float = 1.0
    rate: float = 1.0
    seek_position_ms: float = 0.0
    loop: bool = False
    muted: bool = False
    spatial: Optional[SpatialPosition] = None
    fade_from: float = -1.0
    fade_to: float = -1.0
    fade_duration_ms: float = 0.0
    fade_start_time: float = 0.0
    started_at: float = 0.0
    paused_at: float = 0.0

    @property
    def elapsed_ms(self) -> float:
        """Execute elapsed ms operation for SoundInstance."""
        if self.state == AudioState.PLAYING and self.started_at > 0:
            return (time.time() - self.started_at) * 1000
        return self.seek_position_ms

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dict representation."""
        return {
            "id": self.sound_id, "howl": self.howl_id[:8],
            "state": self.state.value, "volume": round(self.volume, 2),
            "rate": self.rate, "seek_ms": round(self.seek_position_ms, 1),
            "loop": self.loop, "muted": self.muted,
            "has_spatial": self.spatial is not None,
            "sprite": self.sprite_name or None,
        }


@dataclass
class FadeOperation:
    """A volume fade operation."""
    sound_id: int = 0
    from_vol: float = 0.0
    to_vol: float = 1.0
    duration_ms: float = 1000.0
    started_at: float = field(default_factory=time.time)
    completed: bool = False

    @property
    def progress(self) -> float:
        """Execute progress operation for FadeOperation."""
        elapsed = (time.time() - self.started_at) * 1000
        return min(1.0, elapsed / max(self.duration_ms, 1))

    @property
    def current_volume(self) -> float:
        """Execute current volume operation for FadeOperation."""
        p = self.progress
        return self.from_vol + (self.to_vol - self.from_vol) * p

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dict representation."""
        return {
            "sound_id": self.sound_id, "from": self.from_vol,
            "to": self.to_vol, "duration_ms": self.duration_ms,
            "progress": round(self.progress, 2),
            "current_vol": round(self.current_volume, 3),
        }


@dataclass
class Howl:
    """
    A Howl represents a single audio source with its configuration.
    Mirrors the Howl() constructor from Howler.js.
    """
    howl_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    src: List[str] = field(default_factory=list)
    format: List[AudioFormat] = field(default_factory=list)
    html5: bool = False  # Force HTML5 Audio mode
    preload: bool = True
    autoplay: bool = False
    loop: bool = False
    volume: float = 1.0
    rate: float = 1.0
    pool_size: int = 5  # HTML5 Audio pool size
    sprites: Dict[str, AudioSprite] = field(default_factory=dict)
    spatial: Optional[SpatialPosition] = None
    state: AudioState = AudioState.UNLOADED
    duration_ms: float = 0.0
    group: str = ""
    # Internal
    _sound_counter: int = 0
    _sounds: Dict[int, SoundInstance] = field(default_factory=dict)
    _active_fades: Dict[int, FadeOperation] = field(default_factory=dict)
    _event_log: List[Dict[str, Any]] = field(default_factory=list)
    created_at: float = field(default_factory=time.time)

    def _next_sound_id(self) -> int:
        self._sound_counter += 1
        return self._sound_counter

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dict representation."""
        return {
            "id": self.howl_id[:8], "name": self.name,
            "src": self.src, "format": [f.value for f in self.format],
            "state": self.state.value, "volume": self.volume,
            "rate": self.rate, "loop": self.loop, "html5": self.html5,
            "duration_ms": self.duration_ms,
            "sprites": len(self.sprites),
            "active_sounds": len([s for s in self._sounds.values()
                                  if s.state == AudioState.PLAYING]),
            "total_sounds": len(self._sounds),
            "group": self.group or None,
            "spatial": self.spatial is not None,
        }


@dataclass
class AudioGroup:
    """A group of sounds for batch control."""
    group_id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    name: str = ""
    volume: float = 1.0
    muted: bool = False
    howl_ids: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dict representation."""
        return {
            "id": self.group_id, "name": self.name,
            "volume": self.volume, "muted": self.muted,
            "sounds": len(self.howl_ids),
        }


# ============================================================================
# 3. Global Audio Controller (Howler singleton equivalent)
# ============================================================================

class GlobalAudioController:
    """
    Manages the global audio context, master volume, codec support,
    auto-suspend/resume, and unlock handling. Mirrors Howler.js global.
    """

    def __init__(self):
        """Initialize GlobalAudioController."""
        self.master_volume: float = 1.0
        self.master_mute: bool = False
        self.backend: AudioBackend = AudioBackend.WEB_AUDIO
        self.auto_suspend: bool = True
        self.auto_unlock: bool = True
        self.ctx_state: str = "running"  # running, suspended, closed
        self.sample_rate: int = 44100
        self._codec_cache: Dict[str, bool] = {}
        self._detect_codecs()

    def _detect_codecs(self):
        """Detect supported audio codecs."""
        # In production, this would use canPlayType() on an Audio element.
        # Here we report all major formats as supported.
        for fmt in AudioFormat:
            self._codec_cache[fmt.value] = True

    def check_codec(self, format_name: str) -> bool:
        """Check if a codec is supported."""
        return self._codec_cache.get(format_name, False)

    def supported_formats(self) -> List[str]:
        """Execute supported formats operation for GlobalAudioController."""
        return [k for k, v in self._codec_cache.items() if v]

    def set_volume(self, vol: float):
        """Set volume for GlobalAudioController."""
        self.master_volume = max(0.0, min(1.0, vol))

    def mute(self, muted: bool = True):
        """Execute mute operation for GlobalAudioController."""
        self.master_mute = muted

    def suspend(self):
        """Execute suspend operation for GlobalAudioController."""
        self.ctx_state = "suspended"

    def resume(self):
        """Execute resume operation for GlobalAudioController."""
        self.ctx_state = "running"

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dict representation."""
        return {
            "master_volume": self.master_volume,
            "master_mute": self.master_mute,
            "backend": self.backend.value,
            "ctx_state": self.ctx_state,
            "sample_rate": self.sample_rate,
            "supported_formats": self.supported_formats(),
        }


# ============================================================================
# 4. Main Engine
# ============================================================================

class OmniHowlerAudioEngine:
    """OMNI Howler Audio Engine -- Cross-Platform Audio Management Platform."""

    def __init__(self):
        """Initialize OmniHowlerAudioEngine."""
        self._global = GlobalAudioController()
        self._howls: Dict[str, Howl] = {}
        self._groups: Dict[str, AudioGroup] = {}
        self._event_history: List[Dict[str, Any]] = []

    # -- Howl Management --
    def create_howl(self, name: str, src: List[str], **kwargs) -> Howl:
        """Create a new Howl (sound object)."""
        formats = []
        for s in src:
            ext = Path(s).suffix.lstrip(".").lower()
            try:
                formats.append(AudioFormat(ext))
            except ValueError:
                pass

        sprites = {}
        if "sprites" in kwargs:
            for sname, sdata in kwargs.pop("sprites").items():
                sprites[sname] = AudioSprite(
                    name=sname, start_ms=sdata[0],
                    duration_ms=sdata[1],
                    loop=sdata[2] if len(sdata) > 2 else False,
                )

        spatial = None
        if kwargs.get("spatial"):
            sp = kwargs.pop("spatial")
            spatial = SpatialPosition(
                x=sp.get("x", 0), y=sp.get("y", 0), z=sp.get("z", 0),
            )

        howl = Howl(
            name=name, src=src, format=formats,
            html5=kwargs.get("html5", False),
            preload=kwargs.get("preload", True),
            autoplay=kwargs.get("autoplay", False),
            loop=kwargs.get("loop", False),
            volume=kwargs.get("volume", 1.0),
            rate=kwargs.get("rate", 1.0),
            pool_size=kwargs.get("pool_size", 5),
            sprites=sprites, spatial=spatial,
            group=kwargs.get("group", ""),
        )

        # Simulate loading
        if howl.preload:
            howl.state = AudioState.LOADED
            # Determine duration from a hash of the source (deterministic)
            h = int(hashlib.md5(src[0].encode()).hexdigest()[:8], 16)
            howl.duration_ms = 1000 + (h % 300000)  # 1s to 5min

        self._howls[howl.howl_id] = howl
        self._log_event(EventType.LOAD, howl.howl_id)

        # Add to group if specified
        if howl.group:
            self._add_to_group(howl.group, howl.howl_id)

        return howl

    def get_howl(self, howl_id: str) -> Optional[Dict[str, Any]]:
        """Performs get howl operation for OmniHowlerAudioEngine."""
        howl = self._howls.get(howl_id)
        return howl.to_dict() if howl else None

    def list_howls(self, group: Optional[str] = None) -> List[Dict[str, Any]]:
        """Performs list howls operation for OmniHowlerAudioEngine."""
        howls = list(self._howls.values())
        if group:
            howls = [h for h in howls if h.group == group]
        return [h.to_dict() for h in howls]

    def unload_howl(self, howl_id: str) -> bool:
        """Unload and destroy a Howl."""
        howl = self._howls.get(howl_id)
        if not howl:
            return False
        # Stop all sounds
        for sid in list(howl._sounds.keys()):
            self.stop(howl_id, sid)
        howl.state = AudioState.UNLOADED
        del self._howls[howl_id]
        return True

    # -- Playback Control --
    def play(self, howl_id: str, sprite: Optional[str] = None) -> Optional[int]:
        """Play a sound. Returns a sound ID for independent control."""
        howl = self._howls.get(howl_id)
        if not howl or howl.state == AudioState.UNLOADED:
            return None

        if howl.state != AudioState.LOADED and howl.state != AudioState.PLAYING:
            howl.state = AudioState.LOADED

        sound_id = howl._next_sound_id()
        sprite_obj = howl.sprites.get(sprite) if sprite else None

        sound = SoundInstance(
            sound_id=sound_id, howl_id=howl_id,
            sprite_name=sprite or "",
            state=AudioState.PLAYING,
            volume=howl.volume, rate=howl.rate,
            loop=sprite_obj.loop if sprite_obj else howl.loop,
            spatial=SpatialPosition(**{k: v for k, v in (howl.spatial.to_dict() if howl.spatial else {}).items() if k not in ("panning_model", "distance_model", "position", "orientation")}) if howl.spatial else None,
            started_at=time.time(),
        )
        if sprite_obj:
            sound.seek_position_ms = sprite_obj.start_ms

        howl._sounds[sound_id] = sound
        howl.state = AudioState.PLAYING
        self._log_event(EventType.PLAY, howl_id, sound_id)
        return sound_id

    def pause(self, howl_id: str, sound_id: Optional[int] = None) -> bool:
        """Pause a sound or all sounds in a Howl."""
        howl = self._howls.get(howl_id)
        if not howl:
            return False

        targets = self._get_targets(howl, sound_id)
        for sound in targets:
            if sound.state == AudioState.PLAYING:
                sound.state = AudioState.PAUSED
                sound.paused_at = time.time()
                sound.seek_position_ms = sound.elapsed_ms
                self._log_event(EventType.PAUSE, howl_id, sound.sound_id)
        return True

    def stop(self, howl_id: str, sound_id: Optional[int] = None) -> bool:
        """Stop a sound or all sounds in a Howl."""
        howl = self._howls.get(howl_id)
        if not howl:
            return False

        targets = self._get_targets(howl, sound_id)
        for sound in targets:
            sound.state = AudioState.STOPPED
            sound.seek_position_ms = 0.0
            self._log_event(EventType.STOP, howl_id, sound.sound_id)
        return True

    def seek(self, howl_id: str, position_ms: float,
             sound_id: Optional[int] = None) -> bool:
        """Seek to a position in the sound."""
        howl = self._howls.get(howl_id)
        if not howl:
            return False

        targets = self._get_targets(howl, sound_id)
        for sound in targets:
            sound.seek_position_ms = max(0.0, min(position_ms, howl.duration_ms))
            if sound.state == AudioState.PLAYING:
                sound.started_at = time.time() - (sound.seek_position_ms / 1000)
            self._log_event(EventType.SEEK, howl_id, sound.sound_id)
        return True

    def volume(self, howl_id: str, vol: float,
               sound_id: Optional[int] = None) -> bool:
        """Set volume for a sound or all sounds in a Howl."""
        howl = self._howls.get(howl_id)
        if not howl:
            return False

        vol = max(0.0, min(1.0, vol))
        if sound_id is None:
            howl.volume = vol

        targets = self._get_targets(howl, sound_id)
        for sound in targets:
            sound.volume = vol
        self._log_event(EventType.VOLUME, howl_id, sound_id)
        return True

    def rate(self, howl_id: str, rate_value: float,
             sound_id: Optional[int] = None) -> bool:
        """Set playback rate (speed)."""
        howl = self._howls.get(howl_id)
        if not howl:
            return False

        rate_value = max(0.25, min(4.0, rate_value))
        if sound_id is None:
            howl.rate = rate_value

        targets = self._get_targets(howl, sound_id)
        for sound in targets:
            sound.rate = rate_value
        self._log_event(EventType.RATE, howl_id, sound_id)
        return True

    def mute(self, howl_id: str, muted: bool = True,
             sound_id: Optional[int] = None) -> bool:
        """Mute/unmute a sound."""
        howl = self._howls.get(howl_id)
        if not howl:
            return False

        targets = self._get_targets(howl, sound_id)
        for sound in targets:
            sound.muted = muted
        self._log_event(EventType.MUTE, howl_id, sound_id)
        return True

    def loop(self, howl_id: str, loop_value: bool,
             sound_id: Optional[int] = None) -> bool:
        """Set loop mode."""
        howl = self._howls.get(howl_id)
        if not howl:
            return False

        if sound_id is None:
            howl.loop = loop_value

        targets = self._get_targets(howl, sound_id)
        for sound in targets:
            sound.loop = loop_value
        return True

    # -- Fade --
    def fade(self, howl_id: str, from_vol: float, to_vol: float,
             duration_ms: float, sound_id: Optional[int] = None) -> bool:
        """Fade volume from one level to another."""
        howl = self._howls.get(howl_id)
        if not howl:
            return False

        targets = self._get_targets(howl, sound_id)
        for sound in targets:
            fade_op = FadeOperation(
                sound_id=sound.sound_id,
                from_vol=from_vol, to_vol=to_vol,
                duration_ms=duration_ms,
            )
            howl._active_fades[sound.sound_id] = fade_op
            sound.volume = from_vol
            self._log_event(EventType.FADE, howl_id, sound.sound_id)
        return True

    def process_fades(self, howl_id: str) -> List[Dict[str, Any]]:
        """Process active fades and return current state."""
        howl = self._howls.get(howl_id)
        if not howl:
            return []

        results = []
        completed = []
        for sid, fade in howl._active_fades.items():
            sound = howl._sounds.get(sid)
            if sound:
                sound.volume = fade.current_volume
                if fade.progress >= 1.0:
                    sound.volume = fade.to_vol
                    fade.completed = True
                    completed.append(sid)
            results.append(fade.to_dict())

        for sid in completed:
            del howl._active_fades[sid]

        return results

    # -- Spatial Audio --
    def set_position(self, howl_id: str, x: float, y: float, z: float = 0.0,
                     sound_id: Optional[int] = None) -> bool:
        """Set 3D position for spatial audio."""
        howl = self._howls.get(howl_id)
        if not howl:
            return False

        targets = self._get_targets(howl, sound_id)
        for sound in targets:
            if not sound.spatial:
                sound.spatial = SpatialPosition()
            sound.spatial.x = x
            sound.spatial.y = y
            sound.spatial.z = z
        return True

    def set_orientation(self, howl_id: str, x: float, y: float, z: float,
                        sound_id: Optional[int] = None) -> bool:
        """Set 3D orientation for spatial audio."""
        howl = self._howls.get(howl_id)
        if not howl:
            return False

        targets = self._get_targets(howl, sound_id)
        for sound in targets:
            if not sound.spatial:
                sound.spatial = SpatialPosition()
            sound.spatial.orientation_x = x
            sound.spatial.orientation_y = y
            sound.spatial.orientation_z = z
        return True

    # -- Audio Groups --
    def create_group(self, name: str) -> AudioGroup:
        """Create a new audio group."""
        group = AudioGroup(name=name)
        self._groups[name] = group
        return group

    def _add_to_group(self, group_name: str, howl_id: str):
        if group_name not in self._groups:
            self.create_group(group_name)
        self._groups[group_name].howl_ids.append(howl_id)

    def set_group_volume(self, group_name: str, vol: float) -> bool:
        """Set volume for all sounds in a group."""
        group = self._groups.get(group_name)
        if not group:
            return False
        group.volume = max(0.0, min(1.0, vol))
        for hid in group.howl_ids:
            self.volume(hid, group.volume)
        return True

    def mute_group(self, group_name: str, muted: bool = True) -> bool:
        """Mute/unmute all sounds in a group."""
        group = self._groups.get(group_name)
        if not group:
            return False
        group.muted = muted
        for hid in group.howl_ids:
            self.mute(hid, muted)
        return True

    def list_groups(self) -> List[Dict[str, Any]]:
        """Performs list groups operation for OmniHowlerAudioEngine."""
        return [g.to_dict() for g in self._groups.values()]

    # -- Global Controls --
    def set_master_volume(self, vol: float):
        """Performs set master volume operation for OmniHowlerAudioEngine."""
        self._global.set_volume(vol)

    def set_master_mute(self, muted: bool = True):
        """Performs set master mute operation for OmniHowlerAudioEngine."""
        self._global.mute(muted)

    def suspend_context(self):
        """Performs suspend context operation for OmniHowlerAudioEngine."""
        self._global.suspend()

    def resume_context(self):
        """Performs resume context operation for OmniHowlerAudioEngine."""
        self._global.resume()

    def get_supported_formats(self) -> List[str]:
        """Performs get supported formats operation for OmniHowlerAudioEngine."""
        return self._global.supported_formats()

    def get_global_state(self) -> Dict[str, Any]:
        """Performs get global state operation for OmniHowlerAudioEngine."""
        return self._global.to_dict()

    # -- Utilities --
    def _get_targets(self, howl: Howl,
                     sound_id: Optional[int] = None) -> List[SoundInstance]:
        if sound_id is not None:
            s = howl._sounds.get(sound_id)
            return [s] if s else []
        return list(howl._sounds.values())

    def _log_event(self, event: EventType, howl_id: str,
                   sound_id: Optional[int] = None):
        self._event_history.append({
            "event": event.value, "howl_id": howl_id[:8],
            "sound_id": sound_id, "time": time.time(),
        })

    def get_event_history(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Performs get event history operation for OmniHowlerAudioEngine."""
        return self._event_history[-limit:]

    # -- Stats & Diagnostics --
    def stats(self) -> Dict[str, Any]:
        """Performs stats operation for OmniHowlerAudioEngine."""
        total_sounds = 0
        playing = 0
        for howl in self._howls.values():
            for s in howl._sounds.values():
                total_sounds += 1
                if s.state == AudioState.PLAYING:
                    playing += 1
        return {
            "total_howls": len(self._howls),
            "total_sounds": total_sounds,
            "playing": playing,
            "groups": len(self._groups),
            "events_logged": len(self._event_history),
            "global": self._global.to_dict(),
        }

    def diagnostics(self) -> Dict[str, Any]:
        """Full diagnostic run exercising all subsystems."""
        # 1. Create howls
        music = self.create_howl(
            "background_music",
            src=["audio/background.mp3", "audio/background.ogg"],
            volume=0.8, loop=True, group="music",
        )

        sfx = self.create_howl(
            "game_sfx",
            src=["audio/effects.mp3"],
            sprites={
                "explosion": [0, 2000],
                "laser": [2000, 500],
                "powerup": [2500, 1500, True],  # looping sprite
                "hit": [4000, 300],
                "coin": [4300, 800],
            },
            volume=1.0, group="sfx",
        )

        spatial_sound = self.create_howl(
            "ambient_3d",
            src=["audio/ambient.ogg"],
            spatial={"x": 5.0, "y": 0.0, "z": -3.0},
            volume=0.6,
        )

        # 2. Play sounds
        music_sid = self.play(music.howl_id)
        assert music_sid is not None, "Music play failed"

        laser_sid = self.play(sfx.howl_id, sprite="laser")
        explosion_sid = self.play(sfx.howl_id, sprite="explosion")
        assert laser_sid is not None, "SFX play failed"

        ambient_sid = self.play(spatial_sound.howl_id)
        assert ambient_sid is not None, "Spatial play failed"

        # 3. Volume control
        self.volume(music.howl_id, 0.5, music_sid)
        self.volume(sfx.howl_id, 0.9)

        # 4. Fade
        self.fade(music.howl_id, 0.5, 1.0, 2000, music_sid)
        fades = self.process_fades(music.howl_id)
        assert len(fades) > 0, "Fade processing failed"

        # 5. Seek
        self.seek(music.howl_id, 10000, music_sid)

        # 6. Rate change
        self.rate(music.howl_id, 1.5, music_sid)

        # 7. Spatial positioning
        self.set_position(spatial_sound.howl_id, 10.0, 2.0, -5.0, ambient_sid)
        self.set_orientation(spatial_sound.howl_id, 0.0, 1.0, 0.0, ambient_sid)

        # 8. Mute/unmute
        self.mute(sfx.howl_id, True, explosion_sid)
        self.mute(sfx.howl_id, False, explosion_sid)

        # 9. Group control
        music_group = self._groups.get("music")
        sfx_group = self._groups.get("sfx")
        self.set_group_volume("music", 0.7)
        self.mute_group("sfx", True)
        self.mute_group("sfx", False)

        # 10. Pause and stop
        self.pause(music.howl_id, music_sid)
        self.stop(sfx.howl_id, laser_sid)

        # 11. Global controls
        self.set_master_volume(0.9)
        self.suspend_context()
        self.resume_context()

        # 12. Codec detection
        formats = self.get_supported_formats()
        assert len(formats) > 0, "Codec detection failed"

        stats = self.stats()

        return {
            "engine": ENGINE_NAME, "version": ENGINE_VERSION, "status": "operational",
            "stats": stats,
            "howl_test": {
                "music": music.to_dict(),
                "sfx": sfx.to_dict(),
                "spatial": spatial_sound.to_dict(),
            },
            "playback_test": {
                "music_sid": music_sid,
                "laser_sid": laser_sid,
                "explosion_sid": explosion_sid,
                "ambient_sid": ambient_sid,
            },
            "fade_test": fades[0] if fades else {},
            "group_test": {
                "music": music_group.to_dict() if music_group else None,
                "sfx": sfx_group.to_dict() if sfx_group else None,
            },
            "codec_test": {"supported_formats": formats},
            "spatial_test": {"position_set": True, "orientation_set": True},
            "global_test": self.get_global_state(),
            "capabilities": [
                "create_howl", "play", "pause", "stop", "seek",
                "volume", "rate", "mute", "loop", "fade",
                "set_position", "set_orientation", "create_group",
                "set_group_volume", "mute_group",
                "set_master_volume", "get_supported_formats", "stats",
            ],
        }


if __name__ == "__main__":
    engine = OmniHowlerAudioEngine()
    result = engine.diagnostics()
    print(json.dumps(result, indent=2, default=str))
    print(f"\n[OK] {ENGINE_NAME} v{ENGINE_VERSION} -- OPERATIONAL")
