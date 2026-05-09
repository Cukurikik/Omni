# MAPF-GPT-DDG: Multi-Agent Path Finding with Delta Data Generation
# Julia compute layer for highly parallelized path validation and data generation

module OmniMAPF

using LinearAlgebra

struct AgentState
    id::Int32
    pos_x::Float32
    pos_y::Float32
    goal_x::Float32
    goal_y::Float32
end

struct Trajectory
    agent_id::Int32
    path_x::Vector{Float32}
    path_y::Vector{Float32}
end

"""
Delta Data Generation (DDG) - A reward-free active learning approach that 
identifies and corrects failure cases in the policy.
"""
function detect_collisions(trajectories::Vector{Trajectory}, time_steps::Int)::Vector{Tuple{Int32, Int32, Int}}
    collisions = Tuple{Int32, Int32, Int}[]
    num_agents = length(trajectories)
    
    @inbounds for t in 1:time_steps
        for i in 1:num_agents
            for j in (i+1):num_agents
                # Check for vertex collision at time t
                if length(trajectories[i].path_x) >= t && length(trajectories[j].path_x) >= t
                    dist_sq = (trajectories[i].path_x[t] - trajectories[j].path_x[t])^2 + 
                              (trajectories[i].path_y[t] - trajectories[j].path_y[t])^2
                    
                    if dist_sq < 0.5f0 # Threshold for collision
                        push!(collisions, (trajectories[i].agent_id, trajectories[j].agent_id, t))
                    end
                end
            end
        end
    end
    return collisions
end

"""
Generates fine-tuning data by extracting states prior to collision
"""
function generate_delta_data(trajectories::Vector{Trajectory}, collisions::Vector{Tuple{Int32, Int32, Int}}, context_window::Int)
    delta_dataset = []
    
    for (agent1, agent2, t_col) in collisions
        t_start = max(1, t_col - context_window)
        # Extract the sequence of states leading up to the collision
        # This data will be used to fine-tune the MAPF-GPT model
        push!(delta_dataset, (agent1, t_start:t_col))
        push!(delta_dataset, (agent2, t_start:t_col))
    end
    
    return unique(delta_dataset)
end

end # module OmniMAPF
