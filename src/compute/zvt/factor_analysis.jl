module Omni.Compute.ZVT.FactorAnalysis

using LinearAlgebra
using Statistics

# OMNI ZVT: High-Performance Quantitative Factor Analysis
# Computes multi-factor market signals using Julia's fast numerical arrays.
# Source: zvtvz/zvt

struct FactorError <: Exception
    msg::String
end

"""
    compute_momentum_factor(prices::Vector{Float64}, lookback::Int)

Calculates the time-series momentum factor.
"""
function compute_momentum_factor(prices::Vector{Float64}, lookback::Int)::Union{Vector{Float64}, FactorError}
    n = length(prices)
    if n < lookback
        return FactorError("Price history shorter than lookback period.")
    end
    
    momentum = zeros(Float64, n)
    for i in (lookback + 1):n
        # Rate of change
        momentum[i] = (prices[i] - prices[i - lookback]) / prices[i - lookback]
    end
    
    return momentum
end

"""
    compute_bollinger_bands(prices::Vector{Float64}, window::Int, k::Float64)

Calculates Bollinger Band z-scores as a mean-reversion factor.
"""
function compute_bollinger_bands(prices::Vector{Float64}, window::Int, k::Float64)::Union{Vector{Float64}, FactorError}
    n = length(prices)
    if n < window
        return FactorError("Price history shorter than moving average window.")
    end
    
    z_scores = zeros(Float64, n)
    
    for i in window:n
        slice = prices[(i - window + 1):i]
        mu = mean(slice)
        sigma = std(slice)
        
        if sigma != 0
            z_scores[i] = (prices[i] - mu) / sigma
        else
            z_scores[i] = 0.0
        end
    end
    
    return z_scores
end

"""
    cross_sectional_rank(factors::Matrix{Float64})

Ranks factors across multiple assets (columns) at each time step (rows).
Neutralizes market exposure by returning values from -1 to 1.
"""
function cross_sectional_rank(factors::Matrix{Float64})::Matrix{Float64}
    rows, cols = size(factors)
    ranked = zeros(Float64, rows, cols)
    
    for i in 1:rows
        row_data = factors[i, :]
        p = sortperm(row_data)
        
        for (rank, idx) in enumerate(p)
            # Normalize to [-1, 1]
            ranked[i, idx] = (rank - 1) / (cols - 1) * 2.0 - 1.0
        end
    end
    
    return ranked
end

end # module
