module TimeSeriesForecaster

export OmniResult, compute_moving_average

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

# Deterministic calculation of Simple Moving Average (SMA)
# Used as a baseline for LLM-based Time-Series Forecasting
function compute_moving_average(series::Vector{Float64}, window_size::Int) :: OmniResult{Vector{Float64}, String}
    if window_size <= 0 || window_size > length(series)
        return OmniResult("Invalid window size", Vector{Float64})
    end
    
    n = length(series)
    result = zeros(Float64, n - window_size + 1)
    
    # Calculate first window
    current_sum = sum(series[1:window_size])
    result[1] = current_sum / window_size
    
    # Sliding window
    for i in 2:length(result)
        current_sum = current_sum - series[i - 1] + series[i + window_size - 1]
        result[i] = current_sum / window_size
    end
    
    return OmniResult(result)
end

end
