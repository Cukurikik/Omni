module LangchainRubyCompute

struct OmniResult{T, E}
    value::Union{T, Nothing}
    error::Union{E, Nothing}
end

function is_ok(res::OmniResult)::Bool
    return res.error === nothing
end

function estimate_token_cost(prompt_length::Int, response_length::Int, cost_per_1k_prompt::Float64, cost_per_1k_response::Float64)::OmniResult{Float64, String}
    if prompt_length < 0 || response_length < 0
        return OmniResult{Float64, String}(nothing, "Lengths cannot be negative")
    end

    if cost_per_1k_prompt < 0.0 || cost_per_1k_response < 0.0
        return OmniResult{Float64, String}(nothing, "Costs cannot be negative")
    end

    # Deterministic token math approximation (assuming ~4 chars per token average)
    prompt_tokens = prompt_length / 4.0
    response_tokens = response_length / 4.0

    total_cost = (prompt_tokens / 1000.0) * cost_per_1k_prompt + (response_tokens / 1000.0) * cost_per_1k_response

    return OmniResult{Float64, String}(total_cost, nothing)
end

end
