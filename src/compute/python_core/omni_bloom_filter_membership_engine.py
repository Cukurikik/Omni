import datetime
import math
from typing import Any, Dict
from src.compute.python_core.omni_base_engine import Result, Ok, Err


class OmniBloomFilterMembershipEngine:
    """
    OmniBloomFilterMembershipEngine
    Batch: 28 (Semester 10)
    
    A zero-mock Big Data systems structure calculating probabilistic 
    membership tests using mathematical hashing combinations.
    """
    
    def __init__(self, expected_items: int, target_false_positive_rate: float):
        """
        :param expected_items: The max bounded members planned (n)
        :param target_false_positive_rate: Acceptable theoretical error rate (p)
        """
        self.expected_items = expected_items
        self.target_fp_rate = target_false_positive_rate
        
        # Calculate optimal size (m) and hash count (k)
        # m = -(n * ln(p)) / (ln(2)^2)
        m_float = -(expected_items * math.log(target_false_positive_rate)) / (math.log(2) ** 2)
        self.bit_array_size = int(math.ceil(m_float))
        
        # k = (m / n) * ln(2)
        k_float = (self.bit_array_size / expected_items) * math.log(2)
        self.hash_count = int(math.ceil(k_float))
        
        # State
        self.bit_array = bytearray((self.bit_array_size + 7) // 8)
        self.items_added = 0

    def diagnostics(self) -> Dict[str, Any]:
        return {
            "engine": self.__class__.__name__,
            "status": "operational",
            "bit_array_size": self.bit_array_size,
            "hash_count": self.hash_count,
            "items_added": self.items_added,
            "timestamp": datetime.datetime.utcnow().isoformat()
        }

    def _hash_core(self, item_str: str, seed: int) -> int:
        """Deterministic string hashing mixing execute murmur/fnv"""
        h = seed
        for char in item_str:
            h ^= ord(char)
            h = (h * 0x5bd1e995) & 0xFFFFFFFF
            h ^= h >> 15
        return h % self.bit_array_size

    def insert(self, item: str) -> Result[bool, Exception]:
        """
        Records the item into the probabilistic constraint bounds.
        """
        try:
            if not isinstance(item, str):
                return Err(TypeError("Bloom items must be strictly strings in this pipeline"))
                
            for i in range(self.hash_count):
                bit_index = self._hash_core(item, seed=i)
                byte_index = bit_index // 8
                bit_offset = bit_index % 8
                self.bit_array[byte_index] |= (1 << bit_offset)
                
            self.items_added += 1
            return Ok(True)
        except Exception as e:
            return Err(e)

    def contains(self, item: str) -> Result[bool, Exception]:
        """
        Checks membership presence. True: Probably. False: Absolutely not.
        """
        try:
            if not isinstance(item, str):
                return Err(TypeError("Bloom items must be strictly strings in this pipeline"))
                
            for i in range(self.hash_count):
                bit_index = self._hash_core(item, seed=i)
                byte_index = bit_index // 8
                bit_offset = bit_index % 8
                
                # If any bit is 0, it's definitively not present
                if not (self.bit_array[byte_index] & (1 << bit_offset)):
                    return Ok(False)
                    
            return Ok(True)
        except Exception as e:
            return Err(e)

    def estimate_current_fp_rate(self) -> Result[float, Exception]:
        """
        Analytically projects current false positive saturation given items added.
        p_current = (1 - e^(-k * n / m))^k
        """
        try:
            if self.items_added == 0:
                return Ok(0.0)
                
            exponent = -self.hash_count * self.items_added / self.bit_array_size
            inner_term = 1.0 - math.exp(exponent)
            p_current = inner_term ** self.hash_count
            
            return Ok(round(p_current, 6))
        except Exception as e:
            return Err(e)
