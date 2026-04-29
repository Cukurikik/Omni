# OMNI MOTHER - DIVINE MEMORY INTEGRATION
# Gymnasium (OMNI Zero-Mock Implementation)
# Implements Atari deterministic frame-stacking buffer abstraction.

from dataclasses import dataclass
from typing import List, Optional

@dataclass
class Result:
    value: Optional[List[List[float]]] # Output structured stacked frames
    error: Optional[str]
    is_ok: bool

    @staticmethod
    def ok(val: List[List[float]]) -> 'Result':
        return Result(value=val, error=None, is_ok=True)

    @staticmethod
    def err(err: str) -> 'Result':
        return Result(value=None, error=err, is_ok=False)

class AtariFrameStacker:
    def __init__(self, stack_size: int):
        self.stack_size = stack_size
        self.buffer = []

    def observation(self, frame: List[float]) -> Result:
        """
        Stacks new incoming pixel frame mechanically along channels.
        """
        if self.stack_size <= 0:
            return Result.err("Stack size must be fully allocated positive bounds.")
            
        if not frame:
            return Result.err("Incoming frame array empty.")
            
        if not self.buffer:
             # Initial reset fills the entire sequence buffer with identical early frames
             self.buffer = [list(frame) for _ in range(self.stack_size)]
        else:
             if len(frame) != len(self.buffer[0]):
                  return Result.err("Incoming frame dimension mathematical mutation rejected.")
             
             # Pop oldest, push newest mechanically
             self.buffer.pop(0)
             self.buffer.append(list(frame))
             
        # Create Deep copy representation
        stacked = [list(c) for c in self.buffer]
        return Result.ok(stacked)
