# EmbedAnything — Cosine Similarity Search in Julia
module EmbedSearch
struct OmniResult{T, E}
    is_ok::Bool; value::Union{T, Nothing}; error::Union{E, Nothing}
end
const MAX_DIM = 4096; const MAX_DOCS = 10000000
function cosine_search(query::Vector{Float32}, corpus::Matrix{Float32}, top_k::Int)::OmniResult{Vector{Tuple{Int,Float64}}, String}
    d, n = size(corpus)
    if d > MAX_DIM return OmniResult{Vector{Tuple{Int,Float64}}, String}(false, nothing, "Dim exceeds $MAX_DIM") end
    if n > MAX_DOCS return OmniResult{Vector{Tuple{Int,Float64}}, String}(false, nothing, "Docs exceed limit") end
    if length(query) != d return OmniResult{Vector{Tuple{Int,Float64}}, String}(false, nothing, "Query dim mismatch") end
    q_norm = sqrt(sum(query .^ 2))
    if q_norm == 0 return OmniResult{Vector{Tuple{Int,Float64}}, String}(false, nothing, "Zero-norm query") end
    scores = Tuple{Int, Float64}[]
    @simd for i in 1:n
        col = @view corpus[:, i]
        c_norm = sqrt(sum(col .^ 2))
        if c_norm > 0
            sim = Float64(sum(query .* col) / (q_norm * c_norm))
            push!(scores, (i, sim))
        end
    end
    sort!(scores, by=x->x[2], rev=true)
    return OmniResult{Vector{Tuple{Int,Float64}}, String}(true, scores[1:min(top_k, length(scores))], nothing)
end
end
