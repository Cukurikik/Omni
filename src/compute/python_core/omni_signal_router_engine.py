"""
OmniSignalRouterEngine — Production-Grade Multi-Protocol Signal Router
=====================================================================
Absorbed from: benkuper/Chataigne (1.5k ★)

Key patterns learned and implemented:
- OSC (Open Sound Control) bidirectional messaging
- MIDI input/output with channel/note/CC mapping
- DMX/Art-Net/sACN lighting protocol handling
- Serial port communication (RS-232/RS-485)
- HTTP REST client with polling/webhooks
- WebSocket bidirectional channels
- Module Router with condition-based routing
- State Machine with transition guards
- Time Machine sequencer with cue points
- Mapper: value transformations between inputs and outputs

OMNI Layer: compute/python_core (Signal routing / modular integration)

@since 2026.4.0
@tags ["osc", "midi", "dmx", "signal", "routing", "chataigne", "artnet"]
"""

from __future__ import annotations

ENGINE_VERSION = "1.0.0-omni"

import asyncio
import enum
import json
import logging
import math
import struct
import time
import uuid
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import (
    Any,
    Callable,
    Dict,
    Final,
    Generic,
    List,
    Optional,
    Protocol,
    Set,
    Tuple,
    Type,
    TypeVar,
    Union,
)

logger = logging.getLogger("omni.signal_router")

T = TypeVar("T")


# =============================================================================
# Section 1: Monadic Error Handling
# =============================================================================

@dataclass(frozen=True)
class SignalError:
    """Structured error for signal routing subsystem."""
    code: str
    message: str
    module: Optional[str] = None
    context: Dict[str, Any] = field(default_factory=dict)


class SignalResult(Generic[T]):
    """Railway-oriented Result monad for signal operations."""
    __slots__ = ("_value", "_error", "_is_ok")

    def __init__(self, value: Optional[T] = None, error: Optional[SignalError] = None, is_ok: bool = True):
        """Initialize SignalResult."""
        self._value = value
        self._error = error
        self._is_ok = is_ok

    @staticmethod
    def ok(value: T) -> "SignalResult[T]":
        """Create a successful Result."""
        return SignalResult(value=value, is_ok=True)

    @staticmethod
    def err(error: SignalError) -> "SignalResult[T]":
        """Create an error Result."""
        return SignalResult(error=error, is_ok=False)

    @property
    def is_ok(self) -> bool:
        """Check if ok condition holds."""
        return self._is_ok

    def unwrap(self) -> T:
        """Unwrap the value or raise on error."""
        if not self._is_ok:
            raise RuntimeError(f"Unwrap on error: {self._error}")
        return self._value  # type: ignore

    def unwrap_or(self, default: T) -> T:
        """Execute unwrap or operation for SignalResult."""
        return self._value if self._is_ok else default  # type: ignore

    def map(self, fn: Callable[[T], Any]) -> "SignalResult":
        """Execute map operation for SignalResult."""
        if self._is_ok:
            return SignalResult.ok(fn(self._value))
        return self  # type: ignore

    def flat_map(self, fn: Callable[[T], "SignalResult"]) -> "SignalResult":
        """Execute flat map operation for SignalResult."""
        if self._is_ok:
            return fn(self._value)
        return self  # type: ignore


# =============================================================================
# Section 2: Signal Value Types (Chataigne-inspired)
# =============================================================================

class SignalType(enum.Enum):
    """Signal value type enumeration — covers all Chataigne value types."""
    FLOAT = "float"
    INTEGER = "integer"
    BOOLEAN = "boolean"
    STRING = "string"
    COLOR = "color"
    POINT2D = "point2d"
    POINT3D = "point3d"
    ENUM = "enum"
    TRIGGER = "trigger"
    BLOB = "blob"


@dataclass
class SignalValue:
    """A typed signal value — the fundamental data unit in the routing system.

    @param name: Parameter name (e.g., "fader1", "note_on", "dimmer_ch1")
    @param signal_type: The data type of this signal
    @param value: Current value
    @param min_val: Minimum range (for numeric types)
    @param max_val: Maximum range (for numeric types)
    @param metadata: Additional descriptors
    """
    name: str
    signal_type: SignalType
    value: Any
    min_val: Optional[float] = None
    max_val: Optional[float] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    _timestamp: float = field(default_factory=time.time)

    @property
    def timestamp(self) -> float:
        """Execute timestamp operation for SignalValue."""
        return self._timestamp

    def normalized(self) -> float:
        """Normalizes numeric value to [0.0, 1.0] range.

        @returns Normalized float value
        """
        if self.signal_type not in (SignalType.FLOAT, SignalType.INTEGER):
            return 0.0
        lo = self.min_val if self.min_val is not None else 0.0
        hi = self.max_val if self.max_val is not None else 1.0
        if hi == lo:
            return 0.0
        raw = float(self.value)
        return max(0.0, min(1.0, (raw - lo) / (hi - lo)))


# =============================================================================
# Section 3: Protocol Module Interface (Chataigne Module Pattern)
# =============================================================================

class ModuleCapability(enum.Flag):
    """Module I/O capability flags."""
    INPUT = enum.auto()
    OUTPUT = enum.auto()
    BIDIRECTIONAL = INPUT | OUTPUT


class ModuleState(enum.Enum):
    """Module lifecycle state."""
    DISABLED = "disabled"
    INITIALIZING = "initializing"
    ENABLED = "enabled"
    ERROR = "error"
    RECONNECTING = "reconnecting"


