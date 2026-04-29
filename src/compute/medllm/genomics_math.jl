module GenomicsMath

struct OmniResult{T}
    value::Union{T, Nothing}
    error::Union{String, Nothing}
    is_ok::Bool
end

function compute_snp_distance(seq1::Vector{Int}, seq2::Vector{Int})::OmniResult{Float64}
    if length(seq1) != length(seq2)
        return OmniResult{Float64}(nothing, "Sequence length mismatch", false)
    end
    
    # Julia high-performance genomics math
    diffs = sum(seq1 .!= seq2)
    dist = diffs / length(seq1)
    
    return OmniResult{Float64}(dist, nothing, true)
end

end
