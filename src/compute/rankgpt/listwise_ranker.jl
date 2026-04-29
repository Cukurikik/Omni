module RankGPTRanker

struct OmniResult{T}
    value::Union{T, Nothing}
    error::Union{String, Nothing}
    is_ok::Bool
end

function OmniResult(value::T) where T
    OmniResult{T}(value, nothing, true)
end

function OmniResult(::Type{T}, error::String) where T
    OmniResult{T}(nothing, error, false)
end

function compute_listwise_rank(scores::Array{Float64, 1})
    if length(scores) == 0
        return OmniResult(Array{Int, 1}, "Empty scores array")
    end
    
    # Math for permutation probability in listwise ranking
    # Sorting indices based on descending scores
    ranked_indices = sortperm(scores, rev=true)
    
    return OmniResult(ranked_indices)
end

end
