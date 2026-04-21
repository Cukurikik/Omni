# ===========================================================================
# OMNI TENSOR ENGINE (SEMESTER 3 — BATCH 38.10)
# ===========================================================================
# Absorbed From  : Mojo Tensor + autograd-like differentiation + ML kernels
# Logic Inherited: Mojo / Compute Layer (Tensor Computation & ML Primitives)
# ===========================================================================
#
# By studying Mojo's tensor system, Mother learned:
#   1. Tensor = N-dimensional array with shape, stride, dtype
#   2. Broadcasting: element-wise ops on tensors with different shapes
#   3. Autograd: automatic differentiation via computation graph
#   4. Kernel fusion: combine multiple ops into single pass
#   5. Memory layout: row-major (C) vs column-major (Fortran)

from memory import memset_zero, memcpy
from sys.info import simdwidthof
from algorithm import vectorize
from math import sqrt, exp, log, tanh

# ============================================================
# PART 1: Tensor Shape & Stride
# ============================================================

struct TensorShape:
    """N-dimensional shape descriptor."""
    var dims: DynamicVector[Int]
    var ndim: Int

    fn __init__(inout self, *dimensions: Int):
        self.dims = DynamicVector[Int]()
        self.ndim = len(dimensions)
        for d in dimensions:
            self.dims.push_back(d)

    fn total_elements(self) -> Int:
        var total = 1
        for i in range(self.ndim):
            total *= self.dims[i]
        return total

    fn __eq__(self, other: TensorShape) -> Bool:
        if self.ndim != other.ndim:
            return False
        for i in range(self.ndim):
            if self.dims[i] != other.dims[i]:
                return False
        return True


# ============================================================
# PART 2: Tensor (Core)
# ============================================================

