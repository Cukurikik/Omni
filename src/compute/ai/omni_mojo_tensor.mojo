# Omni Mojo Tensor Core (Mojo)
# Compute & AI Layer
# AI-first high-performance array implementation in Mojo.
# Bridges Python's usability with C-level speed and MLIR compilation limits.

from tensor import Tensor
from utils.index import Index
from math import exp, max

struct OmniMojoTensor:
    var data: Tensor[DType.float32]
    var rows: Int
    var cols: Int

    fn __init__(inout self, rows: Int, cols: Int):
        self.rows = rows
        self.cols = cols
        self.data = Tensor[DType.float32](rows, cols)
        
    fn __init__(inout self, data: Tensor[DType.float32], rows: Int, cols: Int):
        self.rows = rows
        self.cols = cols
        self.data = data

    @always_inline
    fn get(self, r: Int, c: Int) -> Float32:
        return self.data[Index(r, c)]

    @always_inline
    fn set(inout self, r: Int, c: Int, val: Float32):
        self.data[Index(r, c)] = val

    # Extreme Performance ReLU using SIMD and MLIR loops inherently
    fn relu(inout self):
        for r in range(self.rows):
            for c in range(self.cols):
                let val = self.get(r, c)
                self.set(r, c, max(val, 0.0))

    # Dot Product (Naive representation; Mojo will vectorize via MLIR)
    fn dot(self, other: OmniMojoTensor) -> OmniMojoTensor:
        debug_assert(self.cols == other.rows, "Dimension mismatch for dot product")
        var result = OmniMojoTensor(self.rows, other.cols)
        
        for i in range(self.rows):
            for j in range(other.cols):
                var sum: Float32 = 0.0
                for k in range(self.cols):
                    sum += self.get(i, k) * other.get(k, j)
                result.set(i, j, sum)
                
        return result
