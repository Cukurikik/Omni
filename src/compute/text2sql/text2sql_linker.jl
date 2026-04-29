# Text2SQL Schema Linker — Julia compute
module Text2SQLLinker

struct OmniResult{T, E}
    is_ok::Bool; value::Union{T, Nothing}; error::Union{E, Nothing}
end

const MAX_TABLES = 200
const MAX_COLUMNS_PER_TABLE = 500

struct TableSchema
    name::String; columns::Vector{String}; types::Vector{String}
end

function link_schema(question::String, schemas::Vector{TableSchema})::OmniResult{Vector{String}, String}
    if isempty(question)
        return OmniResult{Vector{String}, String}(false, nothing, "Empty question")
    end
    if length(schemas) > MAX_TABLES
        return OmniResult{Vector{String}, String}(false, nothing, "Tables exceed $MAX_TABLES")
    end
    tokens = lowercase.(split(question))
    matched = String[]
    for schema in schemas
        if length(schema.columns) > MAX_COLUMNS_PER_TABLE
            return OmniResult{Vector{String}, String}(false, nothing, "Columns exceed limit for $(schema.name)")
        end
        for col in schema.columns
            if lowercase(col) in tokens
                push!(matched, "$(schema.name).$(col)")
            end
        end
    end
    return OmniResult{Vector{String}, String}(true, matched, nothing)
end

end
