module RankingMath

struct OmniResult{T}
    value::Union{T, Nothing}
    error::Union{String, Nothing}
    is_ok::Bool
end

function compute_bm25(tf::Vector{Float64}, idf::Vector{Float64})::OmniResult{Vector{Float64}}
    if length(tf) != length(idf)
        return OmniResult{Vector{Float64}}(nothing, "Dimension mismatch", false)
    end
    
    # Julia high-performance BM25 vectorization
    k1 = 1.5
    b = 0.75
    scores = (tf .* (k1 + 1)) ./ (tf .+ k1) .* idf
    
    return OmniResult{Vector{Float64}}(scores, nothing, true)
end

end
