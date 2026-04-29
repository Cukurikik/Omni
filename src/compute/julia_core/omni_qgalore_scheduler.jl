# Omni Q-GaLore Rank Scheduler (Julia)
# Ref: VITA-Group/Q-GaLore — Apache-2.0
module OmniQGaLoreJulia

function layer_adaptive_rank(grad_norms::Vector{Float64}, base_rank::Int=64, budget::Int=512)
    total = sum(grad_norms)
    total == 0 && return fill(1, length(grad_norms))
    ranks = max.(1, round.(Int, base_rank .* (grad_norms ./ total) .* length(grad_norms)))
    while sum(ranks) > budget
        idx = argmax(ranks)
        ranks[idx] = max(1, ranks[idx] - 1)
    end
    return ranks
end

function int4_quantize(values::Vector{Float64})
    vmin, vmax = extrema(values)
    scale = vmax == vmin ? 1.0 : (vmax - vmin) / 15
    quantized = clamp.(round.(Int, (values .- vmin) ./ scale), 0, 15)
    return quantized, scale, vmin
end

function int4_dequantize(quantized::Vector{Int}, scale::Float64, zero_point::Float64)
    return quantized .* scale .+ zero_point
end

end # module
