// Omni ST-LLM Julia SIMD (Julia)
// Compute Layer: Vectorized temporal position encoding.
// Ref: TencentARC/ST-LLM — ECCV 2024
module OmniSTLLM
function temporal_pe(seq_len::Int, d_model::Int)
    pe = zeros(Float64, seq_len, d_model)
    for pos in 1:seq_len, i in 1:d_model
        angle = (pos - 1) / (10000.0 ^ ((i - 1) / d_model))
        pe[pos, i] = iseven(i) ? cos(angle) : sin(angle)
    end
    return pe
end
end
