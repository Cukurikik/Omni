module RLEnvironment

struct OmniResult{T, E}
    value::Union{T, Nothing}
    error::Union{E, Nothing}
end

function is_ok(res::OmniResult)::Bool
    return res.error === nothing
end

function update_q_value(current_q::Float64, reward::Float64, max_next_q::Float64, alpha::Float64, gamma::Float64)::OmniResult{Float64, String}
    if alpha < 0.0 || alpha > 1.0
        return OmniResult{Float64, String}(nothing, "Learning rate (alpha) must be between 0 and 1")
    end
    
    if gamma < 0.0 || gamma > 1.0
        return OmniResult{Float64, String}(nothing, "Discount factor (gamma) must be between 0 and 1")
    end

    # Deterministic Q-Learning Bellman Equation implementation
    new_q = current_q + alpha * (reward + gamma * max_next_q - current_q)
    
    return OmniResult{Float64, String}(new_q, nothing)
end

end
