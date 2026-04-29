module SatelliteTelemetryDecoder

export OmniResult, compute_ccsds_checksum

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

# Deterministic calculation of CCSDS (Consultative Committee for Space Data Systems) Space Packet Checksums
# Used to verify the integrity of telemetry downloaded from a spacecraft
function compute_ccsds_checksum(packet_data::Vector{UInt8}) :: OmniResult{Bool, String}
    if isempty(packet_data)
        return OmniResult("Packet cannot be empty", Bool)
    end
    
    if length(packet_data) < 2
        return OmniResult("Packet too short for checksum", Bool)
    end
    
    # Simple deterministic CRC/Checksum simulation for CCSDS
    # Sum all bytes, if the modulo 256 matches the last byte, it's valid
    sum::UInt32 = 0
    for i in 1:(length(packet_data)-1)
        sum += packet_data[i]
    end
    
    calculated_checksum = sum % 256
    actual_checksum = packet_data[end]
    
    is_valid = (calculated_checksum == actual_checksum)
    
    return OmniResult(is_valid)
end

end
