module KafkaBroker

export OmniResult, binary_search_offset

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

# Deterministic Binary Search on Kafka Log Index
function binary_search_offset(index_entries::Vector{Int}, target_offset::Int) :: OmniResult{Int, String}
    if isempty(index_entries)
        return OmniResult("Index is empty", Int)
    end

    left = 1
    right = length(index_entries)
    best_match = 1

    while left <= right
        mid = div(left + right, 2)
        if index_entries[mid] == target_offset
            return OmniResult(mid)
        elseif index_entries[mid] < target_offset
            best_match = mid
            left = mid + 1
        else
            right = mid - 1
        end
    end

    # Returns the closest index that is less than or equal to the target offset
    return OmniResult(best_match)
end

end
