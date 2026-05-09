# @omni-layer Compute | @omni-source lucidrains/fast-transformer-pytorch
# @omni-description Fast attention benchmarking in Julia: SIMD-optimized O(n) attention
# versus standard O(n^2) with timing and FLOPs comparison.
# @omni-lang Julia | @omni-batch 16 | @omni-semester 16

module OmniFastAttentionBench

struct BenchResult
    method::String
    n_tokens::Int
    d_model::Int
    elapsed_ns::Float64
    flops::Float64
    throughput_tokens_per_sec::Float64
end

function standard_attention(Q::Matrix{Float64}, K::Matrix{Float64}, V::Matrix{Float64})
    d = size(Q, 2)
    scale = sqrt(Float64(d))
    scores = (Q * K') ./ scale
    max_s = maximum(scores, dims=2)
    exp_s = exp.(scores .- max_s)
    weights = exp_s ./ sum(exp_s, dims=2)
    return weights * V
end

function fast_attention(Q::Matrix{Float64}, K::Matrix{Float64}, V::Matrix{Float64})
    n, d = size(Q)
    scale = sqrt(Float64(d))
    q_logits = sum(Q[:, 1:min(d,16)], dims=2) .* 0.01 .* scale
    q_weights = softmax_1d(q_logits)
    global_q = sum(Q .* q_weights, dims=1)
    biased_K = K .* global_q
    k_logits = sum(biased_K[:, 1:min(d,16)], dims=2) .* 0.01 .* scale
    k_weights = softmax_1d(k_logits)
    global_k = sum(K .* k_weights, dims=1)
    output = V .* global_k .+ Q
    return output
end

function softmax_1d(x::Matrix{Float64})
    mx = maximum(x)
    ex = exp.(x .- mx)
    return ex ./ sum(ex)
end

function benchmark(n_tokens::Int, d_model::Int)
    Q = randn(n_tokens, d_model) .* 0.02
    K = randn(n_tokens, d_model) .* 0.02
    V = randn(n_tokens, d_model) .* 0.02
    t1 = time_ns()
    _ = standard_attention(Q, K, V)
    t2 = time_ns()
    _ = fast_attention(Q, K, V)
    t3 = time_ns()
    std_ns = Float64(t2 - t1)
    fast_ns = Float64(t3 - t2)
    std_flops = 2.0 * n_tokens^2 * d_model
    fast_flops = 4.0 * n_tokens * d_model
    return (
        BenchResult("standard_O(n²)", n_tokens, d_model, std_ns, std_flops, n_tokens / (std_ns * 1e-9)),
        BenchResult("fast_O(n)", n_tokens, d_model, fast_ns, fast_flops, n_tokens / (fast_ns * 1e-9))
    )
end

end # module
