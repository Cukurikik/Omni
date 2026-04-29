module NeutronStarPulsarNavigation

export OmniResult, compute_pulsar_arrival_time

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

# Deterministic calculation of Millisecond Pulsar Radio Timing.
# Pulsars are rapidly spinning neutron stars that emit beams of radiation like lighthouses.
# Their rotation is so stable they rival atomic clocks. By timing the arrival of pulses
# from multiple pulsars, a starship can triangulate its exact position anywhere in the galaxy.
function compute_pulsar_arrival_time(distance_lightyears::Float64, ism_dispersion_measure::Float64, observation_frequency_mhz::Float64) :: OmniResult{Float64, String}
    if distance_lightyears <= 0.0 || observation_frequency_mhz <= 0.0
        return OmniResult("Invalid physical parameters", Float64)
    end
    
    # Physics: Interstellar Medium (ISM) Dispersion.
    # The space between stars is not empty; it contains free electrons.
    # Lower frequency radio waves travel slightly slower through the ISM than higher frequencies.
    # We must calculate this delay to get an exact timing fix.
    
    # Time delay in seconds: t = 4.149e3 * DM * (1/f^2)
    dispersion_delay_seconds = 4149.0 * ism_dispersion_measure * (1.0 / (observation_frequency_mhz^2))
    
    # Base travel time
    c_ly_per_yr = 1.0
    base_time_years = distance_lightyears / c_ly_per_yr
    
    total_arrival_time_seconds = (base_time_years * 3.154e7) + dispersion_delay_seconds
    
    return OmniResult(total_arrival_time_seconds)
end

end
