# OMNI MOTHER: Scientific Data Processing (Production Grade)
using Statistics

module OmniWeatherStats

export compute_climate_drift

function compute_climate_drift(historical_temps::Vector{Float64}, current_temps::Vector{Float64})
    if length(historical_temps) == 0 || length(current_temps) == 0
        return 0.0
    end
    
    hist_mean = mean(historical_temps)
    curr_mean = mean(current_temps)
    
    drift = (curr_mean - hist_mean) / hist_mean * 100.0
    println("[OMNI JULIA] Computed Climate Drift: $drift%")
    
    return drift
end

end # module
