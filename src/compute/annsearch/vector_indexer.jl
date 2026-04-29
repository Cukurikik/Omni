module OmniANNSearch

export struct OmniResult{T}
    data::Union{T, Nothing}
    error::Union{String, Nothing}
end

OmniResult(data::T) where T = OmniResult{T}(data, nothing)
OmniResult(::Type{T}, error::String) where T = OmniResult{T}(nothing, error)

struct VectorIndex
    dimensions::Int
    vectors::Matrix{Float64}
    metric::String
end

function build_index(data_matrix::Matrix{Float64}, metric::String="euclidean")::OmniResult{VectorIndex}
    try
        if size(data_matrix, 1) == 0 || size(data_matrix, 2) == 0
            return OmniResult(VectorIndex, "Data matrix cannot be empty.")
        end
        return OmniResult(VectorIndex(size(data_matrix, 1), data_matrix, metric))
    catch e
        return OmniResult(VectorIndex, "Index build failed: $(string(e))")
    end
end

function exact_knn_search(index::VectorIndex, query::Vector{Float64}, k::Int)::OmniResult{Vector{Int}}
    try
        if length(query) != index.dimensions
            return OmniResult(Vector{Int}, "Query dimension mismatch.")
        end
        
        # Real mathematical distance computation
        num_vectors = size(index.vectors, 2)
        distances = zeros(Float64, num_vectors)
        
        @inbounds for i in 1:num_vectors
            diff = index.vectors[:, i] .- query
            if index.metric == "euclidean"
                distances[i] = sum(diff .^ 2)
            elseif index.metric == "cosine"
                dot_prod = sum(index.vectors[:, i] .* query)
                norm_v = sqrt(sum(index.vectors[:, i] .^ 2))
                norm_q = sqrt(sum(query .^ 2))
                distances[i] = 1.0 - (dot_prod / (norm_v * norm_q + 1e-10))
            end
        end
        
        sorted_indices = sortperm(distances)
        return OmniResult(sorted_indices[1:min(k, num_vectors)])
    catch e
        return OmniResult(Vector{Int}, "Search execution failed: $(string(e))")
    end
end

end # module
