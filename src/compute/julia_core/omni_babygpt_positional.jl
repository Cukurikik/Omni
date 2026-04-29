// Omni BabyGPT Positional Encoding (Julia)
// Ref: TatevKaren/BabyGPT-Build_GPT_From_Scratch
module OmniBabyGPTJulia
function positional_encoding(seq_len::Int, d_model::Int)
    pe = zeros(Float64, seq_len, d_model)
    for pos in 1:seq_len
        for i in 1:d_model
            angle = (pos - 1) / (10000.0 ^ (2 * div(i - 1, 2) / d_model))
            pe[pos, i] = iseven(i) ? cos(angle) : sin(angle)
        end
    end
    return pe
end
function layer_norm(x::Vector{Float64}; eps::Float64=1e-5)
    mu = mean(x); sigma = sqrt(sum((xi - mu)^2 for xi in x) / length(x) + eps)
    return [(xi - mu) / sigma for xi in x]
end
end
