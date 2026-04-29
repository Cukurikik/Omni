module FilewiseDocInsight

export OmniResult, compute_jaccard_similarity

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

# Deterministic calculation of Jaccard Similarity for document deduplication
function compute_jaccard_similarity(set_a_size::Int, set_b_size::Int, intersection_size::Int) :: OmniResult{Float64, String}
    if set_a_size < 0 || set_b_size < 0 || intersection_size < 0
        return OmniResult("Set sizes must be non-negative", Float64)
    end
    
    if intersection_size > set_a_size || intersection_size > set_b_size
        return OmniResult("Intersection cannot be larger than the sets", Float64)
    end

    union_size = set_a_size + set_b_size - intersection_size
    
    if union_size == 0
        return OmniResult(1.0) # Both sets are empty, considered identical
    end

    similarity = intersection_size / union_size
    return OmniResult(similarity)
end

end
