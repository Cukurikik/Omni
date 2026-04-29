module LudwigAutoML

export OmniResult, compute_combiner_concat

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

# Deterministic Concatenation Combiner Math (Ludwig Architecture)
function compute_combiner_concat(features::Vector{Vector{Float64}}) :: OmniResult{Vector{Float64}, String}
    if length(features) == 0
        return OmniResult("Feature vectors cannot be empty", Vector{Float64})
    end

    total_dim = sum(length(v) for v in features)
    if total_dim == 0
        return OmniResult("Total dimension must be strictly positive", Vector{Float64})
    end

    # Deterministic memory allocation and copy for flat representation
    combined = zeros(Float64, total_dim)
    
    offset = 1
    for feature_vec in features
        len = length(feature_vec)
        if len > 0
            combined[offset:(offset+len-1)] .= feature_vec
            offset += len
        end
    end

    return OmniResult(combined)
end

end
