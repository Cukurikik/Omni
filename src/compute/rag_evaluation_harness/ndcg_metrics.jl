module RAGEvaluationHarness

export OmniResult, compute_dcg

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

# Deterministic calculation of Discounted Cumulative Gain (DCG) for RAG Evaluation
function compute_dcg(relevance_scores::Vector{Float64}) :: OmniResult{Float64, String}
    if isempty(relevance_scores)
        return OmniResult("Relevance scores array cannot be empty", Float64)
    end
    
    dcg = 0.0
    for (i, rel) in enumerate(relevance_scores)
        if rel < 0.0
             return OmniResult("Relevance scores must be non-negative", Float64)
        end
        # DCG formula: sum(rel_i / log2(i + 1))
        dcg += rel / log2(i + 1)
    end
    
    return OmniResult(dcg)
end

end
