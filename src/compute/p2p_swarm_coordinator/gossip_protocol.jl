module P2PSwarmCoordinator

export OmniResult, compute_gossip_spread

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

# Deterministic calculation of Gossip Protocol spread times
# Used by decentralized AI Swarms to determine how long it takes for all peers to receive a message
function compute_gossip_spread(num_peers::Int, fanout::Int) :: OmniResult{Int, String}
    if num_peers <= 0 || fanout <= 1
        return OmniResult("Invalid swarm parameters", Int)
    end
    
    # Cycles required to reach all nodes: log_{fanout}(num_peers)
    cycles = ceil(Int, log(num_peers) / log(fanout))
    
    return OmniResult(cycles)
end

end
