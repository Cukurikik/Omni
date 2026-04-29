// Omni UoT Entropy Kernel (Zig)
// Ref: zhiyuanhubj/UoT — NeurIPS 2024
const std = @import("std");
const math = std.math;
pub fn entropy(probs: []const f64) f64 {
    var h: f64 = 0;
    for (probs) |p| {
        if (p > 1e-12) h -= p * math.log2(p);
    }
    return h;
}
pub fn information_gain(prior: []const f64, posterior: []const f64) f64 {
    const h_prior = entropy(prior);
    const h_post = entropy(posterior);
    return if (h_prior > h_post) h_prior - h_post else 0;
}
