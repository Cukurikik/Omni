module HydrogenStorageLLM

export OmniResult, compute_gravimetric_capacity

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

# Deterministic calculation of Gravimetric Capacity (wt%) for Hydrogen Storage Materials
function compute_gravimetric_capacity(mass_hydrogen: Float64, mass_host_material: Float64) :: OmniResult{Float64, String}
    if mass_hydrogen < 0.0 || mass_host_material <= 0.0
        return OmniResult("Mass values must be positive and host mass must be non-zero", Float64)
    end
    
    # Formula: (mass_H / (mass_H + mass_host)) * 100
    wt_percent = (mass_hydrogen / (mass_hydrogen + mass_host_material)) * 100.0
    
    return OmniResult(wt_percent)
end

end
