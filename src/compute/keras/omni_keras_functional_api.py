# OMNI MOTHER - DIVINE MEMORY INTEGRATION
# Keras Functional API (OMNI Zero-Mock Implementation)
# Implements multi-input directed acyclic tensor shapes inference validator.

from dataclasses import dataclass
from typing import List, Dict, Tuple, Optional

@dataclass
class Result:
    value: Optional[Tuple[int, ...]] # The output shape of the layer
    error: Optional[str]
    is_ok: bool

    @staticmethod
    def ok(val: Tuple[int, ...]) -> 'Result':
        return Result(value=val, error=None, is_ok=True)

    @staticmethod
    def err(err: str) -> 'Result':
        return Result(value=None, error=err, is_ok=False)

class KerasShapeInference:
    def infer_dense_shape(self, input_shape: Tuple[int, ...], units: int) -> Result:
        if not input_shape:
             return Result.err("Input shape cannot be empty.")
        if units <= 0:
             return Result.err("Dense units must be strictly positive.")
             
        # Dense keeps batch and all intermediate dims, changes only last dimension
        out_shape = list(input_shape)
        out_shape[-1] = units
        
        return Result.ok(tuple(out_shape))
        
    def infer_concat_shape(self, input_shapes: List[Tuple[int, ...]], axis: int) -> Result:
        if not input_shapes:
             return Result.err("Concatenation requires at least one input shape.")
             
        rank = len(input_shapes[0])
        
        # Negative axis validation
        if axis < 0:
             axis = rank + axis
             
        if axis < 0 or axis >= rank:
             return Result.err(f"Axis {axis} is out of bounds for tensor rank {rank}.")
             
        # Validate all shapes match exactly except for the concatenated axis
        for shape in input_shapes:
             if len(shape) != rank:
                 return Result.err("All tensors in concatenation must have the same rank.")
             for d in range(rank):
                 if d != axis and shape[d] != input_shapes[0][d]:
                     return Result.err("Concatenation dimension mismatch.")
                     
        total_dim = sum(shape[axis] for shape in input_shapes)
        out_shape = list(input_shapes[0])
        out_shape[axis] = total_dim
        
        return Result.ok(tuple(out_shape))
