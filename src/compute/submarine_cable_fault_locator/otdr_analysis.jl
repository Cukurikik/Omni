module SubmarineCableFaultLocator

export OmniResult, compute_otdr_distance

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

# Deterministic calculation of Optical Time-Domain Reflectometer (OTDR) signals.
# When an underwater internet cable is cut (e.g., by a shark or anchor), we pulse a laser
# and measure the time it takes for the backscattered light to return, pinpointing the break.
function compute_otdr_distance(pulse_time_seconds::Float64, return_time_seconds::Float64, index_of_refraction::Float64) :: OmniResult{Float64, String}
    if pulse_time_seconds < 0.0 || return_time_seconds <= pulse_time_seconds || index_of_refraction <= 1.0
        return OmniResult("Invalid time or optical parameters", Float64)
    end
    
    # Speed of light in vacuum (km/s)
    c = 299792.458
    
    # Speed of light in the fiber optic cable
    v_fiber = c / index_of_refraction
    
    # Total round trip time
    delta_t = return_time_seconds - pulse_time_seconds
    
    # Distance = (velocity * time) / 2 (because round trip)
    fault_distance_km = (v_fiber * delta_t) / 2.0
    
    return OmniResult(fault_distance_km)
end

end