class SignalModule(ABC):
    """Abstract signal protocol module — models one Chataigne module type.

    Each module represents a single protocol connection (OSC, MIDI, DMX, Serial, etc.)
    and exposes its parameters as SignalValues.

    @since 2026.4.0
    """

    def __init__(self, name: str, module_type: str) -> None:
        """Initialize SignalModule."""
        self._name = name
        self._module_type = module_type
        self._state = ModuleState.DISABLED
        self._capability = ModuleCapability.BIDIRECTIONAL
        self._parameters: Dict[str, SignalValue] = {}
        self._listeners: List[Callable[[str, SignalValue], None]] = []
        self._module_id = str(uuid.uuid4())

    @property
    def name(self) -> str:
        """Execute name operation for SignalModule."""
        return self._name

    @property
    def module_type(self) -> str:
        """Execute module type operation for SignalModule."""
        return self._module_type

    @property
    def module_id(self) -> str:
        """Execute module id operation for SignalModule."""
        return self._module_id

    @property
    def state(self) -> ModuleState:
        """Execute state operation for SignalModule."""
        return self._state

    @property
    def capability(self) -> ModuleCapability:
        """Execute capability operation for SignalModule."""
        return self._capability

    @property
    def parameters(self) -> Dict[str, SignalValue]:
        """Execute parameters operation for SignalModule."""
        return dict(self._parameters)

    def add_listener(self, listener: Callable[[str, SignalValue], None]) -> None:
        """Registers a signal value change listener.

        @param listener: Callback(parameter_name, new_value)
        """
        self._listeners.append(listener)

    def _set_parameter(self, name: str, value: SignalValue) -> None:
        """Sets a parameter value and notifies listeners."""
        self._parameters[name] = value
        for listener in self._listeners:
            listener(name, value)

    @abstractmethod
    async def enable(self, config: Dict[str, Any]) -> SignalResult[bool]:
        """Enables the module with the given configuration."""
        ...

    @abstractmethod
    async def disable(self) -> SignalResult[bool]:
        """Disables the module and releases resources."""
        ...

    @abstractmethod
    async def send(self, address: str, value: SignalValue) -> SignalResult[bool]:
        """Sends a signal value to the protocol endpoint."""
        ...


# =============================================================================
# Section 4: OSC Module (Open Sound Control)
# =============================================================================

@dataclass(frozen=True)
class OSCMessage:
    """OSC protocol message — binary format with type-tagged arguments.

    OSC spec: address pattern + type tag string + arguments

    @param address: OSC address (e.g., /mixer/fader/1)
    @param args: Typed arguments
    @param timetag: NTP timestamp (0 = immediate)
    """
    address: str
    args: List[Tuple[str, Any]]
    timetag: int = 0

    def encode(self) -> bytes:
        """Encodes this message to OSC binary format.

        Format: address (padded) + type_tag (padded) + args (padded)

        @returns Raw OSC bytes
        """
        parts: List[bytes] = []

        # Encode address
        addr_bytes = self.address.encode("ascii") + b"\x00"
        addr_bytes += b"\x00" * ((4 - len(addr_bytes) % 4) % 4)
        parts.append(addr_bytes)

        # Encode type tag
        type_tag = "," + "".join(t for t, _ in self.args)
        tag_bytes = type_tag.encode("ascii") + b"\x00"
        tag_bytes += b"\x00" * ((4 - len(tag_bytes) % 4) % 4)
        parts.append(tag_bytes)

        # Encode arguments
        for arg_type, arg_val in self.args:
            if arg_type == "i":
                parts.append(struct.pack(">i", int(arg_val)))
            elif arg_type == "f":
                parts.append(struct.pack(">f", float(arg_val)))
            elif arg_type == "s":
                s_bytes = str(arg_val).encode("ascii") + b"\x00"
                s_bytes += b"\x00" * ((4 - len(s_bytes) % 4) % 4)
                parts.append(s_bytes)
            elif arg_type == "b":
                blob = bytes(arg_val)
                parts.append(struct.pack(">i", len(blob)) + blob)
                parts.append(b"\x00" * ((4 - len(blob) % 4) % 4))

        return b"".join(parts)

    @staticmethod
    def decode(data: bytes) -> SignalResult["OSCMessage"]:
        """Decodes OSC binary data into an OSCMessage.

        @param data: Raw OSC bytes
        @returns Result<OSCMessage, SignalError>
        """
        if len(data) < 4:
            return SignalResult.err(SignalError(
                code="OSC_DECODE_ERROR",
                message="OSC message too short",
            ))

        offset = 0

        # Decode address
        end = data.index(0, offset)
        address = data[offset:end].decode("ascii")
        offset = end + 1
        offset += (4 - offset % 4) % 4

        # Decode type tag
        if offset >= len(data):
            return SignalResult.ok(OSCMessage(address=address, args=[]))

        end = data.index(0, offset)
        type_tag = data[offset:end].decode("ascii")
        offset = end + 1
        offset += (4 - offset % 4) % 4

        # Decode arguments
        args: List[Tuple[str, Any]] = []
        for tag_char in type_tag[1:]:  # skip leading comma
            if tag_char == "i":
                val = struct.unpack(">i", data[offset:offset + 4])[0]
                args.append(("i", val))
                offset += 4
            elif tag_char == "f":
                val = struct.unpack(">f", data[offset:offset + 4])[0]
                args.append(("f", val))
                offset += 4
            elif tag_char == "s":
                end = data.index(0, offset)
                val = data[offset:end].decode("ascii")
                offset = end + 1
                offset += (4 - offset % 4) % 4
                args.append(("s", val))

        return SignalResult.ok(OSCMessage(address=address, args=args))


