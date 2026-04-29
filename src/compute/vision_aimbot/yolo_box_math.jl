module VisionAimbotCompute

struct OmniResult{T, E}
    value::Union{T, Nothing}
    error::Union{E, Nothing}
end

function is_ok(res::OmniResult)::Bool
    return res.error === nothing
end

struct BoundingBox
    x1::Float64
    y1::Float64
    x2::Float64
    y2::Float64
end

function calculate_iou(boxA::BoundingBox, boxB::BoundingBox)::OmniResult{Float64, String}
    # Deterministic Intersection over Union (IoU) Math
    
    if boxA.x1 >= boxA.x2 || boxA.y1 >= boxA.y2 || boxB.x1 >= boxB.x2 || boxB.y1 >= boxB.y2
        return OmniResult{Float64, String}(nothing, "Invalid bounding box coordinates")
    end

    x_left = max(boxA.x1, boxB.x1)
    y_top = max(boxA.y1, boxB.y1)
    x_right = min(boxA.x2, boxB.x2)
    y_bottom = min(boxA.y2, boxB.y2)

    if x_right < x_left || y_bottom < y_top
        return OmniResult{Float64, String}(0.0, nothing) # No overlap
    end

    intersection_area = (x_right - x_left) * (y_bottom - y_top)

    boxA_area = (boxA.x2 - boxA.x1) * (boxA.y2 - boxA.y1)
    boxB_area = (boxB.x2 - boxB.x1) * (boxB.y2 - boxB.y1)

    union_area = boxA_area + boxB_area - intersection_area

    if union_area <= 0.0
        return OmniResult{Float64, String}(nothing, "Area calculation error")
    end

    iou = intersection_area / union_area

    return OmniResult{Float64, String}(iou, nothing)
end

end
