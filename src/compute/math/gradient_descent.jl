module OmniMath

function gradient_descent(X::Matrix{Float64}, y::Vector{Float64}, theta::Vector{Float64}, alpha::Float64, num_iters::Int)
    m = length(y)
    for iter in 1:num_iters
        predictions = X * theta
        errors = predictions - y
        gradient = (1/m) * (X' * errors)
        theta = theta - alpha * gradient
    end
    return theta
end

end
