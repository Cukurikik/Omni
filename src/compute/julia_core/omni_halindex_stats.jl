// Omni Hallucination Index Stats (Julia)
// Ref: rungalileo/hallucination-index
module OmniHalIndexJulia
function chainpoll_consistency(responses::Vector{String})
    unique_count = length(unique(responses))
    return 1.0 - (unique_count - 1) / max(length(responses), 1)
end
function context_adherence(resp_tokens::Vector{String}, src_tokens::Vector{String})
    src_set = Set(src_tokens)
    grounded = count(t -> t in src_set, resp_tokens)
    return grounded / max(length(resp_tokens), 1)
end
end
