"""OmniCrcChecksumEngine — Production-grade CRC-32 checksum computation.

Implements CRC-32 using polynomial division with lookup table for O(N) computation,
plus Adler-32 and Fletcher-16 checksums for data integrity verification.
"""
from typing import Any, Dict, List
from src.compute.python_core.omni_base_engine import Result, Ok, Err


class OmniCrcChecksumEngine:
    """Production engine for checksum computation (CRC-32, Adler-32, Fletcher-16)."""

    ENGINE_VERSION = "1.0.0"
    CRC32_POLY = 0xEDB88320

    def __init__(self):
        self._crc32_table = self._build_crc32_table()

    def _build_crc32_table(self) -> List[int]:
        table = []
        for i in range(256):
            crc = i
            for _ in range(8):
                if crc & 1:
                    crc = (crc >> 1) ^ self.CRC32_POLY
                else:
                    crc >>= 1
            table.append(crc)
        return table

    def crc32(self, data: bytes) -> Result:
        """Perform crc32 computation.

            Args:
                    data: bytes

            Returns:
                Result: Monadic result wrapping the computed value or error.
            """
        try:
            if not isinstance(data, (bytes, bytearray)):
                return Err(ValueError("Data must be bytes or bytearray."))
            crc = 0xFFFFFFFF
            for byte in data:
                crc = self._crc32_table[(crc ^ byte) & 0xFF] ^ (crc >> 8)
            crc ^= 0xFFFFFFFF
            return Ok({"checksum": crc, "hex": f"0x{crc:08X}", "data_length": len(data), "algorithm": "CRC-32"})
        except Exception as e:
            return Err(e)

    def adler32(self, data: bytes) -> Result:
        """Perform adler32 computation.

            Args:
                    data: bytes

            Returns:
                Result: Monadic result wrapping the computed value or error.
            """
        try:
            a, b = 1, 0
            MOD = 65521
            for byte in data:
                a = (a + byte) % MOD
                b = (b + a) % MOD
            checksum = (b << 16) | a
            return Ok({"checksum": checksum, "hex": f"0x{checksum:08X}", "data_length": len(data), "algorithm": "Adler-32"})
        except Exception as e:
            return Err(e)

    def fletcher16(self, data: bytes) -> Result:
        """Perform fletcher16 computation.

            Args:
                    data: bytes

            Returns:
                Result: Monadic result wrapping the computed value or error.
            """
        try:
            s1, s2 = 0, 0
            for byte in data:
                s1 = (s1 + byte) % 255
                s2 = (s2 + s1) % 255
            checksum = (s2 << 8) | s1
            return Ok({"checksum": checksum, "hex": f"0x{checksum:04X}", "data_length": len(data), "algorithm": "Fletcher-16"})
        except Exception as e:
            return Err(e)

    def verify(self, data: bytes, expected_crc32: int) -> Result:
        """Perform verify computation.

            Args:
                    data: bytes
                    expected_crc32: int

            Returns:
                Result: Monadic result wrapping the computed value or error.
            """
        try:
            r = self.crc32(data)
            if not r.is_ok():
                return r
            match = r.value["checksum"] == expected_crc32
            return Ok({"match": match, "computed": r.value["checksum"], "expected": expected_crc32})
        except Exception as e:
            return Err(e)

    def diagnostics(self) -> Dict[str, Any]:
        return {"engine": "OmniCrcChecksumEngine", "version": self.ENGINE_VERSION,
                "status": "operational", "algorithms": ["CRC-32", "Adler-32", "Fletcher-16"]}