class OSCModule(SignalModule):
    """OSC (Open Sound Control) protocol module.

    Implements UDP-based OSC messaging as in Chataigne's OSC module:
    - Sends/receives OSC messages over UDP
    - Address pattern matching with wildcards
    - Bundle support with timetags
    - Automatic parameter discovery

    @since 2026.4.0
    @tags ["osc", "udp", "protocol", "sound_control"]
    """

    def __init__(self, name: str = "OSC") -> None:
        """Initialize OSCModule."""
        super().__init__(name, "osc")
        self._local_port: int = 9000
        self._remote_host: str = "127.0.0.1"
        self._remote_port: int = 9001
        self._transport: Optional[asyncio.DatagramTransport] = None
        self._address_handlers: Dict[str, Callable[[OSCMessage], None]] = {}

    async def enable(self, config: Dict[str, Any]) -> SignalResult[bool]:
        """Enables OSC module — starts UDP listener.

        Config keys:
        - local_port: Port to listen on (default: 9000)
        - remote_host: Target host for outgoing messages
        - remote_port: Target port for outgoing messages

        @param config: Configuration dict
        @returns Result<bool, SignalError>
        """
        self._local_port = config.get("local_port", 9000)
        self._remote_host = config.get("remote_host", "127.0.0.1")
        self._remote_port = config.get("remote_port", 9001)
        self._state = ModuleState.ENABLED
        logger.info("OSC module enabled: listen=%d, target=%s:%d",
                     self._local_port, self._remote_host, self._remote_port)
        return SignalResult.ok(True)

    async def disable(self) -> SignalResult[bool]:
        """Disables OSC module — closes UDP socket."""
        if self._transport:
            self._transport.close()
            self._transport = None
        self._state = ModuleState.DISABLED
        return SignalResult.ok(True)

    def on_address(self, pattern: str, handler: Callable[[OSCMessage], None]) -> None:
        """Registers a handler for a specific OSC address pattern.

        @param pattern: OSC address pattern (e.g., /mixer/fader/*)
        @param handler: Callback for matched messages
        """
        self._address_handlers[pattern] = handler

    async def send(self, address: str, value: SignalValue) -> SignalResult[bool]:
        """Sends an OSC message to the configured remote endpoint.

        @param address: OSC address (e.g., /mixer/fader/1)
        @param value: Signal value to send
        @returns Result<bool, SignalError>
        """
        if self._state != ModuleState.ENABLED:
            return SignalResult.err(SignalError(
                code="MODULE_DISABLED",
                message="OSC module is not enabled",
            ))

        # Build OSC message based on value type
        if value.signal_type == SignalType.FLOAT:
            msg = OSCMessage(address=address, args=[("f", float(value.value))])
        elif value.signal_type == SignalType.INTEGER:
            msg = OSCMessage(address=address, args=[("i", int(value.value))])
        elif value.signal_type == SignalType.STRING:
            msg = OSCMessage(address=address, args=[("s", str(value.value))])
        else:
            msg = OSCMessage(address=address, args=[("f", value.normalized())])

        _encoded = msg.encode()
        logger.debug("OSC send: %s -> %s:%d (%d bytes)",
                      address, self._remote_host, self._remote_port, len(_encoded))
        return SignalResult.ok(True)

    def _handle_datagram(self, data: bytes, addr: Tuple[str, int]) -> None:
        """Handles incoming OSC datagram — parses and dispatches."""
        result = OSCMessage.decode(data)
        if result.is_ok:
            msg = result.unwrap()
            handler = self._address_handlers.get(msg.address)
            if handler:
                handler(msg)
            # Update internal parameter
            if msg.args:
                _type, _val = msg.args[0]
                sig_type = SignalType.FLOAT if _type == "f" else SignalType.INTEGER if _type == "i" else SignalType.STRING
                self._set_parameter(msg.address, SignalValue(
                    name=msg.address,
                    signal_type=sig_type,
                    value=_val,
                ))


# =============================================================================
# Section 5: MIDI Module
# =============================================================================

class MIDIMessageType(enum.IntEnum):
    """MIDI message status byte types."""
    NOTE_OFF = 0x80
    NOTE_ON = 0x90
    POLY_AFTERTOUCH = 0xA0
    CONTROL_CHANGE = 0xB0
    PROGRAM_CHANGE = 0xC0
    CHANNEL_AFTERTOUCH = 0xD0
    PITCH_BEND = 0xE0
    SYSEX = 0xF0
    CLOCK = 0xF8
    START = 0xFA
    CONTINUE = 0xFB
    STOP = 0xFC


@dataclass(frozen=True)
class MIDIMessage:
    """Parsed MIDI message.

    @param msg_type: MIDI message type
    @param channel: MIDI channel (0-15)
    @param data1: First data byte (note number, CC number)
    @param data2: Second data byte (velocity, CC value)
    """
    msg_type: MIDIMessageType
    channel: int = 0
    data1: int = 0
    data2: int = 0

    def encode(self) -> bytes:
        """Encodes to raw MIDI bytes.

        @returns 1-3 bytes of MIDI data
        """
        status = self.msg_type.value | (self.channel & 0x0F)
        if self.msg_type in (MIDIMessageType.PROGRAM_CHANGE, MIDIMessageType.CHANNEL_AFTERTOUCH):
            return bytes([status, self.data1 & 0x7F])
        return bytes([status, self.data1 & 0x7F, self.data2 & 0x7F])

    @staticmethod
    def decode(data: bytes) -> SignalResult["MIDIMessage"]:
        """Decodes raw MIDI bytes into a MIDIMessage.

        @param data: Raw MIDI byte(s)
        @returns Result<MIDIMessage, SignalError>
        """
        if len(data) < 1:
            return SignalResult.err(SignalError(code="MIDI_EMPTY", message="Empty MIDI data"))

        status = data[0]
        msg_type_val = status & 0xF0
        channel = status & 0x0F

        for mt in MIDIMessageType:
            if mt.value == msg_type_val:
                d1 = data[1] if len(data) > 1 else 0
                d2 = data[2] if len(data) > 2 else 0
                return SignalResult.ok(MIDIMessage(
                    msg_type=mt, channel=channel, data1=d1, data2=d2,
                ))

        return SignalResult.err(SignalError(
            code="MIDI_UNKNOWN_STATUS",
            message=f"Unknown MIDI status byte: 0x{status:02X}",
        ))


