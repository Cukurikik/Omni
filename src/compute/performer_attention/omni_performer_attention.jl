# omni_performer_attention.jl — Julia Random Feature Performer Attention
# Inspired by: Memformer + TVLT long-range attention needs
# Layer: Compute / Julia
#
# Linear-complexity attention via FAVOR+ random feature approximation.

module OmniPerformerAttention

using LinearAlgebra

export performer_attention, PerformerConfig

struct PerformerConfig
    dim::Int
    num_heads::Int
    head_dim::Int
    num_features::Int
    causal::Bool
end

function PerformerConfig(; dim=512, num_heads=8, num_features=256, causal=false)
    return PerformerConfig(dim, num_heads, div(dim, num_heads), num_features, causal)
end

function softmax_kernel_feature_map(x::Matrix{Float32}, omega::Matrix{Float32})
    m = size(omega, 2)
    proj = omega' * x
    norm_sq = sum(x .^ 2, dims=1) ./ 2.0f0
    scaling = exp.(-norm_sq) ./ sqrt(Float32(m))
    return vcat(cos.(proj), sin.(proj)) .* scaling
end

function causal_prefix_attention(
    phi_q::Matrix{Float32},
    phi_k::Matrix{Float32},
    v::Matrix{Float32}
)
    feat_dim = size(phi_q, 1)
    head_dim, seq_len = size(v)
    output = zeros(Float32, head_dim, seq_len)
    kv_sum = zeros(Float32, head_dim, feat_dim)
    k_sum = zeros(Float32, feat_dim)

    for t in 1:seq_len
        kt = @view phi_k[:, t]
        vt = @view v[:, t]
        qt = @view phi_q[:, t]

        kv_sum .+= vt * kt'
        k_sum .+= kt

        num = kv_sum * qt
        den = max(dot(k_sum, qt), 1.0f-8)
        output[:, t] = num ./ den
    end
    return output
end

function noncausal_linear_attention(
    phi_q::Matrix{Float32},
    phi_k::Matrix{Float32},
    v::Matrix{Float32}
)
    kv = v * phi_k'
    k_sum = sum(phi_k, dims=2)
    z = phi_q' * k_sum
    z = max.(z, 1.0f-8)
    raw = kv * phi_q
    return raw ./ z'
end

function performer_attention(
    Q::Array{Float32, 3},
    K::Array{Float32, 3},
    V::Array{Float32, 3},
    config::PerformerConfig
)
    hd, sl, batch = size(Q)
    omega = randn(Float32, hd, config.num_features) ./ sqrt(Float32(hd))
    output = similar(V)

    Threads.@threads for b in 1:batch
        q = @view Q[:, :, b]
        k = @view K[:, :, b]
        v = @view V[:, :, b]

        pq = softmax_kernel_feature_map(q, omega)
        pk = softmax_kernel_feature_map(k, omega)

        if config.causal
            output[:, :, b] = causal_prefix_attention(pq, pk, v)
        else
            output[:, :, b] = noncausal_linear_attention(pq, pk, v)
        end
    end
    return output
end

function multi_head_performer(
    Q::Array{Float32, 4},
    K::Array{Float32, 4},
    V::Array{Float32, 4},
    config::PerformerConfig
)
    hd, sl, nh, batch = size(Q)
    output = similar(V)

    Threads.@threads for b in 1:batch
        for h in 1:nh
            q3 = reshape(@view(Q[:, :, h, b]), hd, sl, 1)
            k3 = reshape(@view(K[:, :, h, b]), hd, sl, 1)
            v3 = reshape(@view(V[:, :, h, b]), hd, sl, 1)
            result = performer_attention(q3, k3, v3, config)
            output[:, :, h, b] = result[:, :, 1]
        end
    end
    return output
end

end
