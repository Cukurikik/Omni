module TensorboardViz

export OmniResult, compute_histogram_bins

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

# Deterministic Histogram Binning Math matching TensorBoard logic
function compute_histogram_bins(data::Vector{Float64}, num_bins::Int) :: OmniResult{Dict{String, Any}, String}
    if isempty(data)
        return OmniResult("Data array cannot be empty", Dict{String, Any})
    end

    if num_bins <= 0
        return OmniResult("Number of bins must be strictly positive", Dict{String, Any})
    end

    min_val = minimum(data)
    max_val = maximum(data)

    if min_val == max_val
        # Edge case: all identical values
        return OmniResult(Dict{String, Any}(
            "min" => min_val,
            "max" => max_val,
            "counts" => [length(data)],
            "edges" => [min_val, max_val]
        ))
    end

    bin_width = (max_val - min_val) / num_bins
    counts = zeros(Int, num_bins)
    edges = collect(range(min_val, max_val, length=num_bins+1))

    for val in data
        bin_idx = floor(Int, (val - min_val) / bin_width) + 1
        # Handle maximum value edge case
        if bin_idx > num_bins
            bin_idx = num_bins
        end
        counts[bin_idx] += 1
    end

    return OmniResult(Dict{String, Any}(
        "min" => min_val,
        "max" => max_val,
        "counts" => counts,
        "edges" => edges
    ))
end

end
