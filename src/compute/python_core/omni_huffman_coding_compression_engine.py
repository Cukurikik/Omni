import datetime
import heapq
from typing import Any, Dict, List, Optional
from src.compute.python_core.omni_base_engine import Result, Ok, Err


class HuffmanNode:
    """Internal logical mapping for prefix tree bounding representation."""
    def __init__(self, char: Optional[str], freq: int):
        self.char = char
        self.freq = freq
        self.left: Optional['HuffmanNode'] = None
        self.right: Optional['HuffmanNode'] = None
        
    def __lt__(self, other: 'HuffmanNode') -> bool:
        return self.freq < other.freq

class OmniHuffmanCodingCompressionEngine:
    """
    OmniHuffmanCodingCompressionEngine
    Batch: 29 (Semester 10)
    
    A zero-mock information theory systems engine generating optimized 
    mathematical prefix encodings based on character frequency aggregation.
    """
    
    def __init__(self):
        self.root: Optional[HuffmanNode] = None
        self.codes: Dict[str, str] = {}
        self.reverse_mapping: Dict[str, str] = {}

    def diagnostics(self) -> Dict[str, Any]:
        return {
            "engine": self.__class__.__name__,
            "status": "operational",
            "is_compiled": self.root is not None,
            "alphabet_size": len(self.codes),
            "timestamp": datetime.datetime.utcnow().isoformat()
        }

    def _build_tree_internals(self, frequencies: Dict[str, int]) -> Result[bool, Exception]:
        """Constructs the optimal aggregate tree logic."""
        queue = []
        for char, freq in frequencies.items():
            heapq.heappush(queue, HuffmanNode(char, freq))
            
        if not queue:
            return Err(ValueError("Cannot build structural map from empty frequency dictionary"))
            
        while len(queue) > 1:
            node_left = heapq.heappop(queue)
            node_right = heapq.heappop(queue)
            
            merged = HuffmanNode(None, node_left.freq + node_right.freq)
            merged.left = node_left
            merged.right = node_right
            heapq.heappush(queue, merged)
            
        self.root = heapq.heappop(queue)
        
        # single character boundary case
        if self.root.char is not None:
             standard_root = HuffmanNode(None, self.root.freq)
             standard_root.left = self.root
             self.root = standard_root
             
        return Ok(True)

    def _build_codes_recursive(self, current_node: Optional[HuffmanNode], current_code: str):
        if current_node is None:
            return
            
        if current_node.char is not None:
            self.codes[current_node.char] = current_code
            self.reverse_mapping[current_code] = current_node.char
            return
            
        self._build_codes_recursive(current_node.left, current_code + "0")
        self._build_codes_recursive(current_node.right, current_code + "1")

    def compile_encoding_tree(self, payload: str) -> Result[Dict[str, Any], Exception]:
        """
        Maps statistical frequency and mathematically constructs optimal encoding keys.
        """
        try:
            if not isinstance(payload, str):
                return Err(TypeError("Compression payload sequence must strictly be a string"))
                
            if len(payload) == 0:
                return Err(ValueError("Cannot compile tree for an empty temporal sequence"))
                
            frequencies = {}
            for char in payload:
                frequencies[char] = frequencies.get(char, 0) + 1
                
            res = self._build_tree_internals(frequencies)
            if not res.is_ok():
                return Err(res.unwrap_err())
                
            self.codes = {}
            self.reverse_mapping = {}
            self._build_codes_recursive(self.root, "")
            
            # calculate efficiency mapping
            original_bits = len(payload) * 8
            encoded_bits = sum(len(self.codes[char]) for char in payload)
            saving_ratio = 1.0 - (encoded_bits / original_bits) if original_bits > 0 else 0.0
            
            return Ok({
                "unique_characters": len(frequencies),
                "original_bits": original_bits,
                "encoded_bits": encoded_bits,
                "efficiency_saving_ratio": round(saving_ratio, 4),
                "encoding_dictionary": self.codes
            })
            
        except Exception as e:
            return Err(e)

    def encode(self, string_data: str) -> Result[str, Exception]:
        """Translates a structured sequence into prefix bits."""
        try:
            if self.root is None:
                return Err(RuntimeError("Huffman boundary tree is not compiled yet"))
                
            encoded = []
            for char in string_data:
                if char not in self.codes:
                    return Err(ValueError(f"Character '{char}' not found in logical map boundary"))
                encoded.append(self.codes[char])
                
            return Ok("".join(encoded))
        except Exception as e:
            return Err(e)

    def decode(self, binary_string: str) -> Result[str, Exception]:
        """Mathematically reconstructs the pure string state from zero compression logic."""
        try:
            if self.root is None:
                return Err(RuntimeError("Huffman boundary tree is not compiled yet"))
                
            decoded = []
            current_code = ""
            
            for bit in binary_string:
                if bit not in ("0", "1"):
                    return Err(ValueError("Invalid binary structural state boundary in input"))
                    
                current_code += bit
                if current_code in self.reverse_mapping:
                    decoded.append(self.reverse_mapping[current_code])
                    current_code = ""
                    
            if current_code != "":
                return Err(ValueError("Dangling unfinished prefix boundary in physical bit sequence"))
                
            return Ok("".join(decoded))
        except Exception as e:
            return Err(e)
