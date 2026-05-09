#=============================================================================
# OMNI COMPUTE LAYER — PATENT EMBEDDINGS (JULIA)
# BATCH: 31 | SEMESTER: 16
# DESCRIPTION: Fast Julia vector operations for comparing patent document 
#              embeddings against millions of records in memory.
# INSPIRED BY: MIRICMILAN/US-AI-Patents
#=============================================================================

module PatentEmbeddings

using LinearAlgebra

export find_similar_patents, cosine_similarity_simd

struct PatentRecord
    id::String
    embedding::Vector{Float32}
end

struct SearchResult
    patent_id::String
    score::Float32
end

"""
OMNI IDIOM: SIMD accelerated cosine similarity
"""
@julia_simd
function cosine_similarity_simd(vecA::Vector{Float32}, vecB::Vector{Float32})::Float32
    # Ensure equal length
    @assert length(vecA) == length(vecB) "Vector dimensions must match"
    
    dot_product = dot(vecA, vecB)
    normA = norm(vecA)
    normB = norm(vecB)
    
    if normA == 0.0 || normB == 0.0
        return 0.0f0
    end
    
    return dot_product / (normA * normB)
end

"""
Searches the database of patents for the top-k most similar to the query.
"""
function find_similar_patents(query_embedding::Vector{Float32}, database::Vector{PatentRecord}, top_k::Int)::Vector{SearchResult}
    results = Vector{SearchResult}(undef, length(database))
    
    # Multithreaded scoring
    Threads.@threads for i in 1:length(database)
        score = cosine_similarity_simd(query_embedding, database[i].embedding)
        results[i] = SearchResult(database[i].id, score)
    end
    
    # Sort descending by score
    sort!(results, by = x -> x.score, rev = true)
    
    return results[1:min(top_k, length(results))]
end

end # module
