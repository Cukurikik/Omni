module BpfFirewall

export OmniResult, compute_subnet_match

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

# Deterministic Bitwise Subnet Mask Matching for eBPF packet routing math
function compute_subnet_match(ip::UInt32, subnet::UInt32, prefix_len::Int) :: OmniResult{Bool, String}
    if prefix_len < 0 || prefix_len > 32
        return OmniResult("Prefix length must be between 0 and 32", Bool)
    end

    if prefix_len == 0
        return OmniResult(true) # 0.0.0.0/0 matches everything
    end

    # Create mask using shift. Handling 32 shift special case in Julia/C.
    mask = prefix_len == 32 ? UInt32(0xFFFFFFFF) : ~(UInt32(0xFFFFFFFF) >> prefix_len)

    # Big-endian vs Little-endian abstract simulation for matching
    # (ip AND mask) == (subnet AND mask)
    is_match = (ip & mask) == (subnet & mask)

    return OmniResult(is_match)
end

end
