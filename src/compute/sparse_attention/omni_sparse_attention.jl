// @omni-layer Compute | @omni-lang Julia | @omni-batch 18 | @omni-semester 16
// @omni-description Julia sparse attention kernel: top-k sparse attention
// with flash-style memory efficiency for long sequence transformers.

module OmniSparseAttention

export sparse_attention, top_k_attention, local_attention, sliding_window

using LinearAlgebra

"""
    top_k_attention(Q, K, V, top_k; scale=nothing) -> Matrix

Compute top-k sparse attention. For each query, only attend to top-k keys.
"""
function top_k_attention(Q::Matrix{Float64}, K::Matrix{Float64}, V::Matrix{Float64},
                          top_k::Int; scale::Union{Float64,Nothing}=nothing)
    n, d = size(Q)
    s = isnothing(scale) ? 1.0 / sqrt(Float64(d)) : scale
    O = zeros(Float64, n, size(V, 2))

    for i in 1:n
        scores = [dot(Q[i, :], K[j, :]) * s for j in 1:n]
        perm = sortperm(scores, rev=true)
        topk_idx = perm[1:min(top_k, n)]
        topk_scores = [scores[j] for j in topk_idx]
        mx = maximum(topk_scores)
        exps = [exp(sc - mx) for sc in topk_scores]
        sm = sum(exps) + 1e-10
        weights = exps ./ sm
        for (w_idx, j) in enumerate(topk_idx)
            O[i, :] .+= weights[w_idx] .* V[j, :]
        end
    end
    return O
end

"""
    local_attention(Q, K, V, window_size) -> Matrix

Sliding window local attention for O(n*w) complexity.
"""
function local_attention(Q::Matrix{Float64}, K::Matrix{Float64}, V::Matrix{Float64},
                          window_size::Int)
    n, d = size(Q)
    s = 1.0 / sqrt(Float64(d))
    O = zeros(Float64, n, size(V, 2))

    for i in 1:n
        lo = max(1, i - window_size)
        hi = min(n, i + window_size)
        scores = Float64[]
        indices = collect(lo:hi)
        for j in indices
            push!(scores, dot(Q[i, :], K[j, :]) * s)
        end
        mx = maximum(scores)
        exps = exp.(scores .- mx)
        sm = sum(exps) + 1e-10
        weights = exps ./ sm
        for (w_idx, j) in enumerate(indices)
            O[i, :] .+= weights[w_idx] .* V[j, :]
        end
    end
    return O
end

"""
    sparse_attention(Q, K, V; top_k=64, window=128, global_tokens=4) -> Matrix

Combined sparse attention: local window + top-k global + global sink tokens.
"""
function sparse_attention(Q::Matrix{Float64}, K::Matrix{Float64}, V::Matrix{Float64};
                           top_k::Int=64, window::Int=128, global_tokens::Int=4)
    n, d = size(Q)
    s = 1.0 / sqrt(Float64(d))
    O = zeros(Float64, n, size(V, 2))

    for i in 1:n
        attend_set = Set{Int}()
        # Local window
        for j in max(1, i-window):min(n, i+window)
            push!(attend_set, j)
        end
        # Global sink tokens
        for j in 1:min(global_tokens, n)
            push!(attend_set, j)
        end
        # Top-k from remaining
        remaining = [j for j in 1:n if !(j in attend_set)]
        if !isempty(remaining)
            rem_scores = [(j, dot(Q[i,:], K[j,:]) * s) for j in remaining]
            sort!(rem_scores, by=x -> -x[2])
            for (j, _) in rem_scores[1:min(top_k, length(rem_scores))]
                push!(attend_set, j)
            end
        end

        indices = sort(collect(attend_set))
        scores = [dot(Q[i,:], K[j,:]) * s for j in indices]
        mx = maximum(scores)
        exps = exp.(scores .- mx)
        sm = sum(exps) + 1e-10
        weights = exps ./ sm
        for (w_idx, j) in enumerate(indices)
            O[i, :] .+= weights[w_idx] .* V[j, :]
        end
    end
    return O
end

end # module
