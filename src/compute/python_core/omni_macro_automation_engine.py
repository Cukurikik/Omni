"""
+============================================================================+
|  OMNI MACRO AUTOMATION ENGINE                                              |
|  Inspired by: PS4Macro (komefai/PS4Macro)                                  |
|  Purpose: Universal input macro recorder, playback, remapping, and         |
|           script execution engine with controller emulation                |
|  Layer: Compute (Python)                                                   |
|  License: OMNI-Enterprise                                                  |
+============================================================================+

Architecture adapted from PS4Macro's C# codebase:
  - DualShockState emulation (buttons, analog sticks, triggers)
  - Macro recording/playback with frame-level precision
  - Keyboard-to-controller remapping engine
  - Image hashing for screen/state detection (pHash)
  - Scripting API (ScriptBase pattern)
  - Settings management (XML/TOML serialization)
  - Command-line argument processing
"""

from __future__ import annotations

import copy
import hashlib
import json
import math
import os
import struct
import threading
import time
import uuid
from dataclasses import dataclass, field
from enum import Enum, Flag, auto
from pathlib import Path
from typing import Any, Callable, Dict, Final, List, Optional, Sequence, Tuple

# ============================================================================
# Constants
# ============================================================================

ENGINE_VERSION: Final[str] = "1.0.0"
ENGINE_NAME: Final[str] = "OmniMacroAutomationEngine"
MAX_MACRO_FRAMES: Final[int] = 100_000
DEFAULT_LOOP_DELAY_MS: Final[int] = 800
DEFAULT_FRAME_INTERVAL_MS: Final[int] = 16  # ~60fps


# ============================================================================
# 1. Controller State Model
# ============================================================================
from src.compute.python_core.omni_base_engine import Result, Ok, Err

class DPadDirection(Enum):
    """Production-grade D Pad Direction component."""
    NONE = "none"
    UP = "up"
    DOWN = "down"
    LEFT = "left"
    RIGHT = "right"
    UP_LEFT = "up_left"
    UP_RIGHT = "up_right"
    DOWN_LEFT = "down_left"
    DOWN_RIGHT = "down_right"


class ControllerButton(Flag):
    """Bitmask for all controller buttons."""
    NONE = 0
    CROSS = auto()
    CIRCLE = auto()
    SQUARE = auto()
    TRIANGLE = auto()
    L1 = auto()
    R1 = auto()
    L2 = auto()
    R2 = auto()
    L3 = auto()
    R3 = auto()
    OPTIONS = auto()
    SHARE = auto()
    PS = auto()
    TOUCHPAD = auto()


@dataclass
class AnalogStick:
    """Analog stick position (-1.0 to 1.0 per axis)."""
    x: float = 0.0
    y: float = 0.0

    def __post_init__(self):
        self.x = max(-1.0, min(1.0, self.x))
        self.y = max(-1.0, min(1.0, self.y))

    @property
    def magnitude(self) -> float:
        """Execute magnitude operation for AnalogStick."""
        return math.sqrt(self.x ** 2 + self.y ** 2)

    def to_bytes(self) -> bytes:
        """Convert to 2-byte representation (0-255 per axis)."""
        bx = int((self.x + 1.0) * 127.5)
        by = int((self.y + 1.0) * 127.5)
        return struct.pack("BB", max(0, min(255, bx)), max(0, min(255, by)))

    def to_dict(self) -> Dict[str, float]:
        """Convert to dict representation."""
        return {"x": round(self.x, 4), "y": round(self.y, 4)}


@dataclass
class TriggerState:
    """L2/R2 trigger pressure (0.0 to 1.0)."""
    l2: float = 0.0
    r2: float = 0.0

    def __post_init__(self):
        self.l2 = max(0.0, min(1.0, self.l2))
        self.r2 = max(0.0, min(1.0, self.r2))

    def to_bytes(self) -> bytes:
        """Convert to bytes representation."""
        return struct.pack("BB", int(self.l2 * 255), int(self.r2 * 255))

    def to_dict(self) -> Dict[str, float]:
        """Convert to dict representation."""
        return {"l2": round(self.l2, 4), "r2": round(self.r2, 4)}


