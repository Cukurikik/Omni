# OMNI Framework - Julia Simulation of Grokking Dynamics
# Models the sudden generalization phenomenon in neural networks

module OmniGrokkingSimulation

using DifferentialEquations
using Plots

# Simplified model of train and test loss dynamics during grokking
# W: Weights norm, L_train: Training Loss, L_test: Test Loss
function grokking_dynamics!(du, u, p, t)
    W, L_train, L_test = u
    lr, weight_decay, dataset_size = p

    # Training loss drops quickly
    du[2] = -lr * L_train * (1.0 + W)
    
    # Weight norm grows initially, then decays
    du[1] = lr * (L_train * 0.5) - weight_decay * W
    
    # Test loss stays high (memorization), then drops suddenly when W decays (generalization)
    du[3] = (L_test - L_train) * (0.1 / (1.0 + exp(-10.0 * (2.0 - W)))) - 0.001 * L_test
end

export run_simulation
function run_simulation()
    u0 = [0.1, 2.5, 2.5] # Initial W, L_train, L_test
    p = (0.01, 0.005, 1000) # lr, wd, N
    tspan = (0.0, 5000.0)
    
    prob = ODEProblem(grokking_dynamics!, u0, tspan, p)
    sol = solve(prob, Tsit5())
    
    println("OMNI Julia: Grokking Simulation Complete.")
    return sol
end

end # module
