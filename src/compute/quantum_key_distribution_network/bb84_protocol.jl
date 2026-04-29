module QuantumKeyDistributionNetwork

export OmniResult, compute_qubit_error_rate

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

# Deterministic calculation of Quantum Bit Error Rate (QBER) for the BB84 protocol.
# In Quantum Key Distribution, if an eavesdropper (Eve) intercepts the photons,
# the laws of quantum mechanics dictate that she will disturb their state (no-cloning theorem).
# We calculate the QBER to mathematically prove whether the channel is secure.
function compute_qubit_error_rate(photons_sent::Int, basis_matches::Int, errors_detected::Int) :: OmniResult{Float64, String}
    if photons_sent <= 0 || basis_matches < 0 || errors_detected < 0 || basis_matches > photons_sent
        return OmniResult("Invalid BB84 photon counts", Float64)
    end
    
    if basis_matches == 0
        return OmniResult(0.0) # Cannot compute rate
    end
    
    # QBER is the ratio of errors to the number of photons where Bob guessed the correct basis
    qber = Float64(errors_detected) / Float64(basis_matches)
    
    return OmniResult(qber)
end

end
