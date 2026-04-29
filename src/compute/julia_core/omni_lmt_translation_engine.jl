// Omni LMT Translation Engine (Julia)
// Compute: Vectorized BLEU and translation metrics.
// Ref: NiuTrans/LMT
module OmniLMTEngine
function bleu_ngram(candidate::Vector{String}, reference::Vector{String}, n::Int)
    c_ngrams = [candidate[i:min(i+n-1,end)] for i in 1:length(candidate)-n+1]
    r_ngrams = Set([reference[i:min(i+n-1,end)] for i in 1:length(reference)-n+1])
    isempty(c_ngrams) && return 0.0
    matches = count(ng -> ng in r_ngrams, c_ngrams)
    return matches / length(c_ngrams)
end
function brevity_penalty(c_len::Int, r_len::Int)
    c_len >= r_len && return 1.0
    return exp(1.0 - r_len / max(c_len, 1))
end
end