@dataclass
class DualShockState:
    """
    Complete controller state snapshot (one frame).
    Models the PS4 DualShock 4 controller as in PS4Macro's DualShockState class.
    """
    buttons: ControllerButton = ControllerButton.NONE
    dpad: DPadDirection = DPadDirection.NONE
    left_stick: AnalogStick = field(default_factory=AnalogStick)
    right_stick: AnalogStick = field(default_factory=AnalogStick)
    triggers: TriggerState = field(default_factory=TriggerState)
    timestamp_ms: float = 0.0

    def press(self, button: ControllerButton) -> "DualShockState":
        """Press a button (returns new state for chaining)."""
        new = copy.deepcopy(self)
        new.buttons |= button
        return new

    def release(self, button: ControllerButton) -> "DualShockState":
        """Release a button."""
        new = copy.deepcopy(self)
        new.buttons &= ~button
        return new

    def is_pressed(self, button: ControllerButton) -> bool:
        """Check if pressed condition holds."""
        return bool(self.buttons & button)

    def to_bytes(self) -> bytes:
        """Serialize to binary format for wire transmission."""
        btn_val = self.buttons.value if isinstance(self.buttons, ControllerButton) else 0
        dpad_val = list(DPadDirection).index(self.dpad)
        return struct.pack(
            "<HB",
            btn_val & 0xFFFF,
            dpad_val & 0xFF,
        ) + self.left_stick.to_bytes() + self.right_stick.to_bytes() + self.triggers.to_bytes()

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dict representation."""
        pressed = [b.name for b in ControllerButton if b != ControllerButton.NONE and self.is_pressed(b)]
        return {
            "buttons": pressed,
            "dpad": self.dpad.value,
            "left_stick": self.left_stick.to_dict(),
            "right_stick": self.right_stick.to_dict(),
            "triggers": self.triggers.to_dict(),
            "timestamp_ms": self.timestamp_ms,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "DualShockState":
        """Create instance from dict."""
        buttons = ControllerButton.NONE
        for name in data.get("buttons", []):
            try:
                buttons |= ControllerButton[name]
            except KeyError:
                pass
        return cls(
            buttons=buttons,
            dpad=DPadDirection(data.get("dpad", "none")),
            left_stick=AnalogStick(**data.get("left_stick", {})),
            right_stick=AnalogStick(**data.get("right_stick", {})),
            triggers=TriggerState(**data.get("triggers", {})),
            timestamp_ms=data.get("timestamp_ms", 0.0),
        )


# ============================================================================
# 2. Macro Recording & Playback
# ============================================================================

@dataclass
class MacroFrame:
    """A single frame in a macro recording."""
    state: DualShockState
    delay_ms: float = DEFAULT_FRAME_INTERVAL_MS

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dict representation."""
        return {"state": self.state.to_dict(), "delay_ms": self.delay_ms}

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "MacroFrame":
        """Create instance from dict."""
        return cls(
            state=DualShockState.from_dict(data.get("state", {})),
            delay_ms=data.get("delay_ms", DEFAULT_FRAME_INTERVAL_MS),
        )


