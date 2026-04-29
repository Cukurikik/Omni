module OmniCompute.FinancialDataFrame

export calculate_sma, calculate_ema

# OMNI COMPUTE LAYER: Financial DataFrame
# High-performance financial indicator calculations using Julia SIMD capabilities.

struct OmniResult{T, E}
    is_ok::Bool
    ok_value::Union{T, Nothing}
    err_value::Union{E, Nothing}
end

Ok(value) = OmniResult(true, value, nothing)
Err(err) = OmniResult(false, nothing, err)

function calculate_sma(prices::Vector{Float64}, window::Int)::OmniResult{Vector{Float64}, String}
    try
        n = length(prices)
        if window <= 0 || window > n
            return Err("Invalid window size")
        end
        
        sma = zeros(Float64, n)
        sum_val = sum(prices[1:window])
        sma[window] = sum_val / window
        
        @simd for i in (window+1):n
            sum_val = sum_val - prices[i-window] + prices[i]
            sma[i] = sum_val / window
        end
        
        return Ok(sma)
    catch e
        return Err(string("SMA computation failed: ", e))
    end
end

function calculate_ema(prices::Vector{Float64}, window::Int)::OmniResult{Vector{Float64}, String}
    try
        n = length(prices)
        if window <= 0 || window > n
            return Err("Invalid window size")
        end
        
        ema = zeros(Float64, n)
        multiplier = 2.0 / (window + 1)
        ema[window] = sum(prices[1:window]) / window
        
        for i in (window+1):n
            ema[i] = (prices[i] - ema[i-1]) * multiplier + ema[i-1]
        end
        
        return Ok(ema)
    catch e
        return Err(string("EMA computation failed: ", e))
    end
end

end
