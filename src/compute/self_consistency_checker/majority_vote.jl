module SelfConsistencyChecker

export OmniResult, compute_majority_vote

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

# Deterministic computation of Majority Vote for Self-Consistency chains
# Used when an LLM is sampled multiple times for the same question
function compute_majority_vote(votes::Vector{Int}) :: OmniResult{Int, String}
    if isempty(votes)
        return OmniResult("Vote array cannot be empty", Int)
    end
    
    # Tally votes (using dictionary-like logic, optimized for integers)
    counts = Dict{Int, Int}()
    for v in votes
        counts[v] = get(counts, v, 0) + 1
    end
    
    max_count = 0
    winner = -1
    
    for (k, v) in counts
        if v > max_count
            max_count = v
            winner = k
        end
    end
    
    return OmniResult(winner)
end

end