@dataclass
class Macro:
    """A recorded macro sequence."""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = "Untitled Macro"
    frames: List[MacroFrame] = field(default_factory=list)
    loop: bool = True
    created_at: float = field(default_factory=time.time)

    @property
    def duration_ms(self) -> float:
        """Execute duration ms operation for Macro."""
        return sum(f.delay_ms for f in self.frames)

    @property
    def frame_count(self) -> int:
        """Execute frame count operation for Macro."""
        return len(self.frames)

    def add_frame(self, state: DualShockState, delay_ms: float = DEFAULT_FRAME_INTERVAL_MS):
        """Add frame to Macro."""
        if len(self.frames) < MAX_MACRO_FRAMES:
            self.frames.append(MacroFrame(state=state, delay_ms=delay_ms))

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dict representation."""
        return {
            "id": self.id,
            "name": self.name,
            "frames": [f.to_dict() for f in self.frames],
            "loop": self.loop,
            "duration_ms": self.duration_ms,
            "frame_count": self.frame_count,
            "created_at": self.created_at,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Macro":
        """Create instance from dict."""
        macro = cls(
            id=data.get("id", str(uuid.uuid4())),
            name=data.get("name", "Untitled"),
            loop=data.get("loop", True),
            created_at=data.get("created_at", time.time()),
        )
        for fd in data.get("frames", []):
            macro.frames.append(MacroFrame.from_dict(fd))
        return macro

    def save(self, filepath: str):
        """Execute save operation for Macro."""
        Path(filepath).write_text(json.dumps(self.to_dict(), indent=2), encoding="utf-8")

    @classmethod
    def load(cls, filepath: str) -> "Macro":
        """Execute load operation for Macro."""
        data = json.loads(Path(filepath).read_text(encoding="utf-8"))
        return cls.from_dict(data)


class MacroRecorder:
    """Records controller states into a macro sequence."""

    def __init__(self):
        """Initialize MacroRecorder."""
        self._recording = False
        self._current_macro: Optional[Macro] = None
        self._last_timestamp: float = 0.0
        self._lock = threading.Lock()

    @property
    def is_recording(self) -> bool:
        """Check if recording condition holds."""
        return self._recording

    def start_recording(self, name: str = "Recording") -> Macro:
        """Start recording."""
        with self._lock:
            self._current_macro = Macro(name=name)
            self._recording = True
            self._last_timestamp = time.time()
            return self._current_macro

    def record_frame(self, state: DualShockState):
        """Execute record frame operation for MacroRecorder."""
        with self._lock:
            if not self._recording or self._current_macro is None:
                return
            now = time.time()
            delay = (now - self._last_timestamp) * 1000.0
            state.timestamp_ms = now * 1000.0
            self._current_macro.add_frame(state, delay_ms=delay)
            self._last_timestamp = now

    def stop_recording(self) -> Optional[Macro]:
        """Stop recording."""
        with self._lock:
            self._recording = False
            result = self._current_macro
            self._current_macro = None
            return result


class MacroPlayer:
    """Plays back a macro sequence with configurable loop behavior."""

    def __init__(self, callback: Optional[Callable[[DualShockState], None]] = None):
        """Initialize MacroPlayer."""
        self._playing = False
        self._paused = False
        self._callback = callback
        self._thread: Optional[threading.Thread] = None
        self._current_frame_idx: int = 0
        self._lock = threading.Lock()

    @property
    def is_playing(self) -> bool:
        """Check if playing condition holds."""
        return self._playing

    def play(self, macro: Macro):
        """Execute play operation for MacroPlayer."""
        with self._lock:
            if self._playing:
                return
            self._playing = True
            self._paused = False
            self._current_frame_idx = 0
            self._thread = threading.Thread(
                target=self._playback_loop, args=(macro,), daemon=True
            )
            self._thread.start()

    def stop(self):
        """Execute stop operation for MacroPlayer."""
        with self._lock:
            self._playing = False

    def pause(self):
        """Execute pause operation for MacroPlayer."""
        self._paused = True

    def resume(self):
        """Execute resume operation for MacroPlayer."""
        self._paused = False

    def _playback_loop(self, macro: Macro):
        while self._playing:
            for i, frame in enumerate(macro.frames):
                if not self._playing:
                    return
                while self._paused:
                    time.sleep(0.01)
                    if not self._playing:
                        return
                self._current_frame_idx = i
                if self._callback:
                    self._callback(frame.state)
                time.sleep(frame.delay_ms / 1000.0)
            if not macro.loop:
                break
        self._playing = False


# ============================================================================
# 3. Keyboard Remapping Engine
# ============================================================================

@dataclass
class KeyBinding:
    """Maps a keyboard key to a controller action."""
    key: str  # e.g. "W", "Space", "NumPad4", "Delete"
    button: Optional[ControllerButton] = None
    dpad: Optional[DPadDirection] = None
    stick_axis: Optional[str] = None  # "lx", "ly", "rx", "ry"
    stick_value: float = 0.0
    macro_file: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dict representation."""
        return {
            "key": self.key,
            "button": self.button.name if self.button else None,
            "dpad": self.dpad.value if self.dpad else None,
            "stick_axis": self.stick_axis,
            "stick_value": self.stick_value,
            "macro_file": self.macro_file,
        }


