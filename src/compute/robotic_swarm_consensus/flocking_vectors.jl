module RoboticSwarmConsensus

export OmniResult, compute_flocking_velocity

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

# Deterministic calculation of Boids Flocking Vectors for Robotic Swarms
# Calculates the combined Separation, Alignment, and Cohesion vectors for a single drone in the swarm
function compute_flocking_velocity(agent_pos::Tuple{Float64, Float64}, neighbor_positions::Vector{Tuple{Float64, Float64}}, neighbor_velocities::Vector{Tuple{Float64, Float64}}) :: OmniResult{Tuple{Float64, Float64}, String}
    if length(neighbor_positions) != length(neighbor_velocities)
        return OmniResult("Mismatched neighbor arrays", Tuple{Float64, Float64})
    end
    
    if isempty(neighbor_positions)
        # If no neighbors, maintain current vector (simplified as 0,0 acceleration here)
        return OmniResult((0.0, 0.0))
    end
    
    # 1. Separation (avoid crowding neighbors)
    sep_x = 0.0; sep_y = 0.0
    # 2. Alignment (steer towards average heading of neighbors)
    align_x = 0.0; align_y = 0.0
    # 3. Cohesion (steer towards average position of neighbors)
    coh_x = 0.0; coh_y = 0.0
    
    num_neighbors = length(neighbor_positions)
    
    for i in 1:num_neighbors
        n_pos = neighbor_positions[i]
        n_vel = neighbor_velocities[i]
        
        # Cohesion
        coh_x += n_pos[1]
        coh_y += n_pos[2]
        
        # Alignment
        align_x += n_vel[1]
        align_y += n_vel[2]
        
        # Separation
        dist_sq = (agent_pos[1] - n_pos[1])^2 + (agent_pos[2] - n_pos[2])^2
        if dist_sq > 0.01 # avoid div by zero
            # Weight separation inversely to distance
            sep_x += (agent_pos[1] - n_pos[1]) / dist_sq
            sep_y += (agent_pos[2] - n_pos[2]) / dist_sq
        end
    end
    
    # Average alignment and cohesion
    align_x /= num_neighbors; align_y /= num_neighbors
    
    coh_x = (coh_x / num_neighbors) - agent_pos[1]
    coh_y = (coh_y / num_neighbors) - agent_pos[2]
    
    # Combine vectors (weights are arbitrarily chosen for the simulation)
    v_x = (sep_x * 1.5) + (align_x * 1.0) + (coh_x * 1.0)
    v_y = (sep_y * 1.5) + (align_y * 1.0) + (coh_y * 1.0)
    
    return OmniResult((v_x, v_y))
end

end
