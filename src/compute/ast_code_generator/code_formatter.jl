module ASTCodeGenerator

export OmniResult, compute_indentation

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

# Deterministic calculation of indentation levels for AST serialization
# Used to enforce consistent code formatting across the 15+ OMNI languages
function compute_indentation(ast_depth::Int, spaces_per_tab::Int) :: OmniResult{String, String}
    if ast_depth < 0 || spaces_per_tab <= 0
        return OmniResult("Invalid AST depth or tab size", String)
    end
    
    total_spaces = ast_depth * spaces_per_tab
    indent_string = repeat(" ", total_spaces)
    
    return OmniResult(indent_string)
end

end