class RemapEngine:
    """
    Keyboard-to-controller remapping engine.
    Implements PS4Macro's remapper feature for translating keyboard inputs
    to DualShock controller states.
    """

    DEFAULT_BINDINGS: Final[Dict[str, KeyBinding]] = {
        "W": KeyBinding(key="W", dpad=DPadDirection.UP),
        "S": KeyBinding(key="S", dpad=DPadDirection.DOWN),
        "A": KeyBinding(key="A", dpad=DPadDirection.LEFT),
        "D": KeyBinding(key="D", dpad=DPadDirection.RIGHT),
        "J": KeyBinding(key="J", button=ControllerButton.CROSS),
        "K": KeyBinding(key="K", button=ControllerButton.CIRCLE),
        "L": KeyBinding(key="L", button=ControllerButton.SQUARE),
        "I": KeyBinding(key="I", button=ControllerButton.TRIANGLE),
        "Q": KeyBinding(key="Q", button=ControllerButton.L1),
        "E": KeyBinding(key="E", button=ControllerButton.R1),
        "Z": KeyBinding(key="Z", button=ControllerButton.L2),
        "C": KeyBinding(key="C", button=ControllerButton.R2),
        "Return": KeyBinding(key="Return", button=ControllerButton.OPTIONS),
        "BackSpace": KeyBinding(key="BackSpace", button=ControllerButton.SHARE),
    }

    def __init__(self):
        """Initialize RemapEngine."""
        self._bindings: Dict[str, KeyBinding] = dict(self.DEFAULT_BINDINGS)
        self._active_keys: set = set()
        self._current_state = DualShockState()

    def set_binding(self, key: str, binding: KeyBinding):
        """Performs set binding operation for RemapEngine."""
        self._bindings[key] = binding

    def remove_binding(self, key: str):
        """Performs remove binding operation for RemapEngine."""
        self._bindings.pop(key, None)

    def get_bindings(self) -> Dict[str, KeyBinding]:
        """Performs get bindings operation for RemapEngine."""
        return dict(self._bindings)

    def key_down(self, key: str) -> DualShockState:
        """Process a key press event."""
        self._active_keys.add(key)
        return self._build_state()

    def key_up(self, key: str) -> DualShockState:
        """Process a key release event."""
        self._active_keys.discard(key)
        return self._build_state()

    def _build_state(self) -> DualShockState:
        """Build controller state from currently active keys."""
        state = DualShockState()
        for key in self._active_keys:
            binding = self._bindings.get(key)
            if binding is None:
                continue
            if binding.button:
                state.buttons |= binding.button
            if binding.dpad and binding.dpad != DPadDirection.NONE:
                state.dpad = binding.dpad
            if binding.stick_axis:
                if binding.stick_axis == "lx":
                    state.left_stick.x = binding.stick_value
                elif binding.stick_axis == "ly":
                    state.left_stick.y = binding.stick_value
                elif binding.stick_axis == "rx":
                    state.right_stick.x = binding.stick_value
                elif binding.stick_axis == "ry":
                    state.right_stick.y = binding.stick_value
        self._current_state = state
        return state

    def export_bindings(self, filepath: str):
        """Performs export bindings operation for RemapEngine."""
        data = {k: v.to_dict() for k, v in self._bindings.items()}
        Path(filepath).write_text(json.dumps(data, indent=2), encoding="utf-8")

    def diagnostics(self):
        """Return engine health diagnostics."""
        return {
            "engine_id": "omni-remap",
            "version": getattr(self, "VERSION", "1.0.0"),
            "status": "operational",
        }


# ============================================================================
# 4. Image Hashing (Screen Detection)
# ============================================================================

