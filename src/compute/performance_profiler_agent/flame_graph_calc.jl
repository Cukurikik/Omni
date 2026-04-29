module PerformanceProfilerAgent

export OmniResult, compute_stack_duration

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

# Deterministic calculation of function stack durations
# Used by the Performance Profiler to generate Flame Graphs and identify CPU bottlenecks
function compute_stack_duration(entry_timestamp::Int64, exit_timestamp::Int64, child_durations::Vector{Int64}) :: OmniResult{Tuple{Int64, Int64}, String}
    if entry_timestamp > exit_timestamp
        return OmniResult("Exit timestamp must be greater than or equal to entry timestamp", Tuple{Int64, Int64})
    end
    
    total_duration = exit_timestamp - entry_timestamp
    
    sum_children = sum(child_durations)
    if sum_children > total_duration
        return OmniResult("Child durations cannot exceed total stack duration", Tuple{Int64, Int64})
    end
    
    # Self-time is the time spent in THIS function, excluding time spent in child functions
    self_duration = total_duration - sum_children
    
    return OmniResult((total_duration, self_duration))
end

end
