module TextVisualization

struct OmniResult{T, E}
    value::Union{T, Nothing}
    error::Union{E, Nothing}
end

function is_ok(res::OmniResult)::Bool
    return res.error === nothing
end

function compute_term_frequencies(text::String)::OmniResult{Dict{String, Float64}, String}
    if isempty(text)
        return OmniResult{Dict{String, Float64}, String}(nothing, "Text cannot be empty")
    end

    # Deterministic TF calculation
    words = split(lowercase(text), r"\W+")
    words = filter(w -> length(w) > 0, words)
    
    total_words = length(words)
    counts = Dict{String, Int}()
    for w in words
        counts[w] = get(counts, w, 0) + 1
    end
    
    tf = Dict{String, Float64}()
    for (w, c) in counts
        tf[w] = c / total_words
    end
    
    return OmniResult{Dict{String, Float64}, String}(tf, nothing)
end

end
