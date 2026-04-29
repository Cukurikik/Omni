module PEFTTrainer

export OmniResult, train_lora_layer

struct OmniResult{T}
    value::Union{T, Nothing}
    error::Union{String, Nothing}
    is_ok::Bool
end

function train_lora_layer(base_weights::Array{Float64, 2}, rank::Int)::OmniResult{Array{Float64, 2}}
    if rank <= 0
        return OmniResult{Array{Float64, 2}}(nothing, "Rank must be positive", false)
    end
    
    rows, cols = size(base_weights)
    A = randn(rows, rank) .* 0.01
    B = randn(rank, cols) .* 0.01
    
    delta_w = A * B
    updated_weights = base_weights .+ delta_w
    
    return OmniResult{Array{Float64, 2}}(updated_weights, nothing, true)
end

end
