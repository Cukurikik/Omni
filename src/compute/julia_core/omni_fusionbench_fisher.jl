# Omni FusionBench Fisher Merge (Julia)
# Ref: tanganke/fusion_bench — MIT
module OmniFusionBenchFisher

function fisher_weighted_merge(models::Vector{Vector{Float64}}, fisher_diags::Vector{Vector{Float64}})
    n = length(models); d = length(models[1])
    merged = zeros(Float64, d)
    total_fisher = zeros(Float64, d)
    for j in 1:n
        for i in 1:d
            merged[i] += fisher_diags[j][i] * models[j][i]
            total_fisher[i] += fisher_diags[j][i]
        end
    end
    for i in 1:d
        merged[i] /= max(total_fisher[i], 1e-8)
    end
    return merged
end

function compute_fisher_diagonal(gradients::Vector{Vector{Float64}})
    d = length(gradients[1])
    fisher = zeros(Float64, d)
    for g in gradients
        for i in 1:d
            fisher[i] += g[i]^2
        end
    end
    fisher ./= max(length(gradients), 1)
    return fisher
end

end # module
