module OmniQuantumSimulator

export OmniResult, compute_state_probability

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

# Deterministic calculation of quantum state probability from complex amplitudes
function compute_state_probability(real_part::Float64, imag_part::Float64) :: OmniResult{Float64, String}
    # Born's rule: Probability is the squared magnitude of the complex amplitude
    # P = |a + bi|^2 = a^2 + b^2
    
    probability = (real_part * real_part) + (imag_part * imag_part)
    
    if probability > 1.0001 # allowing tiny float error
        return OmniResult("Calculated probability exceeds 1.0, state vector is not normalized", Float64)
    end
    
    return OmniResult(min(1.0, probability))
end

end
