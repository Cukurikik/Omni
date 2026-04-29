module HAProxyLB

export OmniResult, compute_least_connections_node

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

# Deterministic Least Connections Load Balancing Math
function compute_least_connections_node(active_connections::Vector{Int}) :: OmniResult{Int, String}
    if isempty(active_connections)
        return OmniResult("Connection pool cannot be empty", Int)
    end

    min_conn = typemax(Int)
    best_idx = -1

    for i in 1:length(active_connections)
        if active_connections[i] < min_conn
            min_conn = active_connections[i]
            best_idx = i
        end
    end

    # Return 1-based index (Julia standard)
    return OmniResult(best_idx)
end

end
