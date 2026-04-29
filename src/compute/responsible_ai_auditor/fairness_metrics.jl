module ResponsibleAiAuditor

export OmniResult, compute_disparate_impact

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

# Deterministic calculation of Disparate Impact (Fairness Metric)
function compute_disparate_impact(unprivileged_approved::Int, unprivileged_total::Int, privileged_approved::Int, privileged_total::Int) :: OmniResult{Float64, String}
    if unprivileged_total <= 0 || privileged_total <= 0
        return OmniResult("Total population counts must be strictly positive", Float64)
    end
    
    unprivileged_rate = unprivileged_approved / unprivileged_total
    privileged_rate = privileged_approved / privileged_total
    
    if privileged_rate == 0.0
        return OmniResult(1.0) # Edge case: no one was approved in privileged group
    end

    # Standard formula: (Pr(Y^=1 | D=unprivileged)) / (Pr(Y^=1 | D=privileged))
    impact_ratio = unprivileged_rate / privileged_rate
    
    return OmniResult(impact_ratio)
end

end
