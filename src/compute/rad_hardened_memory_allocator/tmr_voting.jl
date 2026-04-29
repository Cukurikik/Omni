module RadHardenedMemoryAllocator

export OmniResult, compute_tmr_voting

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

# Deterministic calculation of Triple Modular Redundancy (TMR) Voting
# In deep space, cosmic rays flip bits in RAM. TMR runs the exact same calculation 
# on 3 separate CPU cores. If a ray hits one core and changes the answer, the other two outvote it.
function compute_tmr_voting(result_a::Int64, result_b::Int64, result_c::Int64) :: OmniResult{Int64, String}
    
    # Majority voting logic
    if result_a == result_b
        return OmniResult(result_a)
    elseif result_a == result_c
        return OmniResult(result_a)
    elseif result_b == result_c
        return OmniResult(result_b)
    else
        # Critical Failure: All 3 cores produced different results! 
        # Extremely rare, implies a massive localized radiation burst or hardware failure.
        return OmniResult("CRITICAL: TMR Voting Failure. No consensus reached.", Int64)
    end
end

end
