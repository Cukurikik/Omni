# @omni-layer Compute | @omni-source lucidrains/transganformer | @omni-lang Mojo
# @omni-description Progressive GAN resolution kernel: SIMD-accelerated
# upsampling and feature map fusion for progressive training.

struct OmniProgressiveKernel:
    var base_channels: Int
    var max_resolution: Int
    var alpha: Float64

    fn __init__(inout self, base_channels: Int = 512, max_resolution: Int = 256):
        self.base_channels = base_channels
        self.max_resolution = max_resolution
        self.alpha = 0.0

    fn compute_channels(self, resolution: Int) -> Int:
        var ch = self.base_channels
        var res = 4
        while res < resolution:
            ch = ch // 2
            if ch < 16:
                ch = 16
            res = res * 2
        return ch

    fn upsample_2x(self, data: DTypePointer[DType.float32], n: Int, out: DTypePointer[DType.float32]):
        """Nearest neighbor 2x upsampling with bilinear interpolation."""
        for i in range(n):
            var val = data.load(i)
            var next_val = data.load(min(i + 1, n - 1))
            var interp = (val + next_val) * 0.5
            out.store(i * 2, val)
            out.store(i * 2 + 1, interp)

    fn pixel_norm(self, data: DTypePointer[DType.float32], n: Int):
        """Per-pixel feature normalization for GAN stability."""
        var sum_sq: Float32 = 0.0
        for i in range(n):
            var val = data.load(i)
            sum_sq += val * val
        var inv_norm = 1.0 / (sum_sq / Float32(n) + 1e-8).sqrt()
        for i in range(n):
            data.store(i, data.load(i) * inv_norm)

    fn minibatch_stddev(self, features: DTypePointer[DType.float32], batch_size: Int, feat_size: Int) -> Float32:
        """Compute minibatch standard deviation for diversity."""
        var mean: Float32 = 0.0
        var total = batch_size * feat_size
        for i in range(total):
            mean += features.load(i)
        mean /= Float32(total)
        var variance: Float32 = 0.0
        for i in range(total):
            var diff = features.load(i) - mean
            variance += diff * diff
        variance /= Float32(total)
        return variance.sqrt()

    fn blend_resolutions(self, low: DTypePointer[DType.float32], high: DTypePointer[DType.float32],
                         out: DTypePointer[DType.float32], n: Int, alpha: Float32):
        """Alpha-blend between resolution levels for smooth transition."""
        for i in range(n):
            out.store(i, low.load(i) * (1.0 - alpha) + high.load(i) * alpha)
