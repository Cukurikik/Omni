# moe_mean_field_games.jl — Compute
# Layer: Compute — Mean Field Games for Phase Transitions
# Inspired by: three-phases-moe (Three Phases of Expert Routing)

module MoEMeanFieldGames

export calculate_expert_equilibrium

"""
    calculate_expert_equilibrium(num_experts::Int, token_distribution::Vector{Float64}, alpha::Float64)
    
Calculates the Nash equilibrium distribution of tokens across experts using Mean Field Game theory.
`alpha` represents the capacity penalty coefficient.
"""
function calculate_expert_equilibrium(num_experts::Int, token_distribution::Vector{Float64}, alpha::Float64)
    equilibrium_state = copy(token_distribution)
    learning_rate = 0.01
    tolerance = 1e-5
    max_iters = 1000
    
    for iter in 1:max_iters
        # 1. Compute Cost Field (Penalty = alpha * load)
        costs = alpha .* equilibrium_state
        
        # 2. Fokker-Planck Update (Tokens migrate to lower cost experts)
        avg_cost = sum(costs) / num_experts
        grad = costs .- avg_cost
        
        old_state = copy(equilibrium_state)
        
        # Update distribution via gradient descent on cost field
        equilibrium_state .-= learning_rate .* grad
        
        # Project to simplex (ensure valid probability distribution)
        equilibrium_state = max.(equilibrium_state, 0.0)
        equilibrium_state ./= sum(equilibrium_state)
        
        # Check convergence
        if maximum(abs.(equilibrium_state .- old_state)) < tolerance
            break
        end
    end
    
    return equilibrium_state
end

end # module
