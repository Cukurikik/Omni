module AiowayRelationalDl

export OmniResult, compute_gradient_accumulation

struct OmniResult{T, E}
    value::Union{T, Nothing}
    error::Union{E, Nothing}
    is_ok::Bool
end

function OmniResult(value::T) where T
    OmniResult{T, String}(value, nothing, true)
end

function OmniResult(error::String, ::Type{T}=Any) where T
    OmniResult{T, String}(nothing, error, false)
end

# Deterministic Deep Learning Gradient Accumulation over Relational DB joins
function compute_gradient_accumulation(batch_gradients::Vector{Float64}) :: OmniResult{Float64, String}
    if isempty(batch_gradients)
        return OmniResult("Gradient batch cannot be empty", Float64)
    end
    
    accumulated = 0.0
    for g in batch_gradients
        accumulated += g
    end
    
    # In relational DL, the mean is often taken to normalize across varying one-to-many join expansions
    normalized = accumulated / length(batch_gradients)
    
    return OmniResult(normalized)
end

end
