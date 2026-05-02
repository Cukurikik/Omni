# @omni-domain Compute Layer (FLOP Estimation)
# @omni-source MrYxJ/calculate-flops.pytorch
# @omni-description CalFLOPs Estimator mimicking model FLOPs counting in Julia.
# @omni-requirement zero-mock, monadic-error

struct OmniResult{T}
    data::Union{T, Nothing}
    error::Union{String, Nothing}
end

OmniResult(data::T) where T = OmniResult{T}(data, nothing)
OmniResult(;error::String) = OmniResult{Nothing}(nothing, error)
is_ok(r::OmniResult) = isnothing(r.error)

struct LayerSpec
    name::String
    input_dim::Int
    output_dim::Int
    kernel_size::Int  # 0 for linear layers
end

function estimate_linear_flops(input_dim::Int, output_dim::Int, batch_size::Int)
    if input_dim <= 0 || output_dim <= 0
        return OmniResult(error="Dimensions must be positive.")
    end
    # FLOPs = 2 * batch * in * out (multiply-add)
    flops = 2 * batch_size * input_dim * output_dim
    return OmniResult(Dict("flops" => flops, "type" => "linear"))
end

function estimate_conv2d_flops(in_channels::Int, out_channels::Int, kernel::Int, spatial::Int, batch::Int)
    if in_channels <= 0 || out_channels <= 0 || kernel <= 0
        return OmniResult(error="Conv params must be positive.")
    end
    flops = 2 * batch * out_channels * in_channels * kernel * kernel * spatial * spatial
    return OmniResult(Dict("flops" => flops, "type" => "conv2d"))
end

function estimate_attention_flops(seq_len::Int, d_model::Int, n_heads::Int, batch::Int)
    if seq_len <= 0 || d_model <= 0 || n_heads <= 0
        return OmniResult(error="Attention params must be positive.")
    end
    d_k = div(d_model, n_heads)
    # QKV projections: 3 * 2 * batch * seq * d_model * d_model
    qkv_flops = 6 * batch * seq_len * d_model * d_model
    # Attention scores: batch * n_heads * seq * seq * d_k
    attn_flops = 2 * batch * n_heads * seq_len * seq_len * d_k
    # Output projection
    out_flops = 2 * batch * seq_len * d_model * d_model
    total = qkv_flops + attn_flops + out_flops
    return OmniResult(Dict("flops" => total, "type" => "attention", "qkv" => qkv_flops, "scores" => attn_flops))
end

function estimate_model_flops(layers::Vector{LayerSpec}, batch::Int)
    if isempty(layers)
        return OmniResult(error="Layer list empty.")
    end
    total = 0
    breakdown = Dict{String,Int}()
    for layer in layers
        if layer.kernel_size > 0
            r = estimate_conv2d_flops(layer.input_dim, layer.output_dim, layer.kernel_size, 1, batch)
        else
            r = estimate_linear_flops(layer.input_dim, layer.output_dim, batch)
        end
        if !is_ok(r)
            return OmniResult(error="Layer $(layer.name) failed: $(r.error)")
        end
        flops = r.data["flops"]
        total += flops
        breakdown[layer.name] = flops
    end
    return OmniResult(Dict("total_flops" => total, "breakdown" => breakdown))
end
