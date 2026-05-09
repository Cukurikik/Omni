# OMNI MOTHER: Julia Entropy Calculation
# Calculates routing entropy to measure load balancing efficiency

module OmniMoEEntropy

export calculate_entropy

function calculate_entropy(routing_probs::Vector{Float64})
    entropy = 0.0
    for p in routing_probs
        if p > 0.0
            entropy -= p * log2(p)
        end
    end
    return entropy
end

end
