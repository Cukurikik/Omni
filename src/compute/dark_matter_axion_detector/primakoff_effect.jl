module DarkMatterAxionDetector

export OmniResult, compute_primakoff_frequency

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

# Deterministic calculation of the Inverse Primakoff Effect.
# Axions are theoretical dark matter particles. If an axion passes through an incredibly strong
# magnetic field, it might decay into a single microwave photon. We tune a microwave cavity
# to resonate at exactly the expected mass of the axion to catch that photon.
function compute_primakoff_frequency(axion_mass_micro_ev::Float64) :: OmniResult{Float64, String}
    if axion_mass_micro_ev <= 0.0
        return OmniResult("Axion mass must be positive", Float64)
    end
    
    # E = h * f  =>  f = E / h
    # where E is the rest mass energy of the axion, and h is Planck's constant.
    # 1 micro-eV corresponds to roughly 241.8 MHz
    
    conversion_factor = 241.79893 # MHz per micro-eV
    
    resonant_frequency_mhz = axion_mass_micro_ev * conversion_factor
    
    return OmniResult(resonant_frequency_mhz)
end

end
