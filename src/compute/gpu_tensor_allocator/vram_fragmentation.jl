module GpuTensorAllocator

export OmniResult, compute_vram_fragmentation

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

# Deterministic calculation of GPU VRAM fragmentation
# Crucial for preventing Out Of Memory (OOM) errors during LLM inference on NVIDIA hardware
function compute_vram_fragmentation(total_vram_mb::Float64, largest_free_block_mb::Float64, free_vram_mb::Float64) :: OmniResult{Float64, String}
    if total_vram_mb <= 0.0 || largest_free_block_mb < 0.0 || free_vram_mb < 0.0
        return OmniResult("Invalid VRAM metrics", Float64)
    end
    
    if largest_free_block_mb > free_vram_mb
        return OmniResult("Largest free block cannot exceed total free VRAM", Float64)
    end
    
    if free_vram_mb == 0.0
        return OmniResult(1.0) # 100% fragmented / full
    end
    
    # Fragmentation Index: 0.0 is perfect contiguous memory, 1.0 is totally shattered
    fragmentation = 1.0 - (largest_free_block_mb / free_vram_mb)
    
    return OmniResult(fragmentation)
end

end
