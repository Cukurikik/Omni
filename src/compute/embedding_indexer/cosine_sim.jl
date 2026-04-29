module EmbeddingIndexer

export OmniResult, compute_cosine_similarity

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

# Deterministic Cosine Similarity Math for Embedding Retrieval
function compute_cosine_similarity(vec_a::Vector{Float64}, vec_b::Vector{Float64}) :: OmniResult{Float64, String}
    if length(vec_a) != length(vec_b)
        return OmniResult("Vectors must have the same dimension", Float64)
    end
    
    if isempty(vec_a)
        return OmniResult("Vectors cannot be empty", Float64)
    end

    dot_product = 0.0
    norm_a_sq = 0.0
    norm_b_sq = 0.0

    for i in 1:length(vec_a)
        dot_product += vec_a[i] * vec_b[i]
        norm_a_sq += vec_a[i] * vec_a[i]
        norm_b_sq += vec_b[i] * vec_b[i]
    end

    if norm_a_sq == 0.0 || norm_b_sq == 0.0
        return OmniResult(0.0) # Zero vector edge case
    end

    similarity = dot_product / (sqrt(norm_a_sq) * sqrt(norm_b_sq))
    
    return OmniResult(similarity)
end

end