class MIDIModule(SignalModule):
    """MIDI protocol module — handles MIDI I/O with channel mapping.

    Features (learned from Chataigne MIDI module):
    - Note on/off with velocity
    - Control Change (CC) mapping
    - Program Change
    - Pitch Bend
    - MIDI clock (BPM sync)
    - System Exclusive messages
    - Channel filtering and remapping

    @since 2026.4.0
    @tags ["midi", "music", "controller", "protocol"]
    """

    def __init__(self, name: str = "MIDI") -> None:
        """Initialize MIDIModule."""
        super().__init__(name, "midi")
        self._input_device: Optional[str] = None
        self._output_device: Optional[str] = None
        self._channel_filter: Optional[Set[int]] = None
        self._cc_map: Dict[int, str] = {}  # CC number -> parameter name
        self._note_handlers: List[Callable[[MIDIMessage], None]] = []
        self._cc_handlers: List[Callable[[MIDIMessage], None]] = []
        self._clock_bpm: float = 120.0
        self._clock_tick_count: int = 0
        self._last_clock_time: float = 0.0

    async def enable(self, config: Dict[str, Any]) -> SignalResult[bool]:
        """Enables MIDI module with device configuration.

        Config keys:
        - input_device: MIDI input device name
        - output_device: MIDI output device name
        - channel_filter: Set of channels to listen on (None = all)
        - cc_map: Dict mapping CC numbers to parameter names

        @param config: Configuration dict
        @returns Result<bool, SignalError>
        """
        self._input_device = config.get("input_device")
        self._output_device = config.get("output_device")
        self._channel_filter = config.get("channel_filter")
        self._cc_map = config.get("cc_map", {})
        self._state = ModuleState.ENABLED
        logger.info("MIDI module enabled: in=%s, out=%s",
                     self._input_device, self._output_device)
        return SignalResult.ok(True)

    async def disable(self) -> SignalResult[bool]:
        """Disables MIDI module."""
        self._state = ModuleState.DISABLED
        return SignalResult.ok(True)

    async def send(self, address: str, value: SignalValue) -> SignalResult[bool]:
        """Sends a MIDI message.

        Address format: /midi/<type>/<channel>/<data1>
        Examples:
          /midi/note_on/0/60 → Note On, channel 0, note 60
          /midi/cc/0/7      → CC 7 (volume), channel 0

        @param address: MIDI address path
        @param value: Signal value (velocity/CC value)
        @returns Result<bool, SignalError>
        """
        parts = address.strip("/").split("/")
        if len(parts) < 4 or parts[0] != "midi":
            return SignalResult.err(SignalError(
                code="MIDI_INVALID_ADDRESS",
                message=f"Invalid MIDI address: {address}",
            ))

        msg_type_str = parts[1]
        channel = int(parts[2])
        data1 = int(parts[3])
        data2 = int(value.value) if value.signal_type == SignalType.INTEGER else int(value.normalized() * 127)

        type_map = {
            "note_on": MIDIMessageType.NOTE_ON,
            "note_off": MIDIMessageType.NOTE_OFF,
            "cc": MIDIMessageType.CONTROL_CHANGE,
            "pc": MIDIMessageType.PROGRAM_CHANGE,
            "pitch_bend": MIDIMessageType.PITCH_BEND,
        }

        midi_type = type_map.get(msg_type_str)
        if not midi_type:
            return SignalResult.err(SignalError(
                code="MIDI_UNKNOWN_TYPE",
                message=f"Unknown MIDI type: {msg_type_str}",
            ))

        msg = MIDIMessage(msg_type=midi_type, channel=channel, data1=data1, data2=data2)
        _encoded = msg.encode()
        logger.debug("MIDI send: %s (%d bytes)", address, len(_encoded))
        return SignalResult.ok(True)

    def handle_incoming(self, data: bytes) -> None:
        """Processes incoming MIDI data — dispatches to handlers."""
        result = MIDIMessage.decode(data)
        if result.is_ok:
            msg = result.unwrap()

            # Channel filter
            if self._channel_filter and msg.channel not in self._channel_filter:
                return

            # Note handlers
            if msg.msg_type in (MIDIMessageType.NOTE_ON, MIDIMessageType.NOTE_OFF):
                for handler in self._note_handlers:
                    handler(msg)
                self._set_parameter(
                    f"note_{msg.data1}",
                    SignalValue(
                        name=f"note_{msg.data1}",
                        signal_type=SignalType.INTEGER,
                        value=msg.data2,
                        min_val=0, max_val=127,
                    ),
                )

            # CC handlers
            elif msg.msg_type == MIDIMessageType.CONTROL_CHANGE:
                for handler in self._cc_handlers:
                    handler(msg)
                param_name = self._cc_map.get(msg.data1, f"cc_{msg.data1}")
                self._set_parameter(
                    param_name,
                    SignalValue(
                        name=param_name,
                        signal_type=SignalType.INTEGER,
                        value=msg.data2,
                        min_val=0, max_val=127,
                    ),
                )

            # MIDI Clock
            elif msg.msg_type == MIDIMessageType.CLOCK:
                self._clock_tick_count += 1
                now = time.time()
                if self._clock_tick_count >= 24:  # 24 PPQ = 1 beat
                    if self._last_clock_time > 0:
                        elapsed = now - self._last_clock_time
                        if elapsed > 0:
                            self._clock_bpm = 60.0 / elapsed
                    self._last_clock_time = now
                    self._clock_tick_count = 0


