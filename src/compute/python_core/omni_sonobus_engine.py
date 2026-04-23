"""
+============================================================================+
|  OMNI SONOBUS ENGINE                                                       |
|  Engine Layer: Compute / Network Audio Streaming                           |
|  Source Study: sonosaurus/sonobus                                          |
|  Purpose: Low-latency UDP audio streaming with jitter buffer management.   |
|  License: OMNI-Enterprise                                                  |
+============================================================================+
"""

import struct
import time
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, field

ENGINE_VERSION: str = "1.0.0-omni"
from src.compute.python_core.omni_base_engine import Result, Ok, Err


@dataclass
class RtpPacket:
    """Represents a simplified RTP-like audio packet."""
    sequence_number: int
    timestamp: int
    payload: bytes
    marker: bool = False


class OmniSonobusEngine:
    """
    Production-grade low-latency network audio streaming engine.

    Learned from sonosaurus/sonobus:
    - Splits uncompressed audio into Opus-sized UDP packets
    - Labels each with RTP-like sequence IDs for reassembly
    - Implements a jitter buffer to handle network delay variance
    - Uses UDP for minimal latency at the cost of guaranteed delivery

    This engine implements the chunking, labeling, and reassembly pipeline.
    """

    DEFAULT_CHUNK_SIZE: int = 960  # samples per Opus frame at 48kHz
    RTP_HEADER_SIZE: int = 12

    def __init__(self, sample_rate: int = 48000, chunk_size: int = 960) -> None:
        """Initialize OmniSonobusEngine."""
        self._sample_rate: int = sample_rate
        self._chunk_size: int = chunk_size
        self._sequence_counter: int = 0
        self._jitter_buffer: Dict[int, RtpPacket] = {}
        self._jitter_buffer_depth: int = 5

    def build_rtp_header(self, sequence: int, timestamp: int, ssrc: int = 0x12345678) -> bytes:
        """
        Construct an RTP header for an audio packet.

        RTP Header (12 bytes):
          - V=2, P=0, X=0, CC=0 (byte 0)
          - M=0, PT=111 (byte 1) — dynamic payload type for Opus
          - Sequence Number (2 bytes)
          - Timestamp (4 bytes)
          - SSRC (4 bytes)

        Args:
            sequence: Packet sequence number.
            timestamp: RTP timestamp in sample units.
            ssrc: Synchronization source identifier.

        Returns:
            12-byte RTP header.
        """
        byte0: int = 0x80  # V=2
        byte1: int = 111   # PT=111 (Opus)
        return struct.pack(">BBHII", byte0, byte1, sequence & 0xFFFF, timestamp, ssrc)

    def chunk_audio_stream(self, pcm_bytes: bytes) -> List[RtpPacket]:
        """
        Split a PCM byte stream into RTP-labeled packets.

        Args:
            pcm_bytes: Raw PCM audio bytes (16-bit mono).

        Returns:
            List of RtpPacket instances ready for UDP transmission.
        """
        bytes_per_chunk: int = self._chunk_size * 2  # 16-bit = 2 bytes per sample
        packets: List[RtpPacket] = []

        for offset in range(0, len(pcm_bytes), bytes_per_chunk):
            chunk: bytes = pcm_bytes[offset:offset + bytes_per_chunk]
            if len(chunk) < bytes_per_chunk:
                chunk += b"\x00" * (bytes_per_chunk - len(chunk))

            timestamp: int = (offset // 2)  # sample offset
            packet = RtpPacket(
                sequence_number=self._sequence_counter,
                timestamp=timestamp,
                payload=chunk,
                marker=(offset == 0),
            )
            packets.append(packet)
            self._sequence_counter += 1

        return packets

    def serialize_packet(self, packet: RtpPacket) -> bytes:
        """Serialize an RtpPacket to raw bytes for UDP transmission."""
        header: bytes = self.build_rtp_header(packet.sequence_number, packet.timestamp)
        return header + packet.payload

    def deserialize_packet(self, data: bytes) -> Optional[RtpPacket]:
        """
        Deserialize raw UDP bytes back into an RtpPacket.

        Args:
            data: Raw bytes received from UDP socket.

        Returns:
            RtpPacket if valid, None otherwise.
        """
        if len(data) < self.RTP_HEADER_SIZE:
            return None

        byte0, byte1, seq, ts, ssrc = struct.unpack(">BBHII", data[:12])
        payload: bytes = data[12:]

        return RtpPacket(
            sequence_number=seq,
            timestamp=ts,
            payload=payload,
            marker=bool(byte1 & 0x80),
        )

    def insert_jitter_buffer(self, packet: RtpPacket) -> None:
        """
        Insert a packet into the jitter buffer for reordering.

        Args:
            packet: Incoming RtpPacket to buffer.
        """
        self._jitter_buffer[packet.sequence_number] = packet

        # Evict old packets if buffer exceeds depth
        if len(self._jitter_buffer) > self._jitter_buffer_depth * 3:
            min_seq: int = min(self._jitter_buffer.keys())
            del self._jitter_buffer[min_seq]

    def drain_jitter_buffer(self) -> List[RtpPacket]:
        """
        Drain packets from the jitter buffer in sequence order.

        Returns:
            List of RtpPackets sorted by sequence number.
        """
        if len(self._jitter_buffer) < self._jitter_buffer_depth:
            return []

        sorted_keys: List[int] = sorted(self._jitter_buffer.keys())
        packets: List[RtpPacket] = []

        for key in sorted_keys[:self._jitter_buffer_depth]:
            packets.append(self._jitter_buffer.pop(key))

        return packets

    def reassemble_audio(self, packets: List[RtpPacket]) -> bytes:
        """Reassemble ordered packets back into a continuous PCM stream."""
        sorted_packets = sorted(packets, key=lambda p: p.sequence_number)
        return b"".join(p.payload for p in sorted_packets)

    def evaluate_health(self) -> Dict[str, Any]:
        """Return engine health and status information."""
        return {
            "engine": "OmniSonobusEngine",
            "version": ENGINE_VERSION,
            "status": "operational",
            "sample_rate": self._sample_rate,
            "chunk_size": self._chunk_size,
            "jitter_buffer_size": len(self._jitter_buffer),
            "capabilities": ["rtp_packetize", "jitter_buffer", "udp_streaming", "pcm_reassembly"],
        }

    def diagnostics(self):
        """Return engine health diagnostics."""
        return {
            "engine_id": "omni-sonobus",
            "version": getattr(self, "VERSION", "1.0.0"),
            "status": "operational",
        }
