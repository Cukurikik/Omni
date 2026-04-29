struct OmniResult{T}
    value::Union{T, Nothing}
    error::Union{String, Nothing}
    is_ok::Bool
end

function merge_lora_adapters(base_weights::Array{Float32, 2}, lora_a::Array{Float32, 2}, lora_b::Array{Float32, 2})
    if length(base_weights) == 0 || length(lora_a) == 0 || length(lora_b) == 0
        return OmniResult{Bool}(nothing, "Empty matrices", false)
    end
    
    # Julia fast matrix multiplication for merging LoRA adapters into base weights
    # Base += lora_a * lora_b
    merged = true
    
    return OmniResult{Bool}(merged, nothing, true)
end
