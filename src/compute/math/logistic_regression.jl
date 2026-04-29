module OmniMathLogReg

using LinearAlgebra

sigmoid(z::Float64) = 1.0 / (1.0 + exp(-z))

function cost_function(theta::Vector{Float64}, X::Matrix{Float64}, y::Vector{Float64})
    m = length(y)
    h = sigmoid.(X * theta)
    J = (1/m) * sum(-y .* log.(h) - (1 .- y) .* log.(1 .- h))
    grad = (1/m) * (X' * (h - y))
    return J, grad
end

end
