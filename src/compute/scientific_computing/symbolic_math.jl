module SymbolicMath

struct OmniResult{T, E}
    value::Union{T, Nothing}
    error::Union{E, Nothing}
end

function is_ok(res::OmniResult)::Bool
    return res.error === nothing
end

function compute_derivative_at_point(polynomial_coeffs::Vector{Float64}, x::Float64)::OmniResult{Float64, String}
    if length(polynomial_coeffs) == 0
        return OmniResult{Float64, String}(nothing, "Polynomial coefficients cannot be empty")
    end

    # Deterministic derivative computation: d/dx (c_0 + c_1*x + c_2*x^2 ...)
    # Evaluated at point x
    derivative_val = 0.0
    for i in 2:length(polynomial_coeffs)
        power = i - 1
        coeff = polynomial_coeffs[i]
        derivative_val += coeff * power * (x ^ (power - 1))
    end
    
    return OmniResult{Float64, String}(derivative_val, nothing)
end

end
