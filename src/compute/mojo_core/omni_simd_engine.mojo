# ===========================================================================
# OMNI SIMD ENGINE (SEMESTER 3 — BATCH 38.10)
# ===========================================================================
# Absorbed From  : Mojo SIMD + Python numpy vectorization + autotune
# Logic Inherited: Mojo / Compute Layer (AI-First High Performance)
# ===========================================================================
#
# By studying Mojo SIMD, Mother learned:
#   1. SIMD[DType, width] processes multiple elements in single instruction
#   2. Vectorize: auto-applies SIMD across loop iterations
#   3. Parallelize: splits work across CPU cores
#   4. fn vs def: fn is strict (checked), def is Python-compatible
#   5. @parameter: compile-time evaluated metaprogramming

from memory import memset_zero, memcpy
from sys.info import simdwidthof, num_physical_cores
from algorithm import vectorize, parallelize
from math import sqrt, abs, min, max

# ============================================================
# PART 1: SIMD Vector Operations
# ============================================================

struct OmniSIMDEngine:
    """
    High-performance SIMD operations for numerical computing.
    Processes multiple data elements per CPU instruction.
    """

    alias float_type = DType.float64
    alias simd_width = simdwidthof[float_type]()

    @staticmethod
    fn dot_product(a: DTypePointer[DType.float64], b: DTypePointer[DType.float64], n: Int) -> Float64:
        """SIMD-accelerated dot product."""
        var result = SIMD[DType.float64, Self.simd_width](0)

        @parameter
        fn _dot[simd_width: Int](idx: Int):
            let va = a.load[width=simd_width](idx)
            let vb = b.load[width=simd_width](idx)
            result += (va * vb).reduce_add()

        vectorize[_dot, Self.simd_width](n)
        return result.reduce_add()

    @staticmethod
    fn vector_add(
        a: DTypePointer[DType.float64],
        b: DTypePointer[DType.float64],
        result: DTypePointer[DType.float64],
        n: Int
    ):
        """SIMD element-wise addition."""
        @parameter
        fn _add[simd_width: Int](idx: Int):
            let va = a.load[width=simd_width](idx)
            let vb = b.load[width=simd_width](idx)
            result.store[width=simd_width](idx, va + vb)

        vectorize[_add, Self.simd_width](n)

    @staticmethod
    fn vector_scale(
        data: DTypePointer[DType.float64],
        result: DTypePointer[DType.float64],
        scalar: Float64,
        n: Int
    ):
        """SIMD scalar multiplication."""
        let s = SIMD[DType.float64, Self.simd_width](scalar)

        @parameter
        fn _scale[simd_width: Int](idx: Int):
            let v = data.load[width=simd_width](idx)
            result.store[width=simd_width](idx, v * s)

        vectorize[_scale, Self.simd_width](n)

    @staticmethod
    fn euclidean_norm(data: DTypePointer[DType.float64], n: Int) -> Float64:
        """SIMD-accelerated L2 norm (Euclidean distance from origin)."""
        var sum_sq = SIMD[DType.float64, Self.simd_width](0)

        @parameter
        fn _norm[simd_width: Int](idx: Int):
            let v = data.load[width=simd_width](idx)
            sum_sq += v * v

        vectorize[_norm, Self.simd_width](n)
        return sqrt(sum_sq.reduce_add())

    @staticmethod
    fn softmax(
        input_data: DTypePointer[DType.float64],
        output_data: DTypePointer[DType.float64],
        n: Int
    ):
        """Numerically stable softmax (used in AI inference)."""
        # Find max for numerical stability
        var max_val = input_data.load[width=1](0)
        for i in range(1, n):
            let v = input_data.load[width=1](i)
            if v > max_val:
                max_val = v

        # Compute exp(x - max) and sum
        var exp_sum: Float64 = 0.0
        for i in range(n):
            let v = input_data.load[width=1](i)
            let exp_v = (v - max_val).exp()
            output_data.store[width=1](i, exp_v)
            exp_sum += exp_v

        # Normalize
        let inv_sum = 1.0 / exp_sum
        @parameter
        fn _normalize[simd_width: Int](idx: Int):
            let v = output_data.load[width=simd_width](idx)
            output_data.store[width=simd_width](idx, v * inv_sum)

        vectorize[_normalize, Self.simd_width](n)


# ============================================================
# PART 2: Parallel Matrix Operations
# ============================================================

struct OmniMatrix:
    """
    Row-major matrix with parallel SIMD operations.
    """
    var data: DTypePointer[DType.float64]
    var rows: Int
    var cols: Int

    fn __init__(inout self, rows: Int, cols: Int):
        self.rows = rows
        self.cols = cols
        self.data = DTypePointer[DType.float64].alloc(rows * cols)
        memset_zero(self.data, rows * cols)

    fn __del__(owned self):
        self.data.free()

    fn set(inout self, row: Int, col: Int, value: Float64):
        self.data.store[width=1](row * self.cols + col, value)

    fn get(self, row: Int, col: Int) -> Float64:
        return self.data.load[width=1](row * self.cols + col)

    @staticmethod
    fn matmul_parallel(
        a: OmniMatrix, b: OmniMatrix, result: OmniMatrix
    ):
        """Parallel SIMD matrix multiplication."""
        let num_cores = num_physical_cores()

        @parameter
        fn _compute_row(row: Int):
            for col in range(b.cols):
                var sum: Float64 = 0.0
                for k in range(a.cols):
                    sum += a.get(row, k) * b.get(k, col)
                result.data.store[width=1](
                    row * result.cols + col, sum
                )

        parallelize[_compute_row](a.rows, num_cores)

    fn transpose(self) -> OmniMatrix:
        """Return transposed matrix."""
        var result = OmniMatrix(self.cols, self.rows)
        for r in range(self.rows):
            for c in range(self.cols):
                result.set(c, r, self.get(r, c))
        return result


# ============================================================
# PART 3: Performance Benchmarking
# ============================================================

struct OmniBenchmark:
    """Benchmark utilities for measuring SIMD performance."""

    @staticmethod
    fn measure[func: fn() -> None](iterations: Int) -> Float64:
        """Measure average execution time in microseconds."""
        from time import now

        let start = now()
        for _ in range(iterations):
            func()
        let elapsed = now() - start
        return Float64(elapsed) / Float64(iterations) / 1000.0  # ns → μs


# ============================================================
# Diagnostics
# ============================================================

fn diagnostics() -> String:
    return String(
        """
        engine: OmniSIMDEngine
        layer: Mojo Compute
        simd_width: """ + str(simdwidthof[DType.float64]()) + """
        cpu_cores: """ + str(num_physical_cores()) + """
        components:
          - OmniSIMDEngine (dot_product, vector_add, scale, norm, softmax)
          - OmniMatrix (matmul_parallel, transpose)
          - OmniBenchmark (measure)
        learned_logic:
          - simd-multi-element-instruction
          - vectorize-auto-simd-loop
          - parallelize-multi-core-split
          - parameter-comptime-metaprog
          - softmax-numerical-stability
          - matmul-parallel-row-compute
          - reduce-add-simd-horizontal
          - fn-strict-type-checking
        """
    )
