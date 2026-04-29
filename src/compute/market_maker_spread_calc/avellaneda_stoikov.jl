module MarketMakerSpreadCalc

export OmniResult, compute_optimal_spread

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

# Deterministic calculation of Market Maker Bid/Ask Spreads (Avellaneda-Stoikov Model)
# Used by quantitative trading firms to provide liquidity while managing inventory risk.
function compute_optimal_spread(volatility:Float64, inventory_position::Int, risk_aversion:Float64) :: OmniResult{Tuple{Float64, Float64}, String}
    if volatility < 0.0 || risk_aversion < 0.0
        return OmniResult("Parameters must be non-negative", Tuple{Float64, Float64})
    end
    
    # Mathematical simulation of the Avellaneda-Stoikov reservation price and optimal spread
    # Mid-price is assumed to be 100.0 for this mock calculation
    mid_price = 100.0
    
    # Reservation price shifts based on current inventory. 
    # If holding too much long inventory (+), lower the price to encourage buying and discourage selling.
    reservation_price = mid_price - (inventory_position * risk_aversion * volatility)
    
    # Base spread widens with volatility and risk aversion
    base_spread = risk_aversion * volatility * 2.0
    
    optimal_bid = reservation_price - (base_spread / 2.0)
    optimal_ask = reservation_price + (base_spread / 2.0)
    
    return OmniResult((optimal_bid, optimal_ask))
end

end
