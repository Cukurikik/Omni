module CircuitBreaker

export OmniResult, compute_exponential_decay_error_rate

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

# Deterministic Exponential Moving Average (EMA) for Error Rates
function compute_exponential_decay_error_rate(prev_ema::Float64, is_error::Bool, alpha::Float64) :: OmniResult{Float64, String}
    if alpha <= 0.0 || alpha > 1.0
        return OmniResult("Alpha smoothing factor must be in (0, 1]", Float64)
    end
    
    if prev_ema < 0.0 || prev_ema > 1.0
        return OmniResult("Previous EMA error rate must be in [0, 1]", Float64)
    end

    current_val = is_error ? 1.0 : 0.0
    
    # EMA formula: (value * alpha) + (prev_ema * (1 - alpha))
    new_ema = (current_val * alpha) + (prev_ema * (1.0 - alpha))
    
    return OmniResult(new_ema)
end

end
