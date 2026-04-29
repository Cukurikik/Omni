module IDETelemetryTracker

export OmniResult, compute_keystroke_efficiency

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

# Deterministic calculation of developer keystroke efficiency
# Used to analyze how often developers use AI autocomplete vs manual typing
function compute_keystroke_efficiency(ai_tokens_accepted::Int, manual_keystrokes::Int) :: OmniResult{Float64, String}
    if ai_tokens_accepted < 0 || manual_keystrokes < 0
        return OmniResult("Metrics cannot be negative", Float64)
    end
    
    total_effort = ai_tokens_accepted + manual_keystrokes
    
    if total_effort == 0
        return OmniResult(0.0) # No activity
    end
    
    efficiency = ai_tokens_accepted / total_effort
    return OmniResult(efficiency)
end

end
