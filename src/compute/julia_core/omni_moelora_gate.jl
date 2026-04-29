# Omni MOELoRA Gate (Julia)
module OmniMOELoRA
function softmax_gate(logits::Vector{Float64})
    mx = maximum(logits); exps = exp.(logits .- mx); s = sum(exps); exps ./ s
end
function load_balance_loss(gate_batch::Vector{Vector{Float64}}, n_experts::Int)
    B = length(gate_batch); B == 0 && return 0.0
    avg = zeros(n_experts); freq = zeros(n_experts)
    for g in gate_batch
        top = argmax(g); freq[top] += 1.0 / B
        for e in 1:n_experts; avg[e] += g[e] / B; end
    end
    n_experts * sum(avg .* freq)
end
end
