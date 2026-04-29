module NvlinkBandwidthCalc

export OmniResult, compute_nvswitch_bandwidth

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

# Deterministic calculation of NVIDIA NVSwitch bidirectional bandwidth
# Used to map out how fast data can move between 8 GPUs on a single HGX baseboard
function compute_nvswitch_bandwidth(num_nvlinks_per_gpu::Int, bandwidth_per_link_gbps::Float64) :: OmniResult{Float64, String}
    if num_nvlinks_per_gpu <= 0 || bandwidth_per_link_gbps <= 0.0
        return OmniResult("Link counts and bandwidth must be positive", Float64)
    end
    
    # Total bidirectional bandwidth = Links * Bandwidth_per_link * 2 (Tx and Rx)
    # E.g., Hopper H100 has 18 NVLink Gen4 connections, each 50 GB/s. Total = 18 * 50 = 900 GB/s bidirectional.
    
    total_bandwidth = Float64(num_nvlinks_per_gpu) * bandwidth_per_link_gbps * 2.0
    
    return OmniResult(total_bandwidth)
end

end
