# @omni-layer Compute | @omni-source lucidrains/ETSformer-pytorch | @omni-lang Julia
# @omni-description SIMD exponential smoothing kernel: high-performance
# Holt-Winters decomposition with vectorized level/trend/season updates.

module OmniExponentialSmoothing

function holt_winters(series::Vector{Float64}, alpha::Float64, beta::Float64, gamma::Float64, period::Int)
    n = length(series)
    level = zeros(Float64, n)
    trend = zeros(Float64, n)
    season = zeros(Float64, n)
    forecast = zeros(Float64, n)
    level[1] = series[1]
    trend[1] = period > 1 ? (series[min(period+1,n)] - series[1]) / period : 0.0
    for i in 1:min(period, n)
        season[i] = series[i] - level[1]
    end
    for t in 2:n
        sp = t > period ? season[t - period] : 0.0
        level[t] = alpha * (series[t] - sp) + (1 - alpha) * (level[t-1] + trend[t-1])
        trend[t] = beta * (level[t] - level[t-1]) + (1 - beta) * trend[t-1]
        season[t] = gamma * (series[t] - level[t]) + (1 - gamma) * sp
        forecast[t] = level[t] + trend[t] + season[t]
    end
    return (level=level, trend=trend, season=season, forecast=forecast)
end

function forecast_ahead(level_last::Float64, trend_last::Float64, season_vec::Vector{Float64}, steps::Int, period::Int)
    preds = zeros(Float64, steps)
    for h in 1:steps
        s_idx = ((h - 1) % period) + 1
        s_val = s_idx <= length(season_vec) ? season_vec[s_idx] : 0.0
        preds[h] = level_last + h * trend_last + s_val
    end
    return preds
end

function mse(actual::Vector{Float64}, predicted::Vector{Float64})
    n = min(length(actual), length(predicted))
    return sum((actual[i] - predicted[i])^2 for i in 1:n) / n
end

end # module
