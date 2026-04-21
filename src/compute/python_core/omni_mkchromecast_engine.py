"""
+============================================================================+
|  OMNI MKCHROMECAST ENGINE                                                  |
|  Engine Layer: Compute / Network mDNS Discovery                            |
|  Source Study: muammar/mkchromecast                                        |
|  Purpose: Native mDNS multicast query for Google Cast device discovery.    |
|  License: OMNI-Enterprise                                                  |
+============================================================================+
"""

import socket
import struct
from typing import Dict, Any, List, Optional, Tuple

ENGINE_VERSION: str = "1.0.0-omni"


class OmniMkchromecastEngine:
    """
    Production-grade mDNS scanner for Google Cast device discovery.

    Learned from muammar/mkchromecast:
    - Uses Multicast DNS (mDNS) on UDP port 5353
    - Queries for _googlecast._tcp.local. service type
    - Discovers Chromecast devices on the local network
    - Launches HTTP server for media streaming to discovered devices

    This engine implements the mDNS query protocol natively in Python.
    """

    MDNS_ADDR: str = "224.0.0.251"
    MDNS_PORT: int = 5353
    SERVICE_TYPE: str = "_googlecast._tcp.local."

    def __init__(self) -> None:
        """Initialize OmniMkchromecastEngine."""
        self._discovered_devices: List[Dict[str, Any]] = []

    def build_mdns_query(self, service_name: str = "") -> bytes:
        """
        Construct a raw mDNS query packet for service discovery.

        The DNS wire format:
          - 12-byte header (ID=0, QR=0, QDCOUNT=1)
          - Question section with encoded domain name

        Args:
            service_name: The service to query (defaults to _googlecast._tcp.local.)

        Returns:
            Raw bytes for the mDNS query datagram.
        """
        if not service_name:
            service_name = self.SERVICE_TYPE

        # DNS Header: ID=0, Flags=0x0000, QDCOUNT=1, ANCOUNT=0, NSCOUNT=0, ARCOUNT=0
        header: bytes = struct.pack(">HHHHHH", 0, 0, 1, 0, 0, 0)

        # Encode domain name in DNS wire format
        qname: bytes = self._encode_dns_name(service_name)

        # QTYPE=PTR(12), QCLASS=IN(1)
        question: bytes = qname + struct.pack(">HH", 12, 1)

        return header + question

    def _encode_dns_name(self, name: str) -> bytes:
        """
        Encode a domain name into DNS wire format.

        Args:
            name: Domain name like '_googlecast._tcp.local.'

        Returns:
            DNS wire-encoded bytes.
        """
        parts: List[str] = name.rstrip(".").split(".")
        encoded: bytes = b""
        for part in parts:
            part_bytes: bytes = part.encode("ascii")
            encoded += bytes([len(part_bytes)]) + part_bytes
        encoded += b"\x00"  # null terminator
        return encoded

    def parse_mdns_response(self, data: bytes) -> List[Dict[str, str]]:
        """
        Parse an mDNS response packet to extract discovered services.

        Args:
            data: Raw response bytes from UDP 5353.

        Returns:
            List of discovered service records.
        """
        if len(data) < 12:
            return []

        _id, flags, qd_count, an_count, ns_count, ar_count = struct.unpack(
            ">HHHHHH", data[:12]
        )

        # Only process responses (QR bit set)
        if not (flags & 0x8000):
            return []

        records: List[Dict[str, str]] = []
        offset: int = 12

        # Skip questions
        for _ in range(qd_count):
            offset = self._skip_dns_name(data, offset)
            offset += 4  # QTYPE + QCLASS

        # Parse answers
        for _ in range(an_count):
            if offset >= len(data) - 10:
                break
            name_end: int = self._skip_dns_name(data, offset)
            if name_end + 10 > len(data):
                break
            rtype, rclass, ttl, rdlength = struct.unpack(
                ">HHIH", data[name_end:name_end + 10]
            )
            rdata_start: int = name_end + 10
            records.append({
                "type": str(rtype),
                "ttl": str(ttl),
                "rdlength": str(rdlength),
            })
            offset = rdata_start + rdlength

        return records

    def _skip_dns_name(self, data: bytes, offset: int) -> int:
        """Skip over a DNS name in wire format, handling compression pointers."""
        while offset < len(data):
            length: int = data[offset]
            if length == 0:
                return offset + 1
            if (length & 0xC0) == 0xC0:  # compression pointer
                return offset + 2
            offset += 1 + length
        return offset

    def scan_for_chromecasts(self, timeout: float = 3.0) -> List[Dict[str, Any]]:
        """
        Perform a full mDNS scan for Google Cast devices.

        Args:
            timeout: Seconds to wait for responses.

        Returns:
            List of discovered Chromecast device info dicts.
        """
        self._discovered_devices.clear()
        query: bytes = self.build_mdns_query()

        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.settimeout(timeout)

        sock.sendto(query, (self.MDNS_ADDR, self.MDNS_PORT))

        while True:
            try:
                data, addr = sock.recvfrom(4096)
                records = self.parse_mdns_response(data)
                if records:
                    self._discovered_devices.append({
                        "address": addr[0],
                        "port": addr[1],
                        "records": records,
                    })
            except socket.timeout:
                break

        sock.close()
        return self._discovered_devices

    def diagnostics(self) -> Dict[str, Any]:
        """Return engine health and status information."""
        return {
            "engine": "OmniMkchromecastEngine",
            "version": ENGINE_VERSION,
            "status": "operational",
            "protocol": "mDNS/UDP 5353",
            "service_type": self.SERVICE_TYPE,
            "discovered_devices": len(self._discovered_devices),
        }
