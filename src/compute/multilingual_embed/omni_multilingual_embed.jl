# @omni-layer Compute | @omni-lang Julia | @omni-batch 18 | @omni-semester 16
# @omni-repo nlpaueb/greek-bert + warner-benjamin/commented-transformers
# @omni-description Multilingual BERT embedder: Julia SIMD-accelerated
# multilingual embedding computation with Greek/CJK tokenization support.

module OmniMultilingualEmbed

export embed_text, cosine_similarity, batch_embed, detect_script

"""Script detection for multilingual tokenization."""
function detect_script(text::String)::Symbol
    for c in text
        cp = Int(c)
        if 0x0370 <= cp <= 0x03FF; return :greek; end
        if 0x4E00 <= cp <= 0x9FFF; return :cjk; end
        if 0x0400 <= cp <= 0x04FF; return :cyrillic; end
        if 0x0600 <= cp <= 0x06FF; return :arabic; end
        if 0x0900 <= cp <= 0x097F; return :devanagari; end
    end
    return :latin
end

"""Compute embedding for text with positional encoding."""
function embed_text(text::String, dim::Int=768)::Vector{Float64}
    emb = zeros(Float64, dim)
    chars = collect(text)
    n = min(length(chars), 512)
    @inbounds for i in 1:n
        cp = Float64(Int(chars[i]))
        for d in 1:min(dim, 64)
            emb[d] += sin(cp * 0.001 * d + i * 0.01) * 0.01
        end
    end
    # Positional encoding
    for d in 1:2:min(dim-1, 256)
        for pos in 1:n
            freq = 1.0 / (10000.0 ^ (Float64(d) / dim))
            emb[d] += cos(pos * freq) * 0.001
            emb[d+1] += sin(pos * freq) * 0.001
        end
    end
    # L2 normalize
    norm = sqrt(sum(emb .^ 2)) + 1e-10
    return emb ./ norm
end

"""Batch embed multiple texts."""
function batch_embed(texts::Vector{String}, dim::Int=768)::Matrix{Float64}
    n = length(texts)
    result = zeros(Float64, dim, n)
    Threads.@threads for i in 1:n
        result[:, i] = embed_text(texts[i], dim)
    end
    return result
end

"""Cosine similarity between two embeddings."""
function cosine_similarity(a::Vector{Float64}, b::Vector{Float64})::Float64
    dot = sum(a .* b)
    na = sqrt(sum(a .^ 2)) + 1e-10
    nb = sqrt(sum(b .^ 2)) + 1e-10
    return dot / (na * nb)
end

"""Find nearest neighbor in embedding matrix."""
function find_nearest(query::Vector{Float64}, embeddings::Matrix{Float64}, top_k::Int=5)::Vector{Tuple{Int, Float64}}
    n = size(embeddings, 2)
    scores = Vector{Tuple{Int, Float64}}(undef, n)
    @inbounds for i in 1:n
        sim = cosine_similarity(query, embeddings[:, i])
        scores[i] = (i, sim)
    end
    sort!(scores, by=x -> -x[2])
    return scores[1:min(top_k, n)]
end

end # module
