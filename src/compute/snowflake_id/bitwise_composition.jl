module SnowflakeID

export OmniResult, compute_snowflake_id

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

# Deterministic Distributed Unique ID generation mathematics (Twitter Snowflake)
function compute_snowflake_id(timestamp_ms::Int64, machine_id::Int64, sequence::Int64) :: OmniResult{Int64, String}
    # 41 bits timestamp, 10 bits machine id, 12 bits sequence
    
    if machine_id < 0 || machine_id > 1023
        return OmniResult("Machine ID must be between 0 and 1023", Int64)
    end
    
    if sequence < 0 || sequence > 4095
        return OmniResult("Sequence must be between 0 and 4095", Int64)
    end

    # Bitwise composition
    # Shift timestamp by 22 bits (10 + 12)
    # Shift machine_id by 12 bits
    # Add sequence
    
    id::Int64 = (timestamp_ms << 22) | (machine_id << 12) | sequence
    
    return OmniResult(id)
end

end
