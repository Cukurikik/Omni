# OMNI MOTHER: Julia Statistical Engine
# Calculates variance of load across experts

module OmniMoELoadStats

export calculate_variance

function calculate_variance(loads::Vector{Float64})
    n = length(loads)
    if n <= 1
        return 0.0
    end
    mean_val = sum(loads) / n
    return sum((x - mean_val)^2 for x in loads) / (n - 1)
end

end
