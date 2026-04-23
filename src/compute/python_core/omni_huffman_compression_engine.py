"""OmniHuffmanCompressionEngine — Production-grade Huffman coding for data compression.

Implements Huffman tree construction via min-heap, variable-length prefix codes,
and bitstream encoding/decoding with compression ratio calculation.
"""
import heapq
from typing import Any, Dict, List, Optional, Tuple
from src.compute.python_core.omni_base_engine import Result, Ok, Err


class _HuffmanNode:
    """Internal node for Huffman tree."""
    __slots__ = ('char', 'freq', 'left', 'right')

    def __init__(self, char: Optional[str], freq: int, left=None, right=None):
        self.char = char
        self.freq = freq
        self.left = left
        self.right = right

    def __lt__(self, other):
        return self.freq < other.freq


class OmniHuffmanCompressionEngine:
    """Production engine for Huffman coding compression."""

    ENGINE_VERSION = "1.0.0"

    def _build_frequency_table(self, text: str) -> Dict[str, int]:
        freq = {}
        for ch in text:
            freq[ch] = freq.get(ch, 0) + 1
        return freq

    def _build_huffman_tree(self, freq: Dict[str, int]) -> Optional[_HuffmanNode]:
        heap = [_HuffmanNode(ch, f) for ch, f in freq.items()]
        heapq.heapify(heap)
        while len(heap) > 1:
            left = heapq.heappop(heap)
            right = heapq.heappop(heap)
            merged = _HuffmanNode(None, left.freq + right.freq, left, right)
            heapq.heappush(heap, merged)
        return heap[0] if heap else None

    def _generate_codes(self, node: Optional[_HuffmanNode], prefix: str = "",
                        codes: Optional[Dict[str, str]] = None) -> Dict[str, str]:
        if codes is None:
            codes = {}
        if node is None:
            return codes
        if node.char is not None:
            codes[node.char] = prefix if prefix else "0"
        self._generate_codes(node.left, prefix + "0", codes)
        self._generate_codes(node.right, prefix + "1", codes)
        return codes

    def compress(self, text: str) -> Result:
        """
        Compress text using Huffman coding.

        Returns:
            Result with encoded bitstring, code table, and compression ratio.
        """
        try:
            if not text:
                return Err(ValueError("Input text must be non-empty."))

            freq = self._build_frequency_table(text)
            tree = self._build_huffman_tree(freq)
            codes = self._generate_codes(tree)

            encoded = "".join(codes[ch] for ch in text)
            original_bits = len(text) * 8
            compressed_bits = len(encoded)
            ratio = round(compressed_bits / original_bits, 6) if original_bits > 0 else 1.0

            return Ok({"encoded": encoded, "codes": codes, "frequency_table": freq,
                        "original_bits": original_bits, "compressed_bits": compressed_bits,
                        "compression_ratio": ratio, "unique_chars": len(freq)})
        except Exception as e:
            return Err(e)

    def decompress(self, encoded: str, codes: Dict[str, str]) -> Result:
        """Decompress a Huffman-encoded bitstring using the code table."""
        try:
            reverse_codes = {v: k for k, v in codes.items()}
            decoded = []
            buffer = ""
            for bit in encoded:
                buffer += bit
                if buffer in reverse_codes:
                    decoded.append(reverse_codes[buffer])
                    buffer = ""
            if buffer:
                return Err(ValueError("Invalid encoded data: leftover bits."))
            return Ok({"decoded": "".join(decoded), "length": len(decoded)})
        except Exception as e:
            return Err(e)

    def diagnostics(self) -> Dict[str, Any]:
        return {"engine": "OmniHuffmanCompressionEngine", "version": self.ENGINE_VERSION,
                "status": "operational", "complexity": "O(N log N) tree construction"}
