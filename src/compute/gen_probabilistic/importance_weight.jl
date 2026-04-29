module GenProbabilistic

export OmniResult, compute_importance_weight

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

# Deterministic Probabilistic Programming Importance Sampling Weight Math
function compute_importance_weight(log_prior::Float64, log_likelihood::Float64, log_proposal::Float64) :: OmniResult{Float64, String}
    # In importance sampling, weight w = (p(x) * p(y|x)) / q(x)
    # Log domain: log(w) = log_prior + log_likelihood - log_proposal
    
    if isnan(log_prior) || isnan(log_likelihood) || isnan(log_proposal)
        return OmniResult("Probabilities cannot be NaN", Float64)
    end
    
    log_weight = log_prior + log_likelihood - log_proposal
    
    return OmniResult(log_weight)
end

end
