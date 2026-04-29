module ScryptKDF

export OmniResult, compute_smix_memory_cost

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

# Deterministic Scrypt SMix Memory Hardness Math simulation
function compute_smix_memory_cost(N::Int, r::Int) :: OmniResult{Int64, String}
    # N = CPU/Memory cost factor (must be power of 2)
    # r = block size parameter
    
    if N <= 1 || (N & (N - 1)) != 0
        return OmniResult("N must be a power of 2 greater than 1", Int64)
    end
    
    if r <= 0
        return OmniResult("r must be strictly positive", Int64)
    end

    # Memory requirement = 128 * r * N bytes
    memory_bytes = Int64(128) * Int64(r) * Int64(N)
    
    return OmniResult(memory_bytes)
end

end
