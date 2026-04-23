import datetime
import math
from typing import Any, Dict, List
from src.compute.python_core.omni_base_engine import Result, Ok, Err


class OmniHyperLogLogCardinalityEngine:
    """
    OmniHyperLogLogCardinalityEngine
    Batch: 27 (Semester 10)
    
    A zero-mock systems data-structure engine implementing a 
    probabilistic HyperLogLog cardinality estimator execute via 
    harmonic mean and leading zero count aggregates.
    """
    
    def __init__(self, bucket_bits: int):
        """
        :param bucket_bits: Number of bits used to address buckets (m = 2^bucket_bits).
        """
        self.bucket_bits = bucket_bits
        self.m = 1 << bucket_bits
        
        # Calculate alpha_m bias correction constant
        if self.m == 16:
            self.alpha_m = 0.673
        elif self.m == 32:
            self.alpha_m = 0.697
        elif self.m == 64:
            self.alpha_m = 0.709
        else:
            self.alpha_m = 0.7213 / (1.0 + 1.079 / self.m)

    def diagnostics(self) -> Dict[str, Any]:
        return {
            "engine": self.__class__.__name__,
            "status": "operational",
            "bucket_bits": self.bucket_bits,
            "buckets_m": self.m,
            "alpha_m": self.alpha_m,
            "timestamp": datetime.datetime.utcnow().isoformat()
        }

    def _hash_mock(self, int_val: int) -> int:
        """
        Simple deterministic 64-bit integer mixing function just for execute.
        (Murmur3/CityHash simplified for mathematical stability)
        """
        int_val = (int_val ^ (int_val >> 30)) * 0xbf58476d1ce4e5b9
        int_val = (int_val ^ (int_val >> 27)) * 0x94d049bb133111eb
        int_val = int_val ^ (int_val >> 31)
        # Force unsigned 64-bit bounds
        return int_val & 0xFFFFFFFFFFFFFFFF

    def _count_leading_zeros(self, val: int, bits: int) -> int:
        """Count leading zeros over the remaining representation bits."""
        if val == 0:
            return bits
        zeros = 0
        while (val & (1 << (bits - 1 - zeros))) == 0 and zeros < bits:
            zeros += 1
        return zeros

    def estimate_cardinality(self, stream: List[int]) -> Result[Dict[str, Any], Exception]:
        """
        Processes an iterable dataset and computes the estimated cardinality limits.
        """
        try:
            if not isinstance(stream, list):
                return Err(TypeError("Stream must be a list of integers"))
                
            buckets = [0] * self.m
            remaining_bits = 64 - self.bucket_bits
            
            for item in stream:
                if not isinstance(item, int):
                    return Err(TypeError(f"Stream items must be integers, got {type(item)}"))
                    
                hashed = self._hash_mock(item)
                bucket_idx = hashed >> remaining_bits
                
                # Mask out the bucket bits to just inspect the remaining bits
                remainder_mask = (1 << remaining_bits) - 1
                remainder = hashed & remainder_mask
                
                # Formula requires rank (position of first 1 bit + 1). Since we count
                # leading zeros from the top of the remaining bits:
                rank = self._count_leading_zeros(remainder, remaining_bits) + 1
                
                buckets[bucket_idx] = max(buckets[bucket_idx], rank)
                
            # Aggregate via Harmonic Mean
            harmonic_sum = sum(0.5 ** val for val in buckets)
            
            if harmonic_sum == 0:
                raw_estimate = 0.0
            else:
                raw_estimate = self.alpha_m * (self.m ** 2) / harmonic_sum
            
            # Linear Counting correction for small range where cardinality < 2.5 * m
            final_estimate = raw_estimate
            zero_buckets = buckets.count(0)
            
            if raw_estimate <= 2.5 * self.m:
                if zero_buckets > 0:
                    final_estimate = self.m * math.log(self.m / float(zero_buckets))
                    
            return Ok({
                "estimated_cardinality": int(round(final_estimate)),
                "raw_estimate": round(raw_estimate, 4),
                "exact_cardinality_count": len(set(stream)),
                "buckets_populated": self.m - zero_buckets
            })
            
        except Exception as e:
            return Err(e)
