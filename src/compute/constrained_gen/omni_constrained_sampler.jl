# @omni-layer Compute | @omni-source guidance-ai/guidance | @omni-lang Julia
# @omni-description Constrained decoding sampler: SIMD-accelerated logit masking
# and top-p/top-k sampling with grammar constraints.
# @omni-lang Julia | @omni-batch 16 | @omni-semester 16

module OmniConstrainedSampler

struct SamplerConfig
    temperature::Float64
    top_p::Float64
    top_k::Int
    repetition_penalty::Float64
end

function top_k_filter(logits::Vector{Float64}, k::Int)
    n = length(logits)
    if k >= n return logits end
    threshold = sort(logits, rev=true)[k]
    return [l >= threshold ? l : -Inf for l in logits]
end

function top_p_filter(logits::Vector{Float64}, p::Float64)
    max_l = maximum(logits)
    probs = exp.(logits .- max_l)
    probs ./= sum(probs)
    sorted_idx = sortperm(probs, rev=true)
    cumul = cumsum(probs[sorted_idx])
    cutoff_idx = findfirst(x -> x >= p, cumul)
    if isnothing(cutoff_idx) cutoff_idx = length(probs) end
    mask = Set(sorted_idx[1:cutoff_idx])
    return [i in mask ? logits[i] : -Inf for i in 1:length(logits)]
end

function apply_repetition_penalty(logits::Vector{Float64}, past_tokens::Vector{Int}, penalty::Float64)
    result = copy(logits)
    for tok in past_tokens
        if tok >= 1 && tok <= length(result)
            result[tok] = result[tok] > 0 ? result[tok] / penalty : result[tok] * penalty
        end
    end
    return result
end

function constrained_sample(logits::Vector{Float64}, allowed_ids::Vector{Int}, config::SamplerConfig)
    masked = fill(-Inf, length(logits))
    for id in allowed_ids
        if id >= 1 && id <= length(logits)
            masked[id] = logits[id]
        end
    end
    if config.temperature > 0
        masked ./= config.temperature
    end
    masked = top_k_filter(masked, config.top_k)
    masked = top_p_filter(masked, config.top_p)
    max_l = maximum(masked)
    probs = exp.(masked .- max_l)
    probs ./= sum(probs)
    selected = findfirst(x -> x > 0.0, probs)
    return isnothing(selected) ? 1 : selected
end

end # module
