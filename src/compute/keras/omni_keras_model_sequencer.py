# OMNI MOTHER - DIVINE MEMORY INTEGRATION
# Keras Model Sequencer (OMNI Zero-Mock Implementation)
# Implements directed sequential feed-forward validation.

from dataclasses import dataclass
from typing import List, Tuple, Optional

@dataclass
class Result:
    value: Optional[List[Tuple[int, int]]]
    error: Optional[str]
    is_ok: bool

    @staticmethod
    def ok(val: List[Tuple[int, int]]) -> 'Result':
        return Result(value=val, error=None, is_ok=True)

    @staticmethod
    def err(err: str) -> 'Result':
        return Result(value=None, error=err, is_ok=False)

class Layer:
    def __init__(self, name: str, in_dim: int, out_dim: int):
        self.name = name
        self.in_dim = in_dim
        self.out_dim = out_dim

class SequentialModel:
    def __init__(self):
        self.layers: List[Layer] = []

    def add(self, layer: Layer) -> Result:
        if self.layers:
            prev_layer = self.layers[-1]
            if prev_layer.out_dim != layer.in_dim:
                return Result.err(f"Dimension mismatch: {prev_layer.name} outputs {prev_layer.out_dim}, but {layer.name} expects {layer.in_dim}")
        
        self.layers.append(layer)
        return Result.ok(None)

    def summary(self) -> Result:
        if not self.layers:
            return Result.err("Model has no layers.")
            
        dims = []
        for l in self.layers:
            dims.append((l.in_dim, l.out_dim))
            
        return Result.ok(dims)
