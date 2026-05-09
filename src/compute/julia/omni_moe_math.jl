module OmniMoEMath

# OMNI MOTHER: Julia Numerical Computing for MoE

export compute_imbalance_factor

function compute_imbalance_factor(expert_loads::Vector{Float64})
    N = length(expert_loads)
    if N == 0
        return 1.0
    end
    
    mean_load = sum(expert_loads) / N
    if mean_load == 0
        return 1.0
    end
    
    variance = sum((x - mean_load)^2 for x in expert_loads) / N
    cv_squared = variance / (mean_load^2)
    
    return 1.0 + cv_squared
end

end
