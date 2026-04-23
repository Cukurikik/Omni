import datetime
from typing import Any, Dict
from src.compute.python_core.omni_base_engine import Result, Ok, Err


class OmniCRCPolynomialHashingEngine:
    """
    OmniCRCPolynomialHashingEngine
    Batch: 28 (Semester 10)
    
    A zero-mock systems integrity engine that calculates CRC hardware simulations 
    using generic Galois field binary polynomial division.
    """
    
    def __init__(self, polynomial: int, width: int, initial_value: int = 0, final_xor_value: int = 0):
        """
        :param polynomial: The generator polynomial (e.g., 0x04C11DB7 for CRC-32)
        :param width: Bit width of the CRC (e.g., 8, 16, 32)
        :param initial_value: The starting value of the register
        :param final_xor_value: XOR boundary applied to the final result
        """
        self.polynomial = polynomial
        self.width = width
        self.initial_value = initial_value
        self.final_xor_value = final_xor_value
        
        # Compute the Top Bit mask
        self.top_bit = 1 << (self.width - 1)
        # Compute generic mask
        self.mask = (1 << self.width) - 1
        
        # Precompute table
        self._table = self._precompute_table()

    def _precompute_table(self) -> list:
        table = []
        for i in range(256):
            register = i << (self.width - 8)
            for _ in range(8):
                if register & self.top_bit:
                    register = (register << 1) ^ self.polynomial
                else:
                    register = (register << 1)
            table.append(register & self.mask)
        return table

    def diagnostics(self) -> Dict[str, Any]:
        return {
            "engine": self.__class__.__name__,
            "status": "operational",
            "width": self.width,
            "polynomial": hex(self.polynomial),
            "timestamp": datetime.datetime.utcnow().isoformat()
        }

    def compute_crc(self, data: bytes) -> Result[int, Exception]:
        """
        Computes the CRC checksum over the byte sequence.
        """
        try:
            if not isinstance(data, (bytes, bytearray)):
                return Err(TypeError("Data must be bytes or bytearray"))
                
            register = self.initial_value
            
            for byte in data:
                # Top 8 bits
                top_idx = (register >> (self.width - 8)) & 0xFF
                # XOR with data byte
                tbl_idx = top_idx ^ byte
                # shift and XOR with table
                register = ((register << 8) ^ self._table[tbl_idx]) & self.mask
                
            final_crc = register ^ self.final_xor_value
            return Ok(final_crc)
            
        except Exception as e:
            return Err(e)

    def verify_integrity(self, data: bytes, expected_crc: int) -> Result[bool, Exception]:
        """
        Computes the target sequence CRC and validates it against the expected integer.
        """
        try:
            res = self.compute_crc(data)
            if not res.is_ok():
                return Err(res.unwrap_err())
                
            actual_crc = res.unwrap()
            return Ok(actual_crc == expected_crc)
        except Exception as e:
            return Err(e)
