module MolecularMPNN

struct OmniResult{T, E}
    value::Union{T, Nothing}
    error::Union{E, Nothing}
end

function is_ok(res::OmniResult)::Bool
    return res.error === nothing
end

function apply_graph_convolution(node_features::Matrix{Float64}, adjacency_matrix::Matrix{Float64})::OmniResult{Matrix{Float64}, String}
    # Validate dimensions
    n_nodes, n_features = size(node_features)
    adj_rows, adj_cols = size(adjacency_matrix)
    
    if n_nodes != adj_rows || n_nodes != adj_cols
        return OmniResult{Matrix{Float64}, String}(nothing, "Dimension mismatch between node features and adjacency matrix")
    end

    # Deterministic simple Graph Convolution: H' = A * H
    # (Where A is adjacency, H is features)
    
    updated_features = adjacency_matrix * node_features
    
    return OmniResult{Matrix{Float64}, String}(updated_features, nothing)
end

end
