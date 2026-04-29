# Omni DuQuant Hadamard (Julia)
module OmniDuQuant
function hadamard_rotate(x::Vector{Float64})
    n = length(x); n == 0 && return Float64[]
    factor = 1.0 / sqrt(n); out = zeros(n)
    for i in 1:n, j in 1:n
        sign = count_ones((i-1) & (j-1)) % 2 == 0 ? 1 : -1
        out[i] += sign * x[j]
    end
    out .* factor
end
function outlier_ratio(w::Vector{Float64}, thresh::Float64 = 3.0)
    n = length(w); n == 0 && return 0.0
    μ = sum(w)/n; σ = sqrt(sum((w .- μ).^2)/n)
    count(x -> abs(x - μ) > thresh * σ, w) / n
end
end
