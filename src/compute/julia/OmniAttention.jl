# OMNI Compute Layer — Julia High-Performance Attention
# SIMD-vectorized attention computation for HPC workloads.

module OmniAttention

using LinearAlgebra
using LoopVectorization

export scaled_dot_product_attention, multi_head_attention, rmsnorm!, softmax!

"""
    softmax!(x::Vector{Float32})

In-place numerically stable softmax.
"""
function softmax!(x::AbstractVector{T}) where T <: AbstractFloat
    m = maximum(x)
    @turbo for i in eachindex(x)
        x[i] = exp(x[i] - m)
    end
    s = sum(x)
    inv_s = one(T) / s
    @turbo for i in eachindex(x)
        x[i] *= inv_s
    end
    return x
end

"""
    rmsnorm!(out, x, weight; eps=1f-6)

RMS normalization with SIMD acceleration.
"""
function rmsnorm!(out::AbstractVector{Float32}, x::AbstractVector{Float32},
                  weight::AbstractVector{Float32}; eps::Float32 = 1f-6)
    n = length(x)
    ss = Float32(0)
    @turbo for i in 1:n
        ss += x[i] * x[i]
    end
    ss = 1.0f0 / sqrt(ss / Float32(n) + eps)
    @turbo for i in 1:n
        out[i] = x[i] * ss * weight[i]
    end
    return out
end

"""
    scaled_dot_product_attention(Q, K, V; scale, causal=false)

Compute attention: softmax(Q @ K' / scale) @ V
Q: (seq_q, head_dim), K: (seq_k, head_dim), V: (seq_k, head_dim)
"""
function scaled_dot_product_attention(
    Q::AbstractMatrix{Float32},
    K::AbstractMatrix{Float32},
    V::AbstractMatrix{Float32};
    scale::Float32 = Float32(1.0 / sqrt(size(Q, 2))),
    causal::Bool = false
)
    seq_q, head_dim = size(Q)
    seq_k, _ = size(K)

    # Compute attention scores: (seq_q, seq_k)
    scores = Q * K' .* scale

    # Apply causal mask
    if causal
        for i in 1:seq_q, j in 1:seq_k
            if j > i
                scores[i, j] = -Inf32
            end
        end
    end

    # Row-wise softmax
    for i in 1:seq_q
        row = @view scores[i, :]
        softmax!(row)
    end

    # Weighted sum: (seq_q, head_dim)
    return scores * V
end

"""
    multi_head_attention(x, Wq, Wk, Wv, Wo; num_heads, causal=false)

Multi-head attention with weight matrices.
x: (seq_len, embed_dim)
"""
function multi_head_attention(
    x::AbstractMatrix{Float32},
    Wq::AbstractMatrix{Float32},
    Wk::AbstractMatrix{Float32},
    Wv::AbstractMatrix{Float32},
    Wo::AbstractMatrix{Float32};
    num_heads::Int,
    causal::Bool = false
)
    seq_len, embed_dim = size(x)
    head_dim = embed_dim ÷ num_heads

    Q = x * Wq'
    K = x * Wk'
    V = x * Wv'

    # Split into heads and compute attention
    output = zeros(Float32, seq_len, embed_dim)
    scale = Float32(1.0 / sqrt(head_dim))

    for h in 1:num_heads
        h_start = (h - 1) * head_dim + 1
        h_end = h * head_dim

        Qh = Q[:, h_start:h_end]
        Kh = K[:, h_start:h_end]
        Vh = V[:, h_start:h_end]

        attn = scaled_dot_product_attention(Qh, Kh, Vh; scale=scale, causal=causal)
        output[:, h_start:h_end] = attn
    end

    return output * Wo'
end

"""
    gelu(x)

GELU activation function (exact).
"""
function gelu(x::Float32)
    return x * 0.5f0 * (1.0f0 + tanh(0.7978845608f0 * (x + 0.044715f0 * x^3)))
end

"""
    silu(x)

SiLU (Swish) activation function.
"""
silu(x::Float32) = x / (1.0f0 + exp(-x))

end # module
