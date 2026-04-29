module PydanticSchema

export OmniResult, compute_type_coercion

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

# Deterministic Type Coercion Math (e.g. String -> Int, Float -> Int)
function compute_type_coercion(value::String, target_type::Symbol) :: OmniResult{Any, String}
    try
        if target_type == :Int
            # Handle float strings being coerced to Int if they end in .0
            if occursin(".", value)
                float_val = parse(Float64, value)
                if float_val == floor(float_val)
                    return OmniResult(Int(float_val))
                else
                    return OmniResult("Data loss: Cannot coerce fractional float to Int", Any)
                end
            else
                return OmniResult(parse(Int, value))
            end
        elseif target_type == :Float
            return OmniResult(parse(Float64, value))
        elseif target_type == :Bool
            lower = lowercase(value)
            if lower in ["true", "1", "yes", "on"]
                return OmniResult(true)
            elseif lower in ["false", "0", "no", "off"]
                return OmniResult(false)
            else
                return OmniResult("Cannot coerce to Bool", Any)
            end
        elseif target_type == :String
            return OmniResult(value)
        else
            return OmniResult("Unknown target type", Any)
        end
    catch e
        return OmniResult("Coercion failed: " * sprint(showerror, e), Any)
    end
end

end
