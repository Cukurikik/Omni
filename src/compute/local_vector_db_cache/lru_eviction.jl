module LocalVectorDbCache

export OmniResult, compute_lru_score

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

# Deterministic calculation of Least Recently Used (LRU) eviction scores
# Used to manage limited RAM on Edge devices holding local RAG vector embeddings
function compute_lru_score(last_access_timestamp::Int64, access_count::Int) :: OmniResult{Float64, String}
    if last_access_timestamp < 0 || access_count < 0
        return OmniResult("Metrics must be non-negative", Float64)
    end
    
    # Weight score heavily by recency, but factor in total frequency (LFU-ish)
    # Higher score = Keep in cache. Lower score = Evict.
    
    score = Float64(last_access_timestamp) + (access_count * 100.0)
    
    return OmniResult(score)
end

end
