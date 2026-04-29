module PaxosConsensus

export OmniResult, compute_quorum

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

# Deterministic Paxos Quorum Intersection Math
function compute_quorum(total_nodes::Int) :: OmniResult{Int, String}
    if total_nodes <= 0
        return OmniResult("Total nodes must be strictly positive", Int)
    end

    # Quorum requires strict majority: floor(N / 2) + 1
    quorum_size = div(total_nodes, 2) + 1
    
    return OmniResult(quorum_size)
end

end
