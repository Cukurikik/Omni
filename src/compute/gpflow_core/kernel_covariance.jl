module GPFlowCoreCompute

using LinearAlgebra

struct OmniResult{T, E}
    value::Union{T, Nothing}
    error::Union{E, Nothing}
end

function is_ok(res::OmniResult)::Bool
    return res.error === nothing
end

function compute_rbf_kernel(X1::Vector{Float64}, X2::Vector{Float64}, lengthscale::Float64, variance::Float64)::OmniResult{Float64, String}
    if lengthscale <= 0.0 || variance <= 0.0
        return OmniResult{Float64, String}(nothing, "Lengthscale and variance must be positive")
    end
    
    if length(X1) != length(X2)
        return OmniResult{Float64, String}(nothing, "Dimensionality mismatch between inputs")
    end

    # Deterministic RBF (Squared Exponential) Kernel Math
    # K(x1, x2) = variance * exp(- ||x1 - x2||^2 / (2 * lengthscale^2))
    
    sq_dist = sum((X1 .- X2) .^ 2)
    
    exponent = -sq_dist / (2.0 * lengthscale^2)
    
    # Cap exponent to prevent underflow/overflow deterministically
    exponent = max(-500.0, min(500.0, exponent))
    
    k_val = variance * exp(exponent)

    return OmniResult{Float64, String}(k_val, nothing)
end

end
