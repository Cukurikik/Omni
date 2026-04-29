module Model2VecEmbedder

using LinearAlgebra

struct OmniResult{T, E}
    value::Union{T, Nothing}
    error::Union{E, Nothing}
end

function is_ok(res::OmniResult)::Bool
    return res.error === nothing
end

function pca_reduce_embeddings(embeddings::Matrix{Float64}, target_dim::Int)::OmniResult{Matrix{Float64}, String}
    n_samples, n_features = size(embeddings)
    
    if target_dim <= 0 || target_dim > n_features
        return OmniResult{Matrix{Float64}, String}(nothing, "Invalid target dimension")
    end
    
    if n_samples == 0
        return OmniResult{Matrix{Float64}, String}(nothing, "Empty embeddings matrix")
    end

    # Deterministic Principal Component Analysis (PCA) Math
    
    # 1. Center the data
    mean_vec = sum(embeddings, dims=1) ./ n_samples
    centered_data = embeddings .- mean_vec
    
    # 2. Compute covariance matrix
    # Using deterministic math: (X^T * X) / (n - 1)
    cov_matrix = (transpose(centered_data) * centered_data) ./ (n_samples - 1)
    
    # 3. Eigen decomposition (Deterministic SVD equivalent for symmetric pos-def)
    eigen_decomp = eigen(cov_matrix)
    
    # 4. Sort eigenvalues and eigenvectors in descending order
    idx = sortperm(eigen_decomp.values, rev=true)
    sorted_vectors = eigen_decomp.vectors[:, idx]
    
    # 5. Select target_dim principal components
    projection_matrix = sorted_vectors[:, 1:target_dim]
    
    # 6. Project data onto new dimensions
    reduced_embeddings = centered_data * projection_matrix
    
    return OmniResult{Matrix{Float64}, String}(reduced_embeddings, nothing)
end

end
