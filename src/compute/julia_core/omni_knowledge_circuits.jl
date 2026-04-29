// Omni Knowledge Circuits Julia SIMD (Julia)
// Compute Layer: Vectorized circuit attribution scoring.
// Ref: zjunlp/KnowledgeCircuits — NeurIPS 2024

module OmniKnowledgeCircuits

function compute_attributions(activations::Matrix{Float64}, threshold::Float64)
    rows, cols = size(activations)
    results = Float64[]
    for i in 1:rows
        for j in 1:cols
            score = tanh(activations[i, j])
            if abs(score) >= threshold
                push!(results, score)
            end
        end
    end
    return results
end

function circuit_importance(scores::Vector{Float64})
    isempty(scores) && return 0.0
    return sum(abs, scores) / length(scores)
end

end # module