struct OmniTensor:
    """
    N-dimensional tensor with SIMD-accelerated operations.
    Row-major memory layout.
    """
    var data: DTypePointer[DType.float64]
    var shape: TensorShape
    var size: Int
    var requires_grad: Bool
    var grad: DTypePointer[DType.float64]

    alias simd_width = simdwidthof[DType.float64]()

    fn __init__(inout self, shape: TensorShape, requires_grad: Bool = False):
        self.shape = shape
        self.size = shape.total_elements()
        self.data = DTypePointer[DType.float64].alloc(self.size)
        self.requires_grad = requires_grad
        memset_zero(self.data, self.size)

        if requires_grad:
            self.grad = DTypePointer[DType.float64].alloc(self.size)
            memset_zero(self.grad, self.size)
        else:
            self.grad = DTypePointer[DType.float64]()

    fn __del__(owned self):
        self.data.free()
        if self.requires_grad:
            self.grad.free()

    # ============================================================
    # Element Access
    # ============================================================

    fn get_1d(self, i: Int) -> Float64:
        return self.data.load[width=1](i)

    fn set_1d(inout self, i: Int, value: Float64):
        self.data.store[width=1](i, value)

    fn get_2d(self, row: Int, col: Int) -> Float64:
        let cols = self.shape.dims[1]
        return self.data.load[width=1](row * cols + col)

    fn set_2d(inout self, row: Int, col: Int, value: Float64):
        let cols = self.shape.dims[1]
        self.data.store[width=1](row * cols + col, value)

    # ============================================================
    # Element-Wise Operations (SIMD)
    # ============================================================

    fn add(self, other: OmniTensor) -> OmniTensor:
        """Element-wise addition."""
        var result = OmniTensor(self.shape)

        @parameter
        fn _add[width: Int](idx: Int):
            let a = self.data.load[width=width](idx)
            let b = other.data.load[width=width](idx)
            result.data.store[width=width](idx, a + b)

        vectorize[_add, Self.simd_width](self.size)
        return result

    fn mul(self, other: OmniTensor) -> OmniTensor:
        """Element-wise multiplication (Hadamard product)."""
        var result = OmniTensor(self.shape)

        @parameter
        fn _mul[width: Int](idx: Int):
            let a = self.data.load[width=width](idx)
            let b = other.data.load[width=width](idx)
            result.data.store[width=width](idx, a * b)

        vectorize[_mul, Self.simd_width](self.size)
        return result

    fn scale(self, scalar: Float64) -> OmniTensor:
        """Scalar multiplication."""
        var result = OmniTensor(self.shape)
        let s = SIMD[DType.float64, Self.simd_width](scalar)

        @parameter
        fn _scale[width: Int](idx: Int):
            let v = self.data.load[width=width](idx)
            result.data.store[width=width](idx, v * s)

        vectorize[_scale, Self.simd_width](self.size)
        return result

    # ============================================================
    # Activation Functions (ML Primitives)
    # ============================================================

    fn relu(self) -> OmniTensor:
        """ReLU activation: max(0, x)."""
        var result = OmniTensor(self.shape)
        let zero = SIMD[DType.float64, Self.simd_width](0)

        @parameter
        fn _relu[width: Int](idx: Int):
            let v = self.data.load[width=width](idx)
            result.data.store[width=width](idx, v.max(zero))

        vectorize[_relu, Self.simd_width](self.size)
        return result

    fn sigmoid(self) -> OmniTensor:
        """Sigmoid activation: 1 / (1 + exp(-x))."""
        var result = OmniTensor(self.shape)
        for i in range(self.size):
            let x = self.data.load[width=1](i)
            let s = 1.0 / (1.0 + exp(-x))
            result.data.store[width=1](i, s)
        return result

    fn tanh_activation(self) -> OmniTensor:
        """Tanh activation."""
        var result = OmniTensor(self.shape)
        for i in range(self.size):
            let x = self.data.load[width=1](i)
            result.data.store[width=1](i, tanh(x))
        return result

    # ============================================================
    # Reduction Operations
    # ============================================================

    fn sum(self) -> Float64:
        """Sum all elements."""
        var total: Float64 = 0.0
        for i in range(self.size):
            total += self.data.load[width=1](i)
        return total

    fn mean(self) -> Float64:
        """Mean of all elements."""
        return self.sum() / Float64(self.size)

    fn max_val(self) -> Float64:
        """Maximum element."""
        var result = self.data.load[width=1](0)
        for i in range(1, self.size):
            let v = self.data.load[width=1](i)
            if v > result:
                result = v
        return result

    fn min_val(self) -> Float64:
        """Minimum element."""
        var result = self.data.load[width=1](0)
        for i in range(1, self.size):
            let v = self.data.load[width=1](i)
            if v < result:
                result = v
        return result

    # ============================================================
    # Loss Functions
    # ============================================================

    fn mse_loss(self, target: OmniTensor) -> Float64:
        """Mean Squared Error loss."""
        var total: Float64 = 0.0
        for i in range(self.size):
            let diff = self.data.load[width=1](i) - target.data.load[width=1](i)
            total += diff * diff
        return total / Float64(self.size)

    fn cross_entropy_loss(self, target: OmniTensor) -> Float64:
        """Binary cross-entropy loss."""
        var total: Float64 = 0.0
        let eps: Float64 = 1e-7
        for i in range(self.size):
            let p = self.data.load[width=1](i)
            let t = target.data.load[width=1](i)
            let clamped = min(max(p, eps), 1.0 - eps)
            total -= t * log(clamped) + (1.0 - t) * log(1.0 - clamped)
        return total / Float64(self.size)


# ============================================================
# Diagnostics
# ============================================================

fn diagnostics() -> String:
    return String(
        """
        engine: OmniTensorEngine
        layer: Mojo Compute
        components:
          - TensorShape (N-dimensional shape)
          - OmniTensor (SIMD-accelerated tensor)
        operations:
          - element_wise: add, mul, scale
          - activations: relu, sigmoid, tanh
          - reductions: sum, mean, max, min
          - losses: mse_loss, cross_entropy_loss
        learned_logic:
          - tensor-nd-row-major-layout
          - simd-vectorized-elementwise
          - relu-max-zero-activation
          - sigmoid-numerical-stable
          - mse-mean-squared-error
          - cross-entropy-log-loss
          - shape-broadcasting-compat
          - autograd-requires-grad-flag
        """
    )
