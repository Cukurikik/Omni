// Omni Flora Gradient Stats (Julia)
// Ref: BorealisAI/flora-opt — ICML 2024
module OmniFloraJulia
function compression_ratio(orig_dim::Int, proj_dim::Int)
    return 1.0 - proj_dim / orig_dim
end
function gradient_norm(grad::Vector{Float64})
    return sqrt(sum(g^2 for g in grad))
end
function random_project(grad::Vector{Float64}, proj_dim::Int, seed::Int=42)
    compressed = zeros(Float64, proj_dim)
    scale = 1.0 / sqrt(proj_dim)
    for (i, g) in enumerate(grad)
        h = mod(seed * i * 2654435761, proj_dim) + 1
        sign = mod(seed * i * 2246822519, 2) == 0 ? 1.0 : -1.0
        compressed[h] += g * sign * scale
    end
    return compressed
end
end
