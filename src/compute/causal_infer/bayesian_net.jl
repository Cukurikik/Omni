module BayesianNetwork

struct OmniResult{T, E}
    value::Union{T, Nothing}
    error::Union{E, Nothing}
end

function is_ok(res::OmniResult)::Bool
    return res.error === nothing
end

function compute_marginal_probability(observations::Vector{Float64}, prior::Float64)::OmniResult{Float64, String}
    if length(observations) == 0
        return OmniResult{Float64, String}(nothing, "Empty observations array")
    end
    
    if prior <= 0.0 || prior >= 1.0
        return OmniResult{Float64, String}(nothing, "Invalid prior probability")
    end

    # Deterministic Bayes Update
    likelihood = sum(observations) / length(observations)
    posterior = (likelihood * prior) / ((likelihood * prior) + ((1.0 - likelihood) * (1.0 - prior)))
    
    return OmniResult{Float64, String}(posterior, nothing)
end

end
