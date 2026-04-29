module TectonicPlateEarthquakePredictor

export OmniResult, compute_seismic_arrival_delta

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

# Deterministic calculation of Seismic Tomography.
# Earthquakes emit fast, harmless P-waves (compressional) and slow, destructive S-waves (shear).
# By calculating the time difference between their arrivals at a seismometer, we can determine
# exactly how far away the earthquake occurred, providing a few seconds of early warning.
function compute_seismic_arrival_delta(distance_to_epicenter_km::Float64, p_wave_velocity_km_s::Float64, s_wave_velocity_km_s::Float64) :: OmniResult{Float64, String}
    if distance_to_epicenter_km < 0.0 || p_wave_velocity_km_s <= 0.0 || s_wave_velocity_km_s <= 0.0
        return OmniResult("Invalid physical parameters", Float64)
    end
    
    if p_wave_velocity_km_s <= s_wave_velocity_km_s
        return OmniResult("P-waves must travel faster than S-waves", Float64)
    end
    
    # Time = Distance / Velocity
    t_p = distance_to_epicenter_km / p_wave_velocity_km_s
    t_s = distance_to_epicenter_km / s_wave_velocity_km_s
    
    # The time difference between the harmless rumble (P) and the destructive shaking (S)
    delta_time_seconds = t_s - t_p
    
    return OmniResult(delta_time_seconds)
end

end
