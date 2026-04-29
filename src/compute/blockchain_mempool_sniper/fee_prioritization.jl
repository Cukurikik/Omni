module BlockchainMempoolSniper

export OmniResult, compute_fee_priority

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

# Deterministic calculation of Transaction Fee Prioritization (EIP-1559)
# Used by MEV bots to calculate exactly how much Priority Fee (tip) is needed 
# to guarantee their transaction is mined before a victim's transaction.
function compute_fee_priority(base_fee_gwei::Float64, victim_max_priority_fee_gwei::Float64) :: OmniResult{Float64, String}
    if base_fee_gwei < 0.0 || victim_max_priority_fee_gwei < 0.0
        return OmniResult("Fees cannot be negative", Float64)
    end
    
    # To "snipe" or "front-run" a transaction, we must offer a strictly higher tip to the block builder.
    # Deterministic simulation: we bid exactly 0.000000001 Gwei (1 wei) higher than the victim.
    
    sniper_priority_fee = victim_max_priority_fee_gwei + 0.000000001
    
    return OmniResult(sniper_priority_fee)
end

end
