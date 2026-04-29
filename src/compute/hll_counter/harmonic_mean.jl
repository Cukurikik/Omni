module HllCounter

export OmniResult, compute_harmonic_mean

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

# Deterministic HyperLogLog Harmonic Mean Calculation Math
function compute_harmonic_mean(registers::Vector{UInt8}) :: OmniResult{Float64, String}
    m = length(registers)
    if m == 0
        return OmniResult("Registers cannot be empty", Float64)
    end
    
    # Mathematical calculation: Z = 1 / sum(2^-M[j])
    sum_inv_pow2 = 0.0
    for j in 1:m
        sum_inv_pow2 += 1.0 / (1 << registers[j])
    end
    
    harmonic_mean = 1.0 / sum_inv_pow2
    
    # Raw cardinality estimate (E = alpha_m * m^2 * Z)
    # We return the harmonic mean directly for the business logic to scale
    return OmniResult(harmonic_mean)
end

end
