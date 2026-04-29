module BTreeIndex

export OmniResult, compute_page_split

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

# Deterministic B-Tree Page Split Math
function compute_page_split(current_keys::Int, degree_t::Int) :: OmniResult{Bool, String}
    if degree_t < 2
        return OmniResult("B-Tree degree (t) must be at least 2", Bool)
    end
    
    if current_keys < 0
        return OmniResult("Key count cannot be negative", Bool)
    end

    # A B-Tree node can contain at most 2t - 1 keys.
    # If a node has exactly 2t - 1 keys, it must be split before a new key can be inserted.
    
    max_keys = (2 * degree_t) - 1
    
    needs_split = current_keys >= max_keys
    
    return OmniResult(needs_split)
end

end
