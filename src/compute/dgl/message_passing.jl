struct OmniResult{T}
    value::Union{T, Nothing}
    error::Union{String, Nothing}
    is_ok::Bool
end

function message_passing(node_features::Array{Float32, 2}, adj_matrix::Array{Float32, 2})
    if size(node_features, 1) != size(adj_matrix, 1)
        return OmniResult{Array{Float32, 2}}(nothing, "Dimension mismatch", false)
    end
    
    # Julia high performance matrix multiplication for DGL message passing
    new_features = adj_matrix * node_features
    
    return OmniResult{Array{Float32, 2}}(new_features, nothing, true)
end
