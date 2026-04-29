module TachyonFieldFtlCommunicator

export OmniResult, compute_tachyonic_antitelephone_delta

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

# Deterministic calculation of Tachyonic Antitelephone Causality Violation.
# Tachyons are theoretical particles that always travel faster than light (FTL).
# According to Special Relativity, any FTL communication implies communicating backwards in time,
# leading to causality paradoxes (e.g., receiving a reply before sending the message).
function compute_tachyonic_antitelephone_delta(distance_lightyears::Float64, tachyon_velocity_c::Float64, relative_frame_velocity_c::Float64) :: OmniResult{Float64, String}
    if distance_lightyears <= 0.0 || tachyon_velocity_c <= 1.0 || relative_frame_velocity_c < 0.0 || relative_frame_velocity_c >= 1.0
        return OmniResult("Invalid relativistic parameters. Tachyons must be v > c.", Float64)
    end
    
    # Physics (simplified Tolman's paradox): Delta t = L/v - L*v_frame/c^2
    # The time difference between sending and receiving in the observer's frame.
    # If delta_t is negative, the message is received BEFORE it was sent.
    
    # Using units where c = 1
    term1 = distance_lightyears / tachyon_velocity_c
    term2 = distance_lightyears * relative_frame_velocity_c
    
    delta_time_years = term1 - term2
    
    return OmniResult(delta_time_years)
end

end
