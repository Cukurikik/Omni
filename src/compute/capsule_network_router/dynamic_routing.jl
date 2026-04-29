module CapsuleNetworkRouter

export OmniResult, compute_dynamic_routing

struct OmniResult{T, E}
    value::Union{T, Nothing}
    error::Union{E, Nothing}
    is_ok::Bool
end

function OmniResult(value::T) where T
    OmniResult{T, String}(value, nothing, true)
end

function OmniResult(error::String, ::Type{T}=Any) where T
    OmniResult{T, String}(nothing, error, false)
end

# Deterministic simulation of Dynamic Routing Between Capsules
function compute_dynamic_routing(u_hat::Vector{Float64}, iterations::Int) :: OmniResult{Vector{Float64}, String}
    if iterations <= 0
        return OmniResult("Routing iterations must be positive", Vector{Float64})
    end
    
    if isempty(u_hat)
        return OmniResult("Input predictions (u_hat) cannot be empty", Vector{Float64})
    end

    # Initialize routing logits b_ij to zero
    b = zeros(Float64, length(u_hat))
    v = zeros(Float64, length(u_hat))
    
    for r in 1:iterations
        # c_ij = softmax(b_ij)
        exp_b = exp.(b)
        c = exp_b ./ sum(exp_b)
        
        # s_j = sum(c_ij * u_hat_j|i)
        s = sum(c .* u_hat)
        
        # v_j = squash(s_j) (Vector magnitude squashing function)
        s_norm_sq = s^2
        squash_factor = s_norm_sq / (1.0 + s_norm_sq) / sqrt(s_norm_sq + 1e-9)
        v = squash_factor .* s .* ones(Float64, length(u_hat))
        
        # b_ij = b_ij + u_hat_j|i * v_j
        b = b .+ (u_hat .* v)
    end
    
    return OmniResult(v)
end

end
