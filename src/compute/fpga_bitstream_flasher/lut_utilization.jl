module FpgaBitstreamFlasher

export OmniResult, compute_lut_utilization

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

# Deterministic calculation of FPGA Look-Up Table (LUT) utilization
# Prevents flashing a bitstream that is too large for the physical FPGA fabric
function compute_lut_utilization(required_luts::Int, total_available_luts::Int) :: OmniResult{Float64, String}
    if required_luts < 0 || total_available_luts <= 0
        return OmniResult("Invalid LUT parameters", Float64)
    end
    
    if required_luts > total_available_luts
        return OmniResult("Bitstream LUT requirement exceeds hardware capacity", Float64)
    end
    
    utilization_pct = (Float64(required_luts) / Float64(total_available_luts)) * 100.0
    
    return OmniResult(utilization_pct)
end

end
