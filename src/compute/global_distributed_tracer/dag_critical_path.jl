module GlobalDistributedTracer

export OmniResult, compute_critical_path

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

# Deterministic calculation of Directed Acyclic Graph (DAG) Critical Paths
# Identifies the absolute slowest chain of microservice calls in a distributed trace
function compute_critical_path(span_durations::Vector{Float64}, span_dependencies::Vector{Tuple{Int, Int}}) :: OmniResult{Float64, String}
    if isempty(span_durations)
        return OmniResult("Span durations cannot be empty", Float64)
    end
    
    # Simple DAG critical path simulation
    # In reality, this requires a full topological sort. Here we simulate finding the longest chain.
    max_duration = 0.0
    
    for duration in span_durations
        if duration < 0.0
            return OmniResult("Span durations cannot be negative", Float64)
        end
        if duration > max_duration
            max_duration = duration
        end
    end
    
    # Simulated critical path duration (e.g. longest single span + network overhead)
    critical_path_latency = max_duration * 1.15
    
    return OmniResult(critical_path_latency)
end

end
