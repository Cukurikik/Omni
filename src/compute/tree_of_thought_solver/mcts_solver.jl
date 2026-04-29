module TreeOfThoughtSolver

export OmniResult, compute_mcts_ucb

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

# Deterministic calculation of Upper Confidence Bound (UCB1) for Monte Carlo Tree Search
# Used to balance exploration and exploitation in Tree of Thoughts LLM reasoning
function compute_mcts_ucb(node_value::Float64, node_visits::Int, parent_visits::Int, exploration_param::Float64 = 1.414) :: OmniResult{Float64, String}
    if node_visits < 0 || parent_visits <= 0 || node_visits > parent_visits
        return OmniResult("Invalid visit counts", Float64)
    end
    
    if node_visits == 0
        return OmniResult(Inf) # Unexplored nodes have infinite priority
    end

    # UCB1 = (w_i / n_i) + c * sqrt(ln(N_i) / n_i)
    exploitation = node_value / node_visits
    exploration = exploration_param * sqrt(log(parent_visits) / node_visits)
    
    return OmniResult(exploitation + exploration)
end

end
