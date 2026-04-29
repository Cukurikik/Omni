module VpcMeshTunnel

export OmniResult, compute_key_rotation_time

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

# Deterministic calculation of WireGuard key rotation schedules
# Ensures cryptographic Perfect Forward Secrecy (PFS) in VPC Mesh Tunnels
function compute_key_rotation_time(bytes_transferred::Float64, max_bytes_per_key::Float64) :: OmniResult{Bool, String}
    if bytes_transferred < 0.0 || max_bytes_per_key <= 0.0
        return OmniResult("Metrics must be positive", Bool)
    end
    
    # If the tunnel has transferred more than the safe data limit (e.g., 2^64 bytes),
    # the symmetric encryption key MUST be rotated to prevent cryptographic exhaustion attacks.
    
    needs_rotation = bytes_transferred >= max_bytes_per_key
    
    return OmniResult(needs_rotation)
end

end
