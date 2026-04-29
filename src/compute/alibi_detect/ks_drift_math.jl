module AlibiDetect

export OmniResult, compute_ks_statistic

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

# Deterministic Kolmogorov-Smirnov Test Math for Drift
function compute_ks_statistic(ref_data::Vector{Float64}, test_data::Vector{Float64}) :: OmniResult{Float64, String}
    if isempty(ref_data) || isempty(test_data)
        return OmniResult("Reference and test data cannot be empty", Float64)
    end

    # Sort arrays
    sorted_ref = sort(ref_data)
    sorted_test = sort(test_data)

    n1 = length(sorted_ref)
    n2 = length(sorted_test)

    # Compute empirical CDFs and find max distance
    max_dist = 0.0
    i = 1
    j = 1

    while i <= n1 && j <= n2
        val1 = sorted_ref[i]
        val2 = sorted_test[j]

        if val1 <= val2
            cdf1 = i / n1
            cdf2 = (j - 1) / n2
            dist = abs(cdf1 - cdf2)
            max_dist = max(max_dist, dist)
            i += 1
        else
            cdf1 = (i - 1) / n1
            cdf2 = j / n2
            dist = abs(cdf1 - cdf2)
            max_dist = max(max_dist, dist)
            j += 1
        end
    end

    return OmniResult(max_dist)
end

end