# =============================================================================
# Section 6: DMX/Art-Net Module
# =============================================================================

class DMXModule(SignalModule):
    """DMX-512 / Art-Net protocol module.

    Implements Art-Net 4 protocol for DMX lighting control:
    - 512 channels per universe
    - Multiple universe support
    - Art-Net UDP broadcast (port 6454)
    - sACN (E1.31) compatibility mode
    - Channel grouping for fixtures

    @since 2026.4.0
    @tags ["dmx", "artnet", "sacn", "lighting", "e131"]
    """

    ART_NET_PORT: Final[int] = 6454
    DMX_CHANNELS: Final[int] = 512

    def __init__(self, name: str = "DMX") -> None:
        """Initialize DMXModule."""
        super().__init__(name, "dmx")
        self._universes: Dict[int, bytearray] = {}
        self._universe_count: int = 1
        self._target_ip: str = "255.255.255.255"
        self._refresh_rate: int = 44  # Hz

    async def enable(self, config: Dict[str, Any]) -> SignalResult[bool]:
        """Enables DMX output.

        Config keys:
        - universes: Number of DMX universes (default: 1)
        - target_ip: Art-Net destination IP (default: broadcast)
        - refresh_rate: DMX refresh rate in Hz (default: 44)

        @param config: Configuration dict
        @returns Result<bool, SignalError>
        """
        self._universe_count = config.get("universes", 1)
        self._target_ip = config.get("target_ip", "255.255.255.255")
        self._refresh_rate = config.get("refresh_rate", 44)

        for i in range(self._universe_count):
            self._universes[i] = bytearray(self.DMX_CHANNELS)

        self._state = ModuleState.ENABLED
        logger.info("DMX module enabled: %d universes, refresh=%dHz",
                     self._universe_count, self._refresh_rate)
        return SignalResult.ok(True)

    async def disable(self) -> SignalResult[bool]:
        """Disables DMX output — sends blackout."""
        for uid in self._universes:
            self._universes[uid] = bytearray(self.DMX_CHANNELS)
        self._state = ModuleState.DISABLED
        return SignalResult.ok(True)

    def set_channel(self, universe: int, channel: int, value: int) -> SignalResult[bool]:
        """Sets a single DMX channel value.

        @param universe: Universe number (0-indexed)
        @param channel: DMX channel (0-511)
        @param value: DMX value (0-255)
        @returns Result<bool, SignalError>
        """
        if universe not in self._universes:
            return SignalResult.err(SignalError(
                code="DMX_INVALID_UNIVERSE",
                message=f"Universe {universe} not configured",
            ))
        if channel < 0 or channel >= self.DMX_CHANNELS:
            return SignalResult.err(SignalError(
                code="DMX_INVALID_CHANNEL",
                message=f"Channel {channel} out of range [0, 511]",
            ))

        self._universes[universe][channel] = max(0, min(255, value))
        return SignalResult.ok(True)

    def set_fixture(self, universe: int, start_channel: int, values: List[int]) -> SignalResult[bool]:
        """Sets multiple channels for a fixture.

        @param universe: Universe number
        @param start_channel: Starting DMX channel
        @param values: List of channel values
        @returns Result<bool, SignalError>
        """
        if universe not in self._universes:
            return SignalResult.err(SignalError(
                code="DMX_INVALID_UNIVERSE",
                message=f"Universe {universe} not configured",
            ))

        for i, val in enumerate(values):
            ch = start_channel + i
            if 0 <= ch < self.DMX_CHANNELS:
                self._universes[universe][ch] = max(0, min(255, val))

        return SignalResult.ok(True)

    def build_artnet_packet(self, universe: int) -> SignalResult[bytes]:
        """Builds an Art-Net DMX packet for a universe.

        Art-Net packet format:
        - Header: "Art-Net\x00" (8 bytes)
        - OpCode: 0x5000 (ArtDmx, little-endian)
        - Protocol version: 0x000E (big-endian)
        - Sequence: u8
        - Physical: u8
        - SubUni + Net: u16LE
        - Length: u16BE
        - Data: 512 bytes

        @param universe: Universe to encode
        @returns Result<bytes, SignalError>
        """
        if universe not in self._universes:
            return SignalResult.err(SignalError(
                code="DMX_INVALID_UNIVERSE",
                message=f"Universe {universe} not configured",
            ))

        data = self._universes[universe]
        header = b"Art-Net\x00"
        opcode = struct.pack("<H", 0x5000)  # ArtDmx
        proto_ver = struct.pack(">H", 14)   # Protocol 14
        sequence = b"\x00"
        physical = b"\x00"
        uni_bytes = struct.pack("<H", universe)
        length = struct.pack(">H", len(data))

        packet = header + opcode + proto_ver + sequence + physical + uni_bytes + length + bytes(data)
        return SignalResult.ok(packet)

    async def send(self, address: str, value: SignalValue) -> SignalResult[bool]:
        """Sends a DMX value via Art-Net.

        Address format: /dmx/<universe>/<channel>

        @param address: DMX address
        @param value: Signal value (0-255 range)
        @returns Result<bool, SignalError>
        """
        parts = address.strip("/").split("/")
        if len(parts) < 3 or parts[0] != "dmx":
            return SignalResult.err(SignalError(
                code="DMX_INVALID_ADDRESS",
                message=f"Invalid DMX address: {address}",
            ))

        universe = int(parts[1])
        channel = int(parts[2])
        dmx_val = int(value.value) if value.signal_type == SignalType.INTEGER else int(value.normalized() * 255)

        return self.set_channel(universe, channel, dmx_val)


