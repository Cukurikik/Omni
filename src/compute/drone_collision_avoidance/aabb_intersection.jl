module DroneCollisionAvoidance

export OmniResult, compute_aabb_intersection

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

# Deterministic calculation of Axis-Aligned Bounding Box (AABB) intersection in 3D space
# Used to rapidly predict mid-air collisions between autonomous drones
function compute_aabb_intersection(
    box1_min::Tuple{Float64, Float64, Float64}, box1_max::Tuple{Float64, Float64, Float64},
    box2_min::Tuple{Float64, Float64, Float64}, box2_max::Tuple{Float64, Float64, Float64}
) :: OmniResult{Bool, String}

    # Check for non-overlap on X axis
    if box1_max[1] < box2_min[1] || box1_min[1] > box2_max[1]
        return OmniResult(false)
    end
    
    # Check for non-overlap on Y axis
    if box1_max[2] < box2_min[2] || box1_min[2] > box2_max[2]
        return OmniResult(false)
    end
    
    # Check for non-overlap on Z axis (Altitude)
    if box1_max[3] < box2_min[3] || box1_min[3] > box2_max[3]
        return OmniResult(false)
    end
    
    # If overlapping on all 3 axes, a collision is predicted!
    return OmniResult(true)
end

end
