module IoTSensorFusion

export OmniResult, compute_kalman_update

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

# Deterministic calculation of 1D Kalman Filter state estimation
# Used to fuse noisy IoT sensor data (e.g. GPS + Accelerometer) into a clean signal
function compute_kalman_update(prior_estimate::Float64, prior_error::Float64, measurement::Float64, measurement_noise::Float64) :: OmniResult{Tuple{Float64, Float64}, String}
    if prior_error <= 0.0 || measurement_noise <= 0.0
        return OmniResult("Error covariances must be positive", Tuple{Float64, Float64})
    end
    
    # Kalman Gain
    k_gain = prior_error / (prior_error + measurement_noise)
    
    # State Update
    new_estimate = prior_estimate + k_gain * (measurement - prior_estimate)
    
    # Error Update
    new_error = (1.0 - k_gain) * prior_error
    
    return OmniResult((new_estimate, new_error))
end

end
