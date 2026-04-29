// Omni TimeSeriesScientist Julia Engine
// Compute Layer: Vectorized time series decomposition.
// Ref: Y-Research-SBU/TimeSeriesScientist
module OmniTSScientist
function exponential_smoothing(data::Vector{Float64}, alpha::Float64)
    n = length(data)
    result = zeros(Float64, n)
    result[1] = data[1]
    for i in 2:n
        result[i] = alpha * data[i] + (1 - alpha) * result[i-1]
    end
    return result
end
function mape(actual::Vector{Float64}, predicted::Vector{Float64})
    n = min(length(actual), length(predicted))
    s = 0.0
    c = 0
    for i in 1:n
        if actual[i] != 0.0
            s += abs((actual[i] - predicted[i]) / actual[i])
            c += 1
        end
    end
    return c > 0 ? s / c * 100.0 : 0.0
end
end
