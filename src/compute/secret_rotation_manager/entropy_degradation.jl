module SecretRotationManager

export OmniResult, compute_entropy_degradation

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

# Deterministic calculation of Cryptographic Entropy Degradation
# Over time, the chance of a secret being leaked or cracked increases. This mathematical curve triggers rotations.
function compute_entropy_degradation(days_active::Int, encryption_bits::Int) :: OmniResult{Float64, String}
    if days_active < 0 || encryption_bits <= 0
        return OmniResult("Metrics must be positive", Float64)
    end
    
    # Simulate entropy loss over time. A 256-bit key loses "effective" secrecy 
    # based on time exposed to physical vectors, employee turnover, or brute-force advances.
    
    # 0.0 means perfect entropy (brand new key). 1.0 means total compromise risk.
    degradation = (Float64(days_active) / 90.0) * (256.0 / Float64(encryption_bits))
    
    # Clamp to [0, 1]
    clamped = min(1.0, max(0.0, degradation))
    
    return OmniResult(clamped)
end

end
