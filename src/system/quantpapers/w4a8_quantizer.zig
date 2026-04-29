const std = @import("std");

pub fn OmniResult(comptime T: type) type {
    return struct {
        value: T,
        error_msg: ?[]const u8,
        is_ok: bool,
    };
}

pub fn quantize_w4a8(allocator: std.mem.Allocator, weights: []const f32) OmniResult([]u8) {
    if (weights.len == 0) {
        return .{ .value = &[_]u8{}, .error_msg = "Empty weights", .is_ok = false };
    }
    
    var quantized = allocator.alloc(u8, weights.len) catch |err| {
        return .{ .value = &[_]u8{}, .error_msg = "Allocation failed", .is_ok = false };
    };
    
    for (weights, 0..) |w, i| {
        // Clamp and scale to 4-bit/8-bit range mathematically
        const scaled = @max(0.0, @min(255.0, w * 127.5 + 128.0));
        quantized[i] = @as(u8, @intFromFloat(scaled));
    }
    
    return .{ .value = quantized, .error_msg = null, .is_ok = true };
}
