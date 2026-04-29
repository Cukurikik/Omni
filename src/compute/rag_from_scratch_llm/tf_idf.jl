module RAGFromScratch

export OmniResult, compute_tf_idf

struct OmniResult{T, E}
    value::Union{T, Nothing}
    error::Union{E, Nothing}
    is_ok::Bool
end

function OmniResult(value::T) where T
    OmniResult{T, String}(value, nothing, true)
end

function OmniResult(error::String, ::Type{T}=Any) where T
    OmniResult{T, String}(nothing, error, false)
end

# Deterministic calculation of TF-IDF (Term Frequency - Inverse Document Frequency)
# Built from scratch for bare-metal RAG implementations
function compute_tf_idf(term_freq: Int, total_terms_in_doc: Int, doc_containing_term: Int, total_documents: Int) :: OmniResult{Float64, String}
    if total_terms_in_doc <= 0 || total_documents <= 0
        return OmniResult("Total counts must be strictly positive", Float64)
    end
    
    if doc_containing_term <= 0
        return OmniResult(0.0) # Term not found in corpus
    end

    # TF: Normalized term frequency
    tf = term_freq / total_terms_in_doc
    
    # IDF: Inverse document frequency (with smoothing)
    idf = log10(total_documents / doc_containing_term)
    
    return OmniResult(tf * idf)
end

end
