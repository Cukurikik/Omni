module CdnEdgePurger

export OmniResult, compute_invalidation_hash

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

# Deterministic calculation of Cache Invalidation Trees
# Uses simple string hashing to determine exactly which CDN edge nodes need to flush their caches
function compute_invalidation_hash(url_path::String) :: OmniResult{Int64, String}
    if isempty(url_path)
        return OmniResult("URL path cannot be empty", Int64)
    end
    
    # Simple deterministic hash (e.g., FNV-1a or similar for simulation)
    hash_val::Int64 = 2166136261
    
    for char in url_path
        hash_val = xor(hash_val, Int64(char))
        hash_val = hash_val * 16777619
    end
    
    return OmniResult(hash_val)
end

end
