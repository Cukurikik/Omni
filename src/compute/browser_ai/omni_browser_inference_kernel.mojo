# @omni-layer Compute | @omni-source jakobhoeg/browser-ai | @omni-lang Mojo
# @omni-description Browser AI inference kernel: high-performance WASM-targeted
# matrix operations for client-side transformer inference.

struct BrowserInferenceConfig:
    var d_model: Int
    var n_heads: Int
    var seq_len: Int
    var vocab_size: Int
    fn __init__(inout self, d: Int, h: Int, s: Int, v: Int):
        self.d_model = d; self.n_heads = h; self.seq_len = s; self.vocab_size = v

fn softmax_1d(logits: DynamicVector[Float64]) -> DynamicVector[Float64]:
    var max_val: Float64 = -1e30
    for i in range(len(logits)):
        if logits[i] > max_val: max_val = logits[i]
    var result = DynamicVector[Float64]()
    var total: Float64 = 0.0
    for i in range(len(logits)):
        let e = math.exp(logits[i] - max_val)
        result.push_back(e); total += e
    for i in range(len(result)):
        result[i] /= (total + 1e-8)
    return result

fn quantize_weights_int8(weights: DynamicVector[Float64]) -> DynamicVector[Int8]:
    var max_abs: Float64 = 0.0
    for i in range(len(weights)):
        let a = math.abs(weights[i])
        if a > max_abs: max_abs = a
    let scale = max_abs / 127.0
    var quantized = DynamicVector[Int8]()
    for i in range(len(weights)):
        let q = Int8(math.round(weights[i] / (scale + 1e-8)))
        quantized.push_back(q)
    return quantized

fn dequantize_int8(quantized: DynamicVector[Int8], scale: Float64) -> DynamicVector[Float64]:
    var result = DynamicVector[Float64]()
    for i in range(len(quantized)):
        result.push_back(Float64(quantized[i]) * scale)
    return result

fn estimate_inference_flops(config: BrowserInferenceConfig) -> Int:
    let attn_flops = 2 * config.seq_len * config.seq_len * config.d_model
    let ffn_flops = 2 * config.seq_len * config.d_model * 4 * config.d_model
    let total = (attn_flops + ffn_flops) * 12  # 12 layers
    return total
