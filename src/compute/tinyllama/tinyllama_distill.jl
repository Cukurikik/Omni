# TinyLlama — Small Model Distillation Loss in Julia
module TinyLlamaLoss
struct OmniResult{T, E}
    is_ok::Bool; value::Union{T, Nothing}; error::Union{E, Nothing}
end
function kl_divergence_loss(teacher_logits::Vector{Float64}, student_logits::Vector{Float64}, temperature::Float64)::OmniResult{Float64, String}
    if length(teacher_logits) != length(student_logits) return OmniResult{Float64, String}(false, nothing, "Logit length mismatch") end
    if temperature <= 0 return OmniResult{Float64, String}(false, nothing, "Temperature must be positive") end
    if length(teacher_logits) > 200000 return OmniResult{Float64, String}(false, nothing, "Vocab exceeds 200K") end
    t_scaled = teacher_logits ./ temperature
    s_scaled = student_logits ./ temperature
    t_probs = exp.(t_scaled .- maximum(t_scaled))
    t_probs ./= sum(t_probs)
    s_probs = exp.(s_scaled .- maximum(s_scaled))
    s_probs ./= sum(s_probs)
    kl = sum(t_probs .* log.(max.(t_probs ./ max.(s_probs, 1e-10), 1e-10)))
    return OmniResult{Float64, String}(true, kl * temperature^2, nothing)
end
end
