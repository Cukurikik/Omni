module VisualQuestionAnswering

export OmniResult, compute_box_alignment

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

# Deterministic calculation of Bounding Box alignment to text coordinates
# Used in Grounded VQA to draw boxes around the exact objects the LLM is referring to
function compute_box_alignment(img_width::Float64, img_height::Float64, normalized_x::Float64, normalized_y::Float64, normalized_w::Float64, normalized_h::Float64) :: OmniResult{Tuple{Float64, Float64, Float64, Float64}, String}
    if img_width <= 0.0 || img_height <= 0.0
        return OmniResult("Image dimensions must be positive", Tuple{Float64, Float64, Float64, Float64})
    end
    
    if normalized_w < 0.0 || normalized_h < 0.0 || normalized_x < 0.0 || normalized_y < 0.0
        return OmniResult("Normalized coordinates must be non-negative", Tuple{Float64, Float64, Float64, Float64})
    end

    # Convert from normalized [0, 1] coordinates output by VQA models to absolute pixel coordinates
    abs_x = normalized_x * img_width
    abs_y = normalized_y * img_height
    abs_w = normalized_w * img_width
    abs_h = normalized_h * img_height
    
    return OmniResult((abs_x, abs_y, abs_w, abs_h))
end

end
