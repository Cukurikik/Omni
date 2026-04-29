const std = @import("std");

pub fn OmniResult(comptime T: type) type {
    return struct {
        value: T,
        error_msg: ?[]const u8,
        is_ok: bool,
    };
}

pub fn forward_pass(x: f32, w: f32) OmniResult(f32) {
    // Computes y = x * w
    const y = x * w;
    return .{ .value = y, .error_msg = null, .is_ok = true };
}

pub fn backward_pass(dout: f32, x: f32) OmniResult(f32) {
    // Computes dw = x * dout
    const dw = x * dout;
    return .{ .value = dw, .error_msg = null, .is_ok = true };
}
