module DoclingExtractor

struct OmniResult{T, E}
    value::Union{T, Nothing}
    error::Union{E, Nothing}
end

function is_ok(res::OmniResult)::Bool
    return res.error === nothing
end

struct BoundingBox
    x0::Float64
    y0::Float64
    x1::Float64
    y1::Float64
end

struct TextElement
    text::String
    bbox::BoundingBox
    confidence::Float64
end

function parse_pdf_layout(elements::Vector{TextElement})::OmniResult{Vector{Vector{TextElement}}, String}
    if isempty(elements)
        return OmniResult{Vector{Vector{TextElement}}, String}(nothing, "Element list is empty")
    end

    # Deterministic mathematical clustering for layout parsing (Y-axis based line clustering)
    sort!(elements, by = e -> e.bbox.y0)
    
    lines = Vector{Vector{TextElement}}()
    current_line = [elements[1]]
    
    # 5.0 is the mathematical threshold for Y-axis deviation to be considered the same line
    Y_TOLERANCE = 5.0
    
    for i in 2:length(elements)
        element = elements[i]
        last_element = current_line[end]
        
        # Check if the current element is on the same line as the previous one
        if abs(element.bbox.y0 - last_element.bbox.y0) <= Y_TOLERANCE || 
           abs(element.bbox.y1 - last_element.bbox.y1) <= Y_TOLERANCE
            push!(current_line, element)
        else
            # Sort current line by X coordinate before pushing
            sort!(current_line, by = e -> e.bbox.x0)
            push!(lines, current_line)
            current_line = [element]
        end
    end
    
    if !isempty(current_line)
        sort!(current_line, by = e -> e.bbox.x0)
        push!(lines, current_line)
    end

    return OmniResult{Vector{Vector{TextElement}}, String}(lines, nothing)
end

end
