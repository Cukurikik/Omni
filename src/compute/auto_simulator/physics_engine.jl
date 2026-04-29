module PhysicsEngine

struct OmniResult{T, E}
    value::Union{T, Nothing}
    error::Union{E, Nothing}
end

function is_ok(res::OmniResult)::Bool
    return res.error === nothing
end

function compute_kinematics(velocity::Float64, acceleration::Float64, time_delta::Float64)::OmniResult{Float64, String}
    if time_delta <= 0.0
        return OmniResult{Float64, String}(nothing, "Time delta must be positive")
    end

    # Deterministic kinematics computation
    new_position = (velocity * time_delta) + (0.5 * acceleration * (time_delta ^ 2))
    
    return OmniResult{Float64, String}(new_position, nothing)
end

end
