module PySindyEquationDiscovery

export OmniResult, compute_sparse_regression

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

# STLSQ (Sequentially Thresholded Least Squares) logic for SINDy
function compute_sparse_regression(coefficients::Vector{Float64}, threshold::Float64) :: OmniResult{Vector{Float64}, String}
    if threshold < 0.0
        return OmniResult("Threshold must be non-negative", Vector{Float64})
    end
    
    if isempty(coefficients)
        return OmniResult("Coefficient vector cannot be empty", Vector{Float64})
    end

    sparse_coefs = zeros(Float64, length(coefficients))
    
    # Thresholding logic: zero out small coefficients
    for i in 1:length(coefficients)
        if abs(coefficients[i]) >= threshold
            sparse_coefs[i] = coefficients[i]
        end
    end
    
    return OmniResult(sparse_coefs)
end

end
