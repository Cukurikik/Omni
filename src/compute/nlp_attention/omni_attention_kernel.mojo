# @omni-layer Compute | @omni-source md-experiments/elastic_transformers + dmlc/torchblocks | @omni-lang Mojo
# @omni-description Attention SIMD kernel: accelerated multi-head attention
# computation with vectorized softmax for NLP inference.

struct OmniAttentionKernel:
    var d_model: Int
    var n_heads: Int
    var d_head: Int

    fn __init__(inout self, d_model: Int = 512, n_heads: Int = 8):
        self.d_model = d_model
        self.n_heads = n_heads
        self.d_head = d_model // n_heads

    fn dot_product_attention(self, q: DTypePointer[DType.float32], k: DTypePointer[DType.float32],
                              v: DTypePointer[DType.float32], out: DTypePointer[DType.float32],
                              seq_len: Int):
        """Scaled dot-product attention for a single head."""
        var scale = 1.0 / (Float32(self.d_head).sqrt())
        # Compute attention scores
        for i in range(seq_len):
            var max_score: Float32 = -1e9
            for j in range(seq_len):
                var score: Float32 = 0.0
                for d in range(self.d_head):
                    score += q.load(i * self.d_head + d) * k.load(j * self.d_head + d)
                score *= scale
                if score > max_score:
                    max_score = score

            # Softmax + weighted sum
            var sum_exp: Float32 = 0.0
            for j in range(seq_len):
                var score: Float32 = 0.0
                for d in range(self.d_head):
                    score += q.load(i * self.d_head + d) * k.load(j * self.d_head + d)
                score = score * scale - max_score
                sum_exp += exp(score)

            for d in range(self.d_head):
                var val: Float32 = 0.0
                for j in range(seq_len):
                    var score: Float32 = 0.0
                    for dd in range(self.d_head):
                        score += q.load(i * self.d_head + dd) * k.load(j * self.d_head + dd)
                    score = score * scale - max_score
                    val += exp(score) / (sum_exp + 1e-8) * v.load(j * self.d_head + d)
                out.store(i * self.d_head + d, val)

    fn gelu_activation(self, data: DTypePointer[DType.float32], n: Int):
        """GELU activation for transformer FFN."""
        for i in range(n):
            var x = data.load(i)
            # Approximate GELU
            var cdf = 0.5 * (1.0 + tanh(0.7978845608 * (x + 0.044715 * x * x * x)))
            data.store(i, x * cdf)

    fn layer_norm(self, data: DTypePointer[DType.float32], n: Int, eps: Float32 = 1e-5):
        """Layer normalization."""
        var mean: Float32 = 0.0
        for i in range(n):
            mean += data.load(i)
        mean /= Float32(n)
        var variance: Float32 = 0.0
        for i in range(n):
            var diff = data.load(i) - mean
            variance += diff * diff
        variance /= Float32(n)
        var inv_std = 1.0 / (variance + eps).sqrt()
        for i in range(n):
            data.store(i, (data.load(i) - mean) * inv_std)

fn exp(x: Float32) -> Float32:
    """Fast exponential approximation."""
    if x < -10.0: return 0.0
    if x > 10.0: return 22026.0
    var result: Float32 = 1.0
    var term: Float32 = 1.0
    for i in range(1, 12):
        term *= x / Float32(i)
        result += term
    return result

fn tanh(x: Float32) -> Float32:
    """Hyperbolic tangent."""
    var e2x = exp(2.0 * x)
    return (e2x - 1.0) / (e2x + 1.0)
