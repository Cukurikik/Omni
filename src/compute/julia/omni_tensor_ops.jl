# OMNI Compute — Julia High-Performance Tensor Ops
# SIMD-vectorized matrix operations for inference.

module OmniTensor

using LinearAlgebra, LoopVectorization

export omni_matmul!, omni_rmsnorm!, omni_softmax!, omni_gelu!, omni_rope!

"""SIMD-accelerated matrix multiply C = A * B'."""
function omni_matmul!(C::Matrix{Float32}, A::Matrix{Float32}, B::Matrix{Float32})
    M, K = size(A); _, N = size(B)
    @turbo for n in 1:N, m in 1:M
        s = zero(Float32)
        for k in 1:K
            s += A[m, k] * B[k, n]
        end
        C[m, n] = s
    end
    return C
end

"""RMS Layer Normalization."""
function omni_rmsnorm!(out::Vector{Float32}, x::Vector{Float32}, w::Vector{Float32}; eps::Float32=1f-5)
    n = length(x)
    ss = zero(Float32)
    @turbo for i in 1:n
        ss += x[i] * x[i]
    end
    ss = 1.0f0 / sqrt(ss / Float32(n) + eps)
    @turbo for i in 1:n
        out[i] = w[i] * (x[i] * ss)
    end
    return out
end

"""In-place softmax."""
function omni_softmax!(x::Vector{Float32})
    m = maximum(x)
    s = zero(Float32)
    @turbo for i in eachindex(x)
        x[i] = exp(x[i] - m)
        s += x[i]
    end
    inv_s = 1.0f0 / s
    @turbo for i in eachindex(x)
        x[i] *= inv_s
    end
    return x
end

"""GELU activation in-place."""
function omni_gelu!(x::Vector{Float32})
    @turbo for i in eachindex(x)
        v = x[i]
        x[i] = 0.5f0 * v * (1.0f0 + tanh(0.7978845608f0 * (v + 0.044715f0 * v^3)))
    end
    return x
end

"""Apply Rotary Position Embedding."""
function omni_rope!(q::Matrix{Float32}, k::Matrix{Float32}, pos::Int; base::Float32=10000.0f0)
    head_dim = size(q, 1)
    for i in 1:2:head_dim
        freq = 1.0f0 / (base ^ (Float32(i - 1) / Float32(head_dim)))
        theta = Float32(pos) * freq
        cos_t, sin_t = cos(theta), sin(theta)
        # Rotate Q
        q0, q1 = q[i, :], q[i+1, :]
        q[i, :] .= q0 .* cos_t .- q1 .* sin_t
        q[i+1, :] .= q1 .* cos_t .+ q0 .* sin_t
        # Rotate K
        k0, k1 = k[i, :], k[i+1, :]
        k[i, :] .= k0 .* cos_t .- k1 .* sin_t
        k[i+1, :] .= k1 .* cos_t .+ k0 .* sin_t
    end
end

"""Benchmark tensor ops."""
function benchmark_matmul(M::Int, K::Int, N::Int; iters::Int=100)
    A = rand(Float32, M, K); B = rand(Float32, K, N); C = zeros(Float32, M, N)
    # Warmup
    omni_matmul!(C, A, B)
    t = @elapsed for _ in 1:iters; omni_matmul!(C, A, B); end
    gflops = 2.0 * M * K * N * iters / t / 1e9
    println("MatMul $(M)x$(K)x$(N): $(round(gflops, digits=2)) GFLOPS")
    return gflops
end

end # module