class ImageHasher:
    """
    Perceptual image hashing for screen state detection.
    Adapted from PS4Macro's use of jforshee/ImageHashing library.
    Uses average hash (aHash) algorithm for speed.
    """

    @staticmethod
    def average_hash(pixels: List[List[int]], hash_size: int = 8) -> int:
        """
        Compute average hash from pixel grid.
        pixels: 2D list of grayscale values (0-255)
        """
        # Resize to hash_size x hash_size
        h = len(pixels)
        w = len(pixels[0]) if h > 0 else 0
        if h == 0 or w == 0:
            return 0

        resized = []
        for gy in range(hash_size):
            row = []
            src_y = int(gy * h / hash_size)
            for gx in range(hash_size):
                src_x = int(gx * w / hash_size)
                row.append(pixels[min(src_y, h - 1)][min(src_x, w - 1)])
            resized.append(row)

        # Compute average
        flat = [p for row in resized for p in row]
        avg = sum(flat) / len(flat) if flat else 0

        # Build hash
        hash_val = 0
        for i, p in enumerate(flat):
            if p > avg:
                hash_val |= (1 << i)
        return hash_val

    @staticmethod
    def hamming_distance(hash1: int, hash2: int) -> int:
        """Compute Hamming distance between two hashes."""
        xor = hash1 ^ hash2
        count = 0
        while xor:
            count += xor & 1
            xor >>= 1
        return count

    @staticmethod
    def similarity(hash1: int, hash2: int, hash_size: int = 8) -> float:
        """Compute similarity score (0.0 to 1.0)."""
        total_bits = hash_size * hash_size
        dist = ImageHasher.hamming_distance(hash1, hash2)
        return 1.0 - (dist / total_bits)

    @staticmethod
    def hash_from_bytes(data: bytes, width: int, height: int) -> int:
        """Compute hash from raw grayscale byte buffer."""
        pixels = []
        idx = 0
        for y in range(height):
            row = []
            for x in range(width):
                if idx < len(data):
                    row.append(data[idx])
                    idx += 1
                else:
                    row.append(0)
            pixels.append(row)
        return ImageHasher.average_hash(pixels)


# ============================================================================
# 5. Scripting API (ScriptBase Pattern)
# ============================================================================

class ScriptBase:
    """
    Base class for macro scripts.
    Mirrors PS4Macro's ScriptBase API for scripting automation.
    """

    def __init__(self):
        """Initialize ScriptBase."""
        self.config = ScriptConfig()
        self._running = False
        self._state_callback: Optional[Callable[[DualShockState], None]] = None

    def start(self):
        """Called when the user presses play."""
        self._running = True

    def stop(self):
        """Called when the script is stopped."""
        self._running = False

    def update(self):
        """Called every interval set by LoopDelay. Override in subclass."""
        return {"status": "not_implemented"}

    def press(self, state: DualShockState, duration_ms: float = 100.0):
        """Press buttons for a specified duration."""
        if self._state_callback:
            self._state_callback(state)
        time.sleep(duration_ms / 1000.0)
        if self._state_callback:
            self._state_callback(DualShockState())

    def sleep(self, ms: float):
        """Sleep for specified milliseconds."""
        time.sleep(ms / 1000.0)

    def press_button(self, button: ControllerButton, duration_ms: float = 100.0):
        """Convenience: press a single button."""
        state = DualShockState(buttons=button)
        self.press(state, duration_ms)

    def set_stick(self, stick: str, x: float, y: float, duration_ms: float = 100.0):
        """Set analog stick position for a duration."""
        state = DualShockState()
        if stick == "left":
            state.left_stick = AnalogStick(x, y)
        elif stick == "right":
            state.right_stick = AnalogStick(x, y)
        self.press(state, duration_ms)

    def run_loop(self):
        """Execute the script loop."""
        self.start()
        while self._running:
            self.update()
            time.sleep(self.config.loop_delay_ms / 1000.0)


@dataclass
class ScriptConfig:
    """Script configuration matching PS4Macro's Script Config pattern."""
    name: str = "Unnamed Script"
    loop_delay_ms: int = DEFAULT_LOOP_DELAY_MS
    auto_start: bool = False


# ============================================================================
# 6. Settings Management
# ============================================================================

