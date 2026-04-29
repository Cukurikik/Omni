module CVEdgeInference

struct OmniResult{T, E}
    value::Union{T, Nothing}
    error::Union{E, Nothing}
end

function is_ok(res::OmniResult)::Bool
    return res.error === nothing
end

function run_tensor_inference(image_tensor::Matrix{Float64}, weights::Matrix{Float64})::OmniResult{Vector{Float64}, String}
    # Validate dimensions for simple Fully Connected layer simulation
    img_rows, img_cols = size(image_tensor)
    w_rows, w_cols = size(weights)
    
    img_flat_size = img_rows * img_cols
    if img_flat_size != w_rows
        return OmniResult{Vector{Float64}, String}(nothing, "Tensor dimension mismatch for inference")
    end

    # Deterministic inference simulation (Flatten -> MatMul -> ReLU)
    flattened = reshape(image_tensor, img_flat_size)
    
    logits = weights' * flattened
    
    # ReLU Activation
    activations = [max(0.0, x) for x in logits]
    
    return OmniResult{Vector{Float64}, String}(activations, nothing)
end

end
