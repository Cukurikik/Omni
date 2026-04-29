# LLM-Inference — Speculative Decoding Acceptance Probability in Julia
module SpeculativeDecode
struct OmniResult{T, E}
    is_ok::Bool; value::Union{T, Nothing}; error::Union{E, Nothing}
end
function acceptance_probability(draft_prob::Float64, target_prob::Float64)::OmniResult{Float64, String}
    if draft_prob < 0 || draft_prob > 1 return OmniResult{Float64, String}(false, nothing, "Draft prob out of [0,1]") end
    if target_prob < 0 || target_prob > 1 return OmniResult{Float64, String}(false, nothing, "Target prob out of [0,1]") end
    if draft_prob == 0 return OmniResult{Float64, String}(true, 1.0, nothing) end
    accept = min(1.0, target_prob / draft_prob)
    return OmniResult{Float64, String}(true, accept, nothing)
end
end
