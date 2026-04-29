module OmniToolRetrievalBench

# Omni Tool Retrieval Benchmark (Julia)
# Based on mangopy/tool-retrieval-benchmark
# Fast tensor similarity for benchmarking LLM tool retrieval.

using LinearAlgebra

export evaluate_tool_retrieval, ToolBenchResult

struct ToolBenchResult
    success::Bool
    recall_at_k::Float64
    error::String
end

function evaluate_tool_retrieval(query_embedding::Vector{Float64}, tool_embeddings::Matrix{Float64}, target_idx::Int, k::Int)::ToolBenchResult
    if isempty(query_embedding) || isempty(tool_embeddings)
        return ToolBenchResult(false, 0.0, "Embeddings cannot be empty")
    end
    
    n_tools = size(tool_embeddings, 2)
    if target_idx < 1 || target_idx > n_tools
        return ToolBenchResult(false, 0.0, "Invalid target index")
    end

    # Compute Cosine Similarities deterministically
    similarities = zeros(Float64, n_tools)
    q_norm = norm(query_embedding)
    
    for i in 1:n_tools
        t_col = tool_embeddings[:, i]
        t_norm = norm(t_col)
        similarities[i] = dot(query_embedding, t_col) / (q_norm * t_norm)
    end

    # Sort indices descending
    sorted_indices = sortperm(similarities, rev=true)
    
    # Check if target is in top-k
    hit = target_idx in sorted_indices[1:min(k, n_tools)]
    
    return ToolBenchResult(true, hit ? 1.0 : 0.0, "")
end

end
