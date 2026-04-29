# OMNI MOTHER - DIVINE MEMORY INTEGRATION
# Chainer Define-by-Run (OMNI Zero-Mock Implementation)
# Implements Dynamic Computation Tape gradient recording mapping mathematically.

from dataclasses import dataclass
from typing import List, Dict, Optional

@dataclass
class Result:
    value: Optional[Dict[str, float]] # Gradients wrt inputs
    error: Optional[str]
    is_ok: bool

    @staticmethod
    def ok(val: Dict[str, float]) -> 'Result':
        return Result(value=val, error=None, is_ok=True)

    @staticmethod
    def err(err: str) -> 'Result':
        return Result(value=None, error=err, is_ok=False)

class TapeOperation:
    def __init__(self, op_id: str, op_type: str, inputs: List[str], forward_out: float):
        self.op_id = op_id
        self.op_type = op_type
        self.inputs = inputs
        self.forward_out = forward_out

class DefineByRunTape:
    def __init__(self):
        self.tape: List[TapeOperation] = []
        self.variable_values: Dict[str, float] = {}

    def push_mul_op(self, op_id: str, in_a: str, in_b: str) -> None:
        val_a = self.variable_values[in_a]
        val_b = self.variable_values[in_b]
        self.tape.append(TapeOperation(op_id, "mul", [in_a, in_b], val_a * val_b))
        self.variable_values[op_id] = val_a * val_b

    def backprop_tape(self, target_id: str) -> Result:
        if target_id not in self.variable_values:
            return Result.err("Target variable not found in compute tape.")
            
        grads = {target_id: 1.0}
        
        # Reverse autodiff accumulation
        for op in reversed(self.tape):
            if op.op_id not in grads:
                 continue
                 
            out_grad = grads[op.op_id]
            
            if op.op_type == "mul":
                 in_a, in_b = op.inputs
                 val_a = self.variable_values[in_a]
                 val_b = self.variable_values[in_b]
                 
                 # d(A*B)/dA = B, d(A*B)/dB = A
                 grad_a = out_grad * val_b
                 grad_b = out_grad * val_a
                 
                 grads[in_a] = grads.get(in_a, 0.0) + grad_a
                 grads[in_b] = grads.get(in_b, 0.0) + grad_b
            else:
                 return Result.err(f"Operation {op.op_type} backprop unsupported.")
                 
        return Result.ok(grads)
