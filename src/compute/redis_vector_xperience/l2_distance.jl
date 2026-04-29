module RedisVectorXperience

export OmniResult, compute_l2_distance

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

# Deterministic calculation of Euclidean L2 Distance for vector similarity search
function compute_l2_distance(vec_a::Vector{Float64}, vec_b::Vector{Float64}) :: OmniResult{Float64, String}
    if length(vec_a) != length(vec_b)
        return OmniResult("Vectors must have the same dimensionality", Float64)
    end
    
    if isempty(vec_a)
        return OmniResult("Vectors cannot be empty", Float64)
    end

    # Sum of squared differences
    sum_sq = 0.0
    for i in 1:length(vec_a)
        diff = vec_a[i] - vec_b[i]
        sum_sq += diff * diff
    end
    
    distance = sqrt(sum_sq)
    return OmniResult(distance)
end

end
