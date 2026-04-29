# OMNI MOTHER - DIVINE MEMORY INTEGRATION
# Robomimic (OMNI Zero-Mock Implementation)
# Implements Behavior Cloning (BC) Trajectory window sequential buffering structure.

from dataclasses import dataclass
from typing import List, Optional

@dataclass
class Result:
    value: Optional[List[List[float]]] # Reconstructed trajectory sequence window
    error: Optional[str]
    is_ok: bool

    @staticmethod
    def ok(val: List[List[float]]) -> 'Result':
        return Result(value=val, error=None, is_ok=True)

    @staticmethod
    def err(err: str) -> 'Result':
        return Result(value=None, error=err, is_ok=False)

class BehavioralCloningBuffer:
    def evaluate_trajectory_window(self, sequence: List[List[float]], sequence_len: int, target_idx: int) -> Result:
        """
        Extracts a sequence window of structured size ending at target step (inclusive).
        If padding is required on the left (e.g. index 0), it perfectly replicates index 0 mathematically.
        """
        if not sequence:
             return Result.err("Source structural trajectory impossible to sequence, length zero.")
             
        if sequence_len <= 0:
             return Result.err("Sequence span must be topologically strictly positive.")
             
        if target_idx < 0 or target_idx >= len(sequence):
             return Result.err("Target span index computationally violates bounds.")
             
        window = []
        for i in range(target_idx - sequence_len + 1, target_idx + 1):
             if i < 0:
                  # Pad left with the boundary step mechanically matching sequence padding algorithms
                  window.append(list(sequence[0]))
             else:
                  window.append(list(sequence[i]))
                  
        return Result.ok(window)
