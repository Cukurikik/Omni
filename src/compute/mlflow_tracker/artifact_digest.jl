module MLFlowTracker

export OmniResult, compute_artifact_digest

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

# Deterministic artifact digest math
function compute_artifact_digest(file_sizes::Vector{Int64}, modification_times::Vector{Float64}) :: OmniResult{Float64, String}
    if length(file_sizes) != length(modification_times)
        return OmniResult("Lengths of sizes and times must match", Float64)
    end
    
    if isempty(file_sizes)
        return OmniResult("Artifact lists cannot be empty", Float64)
    end

    digest = 0.0
    for i in 1:length(file_sizes)
        # Deterministic combination of size and timestamp
        digest += (file_sizes[i] * 0.73) + (modification_times[i] * 0.27)
    end

    # Normalize
    return OmniResult(digest / length(file_sizes))
end

end
