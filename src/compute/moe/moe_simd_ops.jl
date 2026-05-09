# moe_simd_ops.jl — SIMD-Optimized MoE Routing Operations
# Layer: Compute / HPC — MoE Numerical Operations (Julia)
#
# Julia-native SIMD implementations for MoE router computations:
# - Vectorized softmax
# - Top-k selection with partial sort
# - Load balance loss computation
# - Expert capacity management

module MoESIMDOps

using LinearAlgebra
using Statistics

export softmax!, topk_select, load_balance_loss, expert_capacity_mask
export MoERoutingResult, route_tokens

struct MoERoutingResult
    expert_indices::Matrix{Int32}     # (N, top_k)
    expert_weights::Matrix{Float32}   # (N, top_k)
    all_probs::Matrix{Float32}        # (N, num_experts)
    load_balance_loss::Float32
    expert_counts::Vector{Int32}
end

"""
    softmax!(out, logits)

In-place numerically stable softmax with SIMD-friendly loop structure.
Processes each row independently for cache efficiency.
"""
function softmax!(out::Matrix{Float32}, logits::Matrix{Float32})
    N, E = size(logits)
    @inbounds for i in 1:N
        # Find max for numerical stability
        max_val = logits[i, 1]
        @simd for j in 2:E
            max_val = max(max_val, logits[i, j])
        end

        # Compute exp and sum
        sum_exp = Float32(0.0)
        @simd for j in 1:E
            out[i, j] = exp(logits[i, j] - max_val)
            sum_exp += out[i, j]
        end

        # Normalize
        inv_sum = Float32(1.0) / (sum_exp + Float32(1e-8))
        @simd for j in 1:E
            out[i, j] *= inv_sum
        end
    end
    return out
end

"""
    topk_select(probs, k)

Select top-k experts per token using partial sort.
Returns indices and normalized weights.
"""
function topk_select(probs::Matrix{Float32}, k::Int)
    N, E = size(probs)
    indices = zeros(Int32, N, k)
    weights = zeros(Float32, N, k)

    @inbounds for i in 1:N
        # Simple selection sort for small k
        selected = Set{Int}()
        for ki in 1:k
            best_idx = -1
            best_val = Float32(-Inf)
            for j in 1:E
                if j ∉ selected && probs[i, j] > best_val
                    best_val = probs[i, j]
                    best_idx = j
                end
            end
            indices[i, ki] = Int32(best_idx)
            weights[i, ki] = best_val
            push!(selected, best_idx)
        end

        # Normalize top-k weights
        w_sum = Float32(0.0)
        @simd for ki in 1:k
            w_sum += weights[i, ki]
        end
        if w_sum > Float32(0.0)
            inv_w = Float32(1.0) / w_sum
            @simd for ki in 1:k
                weights[i, ki] *= inv_w
            end
        end
    end

    return indices, weights
end

"""
    load_balance_loss(probs, indices, num_experts)

Compute the auxiliary load balance loss L_aux = N * Σ(f_i * p_i).
"""
function load_balance_loss(
    probs::Matrix{Float32},
    indices::Matrix{Int32},
    num_experts::Int
)::Float32
    N = size(probs, 1)
    inv_N = Float32(1.0) / Float32(max(N, 1))

    # f_i: fraction of tokens routed to expert i (top-1)
    f = zeros(Float32, num_experts)
    @inbounds for i in 1:N
        eid = indices[i, 1]
        if 1 <= eid <= num_experts
            f[eid] += inv_N
        end
    end

    # p_i: average router probability for expert i
    p = zeros(Float32, num_experts)
    @inbounds for i in 1:N
        @simd for j in 1:num_experts
            p[j] += probs[i, j]
        end
    end
    @simd for j in 1:num_experts
        p[j] *= inv_N
    end

    # L_aux = N * Σ(f_i * p_i)
    loss = Float32(0.0)
    @simd for j in 1:num_experts
        loss += f[j] * p[j]
    end

    return loss * Float32(num_experts)
end

"""
    expert_capacity_mask(indices, num_experts, capacity)

Create a boolean mask indicating which tokens are within expert capacity.
Tokens exceeding capacity are marked for dropping.
"""
function expert_capacity_mask(
    indices::Matrix{Int32},
    num_experts::Int,
    capacity::Int
)::BitMatrix
    N, K = size(indices)
    mask = trues(N, K)
    counts = zeros(Int32, num_experts)

    @inbounds for i in 1:N
        for k in 1:K
            eid = indices[i, k]
            if 1 <= eid <= num_experts
                counts[eid] += Int32(1)
                if counts[eid] > capacity
                    mask[i, k] = false
                end
            end
        end
    end

    return mask
end

"""
    route_tokens(logits, top_k, capacity_factor, noise_std)

Full routing pipeline: softmax → top-k → capacity → load balance loss.
"""
function route_tokens(
    logits::Matrix{Float32};
    top_k::Int = 2,
    capacity_factor::Float32 = Float32(1.25),
    noise_std::Float32 = Float32(0.1)
)::MoERoutingResult
    N, E = size(logits)

    # Add noise for exploration (training only)
    if noise_std > 0
        noisy = logits .+ randn(Float32, N, E) .* noise_std
    else
        noisy = logits
    end

    # Softmax
    probs = similar(noisy)
    softmax!(probs, noisy)

    # Top-k selection
    indices, weights = topk_select(probs, top_k)

    # Capacity control
    capacity = max(1, round(Int, N / E * capacity_factor))
    cap_mask = expert_capacity_mask(indices, E, capacity)

    # Zero weights for dropped tokens
    @inbounds for i in 1:N
        for k in 1:top_k
            if !cap_mask[i, k]
                weights[i, k] = Float32(0.0)
            end
        end
    end

    # Load balance loss
    lb_loss = load_balance_loss(probs, indices, E)

    # Expert counts
    expert_counts = zeros(Int32, E)
    @inbounds for i in 1:N
        for k in 1:top_k
            if cap_mask[i, k]
                eid = indices[i, k]
                if 1 <= eid <= E
                    expert_counts[eid] += Int32(1)
                end
            end
        end
    end

    return MoERoutingResult(indices, weights, probs, lb_loss, expert_counts)
end

end # module
