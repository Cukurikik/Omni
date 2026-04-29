module ExoPlanetAtmosphereTerraformer

export OmniResult, compute_equilibrium_temperature

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

# Deterministic calculation of Planetary Equilibrium Temperature.
# Terraforming a dead world (like Mars) requires warming it up.
# We calculate the temperature based on the planet's Albedo (reflectivity)
# and the greenhouse gas effect.
function compute_equilibrium_temperature(stellar_luminosity_watts::Float64, distance_from_star_m::Float64, bond_albedo::Float64, greenhouse_effect_kelvin::Float64) :: OmniResult{Float64, String}
    if stellar_luminosity_watts <= 0.0 || distance_from_star_m <= 0.0 || bond_albedo < 0.0 || bond_albedo > 1.0
        return OmniResult("Invalid orbital terraforming parameters", Float64)
    end
    
    # Physics: Stefan-Boltzmann Law
    # T_eq = [ L * (1 - a) / (16 * pi * sigma * D^2) ]^(1/4)
    
    stefan_boltzmann_constant = 5.670374419e-8 # W/(m^2*K^4)
    
    numerator = stellar_luminosity_watts * (1.0 - bond_albedo)
    denominator = 16.0 * pi * stefan_boltzmann_constant * (distance_from_star_m^2)
    
    base_equilibrium_temp_k = (numerator / denominator)^0.25
    
    # Add the greenhouse gas warming effect
    surface_temp_kelvin = base_equilibrium_temp_k + greenhouse_effect_kelvin
    
    return OmniResult(surface_temp_kelvin)
end

end
