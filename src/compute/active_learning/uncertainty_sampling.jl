module ActiveLearning

struct OmniResult{T, E}
    value::Union{T, Nothing}
    error::Union{E, Nothing}
end

function is_ok(res::OmniResult)::Bool
    return res.error === nothing
end

function calculate_entropy(probabilities::Vector{Float64})::OmniResult{Float64, String}
    if length(probabilities) == 0
        return OmniResult{Float64, String}(nothing, "Probabilities array cannot be empty")
    end

    entropy = 0.0
    for p in probabilities
        if p < 0.0 || p > 1.0
            return OmniResult{Float64, String}(nothing, "Probability must be between 0.0 and 1.0")
        end
        if p > 0.0
            entropy -= p * log2(p)
        end
    end
    
    return OmniResult{Float64, String}(entropy, nothing)
end

end
