module ModinDF

export OmniResult, compute_chunked_mean

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

# Deterministic Distributed Chunk GroupBy/Mean Math
function compute_chunked_mean(chunks::Vector{Vector{Float64}}) :: OmniResult{Float64, String}
    if length(chunks) == 0
        return OmniResult("No chunks provided", Float64)
    end

    total_sum = 0.0
    total_count = 0

    for chunk in chunks
        for val in chunk
            total_sum += val
            total_count += 1
        end
    end

    if total_count == 0
        return OmniResult("All chunks are empty", Float64)
    end

    return OmniResult(total_sum / total_count)
end

end
