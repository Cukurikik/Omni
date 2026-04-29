module EnvoyProxy

export OmniResult, compute_consistent_hash_node

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

# Deterministic Consistent Hashing Math (Ketama Ring Simulation)
function compute_consistent_hash_node(key::String, ring_size::Int) :: OmniResult{Int, String}
    if isempty(key)
        return OmniResult("Routing key cannot be empty", Int)
    end
    
    if ring_size <= 0
        return OmniResult("Ring size must be strictly positive", Int)
    end

    # Deterministic FNV-1a hash
    hash_val = UInt64(14695981039346656037)
    for char in key
        hash_val = hash_val ⊻ UInt64(char)
        hash_val = hash_val * UInt64(1099511628211)
    end

    # Modulo arithmetic for ring node assignment
    node_id = Int(hash_val % UInt64(ring_size))
    return OmniResult(node_id)
end

end
