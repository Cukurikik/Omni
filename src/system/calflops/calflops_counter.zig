// @omni-domain System Layer (CalFLOPs Counter)
// @omni-source MrYxJ/calculate-flops.pytorch
// @omni-description CalFLOPs Counter mimicking hardware perf counters in Zig.
// @omni-requirement zero-mock, monadic-error
const std = @import("std");
pub const OmniError = error{ InvalidDimension, Overflow };
pub fn OmniResult(comptime T: type) type {
    return union(enum) { Ok: T, Err: OmniError };
}

pub fn count_linear_flops(in_feat: u64, out_feat: u64, batch: u64) OmniResult(u64) {
    if (in_feat == 0 or out_feat == 0) return .{ .Err = OmniError.InvalidDimension };
    const flops = 2 * batch * in_feat * out_feat;
    return .{ .Ok = flops };
}

pub fn count_conv2d_flops(in_ch: u64, out_ch: u64, k: u64, spatial: u64, batch: u64) OmniResult(u64) {
    if (in_ch == 0 or out_ch == 0 or k == 0) return .{ .Err = OmniError.InvalidDimension };
    const flops = 2 * batch * out_ch * in_ch * k * k * spatial * spatial;
    return .{ .Ok = flops };
}

pub fn count_attention_flops(seq: u64, d_model: u64, heads: u64, batch: u64) OmniResult(u64) {
    if (seq == 0 or d_model == 0 or heads == 0) return .{ .Err = OmniError.InvalidDimension };
    const d_k = d_model / heads;
    const qkv = 6 * batch * seq * d_model * d_model;
    const attn = 2 * batch * heads * seq * seq * d_k;
    const out = 2 * batch * seq * d_model * d_model;
    return .{ .Ok = qkv + attn + out };
}
