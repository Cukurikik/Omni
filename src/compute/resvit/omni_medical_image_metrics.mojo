# @omni-layer Compute | @omni-source icon-lab/ResViT
# @omni-description Medical image quality metrics in Mojo: PSNR, SSIM, and
# perceptual quality for synthesized medical images.
# @omni-lang Mojo | @omni-batch 16 | @omni-semester 16

from math import sqrt, log10, exp

struct MedicalImageMetrics:
    var height: Int
    var width: Int

    fn __init__(inout self, height: Int, width: Int):
        self.height = height
        self.width = width

    fn psnr(self, original: DynamicVector[Float64], synthesized: DynamicVector[Float64]) -> Float64:
        var n = min(len(original), len(synthesized))
        if n == 0: return 0.0
        var mse: Float64 = 0.0
        for i in range(n):
            var diff = original[i] - synthesized[i]
            mse += diff * diff
        mse /= Float64(n)
        if mse < 1e-10: return 100.0
        var max_val: Float64 = 1.0
        return 10.0 * log10(max_val * max_val / mse)

    fn ssim_channel(self, x: DynamicVector[Float64], y: DynamicVector[Float64]) -> Float64:
        var n = min(len(x), len(y))
        if n == 0: return 0.0
        var mean_x: Float64 = 0.0
        var mean_y: Float64 = 0.0
        for i in range(n):
            mean_x += x[i]
            mean_y += y[i]
        mean_x /= Float64(n)
        mean_y /= Float64(n)
        var var_x: Float64 = 0.0
        var var_y: Float64 = 0.0
        var cov: Float64 = 0.0
        for i in range(n):
            var dx = x[i] - mean_x
            var dy = y[i] - mean_y
            var_x += dx * dx
            var_y += dy * dy
            cov += dx * dy
        var_x /= Float64(n)
        var_y /= Float64(n)
        cov /= Float64(n)
        var c1: Float64 = 0.0001
        var c2: Float64 = 0.0009
        var num = (2.0 * mean_x * mean_y + c1) * (2.0 * cov + c2)
        var den = (mean_x * mean_x + mean_y * mean_y + c1) * (var_x + var_y + c2)
        return num / den

    fn comprehensive_eval(self, original: DynamicVector[Float64], synthesized: DynamicVector[Float64]) -> DynamicVector[Float64]:
        var results = DynamicVector[Float64]()
        results.push_back(self.psnr(original, synthesized))
        results.push_back(self.ssim_channel(original, synthesized))
        var n = min(len(original), len(synthesized))
        var mae: Float64 = 0.0
        for i in range(n):
            var diff = original[i] - synthesized[i]
            if diff < 0: diff = -diff
            mae += diff
        mae /= Float64(max(n, 1))
        results.push_back(mae)
        return results
