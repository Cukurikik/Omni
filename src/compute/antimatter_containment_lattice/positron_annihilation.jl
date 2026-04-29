module AntimatterContainmentLattice

export OmniResult, compute_annihilation_yield

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

# Deterministic calculation of Positron-Electron Annihilation Yield.
# Antimatter is the most energy-dense fuel in the universe. When a positron (anti-electron)
# touches an electron, 100% of their mass is converted into pure gamma-ray energy (E=mc^2).
function compute_annihilation_yield(antimatter_mass_kg::Float64) :: OmniResult{Float64, String}
    if antimatter_mass_kg <= 0.0
        return OmniResult("Antimatter mass must be positive", Float64)
    end
    
    # Physics: Total mass annihilated is 2x the antimatter mass 
    # (because it annihilates an equal amount of normal matter)
    total_mass_kg = antimatter_mass_kg * 2.0
    
    # E = mc^2
    c = 299792458.0 # m/s
    energy_joules = total_mass_kg * (c^2)
    
    # Convert Joules to Megatons of TNT equivalent for easier visualization
    # 1 Megaton TNT = 4.184e15 Joules
    energy_megatons = energy_joules / 4.184e15
    
    return OmniResult(energy_megatons)
end

end
