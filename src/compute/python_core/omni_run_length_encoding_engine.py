"""OmniRunLengthEncodingEngine — Production-grade RLE compression.

Implements Run-Length Encoding for data compression/decompression
with support for string and byte sequences.
"""
from typing import Any, Dict, List, Tuple
from src.compute.python_core.omni_base_engine import Result, Ok, Err


class OmniRunLengthEncodingEngine:
    """Production engine for Run-Length Encoding compression."""

    ENGINE_VERSION = "1.0.0"

    def encode(self, data: str) -> Result:
        """Perform encode computation.

            Args:
                    data: str

            Returns:
                Result: Monadic result wrapping the computed value or error.
            """
        try:
            if not data:
                return Err(ValueError("Data must be non-empty."))
            runs = []
            i = 0
            while i < len(data):
                ch = data[i]
                count = 1
                while i + count < len(data) and data[i + count] == ch:
                    count += 1
                runs.append((ch, count))
                i += count
            encoded = "".join(f"{c}{n}" for c, n in runs)
            ratio = round(len(encoded) / len(data), 6) if len(data) > 0 else 1.0
            return Ok({"encoded": encoded, "runs": [{"char": c, "count": n} for c, n in runs],
                        "original_length": len(data), "encoded_length": len(encoded),
                        "compression_ratio": ratio, "num_runs": len(runs)})
        except Exception as e:
            return Err(e)

    def decode(self, encoded: str) -> Result:
        """Perform decode computation.

            Args:
                    encoded: str

            Returns:
                Result: Monadic result wrapping the computed value or error.
            """
        try:
            if not encoded:
                return Err(ValueError("Encoded data must be non-empty."))
            result = []
            i = 0
            while i < len(encoded):
                ch = encoded[i]
                i += 1
                num = ""
                while i < len(encoded) and encoded[i].isdigit():
                    num += encoded[i]
                    i += 1
                if not num:
                    return Err(ValueError(f"Missing count after character '{ch}'."))
                result.append(ch * int(num))
            decoded = "".join(result)
            return Ok({"decoded": decoded, "length": len(decoded)})
        except Exception as e:
            return Err(e)

    def diagnostics(self) -> Dict[str, Any]:
        return {"engine": "OmniRunLengthEncodingEngine", "version": self.ENGINE_VERSION,
                "status": "operational", "complexity": "O(N) encode/decode"}