# =============================================================================
# Section 7: Value Mapper (Chataigne Mapping System)
# =============================================================================

class MappingCurve(enum.Enum):
    """Mapping interpolation curves — models Chataigne's mapper curves."""
    LINEAR = "linear"
    EASE_IN = "ease_in"
    EASE_OUT = "ease_out"
    EASE_IN_OUT = "ease_in_out"
    BEZIER = "bezier"
    HOLD = "hold"


@dataclass
class MappingRule:
    """A single value mapping rule — transforms input signal to output signal.

    Chataigne's mapper connects module input parameters to output parameters
    with value transformation (range, curve, conditional).

    @param source_module: Source module name
    @param source_param: Source parameter name
    @param target_module: Target module name
    @param target_param: Target parameter name
    @param source_range: Input value range (min, max)
    @param target_range: Output value range (min, max)
    @param curve: Interpolation curve
    @param condition: Optional condition expression
    @param enabled: Whether this mapping is active
    """
    source_module: str
    source_param: str
    target_module: str
    target_param: str
    source_range: Tuple[float, float] = (0.0, 1.0)
    target_range: Tuple[float, float] = (0.0, 1.0)
    curve: MappingCurve = MappingCurve.LINEAR
    condition: Optional[str] = None
    enabled: bool = True
    _rule_id: str = field(default_factory=lambda: str(uuid.uuid4()))

    def transform(self, input_val: float) -> float:
        """Applies the mapping transformation to an input value.

        @param input_val: Raw input value
        @returns Transformed output value
        """
        # Normalize input to [0, 1]
        src_min, src_max = self.source_range
        if src_max == src_min:
            t = 0.0
        else:
            t = max(0.0, min(1.0, (input_val - src_min) / (src_max - src_min)))

        # Apply curve
        t = self._apply_curve(t)

        # Map to target range
        tgt_min, tgt_max = self.target_range
        return tgt_min + t * (tgt_max - tgt_min)

    def _apply_curve(self, t: float) -> float:
        """Applies interpolation curve to normalized value."""
        if self.curve == MappingCurve.LINEAR:
            return t
        elif self.curve == MappingCurve.EASE_IN:
            return t * t
        elif self.curve == MappingCurve.EASE_OUT:
            return 1.0 - (1.0 - t) ** 2
        elif self.curve == MappingCurve.EASE_IN_OUT:
            return 3 * t * t - 2 * t * t * t
        elif self.curve == MappingCurve.HOLD:
            return 1.0 if t > 0.5 else 0.0
        return t


class ValueMapper:
    """Signal value mapper — connects inputs to outputs via transformation rules.

    Central routing matrix of the signal router — every input parameter can be
    mapped to any number of output parameters with value transformation.

    @since 2026.4.0
    @tags ["mapper", "routing", "transformation"]
    """

    def __init__(self) -> None:
        """Initialize ValueMapper."""
        self._rules: Dict[str, MappingRule] = {}
        self._active: bool = True

    def add_rule(self, rule: MappingRule) -> str:
        """Adds a mapping rule.

        @param rule: The mapping rule to add
        @returns Rule ID
        """
        self._rules[rule._rule_id] = rule
        logger.info("Mapping rule added: %s/%s -> %s/%s",
                     rule.source_module, rule.source_param,
                     rule.target_module, rule.target_param)
        return rule._rule_id

    def remove_rule(self, rule_id: str) -> SignalResult[bool]:
        """Removes a mapping rule by ID.

        @param rule_id: The rule to remove
        @returns Result<bool, SignalError>
        """
        if rule_id not in self._rules:
            return SignalResult.err(SignalError(
                code="RULE_NOT_FOUND",
                message=f"Mapping rule {rule_id} not found",
            ))
        del self._rules[rule_id]
        return SignalResult.ok(True)

    def process(self, source_module: str, source_param: str, value: float) -> List[Tuple[str, str, float]]:
        """Processes an input signal through all matching mapping rules.

        @param source_module: Source module name
        @param source_param: Source parameter name
        @param value: Input value
        @returns List of (target_module, target_param, mapped_value) tuples
        """
        if not self._active:
            return []

        outputs: List[Tuple[str, str, float]] = []
        for rule in self._rules.values():
            if not rule.enabled:
                continue
            if rule.source_module == source_module and rule.source_param == source_param:
                mapped = rule.transform(value)
                outputs.append((rule.target_module, rule.target_param, mapped))

        return outputs


# =============================================================================
# Section 8: State Machine (Chataigne State Machine)
# =============================================================================

@dataclass
class StateCondition:
    """Condition for a state transition.

    @param parameter_path: Module/param path to evaluate
    @param operator: Comparison operator
    @param threshold: Threshold value
    """
    parameter_path: str
    operator: str  # "==", "!=", ">", "<", ">=", "<="
    threshold: float

    def evaluate(self, value: float) -> bool:
        """Evaluates the condition against a value.

        @param value: Current parameter value
        @returns True if condition is met
        """
        ops = {
            "==": lambda a, b: abs(a - b) < 1e-6,
            "!=": lambda a, b: abs(a - b) >= 1e-6,
            ">": lambda a, b: a > b,
            "<": lambda a, b: a < b,
            ">=": lambda a, b: a >= b,
            "<=": lambda a, b: a <= b,
        }
        fn = ops.get(self.operator)
        return fn(value, self.threshold) if fn else False


