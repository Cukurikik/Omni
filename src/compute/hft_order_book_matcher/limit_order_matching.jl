module HftOrderBookMatcher

export OmniResult, compute_order_match

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

# Deterministic calculation of High-Frequency Trading Limit Order Matching
# Follows strict Price-Time priority matching logic for financial exchanges.
function compute_order_match(incoming_order_price::Float64, incoming_order_qty::Int, is_buy::Bool, book_best_price::Float64, book_best_qty::Int) :: OmniResult{Tuple{Int, Int}, String}
    if incoming_order_qty <= 0 || book_best_qty <= 0
        return OmniResult("Quantities must be positive", Tuple{Int, Int})
    end
    
    matched_qty = 0
    remaining_qty = incoming_order_qty
    
    # Matching logic
    if is_buy
        if incoming_order_price >= book_best_price
            matched_qty = min(remaining_qty, book_best_qty)
            remaining_qty -= matched_qty
        end
    else # is_sell
        if incoming_order_price <= book_best_price
            matched_qty = min(remaining_qty, book_best_qty)
            remaining_qty -= matched_qty
        end
    end
    
    return OmniResult((matched_qty, remaining_qty))
end

end
