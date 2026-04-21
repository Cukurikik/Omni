# ===========================================================================
# OMNI MATRIX COMPUTE ENGINE (SEMESTER 3 REMEDIATION — BATCH 38.1)
# ===========================================================================
# Absorbed From  : LinearAlgebra.jl + StaticArrays.jl + BLAS concepts
# Logic Inherited: Julia / Compute Layer (SIMD-Ready Matrix Operations)
# Domain Layer   : Compute (Julia Core)
# ===========================================================================
#
# By studying Julia's LinearAlgebra stdlib and StaticArrays.jl, Mother
# learned that Julia's multiple dispatch + column-major storage enables
# matrix operations that rival hand-tuned BLAS:
#   1. Column-major iteration for cache-friendly access patterns
#   2. @inbounds + @simd for loop vectorization without bounds checks
#   3. Generic type parameterization via Julia's type system
#   4. In-place operations (mul!, add!) to avoid allocation
#
# Julia is THE language for numerical computing in OMNI's Compute Layer.

module OmniMatrixComputeEngine

export OmniMatrix, zeros_matrix, ones_matrix, identity_matrix,
       mat_add!, mat_mul!, mat_transpose!, mat_scale!,
       mat_determinant, mat_trace, mat_frobenius_norm,
       diagnostics

"""
    OmniMatrix{T<:Number}

Column-major dense matrix with pre-allocated storage.
Stores data in a flat Vector for cache-friendly column access.
"""
mutable struct OmniMatrix{T<:Number}
    data::Vector{T}
    rows::Int
    cols::Int
    # Statistics
    total_ops::Int
end

# ---- Constructors ----

"""Create a zero-filled matrix."""
function zeros_matrix(::Type{T}, rows::Int, cols::Int) where T<:Number
    return OmniMatrix{T}(zeros(T, rows * cols), rows, cols, 0)
end

"""Create a ones-filled matrix."""
function ones_matrix(::Type{T}, rows::Int, cols::Int) where T<:Number
    return OmniMatrix{T}(ones(T, rows * cols), rows, cols, 0)
end

"""Create an identity matrix."""
function identity_matrix(::Type{T}, n::Int) where T<:Number
    m = zeros_matrix(T, n, n)
    @inbounds for i in 1:n
        m.data[(i - 1) * n + i] = one(T)
    end
    return m
end

"""Create matrix from 2D array."""
function OmniMatrix(arr::Matrix{T}) where T<:Number
    rows, cols = size(arr)
    data = Vector{T}(undef, rows * cols)
    # Column-major copy
    @inbounds for j in 1:cols
        for i in 1:rows
            data[(j - 1) * rows + i] = arr[i, j]
        end
    end
    return OmniMatrix{T}(data, rows, cols, 0)
end

# ---- Element Access (1-indexed, column-major) ----

"""Get element at (row, col). O(1) via column-major indexing."""
@inline function Base.getindex(m::OmniMatrix{T}, i::Int, j::Int) where T
    @boundscheck (1 <= i <= m.rows && 1 <= j <= m.cols) ||
        throw(BoundsError(m, (i, j)))
    @inbounds return m.data[(j - 1) * m.rows + i]
end

"""Set element at (row, col)."""
@inline function Base.setindex!(m::OmniMatrix{T}, val::T, i::Int, j::Int) where T
    @boundscheck (1 <= i <= m.rows && 1 <= j <= m.cols) ||
        throw(BoundsError(m, (i, j)))
    @inbounds m.data[(j - 1) * m.rows + i] = val
end

Base.size(m::OmniMatrix) = (m.rows, m.cols)

# ---- In-Place Operations (zero allocation) ----

"""
    mat_add!(C, A, B)

In-place matrix addition: C = A + B.
Uses @simd for vectorized loop execution.
"""
function mat_add!(C::OmniMatrix{T}, A::OmniMatrix{T}, B::OmniMatrix{T}) where T
    @assert A.rows == B.rows == C.rows && A.cols == B.cols == C.cols
    n = length(A.data)
    @inbounds @simd for k in 1:n
        C.data[k] = A.data[k] + B.data[k]
    end
    C.total_ops += n
    return C
end

"""
    mat_scale!(C, A, scalar)

In-place scalar multiplication: C = scalar * A.
"""
function mat_scale!(C::OmniMatrix{T}, A::OmniMatrix{T}, s::T) where T
    n = length(A.data)
    @inbounds @simd for k in 1:n
        C.data[k] = s * A.data[k]
    end
    C.total_ops += n
    return C