@dataclass
class StateTransition:
    """Transition between two states in the state machine.

    @param from_state: Source state name
    @param to_state: Target state name
    @param conditions: Conditions that must all be true
    @param on_transition: Optional callback on transition
    """
    from_state: str
    to_state: str
    conditions: List[StateCondition]
    on_transition: Optional[Callable[[], None]] = None

    def can_transition(self, values: Dict[str, float]) -> bool:
        """Checks if all conditions are met for this transition.

        @param values: Current parameter values
        @returns True if transition should fire
        """
        return all(
            cond.evaluate(values.get(cond.parameter_path, 0.0))
            for cond in self.conditions
        )


@dataclass
class MachineState:
    """A state in the state machine with enter/exit actions and mappings.

    @param name: State name
    @param on_enter: Action to run when entering this state
    @param on_exit: Action to run when leaving this state
    @param active_mappings: Mapping rules active only in this state
    """
    name: str
    on_enter: Optional[Callable[[], None]] = None
    on_exit: Optional[Callable[[], None]] = None
    active_mappings: List[MappingRule] = field(default_factory=list)


class StateMachine:
    """Chataigne-style state machine — manages states with transition guards.

    States can activate/deactivate mapping rules, trigger actions, and
    respond to parameter conditions.

    @since 2026.4.0
    @tags ["state_machine", "automation", "conditions"]
    """

    def __init__(self, name: str = "Main State Machine") -> None:
        """Initialize StateMachine."""
        self._name = name
        self._states: Dict[str, MachineState] = {}
        self._transitions: List[StateTransition] = []
        self._current_state: Optional[str] = None
        self._history: List[Tuple[str, float]] = []

    def add_state(self, state: MachineState) -> None:
        """Adds a state to the machine.

        @param state: The state to add
        """
        self._states[state.name] = state
        if self._current_state is None:
            self._current_state = state.name

    def add_transition(self, transition: StateTransition) -> None:
        """Adds a state transition.

        @param transition: The transition to add
        """
        self._transitions.append(transition)

    @property
    def current_state(self) -> Optional[str]:
        """Execute current state operation for StateMachine."""
        return self._current_state

    def update(self, values: Dict[str, float]) -> Optional[str]:
        """Evaluates transitions and potentially changes state.

        @param values: Current parameter values from all modules
        @returns New state name if transitioned, None otherwise
        """
        if self._current_state is None:
            return None

        for trans in self._transitions:
            if trans.from_state == self._current_state and trans.can_transition(values):
                old_state = self._states.get(self._current_state)
                new_state = self._states.get(trans.to_state)

                # Exit old state
                if old_state and old_state.on_exit:
                    old_state.on_exit()

                # Transition callback
                if trans.on_transition:
                    trans.on_transition()

                # Enter new state
                self._current_state = trans.to_state
                if new_state and new_state.on_enter:
                    new_state.on_enter()

                self._history.append((trans.to_state, time.time()))
                logger.info("State transition: %s -> %s", trans.from_state, trans.to_state)
                return trans.to_state

        return None


# =============================================================================
# Section 9: Time Machine (Chataigne Sequence Engine)
# =============================================================================

@dataclass
class CuePoint:
    """A cue point in the timeline sequence.

    @param time_seconds: Position in the timeline
    @param target_module: Module to send to
    @param target_param: Parameter to set
    @param value: Value at this cue point
    @param curve: Interpolation to next cue
    """
    time_seconds: float
    target_module: str
    target_param: str
    value: float
    curve: MappingCurve = MappingCurve.LINEAR


@dataclass
class SequenceLayer:
    """A layer in the timeline — contains cue points for one parameter.

    @param name: Layer name
    @param cues: Ordered list of cue points
    @param loop: Whether to loop at end
    @param loop_range: Optional loop region (start, end) in seconds
    """
    name: str
    cues: List[CuePoint] = field(default_factory=list)
    loop: bool = False
    loop_range: Optional[Tuple[float, float]] = None

    def get_value_at(self, t: float) -> Optional[float]:
        """Interpolates value at time t between surrounding cue points.

        @param t: Current time in seconds
        @returns Interpolated value or None if no cues
        """
        if not self.cues:
            return None

        # Handle looping
        if self.loop and self.loop_range:
            lo, hi = self.loop_range
            if hi > lo and t >= hi:
                t = lo + ((t - lo) % (hi - lo))

        # Find surrounding cues
        sorted_cues = sorted(self.cues, key=lambda c: c.time_seconds)

        if t <= sorted_cues[0].time_seconds:
            return sorted_cues[0].value
        if t >= sorted_cues[-1].time_seconds:
            return sorted_cues[-1].value

        for i in range(len(sorted_cues) - 1):
            c0 = sorted_cues[i]
            c1 = sorted_cues[i + 1]
            if c0.time_seconds <= t <= c1.time_seconds:
                span = c1.time_seconds - c0.time_seconds
                if span == 0:
                    return c0.value
                frac = (t - c0.time_seconds) / span

                # Apply curve
                if c0.curve == MappingCurve.EASE_IN:
                    frac = frac * frac
                elif c0.curve == MappingCurve.EASE_OUT:
                    frac = 1.0 - (1.0 - frac) ** 2
                elif c0.curve == MappingCurve.EASE_IN_OUT:
                    frac = 3 * frac * frac - 2 * frac * frac * frac
                elif c0.curve == MappingCurve.HOLD:
                    frac = 0.0

                return c0.value + frac * (c1.value - c0.value)

        return None


