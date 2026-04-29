# Omni LoRI Interference Analysis (Julia)
module OmniLoRI
using LinearAlgebra
function task_interference(deltas::Vector{Vector{Float64}})
    n = length(deltas); n < 2 && return 0.0
    total = 0.0; pairs = 0
    for i in 1:n, j in (i+1):n
        cosine = dot(deltas[i], deltas[j]) / (max(norm(deltas[i]),1e-8) * max(norm(deltas[j]),1e-8))
        total += abs(cosine); pairs += 1
    end
    total / pairs
end
function ortho_reg_loss(A::Matrix{Float64}, λ::Float64 = 0.1)
    G = A * A'; I = Matrix{Float64}(LinearAlgebra.I, size(G))
    λ * sum((G .- I).^2)
end
end
