module APIContractVerifier

export OmniResult, validate_schema_fields

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

# Deterministic validation of OpenAPI/GraphQL schema fields
# Ensures that API responses exactly match the defined contract structures
function validate_schema_fields(required_fields::Vector{String}, provided_fields::Vector{String}) :: OmniResult{Bool, String}
    if isempty(required_fields)
        return OmniResult(true) # Nothing required
    end
    
    provided_set = Set(provided_fields)
    
    for field in required_fields
        if !(field in provided_set)
            return OmniResult(false) # Missing required field
        end
    end
    
    return OmniResult(true)
end

end
