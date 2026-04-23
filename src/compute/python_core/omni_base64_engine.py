"""OmniBase64Engine — Production-grade Base64 encoding/decoding.

Implements RFC 4648 Base64 encoding and decoding from scratch,
with URL-safe variant and padding control.
"""
from typing import Any, Dict
from src.compute.python_core.omni_base_engine import Result, Ok, Err


class OmniBase64Engine:
    """Production engine for Base64 encoding/decoding (RFC 4648)."""

    ENGINE_VERSION = "1.0.0"
    ALPHABET = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/"
    URL_SAFE_ALPHABET = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-_"

    def encode(self, data: bytes, url_safe: bool = False) -> Result:
        """Perform encode computation.

            Args:
                    data: bytes
                    url_safe: bool

            Returns:
                Result: Monadic result wrapping the computed value or error.
            """
        try:
            alpha = self.URL_SAFE_ALPHABET if url_safe else self.ALPHABET
            result = []
            padding = 0
            for i in range(0, len(data), 3):
                chunk = data[i:i+3]
                n = len(chunk)
                val = 0
                for j, b in enumerate(chunk):
                    val |= b << (8 * (2 - j))
                for j in range(4):
                    if j < n + 1:
                        idx = (val >> (6 * (3 - j))) & 0x3F
                        result.append(alpha[idx])
                    else:
                        result.append('=')
                        padding += 1
            encoded = ''.join(result)
            return Ok({"encoded": encoded, "input_bytes": len(data), "output_length": len(encoded),
                        "padding": padding, "url_safe": url_safe})
        except Exception as e:
            return Err(e)

    def decode(self, encoded: str, url_safe: bool = False) -> Result:
        """Perform decode computation.

            Args:
                    encoded: str
                    url_safe: bool

            Returns:
                Result: Monadic result wrapping the computed value or error.
            """
        try:
            alpha = self.URL_SAFE_ALPHABET if url_safe else self.ALPHABET
            lookup = {c: i for i, c in enumerate(alpha)}
            encoded = encoded.rstrip('=')
            result = []
            buffer = 0
            bits = 0
            for ch in encoded:
                if ch not in lookup:
                    return Err(ValueError(f"Invalid Base64 character: '{ch}'"))
                buffer = (buffer << 6) | lookup[ch]
                bits += 6
                if bits >= 8:
                    bits -= 8
                    result.append((buffer >> bits) & 0xFF)
            decoded = bytes(result)
            return Ok({"decoded": decoded, "decoded_str": decoded.decode('utf-8', errors='replace'),
                        "output_bytes": len(decoded), "url_safe": url_safe})
        except Exception as e:
            return Err(e)

    def diagnostics(self) -> Dict[str, Any]:
        return {"engine": "OmniBase64Engine", "version": self.ENGINE_VERSION,
                "status": "operational", "compliance": "RFC 4648"}
