# OMNI MOTHER - DIVINE MEMORY INTEGRATION
# PyTorch Lightning Trainer (OMNI Zero-Mock Implementation)
# Implements validation early stopping patience math.

from dataclasses import dataclass
from typing import List, Optional

@dataclass
class Result:
    value: Optional[bool] # True if training should stop
    error: Optional[str]
    is_ok: bool

    @staticmethod
    def ok(val: bool) -> 'Result':
        return Result(value=val, error=None, is_ok=True)

    @staticmethod
    def err(err: str) -> 'Result':
        return Result(value=None, error=err, is_ok=False)

class EarlyStoppingEngine:
    def __init__(self, patience: int, min_delta: float):
        self.patience = patience
        self.min_delta = min_delta
        self.best_loss = float('inf')
        self.wait_count = 0

    def step(self, current_val_loss: float) -> Result:
        if current_val_loss < 0.0:
            return Result.err("Validation loss must be structurally non-negative in this context.")
            
        if current_val_loss < self.best_loss - self.min_delta:
            self.best_loss = current_val_loss
            self.wait_count = 0
            return Result.ok(False)
        else:
            self.wait_count += 1
            if self.wait_count >= self.patience:
                return Result.ok(True) # Stop training
            return Result.ok(False)
