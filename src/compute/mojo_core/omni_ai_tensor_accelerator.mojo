# Omni Tensor Accelerator in Mojo
# High-performance AI computing bypassing Python GIL

from tensor import Tensor
from math import sqrt

struct OmniMojoEngine:
    var dim: Int

    fn __init__(inout self, dim: Int):
        self.dim = dim
        
    fn compute_l2_norm(self, t: Tensor[DType.float32]) raises -> Float32:
        if t.num_elements() != self.dim:
            raise Error("Dimension mismatch in OmniMojoEngine")
            
        var sum_sq: Float32 = 0.0
        for i in range(self.dim):
            sum_sq += t[i] * t[i]
            
        return sqrt(sum_sq)

fn run_accelerator(t: Tensor[DType.float32]) -> Float32:
    try:
        var engine = OmniMojoEngine(t.num_elements())
        return engine.compute_l2_norm(t)
    except:
        return -1.0
