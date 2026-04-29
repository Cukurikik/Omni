module FastApiRouter

export OmniResult, compute_radix_hash

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

# Deterministic Radix Tree Path Matching Hash
function compute_radix_hash(path::String) :: OmniResult{Int64, String}
    if isempty(path)
        return OmniResult("Path cannot be empty", Int64)
    end

    # Deterministic hashing mimicking strict router matching
    hash_val = 5381
    for char in path
        hash_val = ((hash_val << 5) + hash_val) + Int(char) # djb2
    end

    return OmniResult(Int64(hash_val & 0x7FFFFFFFFFFFFFFF))
end

end
