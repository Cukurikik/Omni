# OMNI Framework - Julia Math Operations for Stance Detection KE-MLM
module OmniStanceMath

using LinearAlgebra

"""
    compute_cosine_similarity(vec_a::Vector{Float64}, vec_b::Vector{Float64}) -> Float64

Computes the cosine similarity between two embedding vectors for stance detection.
Utilizes Julia's fast BLAS/LAPACK bindings.
"""
function compute_cosine_similarity(vec_a::Vector{Float64}, vec_b::Vector{Float64})::Float64
    dot_product = dot(vec_a, vec_b)
    norm_a = norm(vec_a)
    norm_b = norm(vec_b)
    
    if norm_a == 0.0 || norm_b == 0.0
        return 0.0
    end
    
    return dot_product / (norm_a * norm_b)
end

"""
    apply_knowledge_enhancement(embeddings::Matrix{Float64}, knowledge_graph::Matrix{Float64}, alpha::Float64)

Applies a knowledge graph embedding to the base language model embeddings using a mixing weight `alpha`.
"""
function apply_knowledge_enhancement(embeddings::Matrix{Float64}, knowledge_graph::Matrix{Float64}, alpha::Float64)::Matrix{Float64}
    return (1.0 - alpha) .* embeddings .+ alpha .* knowledge_graph
end

end # module
