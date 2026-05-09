#=============================================================================
# OMNI COMPUTE LAYER — NER ALIGNMENT (JULIA)
# BATCH: 31 | SEMESTER: 16
# DESCRIPTION: Extremely fast Named Entity Recognition (NER) token alignment 
#              and resolution using Julia.
#=============================================================================

module NERAlignment

export align_tokens_to_entities

struct Token
    text::String
    start_pos::Int
    end_pos::Int
end

struct EntityPrediction
    label::String
    confidence::Float32
    token_indices::Vector{Int}
end

struct ResolvedEntity
    text::String
    label::String
    start_pos::Int
    end_pos::Int
    confidence::Float32
end

"""
OMNI IDIOM: Vectorized operations for merging contiguous NER predictions
"""
function align_tokens_to_entities(
    tokens::Vector{Token}, 
    predictions::Vector{EntityPrediction}
)::Vector{ResolvedEntity}
    
    resolved = Vector{ResolvedEntity}()
    
    for pred in predictions
        if isempty(pred.token_indices)
            continue
        end
        
        # Extract corresponding tokens
        entity_tokens = tokens[pred.token_indices]
        
        # Combine text (naive join, zero-mock assumes proper spacing handling in prod)
        combined_text = join([t.text for t in entity_tokens], " ")
        
        start_idx = entity_tokens[1].start_pos
        end_idx = entity_tokens[end].end_pos
        
        push!(resolved, ResolvedEntity(
            combined_text, 
            pred.label, 
            start_idx, 
            end_idx, 
            pred.confidence
        ))
    end
    
    return resolved
end

end # module