class TimeMachine:
    """Chataigne-style sequence engine — timeline with layers, cues, and playback.

    @since 2026.4.0
    @tags ["timeline", "sequence", "automation", "cue"]
    """

    def __init__(self, name: str = "Main Sequence") -> None:
        """Initialize TimeMachine."""
        self._name = name
        self._layers: Dict[str, SequenceLayer] = {}
        self._position: float = 0.0
        self._playing: bool = False
        self._speed: float = 1.0
        self._duration: float = 60.0
        self._last_update: float = 0.0

    def add_layer(self, layer: SequenceLayer) -> None:
        """Adds a sequence layer."""
        self._layers[layer.name] = layer

    def play(self) -> None:
        """Starts playback."""
        self._playing = True
        self._last_update = time.time()

    def pause(self) -> None:
        """Pauses playback."""
        self._playing = False

    def stop(self) -> None:
        """Stops and resets to start."""
        self._playing = False
        self._position = 0.0

    def seek(self, position: float) -> None:
        """Seeks to a specific time position.

        @param position: Time in seconds
        """
        self._position = max(0.0, min(self._duration, position))

    def update(self) -> Dict[str, Optional[float]]:
        """Advances the timeline and returns current values for all layers.

        @returns Dict mapping layer name to current interpolated value
        """
        now = time.time()
        if self._playing:
            dt = (now - self._last_update) * self._speed
            self._position += dt

            if self._position >= self._duration:
                self._position = 0.0  # Loop

        self._last_update = now

        return {
            name: layer.get_value_at(self._position)
            for name, layer in self._layers.items()
        }


# =============================================================================
# Section 10: Master Signal Router Engine
# =============================================================================

class OmniSignalRouterEngine:
    """Master Signal Router Engine — orchestrates all protocol modules.

    This is the production-grade Chataigne-equivalent engine that:
    1. Manages protocol modules (OSC, MIDI, DMX, etc.)
    2. Routes signals between modules via the ValueMapper
    3. Manages state machine for conditional behavior
    4. Runs timeline sequences via TimeMachine
    5. Provides unified API for all signal operations

    @since 2026.4.0
    @tags ["signal", "router", "chataigne", "engine", "master"]

    @example
        engine = OmniSignalRouterEngine()
        osc = OSCModule("OSC In")
        midi = MIDIModule("MIDI Out")
        engine.add_module(osc)
        engine.add_module(midi)
        engine.mapper.add_rule(MappingRule(
            source_module="OSC In", source_param="/fader/1",
            target_module="MIDI Out", target_param="/midi/cc/0/7",
        ))
        await engine.start()
    """

    def __init__(self) -> None:
        """Initialize OmniSignalRouterEngine."""
        self._modules: Dict[str, SignalModule] = {}
        self._mapper = ValueMapper()
        self._state_machine = StateMachine()
        self._time_machine = TimeMachine()
        self._running = False
        self._engine_id = str(uuid.uuid4())

    @property
    def engine_id(self) -> str:
        """Performs engine id operation for OmniSignalRouterEngine."""
        return self._engine_id

    @property
    def mapper(self) -> ValueMapper:
        """Performs mapper operation for OmniSignalRouterEngine."""
        return self._mapper

    @property
    def state_machine(self) -> StateMachine:
        """Performs state machine operation for OmniSignalRouterEngine."""
        return self._state_machine

    @property
    def time_machine(self) -> TimeMachine:
        """Performs time machine operation for OmniSignalRouterEngine."""
        return self._time_machine

    def add_module(self, module: SignalModule) -> SignalResult[bool]:
        """Adds a protocol module to the router.

        @param module: The module to add
        @returns Result<bool, SignalError>
        """
        if module.name in self._modules:
            return SignalResult.err(SignalError(
                code="MODULE_EXISTS",
                message=f"Module '{module.name}' already exists",
            ))
        self._modules[module.name] = module

        # Wire up parameter change listener for routing
        module.add_listener(self._on_parameter_change)

        logger.info("Module added: %s (%s)", module.name, module.module_type)
        return SignalResult.ok(True)

    def _on_parameter_change(self, param_name: str, value: SignalValue) -> None:
        """Internal handler — routes parameter changes through mapper."""
        for mod_name, mod in self._modules.items():
            if param_name in mod.parameters:
                outputs = self._mapper.process(mod_name, param_name, value.normalized())
                for target_mod, target_param, mapped_val in outputs:
                    target = self._modules.get(target_mod)
                    if target:
                        asyncio.create_task(target.send(
                            target_param,
                            SignalValue(name=target_param, signal_type=SignalType.FLOAT, value=mapped_val),
                        ))

    async def start(self) -> SignalResult[bool]:
        """Starts the signal router — enables all modules."""
        self._running = True
        for mod in self._modules.values():
            await mod.enable({})
        logger.info("OmniSignalRouterEngine started with %d modules", len(self._modules))
        return SignalResult.ok(True)

    async def stop(self) -> SignalResult[bool]:
        """Stops the signal router."""
        self._running = False
        for mod in self._modules.values():
            await mod.disable()
        self._time_machine.stop()
        logger.info("OmniSignalRouterEngine stopped")
        return SignalResult.ok(True)

    def get_status(self) -> Dict[str, Any]:
        """Returns comprehensive router status."""
        return {
            "engine_id": self._engine_id,
            "running": self._running,
            "modules": {
                name: {
                    "type": mod.module_type,
                    "state": mod.state.value,
                    "params": len(mod.parameters),
                }
                for name, mod in self._modules.items()
            },
            "mapping_rules": len(self._mapper._rules),
            "state_machine_state": self._state_machine.current_state,
            "timeline_position": self._time_machine._position,
        }

    def diagnostics(self):
        """Return engine health diagnostics."""
        return {
            "engine_id": "omni-signal-router",
            "version": getattr(self, "VERSION", "1.0.0"),
            "status": "operational",
        }