end

"""
    mat_mul!(C, A, B)

In-place matrix multiplication: C = A * B.
Uses column-major access pattern for cache efficiency.
Inner loop is @simd-vectorized over rows.
"""
function mat_mul!(C::OmniMatrix{T}, A::OmniMatrix{T}, B::OmniMatrix{T}) where T
    @assert A.cols == B.rows && C.rows == A.rows && C.cols == B.cols
    m, n, p = A.rows, B.cols, A.cols

    # Zero out C
    fill!(C.data, zero(T))

    # Column-major triple loop: j (col of B), k (col of A / row of B), i (row of A)
    # This order maximizes column-major cache hits
    @inbounds for j in 1:n
        for k in 1:p
            b_kj = B.data[(j - 1) * B.rows + k]
            @simd for i in 1:m
                C.data[(j - 1) * m + i] += A.data[(k - 1) * m + i] * b_kj
            end
        end
    end

    C.total_ops += 2 * m * n * p  # multiply + add per element
    return C
end

"""
    mat_transpose!(B, A)

In-place transpose: B = Aᵀ.
"""
function mat_transpose!(B::OmniMatrix{T}, A::OmniMatrix{T}) where T
    @assert B.rows == A.cols && B.cols == A.rows
    @inbounds for j in 1:A.cols
        for i in 1:A.rows
            B.data[(i - 1) * B.rows + j] = A.data[(j - 1) * A.rows + i]
        end
    end
    B.total_ops += A.rows * A.cols
    return B
end

# ---- Reductions ----

"""Matrix trace (sum of diagonal elements)."""
function mat_trace(A::OmniMatrix{T}) where T
    @assert A.rows == A.cols "Trace requires square matrix"
    s = zero(T)
    @inbounds for i in 1:A.rows
        s += A.data[(i - 1) * A.rows + i]
    end
    return s
end

"""Frobenius norm: ||A||_F = sqrt(sum(a_ij^2))."""
function mat_frobenius_norm(A::OmniMatrix{T}) where T
    s = zero(T)
    @inbounds @simd for k in 1:length(A.data)
        s += A.data[k] * A.data[k]
    end
    return sqrt(s)
end

"""
    mat_determinant(A)

Determinant via LU decomposition (in-place Gaussian elimination).
Only for square matrices.
"""
function mat_determinant(A::OmniMatrix{T}) where T<:AbstractFloat
    @assert A.rows == A.cols "Determinant requires square matrix"
    n = A.rows
    # Work on a copy
    work = copy(A.data)
    det = one(T)
    swaps = 0

    @inbounds for col in 1:n
        # Partial pivot
        max_val = abs(work[(col - 1) * n + col])
        max_row = col
        for row in (col + 1):n
            v = abs(work[(col - 1) * n + row])
            if v > max_val
                max_val = v
                max_row = row
            end
        end

        if max_val < eps(T)
            return zero(T)  # Singular
        end

        # Swap rows
        if max_row != col
            swaps += 1
            for j in 1:n
                idx1 = (j - 1) * n + col
                idx2 = (j - 1) * n + max_row
                work[idx1], work[idx2] = work[idx2], work[idx1]
            end
        end

        pivot = work[(col - 1) * n + col]
        det *= pivot

        # Eliminate below
        for row in (col + 1):n
            factor = work[(col - 1) * n + row] / pivot
            for j in col:n
                work[(j - 1) * n + row] -= factor * work[(j - 1) * n + col]
            end
        end
    end

    return iseven(swaps) ? det : -det
end

# ---- Diagnostics ----

"""OMNI Engine Registry diagnostics."""
function diagnostics(m::OmniMatrix{T}) where T
    return Dict{String, Any}(
        "engine" => "OmniMatrixComputeEngine",
        "layer" => "Julia Compute",
        "element_type" => string(T),
        "dimensions" => "$(m.rows)×$(m.cols)",
        "total_elements" => m.rows * m.cols,
        "total_ops_performed" => m.total_ops,
        "memory_bytes" => sizeof(T) * length(m.data),
        "storage_layout" => "column-major",
        "learned_logic" => [
            "column-major-cache-friendly-iteration",
            "simd-vectorized-inner-loops",
            "inbounds-elide-bounds-checks",
            "in-place-zero-allocation-ops",
            "partial-pivot-lu-determinant",
            "multiple-dispatch-generic-types",
            "jkm-loop-order-matmul",
        ]
    )
end

end # module
