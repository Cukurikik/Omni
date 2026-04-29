module DocExtractorCompute

struct OmniResult{T, E}
    value::Union{T, Nothing}
    error::Union{E, Nothing}
end

function is_ok(res::OmniResult)::Bool
    return res.error === nothing
end

struct BBox
    x0::Float64
    y0::Float64
    x1::Float64
    y1::Float64
end

struct OCRToken
    text::String
    box::BBox
end

function align_lines(tokens::Vector{OCRToken}, vertical_tolerance::Float64)::OmniResult{Vector{Vector{OCRToken}}, String}
    if isempty(tokens)
        return OmniResult{Vector{Vector{OCRToken}}, String}([], nothing)
    end

    if vertical_tolerance < 0.0
        return OmniResult{Vector{Vector{OCRToken}}, String}(nothing, "Tolerance must be positive")
    end

    # Deterministic spatial clustering algorithm for line formation
    
    # 1. Sort tokens by Y coordinate primarily, X secondarily
    sorted_tokens = sort(tokens, by = t -> (t.box.y0, t.box.x0))
    
    lines = Vector{Vector{OCRToken}}()
    current_line = Vector{OCRToken}()
    
    current_y0 = sorted_tokens[1].box.y0
    current_y1 = sorted_tokens[1].box.y1
    
    for token in sorted_tokens
        # Check if vertically aligned within tolerance
        # Compare token's vertical center with current line's vertical bounds
        center_y = (token.box.y0 + token.box.y1) / 2.0
        
        if center_y >= current_y0 - vertical_tolerance && center_y <= current_y1 + vertical_tolerance
            push!(current_line, token)
            # Expand bounding box
            current_y0 = min(current_y0, token.box.y0)
            current_y1 = max(current_y1, token.box.y1)
        else
            # Start new line
            # Sort current line by X coordinate before saving
            sort!(current_line, by = t -> t.box.x0)
            push!(lines, current_line)
            
            current_line = [token]
            current_y0 = token.box.y0
            current_y1 = token.box.y1
        end
    end
    
    if !isempty(current_line)
        sort!(current_line, by = t -> t.box.x0)
        push!(lines, current_line)
    end

    return OmniResult{Vector{Vector{OCRToken}}, String}(lines, nothing)
end

end