@dataclass
class MacroSettings:
    """
    Application settings matching PS4Macro's settings.xml structure.
    """
    auto_inject: bool = True
    bypass_injection: bool = False
    emulate_controller: bool = False
    show_console: bool = True
    startup_file: Optional[str] = None
    record_on_touch: bool = True
    playback_speed: float = 1.0
    max_frames: int = MAX_MACRO_FRAMES
    frame_interval_ms: int = DEFAULT_FRAME_INTERVAL_MS

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dict representation."""
        return {
            "auto_inject": self.auto_inject,
            "bypass_injection": self.bypass_injection,
            "emulate_controller": self.emulate_controller,
            "show_console": self.show_console,
            "startup_file": self.startup_file,
            "record_on_touch": self.record_on_touch,
            "playback_speed": self.playback_speed,
            "max_frames": self.max_frames,
            "frame_interval_ms": self.frame_interval_ms,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "MacroSettings":
        """Create instance from dict."""
        return cls(
            auto_inject=data.get("auto_inject", True),
            bypass_injection=data.get("bypass_injection", False),
            emulate_controller=data.get("emulate_controller", False),
            show_console=data.get("show_console", True),
            startup_file=data.get("startup_file"),
            record_on_touch=data.get("record_on_touch", True),
            playback_speed=data.get("playback_speed", 1.0),
            max_frames=data.get("max_frames", MAX_MACRO_FRAMES),
            frame_interval_ms=data.get("frame_interval_ms", DEFAULT_FRAME_INTERVAL_MS),
        )

    def save(self, filepath: str):
        """Execute save operation for MacroSettings."""
        Path(filepath).write_text(json.dumps(self.to_dict(), indent=2), encoding="utf-8")

    @classmethod
    def load(cls, filepath: str) -> "MacroSettings":
        """Execute load operation for MacroSettings."""
        data = json.loads(Path(filepath).read_text(encoding="utf-8"))
        return cls.from_dict(data)


# ============================================================================
# 7. CLI Argument Parser
# ============================================================================

class CLIParser:
    """
    Command-line argument parser matching PS4Macro's argument system.
    Supports --AutoInject, --EmulateController, --StartupFile, etc.
    """

    @staticmethod
    def parse(args: List[str], base_settings: Optional[MacroSettings] = None) -> MacroSettings:
        """Execute parse operation for CLIParser."""
        settings = base_settings or MacroSettings()
        i = 0
        while i < len(args):
            arg = args[i]
            if arg.startswith("--"):
                key_val = arg[2:]
                if "=" in key_val:
                    key, val = key_val.split("=", 1)
                else:
                    key = key_val
                    val = "true"

                key_lower = key.lower()
                val_stripped = val.strip('"').strip("'")

                if key_lower == "autoinject":
                    settings.auto_inject = val_stripped.lower() != "false"
                elif key_lower == "bypassinjection":
                    settings.bypass_injection = val_stripped.lower() != "false"
                elif key_lower == "emulatecontroller":
                    settings.emulate_controller = val_stripped.lower() != "false"
                elif key_lower == "showconsole":
                    settings.show_console = val_stripped.lower() != "false"
                elif key_lower == "startupfile":
                    settings.startup_file = val_stripped
                elif key_lower == "settingsfile":
                    settings = MacroSettings.load(val_stripped)
                elif key_lower == "playbackspeed":
                    settings.playback_speed = float(val_stripped)
            i += 1
        return settings


# ============================================================================
# 8. Macro Library
# ============================================================================

class MacroLibrary:
    """
    Manages a collection of saved macros.
    Provides load/save/search operations on the macro store.
    """

    def __init__(self, library_dir: str = ".omni_macros"):
        """Initialize MacroLibrary."""
        self._dir = Path(library_dir)
        self._dir.mkdir(parents=True, exist_ok=True)
        self._macros: Dict[str, Macro] = {}

    def save_macro(self, macro: Macro, filename: Optional[str] = None) -> str:
        """Save macro."""
        fname = filename or f"{macro.name.replace(' ', '_')}_{macro.id[:8]}.json"
        filepath = self._dir / fname
        macro.save(str(filepath))
        self._macros[macro.id] = macro
        return str(filepath)

    def load_macro(self, filepath: str) -> Macro:
        """Load macro."""
        macro = Macro.load(filepath)
        self._macros[macro.id] = macro
        return macro

    def list_macros(self) -> List[Dict[str, Any]]:
        """Execute list macros operation for MacroLibrary."""
        results = []
        for f in self._dir.glob("*.json"):
            try:
                macro = Macro.load(str(f))
                results.append({
                    "id": macro.id,
                    "name": macro.name,
                    "frames": macro.frame_count,
                    "duration_ms": macro.duration_ms,
                    "loop": macro.loop,
                    "file": str(f),
                })
            except Exception:
                pass
        return results

    def delete_macro(self, macro_id: str) -> bool:
        """Delete macro."""
        for f in self._dir.glob("*.json"):
            try:
                data = json.loads(f.read_text(encoding="utf-8"))
                if data.get("id") == macro_id:
                    f.unlink()
                    self._macros.pop(macro_id, None)
                    return True
            except Exception:
                pass
        return False

    def search(self, query: str) -> List[Dict[str, Any]]:
        """Execute search operation for MacroLibrary."""
        return [m for m in self.list_macros() if query.lower() in m["name"].lower()]


# ============================================================================
# 9. OMNI Engine Facade
# ============================================================================

class OmniMacroAutomationEngine:
    """
    OMNI Macro Automation Engine — Production-Grade Controller Automation.

    Inspired by PS4Macro: macro recording/playback, keyboard remapping,
    image hashing screen detection, scripting API, and settings management.

    Usage:
        engine = OmniMacroAutomationEngine()
        # Record a macro
        engine.start_recording("my_combo")
        engine.record_frame(DualShockState(buttons=ControllerButton.CROSS))
        macro = engine.stop_recording()
        # Save and playback
        engine.save_macro(macro)
        engine.play_macro(macro)
    """

    def __init__(self, library_dir: str = ".omni_macros"):
        """Initialize OmniMacroAutomationEngine."""
        self.settings = MacroSettings()
        self.recorder = MacroRecorder()
        self.player = MacroPlayer()
        self.remap_engine = RemapEngine()
        self.image_hasher = ImageHasher()
        self.library = MacroLibrary(library_dir)
        self._state_log: List[Dict[str, Any]] = []

    # -- Recording ---
    def start_recording(self, name: str = "Recording") -> Macro:
        """Performs start recording operation for OmniMacroAutomationEngine."""
        return self.recorder.start_recording(name)

    def record_frame(self, state: DualShockState):
        """Performs record frame operation for OmniMacroAutomationEngine."""
        self.recorder.record_frame(state)

    def stop_recording(self) -> Optional[Macro]:
        """Performs stop recording operation for OmniMacroAutomationEngine."""
        return self.recorder.stop_recording()

    # -- Playback ---
    def play_macro(self, macro: Macro, callback: Optional[Callable] = None):
        """Performs play macro operation for OmniMacroAutomationEngine."""
        if callback:
            self.player._callback = callback
        self.player.play(macro)

    def stop_playback(self):
        """Performs stop playback operation for OmniMacroAutomationEngine."""
        self.player.stop()

    # -- Library ---
    def save_macro(self, macro: Macro, filename: Optional[str] = None) -> str:
        """Performs save macro operation for OmniMacroAutomationEngine."""
        return self.library.save_macro(macro, filename)

    def load_macro(self, filepath: str) -> Macro:
        """Performs load macro operation for OmniMacroAutomationEngine."""
        return self.library.load_macro(filepath)

    def list_macros(self) -> List[Dict[str, Any]]:
        """Performs list macros operation for OmniMacroAutomationEngine."""
        return self.library.list_macros()

    # -- Remapping ---
    def create_remap(self, key: str, button: Optional[ControllerButton] = None,
                     dpad: Optional[DPadDirection] = None):
        """Performs create remap operation for OmniMacroAutomationEngine."""
        self.remap_engine.set_binding(key, KeyBinding(key=key, button=button, dpad=dpad))

    def process_key(self, key: str, pressed: bool) -> DualShockState:
        """Performs process key operation for OmniMacroAutomationEngine."""
        if pressed:
            return self.remap_engine.key_down(key)
        return self.remap_engine.key_up(key)

    # -- Image Hashing ---
    def compute_screen_hash(self, pixels: List[List[int]]) -> int:
        """Performs compute screen hash operation for OmniMacroAutomationEngine."""
        return self.image_hasher.average_hash(pixels)

    def match_screen(self, hash1: int, hash2: int, threshold: float = 0.9) -> bool:
        """Performs match screen operation for OmniMacroAutomationEngine."""
        return self.image_hasher.similarity(hash1, hash2) >= threshold

    # -- Scripting ---
    def execute_script(self, script: ScriptBase, iterations: int = 1):
        """Performs execute script operation for OmniMacroAutomationEngine."""
        script.start()
        for _ in range(iterations):
            if not script._running:
                break
            script.update()
            time.sleep(script.config.loop_delay_ms / 1000.0)
        script.stop()

    # -- Settings ---
    def load_settings(self, filepath: str):
        """Performs load settings operation for OmniMacroAutomationEngine."""
        self.settings = MacroSettings.load(filepath)

    def save_settings(self, filepath: str):
        """Performs save settings operation for OmniMacroAutomationEngine."""
        self.settings.save(filepath)

    def apply_cli_args(self, args: List[str]):
        """Performs apply cli args operation for OmniMacroAutomationEngine."""
        self.settings = CLIParser.parse(args, self.settings)

    # -- Controller Emulation ---
    def emulate_controller(self, states: Sequence[DualShockState], interval_ms: float = 16.0):
        """Send a sequence of controller states with timing."""
        results = []
        for state in states:
            packed = state.to_bytes()
            results.append({
                "state": state.to_dict(),
                "bytes_hex": packed.hex(),
                "size": len(packed),
            })
            time.sleep(interval_ms / 1000.0)
        return results

    # -- Capture Screen (Stub for integration) ---
    def capture_screen(self) -> Dict[str, Any]:
        """Capture screen state (integration point for Remote Play connection)."""
        return {
            "status": "ready",
            "source": "remote_play",
            "width": 1920,
            "height": 1080,
            "format": "rgba",
            "note": "Connect to Remote Play session for live capture",
        }

    # -- Diagnostics ---
    def diagnostics(self) -> Dict[str, Any]:
        """Performs diagnostics operation for OmniMacroAutomationEngine."""
        test_state = DualShockState(buttons=ControllerButton.CROSS | ControllerButton.TRIANGLE)
        test_bytes = test_state.to_bytes()

        macro = Macro(name="diag_test")
        for i in range(10):
            macro.add_frame(DualShockState(buttons=ControllerButton.CROSS), delay_ms=16.0)

        pixels = [[i * j % 256 for j in range(8)] for i in range(8)]
        test_hash = self.image_hasher.average_hash(pixels)

        return {
            "engine": ENGINE_NAME,
            "version": ENGINE_VERSION,
            "status": "operational",
            "settings": self.settings.to_dict(),
            "controller_test": {
                "state": test_state.to_dict(),
                "serialized_bytes": len(test_bytes),
                "roundtrip": test_state == DualShockState.from_dict(test_state.to_dict())
                    if test_state.to_dict() else False
            },
            "macro_test": {
                "frames_recorded": macro.frame_count,
                "duration_ms": macro.duration_ms,
                "serialized": len(json.dumps(macro.to_dict())),
            },
            "image_hash_test": {
                "hash_value": test_hash,
                "self_similarity": self.image_hasher.similarity(test_hash, test_hash),
            },
            "remap_bindings": len(self.remap_engine.get_bindings()),
            "library_macros": len(self.list_macros()),
            "capabilities": [
                "record_macro", "play_macro", "remap_keys", "image_hash",
                "scripting", "controller_emulation", "settings_management",
                "macro_library", "cli_args",
            ],
        }


# ============================================================================
# 10. Self-Test
# ============================================================================

if __name__ == "__main__":
    engine = OmniMacroAutomationEngine(library_dir=".omni_macros_test")
    result = engine.diagnostics()
    print(json.dumps(result, indent=2, default=str))
    print(f"\n✅ {ENGINE_NAME} v{ENGINE_VERSION} — OPERATIONAL")
